#!/usr/bin/env python
"""Test sending an actual confirmation email."""

from email_utils import send_confirmation_email

result = send_confirmation_email(
    recipient_email="bookingassisstant@gmail.com",
    customer_name="Test Customer",
    booking_type="Consultation",
    booking_date="2026-01-25",
    booking_time="10:00 AM"
)

if result:
    print("✅ Email sent successfully!")
else:
    print("❌ Email sending failed")
