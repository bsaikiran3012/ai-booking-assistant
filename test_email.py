#!/usr/bin/env python
"""Test Gmail SMTP connection."""

import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

gmail_user = os.getenv("GMAIL_USER")
gmail_password = os.getenv("GMAIL_PASSWORD")

print(f"Testing Gmail credentials...")
print(f"Email: {gmail_user}")
print(f"Password length: {len(gmail_password) if gmail_password else 0}")

try:
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(gmail_user, gmail_password)
    server.quit()
    print("✅ Gmail authentication SUCCESSFUL")
except smtplib.SMTPAuthenticationError as e:
    print(f"❌ Gmail authentication FAILED: {e}")
    print("\nTo fix this:")
    print("1. Go to https://myaccount.google.com/apppasswords")
    print("2. Make sure 2-Step Verification is enabled")
    print("3. Generate a new app password for 'Mail' and 'Windows Computer'")
    print("4. Copy the 16-character password (without spaces)")
    print("5. Update GMAIL_PASSWORD in .env file")
except Exception as e:
    print(f"❌ Connection error: {e}")
