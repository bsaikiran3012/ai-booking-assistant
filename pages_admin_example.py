"""
Pages module for multi-page Streamlit app.
This allows the admin dashboard to work on Streamlit Cloud.
Copy this as pages/admin.py for Streamlit pages routing.
"""

import streamlit as st
import pandas as pd
from db import get_all_bookings, search_bookings
import logging

logger = logging.getLogger(__name__)


def show_admin_dashboard():
    """Display the admin dashboard."""
    st.set_page_config(page_title="Admin Dashboard", layout="wide")

    st.title("📊 Admin Dashboard")
    st.markdown("---")

    # Authentication check (basic)
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    if not st.session_state.admin_authenticated:
        st.warning("⚠️ Admin access required")
        password = st.text_input("Enter admin password:", type="password")
        if password:
            # In production, use environment variable or proper authentication
            if password == st.secrets.get("ADMIN_PASSWORD", "admin123"):
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("Invalid password")
        return

    # Admin menu
    admin_option = st.sidebar.radio(
        "Admin Menu", ["View All Bookings", "Search Bookings", "Analytics"]
    )

    if admin_option == "View All Bookings":
        show_all_bookings()
    elif admin_option == "Search Bookings":
        search_bookings_ui()
    elif admin_option == "Analytics":
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
        st.pie_chart(status_counts)

    except Exception as e:
        st.error(f"Error loading analytics: {e}")
        logger.error(f"Error loading analytics: {e}")


if __name__ == "__main__":
    show_admin_dashboard()
