"""
Admin Dashboard for the AI Booking Assistant.
Displays all bookings and provides filtering capabilities.
"""

import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from db import get_all_bookings, search_bookings
import logging

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


def show_admin_dashboard():
    """Display the admin dashboard."""
    st.set_page_config(page_title="Admin Dashboard", layout="wide")

    # Custom CSS for admin dashboard with dark theme
    st.markdown("""
    <style>
        /* Main container styling */
        .main {
            background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
        }
        
        /* Header styling */
        .admin-header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            padding: 2rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(30, 60, 114, 0.3);
        }
        
        .admin-header h1 {
            font-size: 2.5rem;
            margin: 0;
            font-weight: 700;
        }
        
        .admin-header p {
            font-size: 0.95rem;
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
        }
        
        /* Stat cards */
        .stat-card {
            background: #1a1f2e;
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid #2a3f5f;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: 700;
            color: #2a5298;
            margin: 0.5rem 0;
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: #b0b0b0;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Data table styling */
        .stDataFrame {
            background: #1a1f2e !important;
            color: #e0e0e0 !important;
        }
        
        /* Button styling */
        .stButton>button {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%) !important;
            color: white !important;
            border: none !important;
            padding: 0.75rem 1.5rem !important;
            font-size: 1rem !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: transform 0.2s, box-shadow 0.2s !important;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 15px rgba(42, 82, 152, 0.4) !important;
        }
        
        /* Input styling */
        .stTextInput>div>div>input,
        .stPasswordInput>div>div>input,
        .stSelectbox>div>div>select,
        .stDateInput>div>div>input {
            background-color: #1a1f2e !important;
            border-radius: 8px !important;
            border: 2px solid #2a3f5f !important;
            color: #e0e0e0 !important;
        }
        
        .stTextInput>div>div>input:focus,
        .stPasswordInput>div>div>input:focus,
        .stSelectbox>div>div>select:focus,
        .stDateInput>div>div>input:focus {
            border: 2px solid #2a5298 !important;
            box-shadow: 0 0 0 3px rgba(42, 82, 152, 0.1) !important;
        }
        
        /* Sidebar styling */
        .stSidebar {
            background: linear-gradient(135deg, #1a1f2e 0%, #0f1419 100%);
        }
        
        /* Text styling */
        .stMarkdown {
            color: #e0e0e0;
        }
        
        /* Info card */
        .stInfo {
            background-color: #1a2f4d !important;
            color: #60a5fa !important;
        }
        
        /* Success message */
        .stSuccess {
            background-color: #1a4d2e !important;
            color: #4ade80 !important;
        }
        
        /* Error message */
        .stError {
            background-color: #4d1a1a !important;
            color: #f87171 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Authentication check (basic)
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    if not st.session_state.admin_authenticated:
        st.markdown("""
        <div class="admin-header">
            <h1>🔐 Admin Access Required</h1>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.info("🔒 Enter your admin password to proceed", icon="🔐")
            password = st.text_input("Admin Password:", type="password", key="admin_pwd")
            if password:
                # In production, use environment variable or proper authentication
                if password == "admin123":  # This should be in environment variable
                    st.session_state.admin_authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Invalid password")
        return

    # Admin header
    st.markdown("""
    <div class="admin-header">
        <h1>📊 Admin Dashboard</h1>
        <p>Manage bookings and view analytics</p>
    </div>
    """, unsafe_allow_html=True)

    # Admin menu
    admin_option = st.sidebar.radio(
        "Admin Menu", ["📋 View All Bookings", "🔍 Search Bookings", "📈 Analytics"]
    )

    if admin_option == "📋 View All Bookings":
        show_all_bookings()
    elif admin_option == "🔍 Search Bookings":
        search_bookings_ui()
    elif admin_option == "📈 Analytics":
        show_analytics()

    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.admin_authenticated = False
        st.rerun()


def show_all_bookings():
    """Display all bookings in a table."""
    st.subheader("All Bookings")

    try:
        bookings = get_all_bookings()

        if not bookings:
            st.info("No bookings found.")
            return

        # Convert to DataFrame
        df = pd.DataFrame(bookings)

        # Format the dataframe
        df = df[
            [
                "id",
                "name",
                "email",
                "phone",
                "booking_type",
                "date",
                "time",
                "status",
                "created_at",
            ]
        ].copy()

        df.columns = [
            "Booking ID",
            "Customer Name",
            "Email",
            "Phone",
            "Service Type",
            "Date",
            "Time",
            "Status",
            "Created At",
        ]

        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Bookings", len(df))
        with col2:
            confirmed = len(df[df["Status"] == "confirmed"])
            st.metric("Confirmed", confirmed)
        with col3:
            today_df = df[df["Date"] >= pd.Timestamp.today().strftime("%Y-%m-%d")]
            st.metric("Upcoming", len(today_df))
        with col4:
            st.metric("Customers", df["Email"].nunique())

        st.markdown("---")

        # Display table
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

        # Download CSV option
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name="bookings.csv",
            mime="text/csv",
        )

    except Exception as e:
        st.error(f"Error loading bookings: {e}")
        logger.error(f"Error loading bookings: {e}")


def search_bookings_ui():
    """Search bookings by email or date."""
    st.subheader("Search Bookings")

    col1, col2 = st.columns(2)

    with col1:
        search_email = st.text_input("Search by email:", placeholder="user@example.com")

    with col2:
        search_date = st.text_input("Search by date:", placeholder="YYYY-MM-DD")

    if st.button("🔍 Search"):
        try:
            bookings = search_bookings(email=search_email, date=search_date)

            if not bookings:
                st.info("No bookings found matching your criteria.")
                return

            df = pd.DataFrame(bookings)
            df = df[
                [
                    "id",
                    "name",
                    "email",
                    "phone",
                    "booking_type",
                    "date",
                    "time",
                    "status",
                    "created_at",
                ]
            ].copy()

            df.columns = [
                "Booking ID",
                "Customer Name",
                "Email",
                "Phone",
                "Service Type",
                "Date",
                "Time",
                "Status",
                "Created At",
            ]

            st.success(f"Found {len(df)} booking(s)")
            st.dataframe(df, use_container_width=True, hide_index=True)

            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name="bookings_search.csv",
                mime="text/csv",
            )

        except Exception as e:
            st.error(f"Error searching bookings: {e}")
            logger.error(f"Error searching bookings: {e}")


def show_analytics():
    """Display booking analytics."""
    st.subheader("Booking Analytics")

    try:
        bookings = get_all_bookings()

        if not bookings:
            st.info("No booking data available.")
            return

        df = pd.DataFrame(bookings)

        # Bookings by service type
        st.markdown("#### Bookings by Service Type")
        service_counts = df["booking_type"].value_counts()
        st.bar_chart(service_counts)

        # Bookings over time
        st.markdown("#### Bookings Over Time")
        df["created_date"] = pd.to_datetime(df["created_at"]).dt.date
        daily_counts = df["created_date"].value_counts().sort_index()
        st.line_chart(daily_counts)

        # Status distribution
        st.markdown("#### Status Distribution")
        status_counts = df["status"].value_counts()
        st.bar_chart(status_counts)

    except Exception as e:
        st.error(f"Error loading analytics: {e}")
        logger.error(f"Error loading analytics: {e}")


if __name__ == "__main__":
    show_admin_dashboard()
