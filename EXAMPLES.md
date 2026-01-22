# EXAMPLE USAGE & WALKTHROUGHS

## Scenario 1: Complete Booking Flow

### User Interaction Example

```
User: new booking
Assistant: 🎯 Great! Let's start your booking process.
          What is your full name?

User: John Smith
Assistant: ✅ Name recorded: John Smith
          What is your email address?

User: john.smith@gmail.com
Assistant: ✅ Email recorded: john.smith@gmail.com
          What is your phone number?

User: (555) 123-4567
Assistant: ✅ Phone recorded: (555) 123-4567
          What service type would you like to book?

User: Haircut
Assistant: ✅ Service type recorded: Haircut
          What date would you prefer? (YYYY-MM-DD format)

User: 2024-02-15
Assistant: ✅ Date recorded: 2024-02-15
          What time would you prefer? (HH:MM format, e.g., 14:30)

User: 10:00
Assistant: ✅ Time recorded: 10:00

BOOKING SUMMARY
- Name: John Smith
- Email: john.smith@gmail.com
- Phone: (555) 123-4567
- Service Type: Haircut
- Date: 2024-02-15
- Time: 10:00

Please confirm this booking to proceed.

User: yes
Assistant: BOOKING CONFIRMED!
Your booking has been successfully saved.
- Booking ID: 1
- Confirmation Status: Saved in database

A confirmation email has been sent to your email address.
Thank you for using our AI Booking Assistant!
```

---

## Scenario 2: Input Validation Examples

### Email Validation Failure
```
User: what is your email?
Assistant: please enter a valid email address (e.g., user@example.com)

ACCEPTED: user@example.com, john.smith@company.co.uk
REJECTED: notanemail, @invalid.com, user@.com
```

### Date Validation
```
USER ENTERS: 2020-01-01 (past date)
ASSISTANT: Please select a future date

USER ENTERS: 2024-02-15 (valid future date)
ASSISTANT: Date recorded: 2024-02-15

ACCEPTED: 2024-12-25, 2025-06-15
REJECTED: 2020-01-01, invalid-date, 02-15-2024
```

### Phone Validation
```
USER ENTERS: 123 (too short)
ASSISTANT: Please enter a valid phone number (at least 10 digits)

USER ENTERS: (555) 123-4567 (valid)
ASSISTANT: Phone recorded: (555) 123-4567

ACCEPTED: 1234567890, (555) 123-4567, 555-123-4567
REJECTED: 123, 555, (incomplete)
```

---

## Scenario 3: Using RAG with PDF

### Interaction Flow

```
SIDEBAR: User uploads company_handbook.pdf
SYSTEM: Processing PDF...
        - Extracting text (2,845 words)
        - Chunking into 18 segments
        - Creating embeddings
        - Saving to FAISS index
SUCCESS: PDF processed! (18 chunks added to knowledge base)

USER: What are the company holidays?
SYSTEM:
  1. Searches FAISS for related chunks
  2. Retrieves top 3 matching chunks
  3. Sends to LLM with question
  4. LLM generates answer from context

ASSISTANT: Based on the company handbook, here are the holidays:
- New Year's Day (January 1)
- Memorial Day (Last Monday of May)
- Independence Day (July 4)
- Labor Day (First Monday of September)
- Thanksgiving (Fourth Thursday of November)
- Christmas Day (December 25)

All employees receive these days off with pay.

Would you like to make a booking? Type 'new booking' to get started.
```

---

## Scenario 4: Admin Dashboard Usage

### Login & View All Bookings

```
URL: http://localhost:8501/admin.py

PROMPT: Enter admin password: [admin123]
SUCCESS: Admin authenticated

DASHBOARD METRICS:
- Total Bookings: 12
- Confirmed: 12
- Upcoming: 8
- Customers: 10

BOOKINGS TABLE:
ID | Name       | Email                 | Phone         | Service   | Date       | Time
1  | John Smith | john.smith@gmail.com  | (555) 123-4567| Haircut   | 2024-02-15 | 10:00
2  | Jane Doe   | jane.doe@company.com  | (555) 987-6543| Massage   | 2024-02-16 | 14:00
3  | Bob Wilson | bob@email.com         | (555) 456-7890| Cleaning  | 2024-02-17 | 09:00
...
```

### Search by Email

```
INPUT: Search by email: "john.smith"
RESULT: Found 3 booking(s)

FILTERED TABLE:
ID | Name       | Email                | Phone          | Service | Date       | Time
1  | John Smith | john.smith@gmail.com | (555) 123-4567 | Haircut | 2024-02-15 | 10:00
12 | John Smith | john.smith@gmail.com | (555) 123-4567 | Massage | 2024-02-25 | 15:00
```

### Analytics Charts

```
BOOKINGS BY SERVICE TYPE:
- Haircut: 5
- Massage: 4
- Cleaning: 3

STATUS DISTRIBUTION:
- Confirmed: 12

BOOKINGS OVER TIME:
Feb 14: 2 bookings
Feb 15: 4 bookings
Feb 16: 3 bookings
Feb 17: 2 bookings
Feb 18: 1 booking
```

---

## Scenario 5: Error Handling Examples

### Missing OpenAI API Key

