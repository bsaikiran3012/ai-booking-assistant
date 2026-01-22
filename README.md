# AI Booking Assistant

A production-ready AI-powered booking assistant built with Python, Streamlit, and RAG (Retrieval-Augmented Generation).

## Features

✅ **Chat-Based Interface** - Multi-turn conversations with context memory  
✅ **RAG Integration** - Upload PDFs and answer questions from document knowledge base  
✅ **Automatic Intent Detection** - Detects when users want to make bookings  
✅ **Conversational Booking Flow** - Collects customer info step-by-step  
✅ **Email Confirmations** - Sends SMTP confirmation emails (Gmail)  
✅ **SQLite Database** - Persistent storage for customers and bookings  
✅ **Admin Dashboard** - View and search all bookings  
✅ **Input Validation** - Email, phone, date, and time validation  
✅ **Error Handling** - Graceful handling of all failure scenarios  
✅ **Streamlit Cloud Ready** - Deployable on Streamlit Cloud  

## Project Structure

```
ai-booking-assistant/
├── app.py                 # Main Streamlit application
├── rag.py                # RAG module (PDF processing, embeddings, retrieval)
├── booking.py            # Booking logic and validation
├── db.py                 # SQLite database operations
├── email_utils.py        # Email sending via SMTP
├── admin.py              # Admin dashboard
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
├── .streamlit/           # Streamlit configuration (created at runtime)
└── README.md             # This file
```

## Installation & Setup

### Prerequisites

- Python 3.10+
- OpenAI API key (for ChatGPT and embeddings)
- Gmail account with app-specific password (for email confirmations)

### 1. Clone/Create Project

```bash
git clone <repository-url>
cd ai-booking-assistant
```

### 2. Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
GMAIL_USER=your-email@gmail.com
GMAIL_PASSWORD=your-app-specific-password
DEBUG_MODE=false
```

**Getting Gmail App Password:**
1. Go to https://myaccount.google.com/apppasswords
2. Select Mail and Windows (or your device)
3. Copy the generated 16-character password
4. Paste it in `GMAIL_PASSWORD` in `.env`

### 5. Run Locally

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

To access the admin dashboard in development:
```bash
streamlit run admin.py
```

Default admin password: `admin123` (change in production!)

## Usage

### Making a Booking

1. **Start booking:** Type "new booking" or "make a booking"
2. **Fill details:** Answer prompts for:
   - Name
   - Email (e.g., user@example.com)
   - Phone (e.g., 123-456-7890)
   - Service Type (e.g., "Haircut", "Consultation")
   - Date (format: YYYY-MM-DD, e.g., 2024-12-25)
   - Time (format: HH:MM, e.g., 14:30)
3. **Confirm:** Review and type "yes" or "confirm"
4. **Done:** Booking saved and confirmation email sent

### Using RAG

1. **Upload PDF:** In the sidebar, upload a PDF document
2. **Ask questions:** Ask questions related to the PDF content
3. **Get answers:** The AI retrieves relevant content and answers your question

### Admin Dashboard

1. Run: `streamlit run admin.py`
2. Login with password: `admin123`
3. View all bookings, search by email/date, and analyze booking trends

## Database Schema

### customers table
```sql
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT NOT NULL,
    created_at TIMESTAMP
);
```

### bookings table
```sql
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    booking_type TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    status TEXT DEFAULT 'confirmed',
    created_at TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
```

## Deployment to Streamlit Cloud

### 1. Prepare Repository

Push your code to GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click "New app"
3. Select your GitHub repository
4. Set:
   - **Repository:** your-username/ai-booking-assistant
   - **Branch:** main
   - **Main file path:** app.py
5. Click "Deploy"

### 3. Set Secrets

In Streamlit Cloud dashboard:
1. Click your app → Settings (gear icon)
2. Go to "Secrets"
3. Add:
   ```
   OPENAI_API_KEY = "sk-..."
   GMAIL_USER = "your-email@gmail.com"
   GMAIL_PASSWORD = "your-app-password"
   ```

### 4. Create Multi-Page App (Optional)

For the admin dashboard on Streamlit Cloud, create a pages directory:

```
ai-booking-assistant/
├── app.py
├── pages/
│   └── admin.py
└── ...
```

Streamlit will automatically create navigation tabs.

## Input Validation

- **Email:** Standard email format validation
- **Phone:** Minimum 10 digits, various formats accepted
- **Date:** YYYY-MM-DD format, must be in the future
- **Time:** HH:MM format (24-hour)
- **Name:** Minimum 2 characters

## Error Handling

| Error | Handling |
|-------|----------|
| Invalid email | Re-prompt with format example |
| Invalid date | Re-prompt with past date warning |
| Database error | Log and display user-friendly message |
| Email failure | Graceful failure with notification |
| PDF processing error | Show error in UI and log details |
| Missing OpenAI key | Error message on startup |

## Configuration

Edit these constants in their respective files:

- **CHUNK_SIZE** (rag.py): 1000 (text chunk size for embeddings)
- **CHUNK_OVERLAP** (rag.py): 200 (overlap between chunks)
- **Conversation memory** (app.py): 25 message pairs (1250 messages total)
- **Admin password** (admin.py): Change from `admin123`

## Development Tips

### Enable Debug Mode
```env
DEBUG_MODE=true
```

### Run Tests
```bash
pytest tests/ -v
```

### Local Database
The SQLite database is created as `booking_assistant.db` in the project root.

### View Database
```bash
sqlite3 booking_assistant.db
.tables
SELECT * FROM bookings;
```

## Troubleshooting

### "ModuleNotFoundError" when running
```bash
pip install -r requirements.txt
```

### OpenAI API errors
- Verify `OPENAI_API_KEY` is set correctly
- Check your API quota at https://platform.openai.com/account/billing/limits

### Gmail authentication failed
- Ensure you're using an app-specific password, not your Gmail password
- Verify 2FA is enabled on your Google account
- Check password is correct (16 characters, no spaces)

### Database locked error
- Close any other instances of the app
- Delete `booking_assistant.db` and restart (will recreate)

### PDF not processing
- Ensure PDF file is valid (not corrupted)
- Check file size (typically < 50MB)
- Verify OPENAI_API_KEY is set (needed for embeddings)

## Production Checklist

- [ ] Change admin password from `admin123`
- [ ] Set strong `GMAIL_PASSWORD` with app-specific password
- [ ] Enable HTTPS for Streamlit Cloud deployment
- [ ] Set `DEBUG_MODE=false`
- [ ] Configure email rate limiting
- [ ] Add backup strategy for SQLite database
- [ ] Implement proper authentication for admin dashboard
- [ ] Monitor API usage and costs
- [ ] Add logging to external service (e.g., Sentry)
- [ ] Regular security audits

## Technologies Used

- **Streamlit** - Web UI framework
- **LangChain** - RAG and LLM orchestration
- **OpenAI** - ChatGPT and text embeddings
- **FAISS** - Vector database for embeddings
- **SQLite** - Data persistence
- **Python** - Backend language

## License

MIT License - Free for use and modification

## Support

For issues, questions, or contributions, please open a GitHub issue or contact support.

---

**Created:** January 2026  
**Version:** 1.0.0  
**Status:** Production Ready
