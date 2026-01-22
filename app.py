"""
Main Streamlit application for the AI Booking Assistant.
Implements chat-based UI with RAG and booking flow.
"""

import streamlit as st
import logging
import os
from datetime import datetime
from typing import List, Tuple
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import custom modules
from db import initialize_db, get_or_create_customer, save_booking
from rag import (
    extract_text_from_pdf,
    chunk_text,
    add_documents_to_store,
    answer_with_rag,
    detect_booking_intent,
)
from booking import (
    BookingState,
    extract_field_value,
    get_next_field_prompt,
    format_booking_summary,
)
from email_utils import send_confirmation_email

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="AI Booking Assistant",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database
initialize_db()

# Session state initialization
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

if "booking_state" not in st.session_state:
    st.session_state.booking_state = BookingState()

if "in_booking_flow" not in st.session_state:
    st.session_state.in_booking_flow = False

if "pdf_uploaded" not in st.session_state:
    st.session_state.pdf_uploaded = False


def add_to_conversation_history(user_message: str, assistant_message: str):
    """Add message pair to conversation history (maintain last 20-25 messages)."""
    st.session_state.conversation_history.append((user_message, assistant_message))

    # Keep only last 20-25 message pairs (40-50 individual messages)
    if len(st.session_state.conversation_history) > 25:
        st.session_state.conversation_history = st.session_state.conversation_history[-25:]


def display_chat_history():
    """Display all messages in chat history."""
    for user_msg, assistant_msg in st.session_state.conversation_history:
        with st.chat_message("user"):
            st.markdown(user_msg)
        with st.chat_message("assistant"):
            st.markdown(assistant_msg)


def process_booking_input(user_input: str) -> str:
    """Process user input during booking flow."""
    booking_state = st.session_state.booking_state

    # If booking is not complete, continue collecting fields
    if not booking_state.is_complete():
        missing_fields = booking_state.get_missing_fields()
        current_field = missing_fields[0]

        # Validate and extract field value
        is_valid, error_msg, cleaned_value = extract_field_value(
            user_input, current_field
        )

        if not is_valid:
            return f"❌ {error_msg}\n\n{get_next_field_prompt(current_field)}"

        # Set the field value
        booking_state.set_field(current_field, cleaned_value)

        # If all fields are now complete, show summary
        if booking_state.is_complete():
            summary = format_booking_summary(booking_state.to_dict())
            return (
                summary
                + "\n\nPlease reply with **'yes'** or **'confirm'** to save this booking."
            )

        # Move to next field
        next_field = booking_state.get_missing_fields()[0]
        return get_next_field_prompt(next_field)

    # All fields complete, waiting for confirmation
    if user_input.lower() in ["yes", "confirm", "ok", "proceed", "save"]:
        try:
            booking_data = booking_state.to_dict()

            # Get or create customer
            customer_id = get_or_create_customer(
                name=booking_data["name"],
                email=booking_data["email"],
                phone=booking_data["phone"],
            )

            # Save booking
            booking_id = save_booking(
                customer_id=customer_id,
                booking_type=booking_data["booking_type"],
                date=booking_data["date"],
                time=booking_data["time"],
            )

            # Send confirmation email
            email_sent = send_confirmation_email(
                recipient_email=booking_data["email"],
                customer_name=booking_data["name"],
                booking_type=booking_data["booking_type"],
                booking_date=booking_data["date"],
                booking_time=booking_data["time"],
            )

            # Prepare response
            response = f"""✅ **Booking Confirmed!**

Your booking has been successfully saved.
- **Booking ID:** {booking_id}
- **Confirmation Status:** Saved in database

"""
            if email_sent:
                response += "📧 A confirmation email has been sent to your email address.\n\n"
            else:
                response += "📧 Note: Could not send confirmation email. Please save your booking details.\n\n"

            response += (
                "Thank you for using our AI Booking Assistant! Type 'new booking' for another booking."
            )

            # Reset booking state
            st.session_state.booking_state.reset()
            st.session_state.in_booking_flow = False

            return response

        except Exception as e:
            logger.error(f"Error saving booking: {e}")
            return f"❌ Error saving booking: {str(e)}\n\nPlease try again or contact support."

    elif user_input.lower() in ["no", "cancel", "back"]:
        st.session_state.booking_state.reset()
        st.session_state.in_booking_flow = False
        return "Booking cancelled. How can I help you today?"

    else:
        return "Please reply with **'yes'** to confirm or **'no'** to cancel this booking."


