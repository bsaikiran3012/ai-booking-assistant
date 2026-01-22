"""
Email utilities for the AI Booking Assistant.
Handles sending confirmation emails via Gmail SMTP.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


def send_confirmation_email(
    recipient_email: str,
    customer_name: str,
    booking_type: str,
    booking_date: str,
    booking_time: str,
) -> bool:
    """
    Send booking confirmation email.
    Requires GMAIL_USER and GMAIL_PASSWORD environment variables.
    GMAIL_PASSWORD should be an app-specific password, not the Gmail password.
    """
    try:
        # Get credentials from environment
        gmail_user = os.getenv("GMAIL_USER")
        gmail_password = os.getenv("GMAIL_PASSWORD")

        if not gmail_user or not gmail_password:
            logger.warning(
                "Gmail credentials not configured. Email not sent. "
                "Set GMAIL_USER and GMAIL_PASSWORD environment variables."
            )
            return False

        # Create email
        sender = gmail_user
        subject = f"Booking Confirmation - {booking_type}"

        body = f"""
Dear {customer_name},

Your booking has been confirmed!

Booking Details:
- Service Type: {booking_type}
- Date: {booking_date}
- Time: {booking_time}

Thank you for using our AI Booking Assistant.

Best regards,
AI Booking Assistant Team
"""

        # Create message
        message = MIMEMultipart()
        message["From"] = sender
        message["To"] = recipient_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        # Send via Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_password)
            server.send_message(message)

        logger.info(f"Confirmation email sent to {recipient_email}")
        return True

    except smtplib.SMTPAuthenticationError as e:
        logger.error(
            f"Gmail authentication failed: {str(e)}. Check GMAIL_USER and GMAIL_PASSWORD. "
            f"Make sure you're using an app-specific password, not your Gmail password. "
            f"Get one from: https://myaccount.google.com/apppasswords"
        )
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {e}")
        return False
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False


def send_error_notification(error_message: str) -> bool:
    """Send error notification to admin (optional)."""
    try:
        gmail_user = os.getenv("GMAIL_USER")
        gmail_password = os.getenv("GMAIL_PASSWORD")
        admin_email = os.getenv("ADMIN_EMAIL", gmail_user)

        if not gmail_user or not gmail_password:
            return False

        subject = "AI Booking Assistant - Error Notification"
        body = f"""
An error occurred in the AI Booking Assistant:

{error_message}

Please investigate.
"""

        message = MIMEMultipart()
        message["From"] = gmail_user
        message["To"] = admin_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_password)
            server.send_message(message)

        logger.info(f"Error notification sent to {admin_email}")
        return True

    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        return False