```
ERROR on startup: OpenAI API key not configured.
Please set OPENAI_API_KEY environment variable.

SOLUTION:
1. Create .env file
2. Add: OPENAI_API_KEY=sk-your-key-here
3. Restart the app
```

### Database Connection Error

```
USER: new booking
[...completes booking...]
USER: yes

ASSISTANT: Error saving booking: database is locked

Please try again or contact support.

LOGGING: ERROR - Database lock timeout after 30 seconds
```

### Email Sending Failure

```
[Booking saved successfully]

Note: Could not send confirmation email. 
Please save your booking details.

LOGGING: WARNING - Gmail credentials not configured.
Email not sent. Set GMAIL_USER and GMAIL_PASSWORD.
```

### PDF Processing Error

```
USER: [uploads corrupted_file.pdf]

SYSTEM: Error processing PDF: PDF file is corrupted

SOLUTION: Please upload a valid PDF file.

LOGGING: ERROR - Error extracting PDF text: invalid PDF structure
```

---

## Scenario 6: Multi-Turn Conversation with RAG

```
USER: Can I book a consultation?
ASSISTANT: Yes, I'd be happy to help! Would you like to make a booking?
          Type 'new booking' to get started.

USER: Tell me about your services first
[RAG searches PDF for services info]
ASSISTANT: Based on our service guide, we offer:
- Hair services (cuts, styling, coloring)
- Massage therapy (Swedish, deep tissue)
- Skin consultations (facials, treatments)
- Wellness coaching (nutrition, fitness)

💡 Would you like to make a booking? 
   Type 'new booking' to get started.

USER: new booking
ASSISTANT: Great! Let's start your booking process.
          What is your full name?

[Booking flow continues...]
```

---

## Scenario 7: Multiple Bookings from Same Customer

```
FIRST BOOKING:
Customer: john.smith@gmail.com
- Service: Haircut
- Date: 2024-02-15
- Time: 10:00

[Email sent, booking saved]

SECOND BOOKING (same customer):
USER: new booking
ASSISTANT: Great! Let's start.
          What is your full name?

USER: John Smith
[...continues through booking flow...]
USER: john.smith@gmail.com

[System checks: customer already exists]
[Links to existing customer record]
[New booking created with same customer_id]

DATABASE RESULT:
customers table: 1 record (no duplicate)
bookings table: 2 records (both linked to customer_id=1)
```

---

## Scenario 8: Booking Cancellation

```
USER: new booking
ASSISTANT: What is your full name?

USER: cancel
ASSISTANT: Booking cancelled. How can I help you today?

[Booking state reset]
[No database changes]
[User can continue chatting or start new booking]
```

---

## Testing Commands (Local)

### Test Booking Flow
```
streamlit run app.py
- Type "new booking"
- Complete all fields
- Confirm with "yes"
- Check email
- Verify database: sqlite3 booking_assistant.db
  SELECT * FROM bookings;
```

### Test RAG
```
streamlit run app.py
- Upload a PDF in sidebar
- Ask a question about PDF content
- Verify answer uses PDF information
```

### Test Admin Dashboard
```
# Terminal 1: Main app
streamlit run app.py

# Terminal 2: Admin dashboard
streamlit run admin.py
- Login: admin123
- View bookings
- Search by email
- Download CSV
```

### Test Database Directly
```
sqlite3 booking_assistant.db
sqlite> .tables
sqlite> SELECT COUNT(*) FROM bookings;
sqlite> SELECT * FROM customers;
sqlite> SELECT b.id, c.name, b.date, b.time FROM bookings b JOIN customers c;
sqlite> .exit
```

---

## Performance Notes

### Response Times (Approximate)
- Chat message processing: 1-2 seconds
- PDF embedding: 5-15 seconds (depends on size)
- Database query: <100ms
- Email sending: 1-3 seconds
- Admin dashboard load: <500ms

### Memory Usage
- App memory: ~300MB
- Vector store (typical): ~50MB
- Database (100 bookings): ~1MB
- Conversation history: ~2KB

### Rate Limiting
- OpenAI API: Based on your plan tier
- Gmail: ~100 emails/day (free account)
- Streamlit Cloud: Free tier has resource limits

---

## Development Tips

### Enable Debug Mode
```env
DEBUG_MODE=true
```
This shows:
- Conversation history length
- Booking state
- Database operations
- API calls

### View Console Logs
```bash
# All logs printed to console
# Filter for errors:
grep ERROR console.log
```

### Test Email Configuration
```python
from email_utils import send_confirmation_email

send_confirmation_email(
    recipient_email="test@gmail.com",
    customer_name="Test User",
    booking_type="Test Service",
    booking_date="2024-02-15",
    booking_time="10:00"
)
```

### Reset Database
```bash
rm booking_assistant.db  # Deletes database
# Restart app - new database created automatically
```

---

## Production Deployment Notes

### Streamlit Cloud Requirements
1. GitHub repository
2. .env variables as Secrets
3. Database: SQLite (local) or PostgreSQL (recommended)
4. Email: Gmail app password or SendGrid API

### Monitoring
```python
# Add to app.py for monitoring
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### Backup
```bash
# Backup database
cp booking_assistant.db booking_assistant.backup.db
```

---

This documentation provides real-world examples of how to use the AI Booking Assistant
in various scenarios and how to handle common situations.
