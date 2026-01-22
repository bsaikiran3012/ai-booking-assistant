# DEPLOYMENT GUIDE

## Quick Start (Local Development)

### Windows (PowerShell)

```powershell
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file with your credentials
copy .env.example .env
# Edit .env with your OpenAI API key and Gmail credentials

# 5. Run the app
streamlit run app.py

# 6. Open in browser
# http://localhost:8501
```

### macOS/Linux

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Edit .env with your OpenAI API key and Gmail credentials

# 5. Run the app
streamlit run app.py

# 6. App opens at http://localhost:8501
```

## Admin Dashboard (Local)

```bash
# In a new terminal (with venv activated)
streamlit run admin.py

# Login with password: admin123
```

## Deployment to Streamlit Cloud

### Prerequisites
- GitHub account
- GitHub repository with code pushed
- Streamlit Cloud account (free at https://share.streamlit.io/)

### Step 1: Prepare GitHub Repository

```bash
git init
git add .
git commit -m "AI Booking Assistant - Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-booking-assistant.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click "New app"
3. Fill in:
   - **GitHub repo:** YOUR_USERNAME/ai-booking-assistant
   - **Branch:** main
   - **Main file:** app.py
4. Click "Deploy"

### Step 3: Set Secrets in Streamlit Cloud

1. Open your deployed app on Streamlit Cloud
2. Click the menu (three dots) → Settings
3. Click "Secrets"
4. Paste your secrets:

```toml
OPENAI_API_KEY = "sk-your-key-here"
GMAIL_USER = "your-email@gmail.com"
GMAIL_PASSWORD = "your-app-password"
DEBUG_MODE = "false"
```

### Step 4: Create Multi-Page App (Optional - for Admin Dashboard)

Create this directory structure:

```
ai-booking-assistant/
├── app.py              # Main chat app
├── pages/
│   └── admin.py        # Admin dashboard
├── requirements.txt
├── db.py
├── rag.py
├── booking.py
├── email_utils.py
└── ...
```

Streamlit will automatically create tabs for `app.py` and `pages/admin.py`.

## Environment Variables Reference

Required:
- `OPENAI_API_KEY` - OpenAI API key for ChatGPT and embeddings
- `GMAIL_USER` - Gmail address for sending confirmations
- `GMAIL_PASSWORD` - Gmail app-specific password

Optional:
- `ADMIN_EMAIL` - Email for error notifications (defaults to GMAIL_USER)
- `DEBUG_MODE` - Enable debug info (default: false)

## Getting Your API Keys

### OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign in or create account
3. Click "Create new secret key"
4. Copy the key (shown only once)
5. Add to `.env` or Streamlit Cloud secrets

Cost: Pay as you go (~$0.002 per 1K tokens for GPT-3.5)

### Gmail App Password

1. Go to https://myaccount.google.com/
2. Click "Security" (left sidebar)
3. Enable "2-Step Verification" if not already enabled
4. Scroll to "App passwords"
5. Select Mail + Windows PC (or your device)
6. Google generates 16-character password
7. Add to `.env` or Streamlit Cloud secrets

## Testing

### Local Testing
```bash
# Test chat interface
# 1. Run: streamlit run app.py
# 2. Type: "new booking"
# 3. Fill in details step by step
# 4. Confirm booking (type "yes")
# 5. Check email for confirmation

# Test RAG
# 1. Upload a PDF via sidebar
# 2. Ask a question about the PDF content

# Test admin dashboard
# Run: streamlit run admin.py
# Login with: admin123
```

### Database Testing
```bash
# View bookings
sqlite3 booking_assistant.db
sqlite> SELECT * FROM bookings;
sqlite> SELECT * FROM customers;
sqlite> .exit
```

## Troubleshooting Deployment

### App not starting
- Check all environment variables are set
- Verify requirements.txt has all dependencies
- Look at "Manage App" → "View Logs" in Streamlit Cloud

### OpenAI errors
- Verify API key is correct and has remaining credits
- Check https://platform.openai.com/account/billing/limits
- Try with a new API key if issues persist

### Email not sending
- Use app-specific password, NOT your Gmail password
- Enable 2FA on Google account
- Check credentials in Streamlit Cloud Secrets
- Verify test email in local environment first

### Database errors
- SQLite databases on Streamlit Cloud don't persist between deploys
- For production, migrate to PostgreSQL or use cloud storage
- See "Production Upgrades" section

### Rate limiting
- OpenAI API has rate limits based on your plan
- Gmail has sending limits (~100 per day for free accounts)
- Implement queue/retry logic for production

## Production Upgrades

### 1. Replace SQLite with PostgreSQL

```python
# Install: pip install psycopg2-binary
import psycopg2

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
```

### 2. Use Streamlit Cloud File Storage

```python
import streamlit_cloud_file_storage as scfs

# Save files to cloud storage instead of local
```

### 3. Add Monitoring

```python
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=1.0
)
```

### 4. Improve Email Handling

```python
# Use SendGrid or AWS SES instead of Gmail
import sendgrid
from sendgrid.helpers.mail import Mail
```

### 5. Add Authentication

```python
# Implement proper authentication instead of hardcoded password
import streamlit_authenticator as stauth
```

## Performance Tips

1. **Embeddings caching:** FAISS index persists locally, no recomputation
2. **Conversation memory:** Keeps only last 25 exchanges (~2KB)
3. **Database indexing:** Add indexes on frequently searched columns
4. **Connection pooling:** Use connection pool for database queries

## Monitoring & Maintenance

### Monitor API Usage
```bash
# Monthly costs
# OpenAI: Track at https://platform.openai.com/account/billing/overview
# Gmail: Track via Google Workspace admin console
```

### Backup Database
```bash
# Local backup
cp booking_assistant.db booking_assistant.backup.db

# Cloud backup (for production PostgreSQL)
pg_dump database_name > backup.sql
```

### Update Dependencies
```bash
# Check for updates
pip list --outdated

# Update safely
pip install --upgrade streamlit langchain openai
```

## Security Checklist

- [ ] Never commit `.env` or secrets to Git
- [ ] Change admin password from `admin123`
- [ ] Use environment variables for all sensitive data
- [ ] Enable HTTPS (automatic on Streamlit Cloud)
- [ ] Implement rate limiting on API calls
- [ ] Add input sanitization for user data
- [ ] Regular security audits of dependencies
- [ ] Use strong random passwords for admin
- [ ] Implement email verification for bookings
- [ ] Add CAPTCHA for public forms (optional)

## Support & Resources

- Streamlit Docs: https://docs.streamlit.io/
- LangChain Docs: https://python.langchain.com/
- OpenAI API: https://platform.openai.com/docs/
- Streamlit Cloud: https://share.streamlit.io/

---

Questions? Check the README.md for more information.
