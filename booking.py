"""
Booking module for the AI Booking Assistant.
Handles booking flow logic, validation, and state management.
"""

import re
from datetime import datetime
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class BookingState:
    """Manages booking state during conversation."""

    def __init__(self):
        self.data = {
            "name": None,
            "email": None,
            "phone": None,
            "booking_type": None,
            "date": None,
            "time": None,
        }
        self.current_field = None
        self.confirmed = False

    def set_field(self, field: str, value):
        """Set a booking field value."""
        if field in self.data:
            self.data[field] = value
            logger.info(f"Booking field '{field}' set to: {value}")

    def get_field(self, field: str):
        """Get a booking field value."""
        return self.data.get(field)

    def get_missing_fields(self) -> list:
        """Get list of missing required fields."""
        return [field for field, value in self.data.items() if value is None]

    def is_complete(self) -> bool:
        """Check if all required fields are filled."""
        return all(value is not None for value in self.data.values())

    def reset(self):
        """Reset booking state."""
        self.data = {
            "name": None,
            "email": None,
            "phone": None,
            "booking_type": None,
            "date": None,
            "time": None,
        }
        self.current_field = None
        self.confirmed = False

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return self.data.copy()


def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if re.match(pattern, email):
        return True, ""
    return False, "Please enter a valid email address (e.g., user@example.com)"


def validate_phone(phone: str) -> Tuple[bool, str]:
    """Validate phone number format."""
    # Accept various formats: 123-456-7890, (123) 456-7890, 1234567890, etc.
    phone_cleaned = re.sub(r"\D", "", phone)
    if len(phone_cleaned) >= 10:
        return True, ""
    return False, "Please enter a valid phone number (at least 10 digits)"


def validate_date(date_str: str) -> Tuple[bool, str]:
    """Validate date in YYYY-MM-DD format."""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        if date_obj < datetime.now():
            return False, "Please select a future date"
        return True, ""
    except ValueError:
        return False, "Please enter date in YYYY-MM-DD format (e.g., 2024-12-25)"


def validate_time(time_str: str) -> Tuple[bool, str]:
    """Validate time in HH:MM format."""
    try:
        datetime.strptime(time_str, "%H:%M")
        return True, ""
    except ValueError:
        return False, "Please enter time in HH:MM format (e.g., 14:30)"


def format_booking_summary(booking_data: Dict) -> str:
    """Format booking data into a readable summary."""
    summary = f"""
📋 **Booking Summary**
- **Name:** {booking_data['name']}
- **Email:** {booking_data['email']}
- **Phone:** {booking_data['phone']}
- **Service Type:** {booking_data['booking_type']}
- **Date:** {booking_data['date']}
- **Time:** {booking_data['time']}

Please confirm this booking to proceed.
"""
    return summary


def extract_field_value(
    user_input: str, field_type: str
) -> Tuple[bool, str, str]:
    """
    Extract and validate field value from user input.
    Returns: (is_valid, error_message, cleaned_value)
    """
    user_input = user_input.strip()

    if field_type == "name":
        if len(user_input) < 2:
            return False, "Name must be at least 2 characters", ""
        return True, "", user_input

    elif field_type == "email":
        is_valid, error = validate_email(user_input)
        return is_valid, error, user_input.lower()

    elif field_type == "phone":
        is_valid, error = validate_phone(user_input)
        return is_valid, error, user_input

    elif field_type == "booking_type":
        if len(user_input) < 2:
            return False, "Booking type must be at least 2 characters", ""
        return True, "", user_input

    elif field_type == "date":
        is_valid, error = validate_date(user_input)
        return is_valid, error, user_input

    elif field_type == "time":
        is_valid, error = validate_time(user_input)
        return is_valid, error, user_input

    return False, "Unknown field type", ""


def get_next_field_prompt(field: str) -> str:
    """Get a friendly prompt for the next field to collect."""
    prompts = {
        "name": "What is your full name?",
        "email": "What is your email address?",
        "phone": "What is your phone number?",
        "booking_type": "What service type would you like to book?",
        "date": "What date would you prefer? (YYYY-MM-DD format)",
        "time": "What time would you prefer? (HH:MM format, e.g., 14:30)",
    }
    return prompts.get(field, "Please provide the required information.")
