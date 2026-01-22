#!/usr/bin/env python
"""Comprehensive email diagnostic script."""

import os
import sys
from dotenv import load_dotenv

print("=" * 60)
print("EMAIL CONFIGURATION DIAGNOSTIC")
print("=" * 60)

# Force reload environment
load_dotenv(override=True)

# Check environment variables
print("\n1. Environment Variables:")
gmail_user = os.getenv("GMAIL_USER")
gmail_password = os.getenv("GMAIL_PASSWORD")

print(f"   GMAIL_USER: {gmail_user}")
print(f"   GMAIL_PASSWORD: {'*' * 8 if gmail_password else 'NOT SET'}")

if not gmail_user or not gmail_password:
    print("\n❌ ERROR: Gmail credentials not configured!")
    sys.exit(1)

# Test SMTP connection
print("\n2. Testing SMTP Connection:")
import smtplib
try:
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10)
    print("   ✅ Connected to smtp.gmail.com:465")
    
    server.login(gmail_user, gmail_password)
    print(f"   ✅ Successfully logged in as {gmail_user}")
    server.quit()
except smtplib.SMTPAuthenticationError as e:
    print(f"   ❌ Authentication failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ Connection error: {e}")
    sys.exit(1)

# Test email sending
print("\n3. Testing Email Sending:")
from email_utils import send_confirmation_email

result = send_confirmation_email(
    recipient_email=gmail_user,  # Send to self for testing
    customer_name="Test User",
    booking_type="Consultation",
    booking_date="2026-01-25",
    booking_time="10:00 AM"
)

if result:
    print("   ✅ Test email sent successfully!")
else:
    print("   ❌ Email sending failed!")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL DIAGNOSTICS PASSED - EMAIL IS CONFIGURED CORRECTLY")
print("=" * 60)