def main():
    """Main application function."""
    st.title("📅 AI Booking Assistant")
    st.markdown(
        "Your intelligent booking and information assistant powered by AI and RAG."
    )

    # Sidebar configuration
    st.sidebar.title("⚙️ Configuration")

    # Navigation
    page = st.sidebar.radio("Navigation", ["Chat", "Admin Dashboard"])

    if page == "Admin Dashboard":
        st.sidebar.markdown("---")
        st.info("Redirecting to Admin Dashboard...")
        # In production, use proper multi-page setup with Streamlit pages
        st.warning("To access the admin dashboard, run: `streamlit run admin.py`")
        return

    # Chat page
    st.sidebar.markdown("---")
    st.sidebar.subheader("📄 Document Upload")

    uploaded_pdf = st.sidebar.file_uploader(
        "Upload PDF for knowledge base:", type=["pdf"], key="pdf_uploader"
    )

    if uploaded_pdf is not None:
        try:
            with st.sidebar.spinner("Processing PDF..."):
                # Extract text
                pdf_text = extract_text_from_pdf(uploaded_pdf)

                # Chunk text
                chunks = chunk_text(pdf_text)

                # Add to vector store
                add_documents_to_store(chunks)

                st.sidebar.success(
                    f"✅ PDF processed! ({len(chunks)} chunks added to knowledge base)"
                )
                st.session_state.pdf_uploaded = True

        except Exception as e:
            st.sidebar.error(f"❌ Error processing PDF: {str(e)}")
            logger.error(f"Error processing PDF: {e}")

    # Chat interface
    st.markdown("---")

    # Display conversation history
    display_chat_history()

    # Chat input
    user_input = st.chat_input(
        "Type your message or booking request...",
        key="chat_input",
    )

    if user_input:
        # Add user message to display
        with st.chat_message("user"):
            st.markdown(user_input)

        # Process message
        with st.spinner("Processing..."):
            try:
                # Check if we're in booking flow
                if st.session_state.in_booking_flow:
                    assistant_response = process_booking_input(user_input)
                else:
                    # Detect booking intent
                    is_booking_intent = detect_booking_intent(user_input)

                    if is_booking_intent and user_input.lower().strip() in [
                        "new booking",
                        "make a booking",
                        "book",
                        "booking",
                        "schedule appointment",
                    ]:
                        # Start booking flow
                        st.session_state.in_booking_flow = True
                        st.session_state.booking_state.reset()
                        next_field = st.session_state.booking_state.get_missing_fields()[
                            0
                        ]
                        assistant_response = (
                            "🎯 Great! Let's start your booking process.\n\n"
                            + get_next_field_prompt(next_field)
                        )

                    else:
                        # Use RAG to answer question
                        assistant_response = answer_with_rag(
                            user_input, st.session_state.conversation_history
                        )

                        # Check if response suggests booking
                        if is_booking_intent and "book" in assistant_response.lower():
                            assistant_response += (
                                "\n\n💡 Would you like to make a booking? Type **'new booking'** to get started."
                            )

            except Exception as e:
                logger.error(f"Error processing message: {e}")
                assistant_response = f"❌ Error processing your request: {str(e)}\n\nPlease try again."

        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(assistant_response)

        # Add to conversation history
        add_to_conversation_history(user_input, assistant_response)

        # Rerun to update display
        st.rerun()

    # Sidebar info
    st.sidebar.markdown("---")
    st.sidebar.subheader("ℹ️ Information")

    with st.sidebar.expander("About this assistant"):
        st.markdown(
            """
        This AI Booking Assistant helps you:
        - 📚 Answer questions using uploaded PDFs (RAG)
        - 📅 Make bookings with automatic intent detection
        - 💬 Have multi-turn conversations with context
        - ✅ Receive confirmation emails for bookings
        
        **Start a booking:** Say "new booking" or "make a booking"
        """
        )

    with st.sidebar.expander("Booking Fields"):
        st.markdown(
            """
        Required information:
        - Name
        - Email (validated)
        - Phone
        - Service Type
        - Date (YYYY-MM-DD)
        - Time (HH:MM)
        """
        )

    # Debug info (only in development)
    if os.getenv("DEBUG_MODE"):
        st.sidebar.markdown("---")
        with st.sidebar.expander("🐛 Debug Info"):
            st.write(
                f"Conversation history length: {len(st.session_state.conversation_history)}"
            )
            st.write(f"In booking flow: {st.session_state.in_booking_flow}")
            if st.session_state.in_booking_flow:
                st.write(
                    f"Booking state: {st.session_state.booking_state.to_dict()}"
                )


if __name__ == "__main__":
    main()
