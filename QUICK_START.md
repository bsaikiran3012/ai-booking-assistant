# QUICK START GUIDE

## 60-Second Setup

### Windows PowerShell

```powershell
# 1. Create & activate environment
python -m venv venv
venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up credentials
copy .env.example .env
notepad .env  # Add your OpenAI API key and Gmail credentials

# 4. Run the app
streamlit run app.py
```

Then open: **http://localhost:8501**

### macOS/Linux

```bash
# 1. Create & activate environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up credentials
cp .env.example .env
nano .env  # Add your OpenAI API key and Gmail credentials

# 4. Run the app
streamlit run app.py
```

Then open: **http://localhost:8501**

---

## What You Need Before Starting

1. **OpenAI API Key**
   - Go to: https://platform.openai.com/api-keys
   - Create a new secret key
   - Copy it to `.env` as `OPENAI_API_KEY`

2. **Gmail App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Generate one for "Mail" on "Windows PC" (or your device)
   - Copy it to `.env` as `GMAIL_PASSWORD`
   - Also set `GMAIL_USER` to your Gmail address

---

## File Structure

```
ai-booking-assistant/
│
├── app.py                      ✅ MAIN APP - Run this with: streamlit run app.py
│
├── admin.py                    ✅ ADMIN DASHBOARD - Run with: streamlit run admin.py
│                                  (Login: admin123)
│
├── Core Modules:
│   ├── db.py                   SQLite database operations
│   ├── rag.py                  PDF upload, embeddings, retrieval
│   ├── booking.py              Booking logic and validation
│   └── email_utils.py          Email sending
│
├── Configuration:
│   ├── requirements.txt        Python dependencies
│   ├── .env.example            Environment variables template
│   ├── .env                    Your credentials (create from .env.example)
│   ├── .streamlit/config.toml  Streamlit configuration
│   └── .gitignore              Git ignore rules
│
└── Documentation:
    ├── README.md               Full documentation
    ├── DEPLOYMENT.md           Production deployment guide
    └── QUICK_START.md          This file
```

---

## First Time Using the App

1. **Start a Booking**
   - Type: `new booking`
   - Answer questions about name, email, phone, service type, date, time
   - Confirm with: `yes`
   - ✅ Booking saved! Check your email for confirmation

2. **Use RAG (Ask PDF Questions)**
   - Upload a PDF in the sidebar
   - Ask questions about the PDF content
   - AI retrieves relevant sections and answers

3. **Try Admin Dashboard**
   - Open new terminal, activate venv
   - Run: `streamlit run admin.py`
   - Login with: `admin123`
   - View all bookings and analytics

---

## Common Commands

| Task | Command |
|------|---------|
| Start main app | `streamlit run app.py` |
| Start admin dashboard | `streamlit run admin.py` |
| View database | `sqlite3 booking_assistant.db` |
| View logs | Check `.log` files in project |
| Deactivate environment | `deactivate` (PowerShell/bash) |
| Update dependencies | `pip install --upgrade -r requirements.txt` |

---

## Troubleshooting

**"ModuleNotFoundError: No module named 'streamlit'"**
- Activate venv: `venv\Scripts\Activate.ps1` (Windows) or `source venv/bin/activate` (Mac/Linux)
- Install dependencies: `pip install -r requirements.txt`

**"OpenAI API error"**
- Check API key in `.env` (should start with `sk-`)
- Verify you have credits at https://platform.openai.com/account/billing/overview

**"Gmail authentication failed"**
- Use app-specific password, NOT Gmail password
- Get it at: https://myaccount.google.com/apppasswords
- Verify 2FA is enabled on Google account

**"Database locked"**
- Close other instances of the app
- Delete `booking_assistant.db` and restart (will recreate)

---

## What Each File Does

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit chat interface with RAG and booking flow |
| `admin.py` | Admin dashboard for viewing bookings |
| `db.py` | SQLite database - customers and bookings tables |
| `rag.py` | PDF upload, text extraction, embeddings, retrieval |
| `booking.py` | Booking validation, state management, form logic |
| `email_utils.py` | Email sending via Gmail SMTP |
| `requirements.txt` | Python package dependencies |

---

## Next Steps

- [ ] Set up `.env` with your API keys
- [ ] Run `streamlit run app.py`
- [ ] Test a booking end-to-end
- [ ] Upload a sample PDF
- [ ] Check admin dashboard
- [ ] Read `DEPLOYMENT.md` for cloud deployment
- [ ] Customize email templates in `email_utils.py`
- [ ] Change admin password in `admin.py`

---

## Need Help?

1. Check `README.md` for detailed documentation
2. Check `DEPLOYMENT.md` for deployment issues
3. Verify all environment variables are set in `.env`
4. Check logs in the console output
5. Test with local `.env` file first before deploying

---

**Ready to deploy?** See `DEPLOYMENT.md` for Streamlit Cloud setup.
