# The Closer - Cold Email Writer + Send Bot

A Python CLI tool for generating and sending personalized cold emails with safety-first design.

## Features

- **Personalized Email Generation**: Six-part email anatomy (subject, hook, intro, value, ask, sign-off)
- **Human-in-the-Loop**: Preview each email before sending
- **Safety by Default**: Dry-run mode prevents accidental sends
- **Volume Control**: Configurable cap on emails per run
- **Audit Logging**: All attempts logged to CSV for tracking
- **SMTP Delivery**: Gmail SMTP support with App Password authentication
- **Web UI**: Streamlit-based web interface for easier use (stretch goal)

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Configure your SMTP credentials in `.env`:
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   SENDER_NAME=Your Name
   DRY_RUN=true
   SEND_MODE=draft
   MAX_OUTREACH_PER_RUN=5
   INPUT_PATH=contacts.json
   ```

### Setting up Gmail App Password

1. Enable 2-Factor Authentication on your Google Account
2. Go to https://myaccount.google.com/apppasswords
3. Select "Mail" and "Other (Custom name)"
4. Enter a name like "The Closer Email Bot"
5. Copy the 16-character password
6. Use this password in `.env` as `SMTP_PASSWORD`

## Usage

### CLI Interface

#### Dry Run (Safe Default)

The default configuration runs in dry-run mode, which simulates sending without actual delivery:

```bash
python main.py
```

This will:
- Load contacts from `contacts.json`
- Generate personalized emails
- Show preview for each email
- Prompt for action (send/draft/skip)
- Log all attempts to `outreach_log.csv`
- **Skip actual email delivery**

#### Live Send

To send real emails:

1. Set `DRY_RUN=false` in `.env`
2. Set `MAX_OUTREACH_PER_RUN=1` for first test
3. Run:
   ```bash
   python main.py
   ```
4. Verify email arrives in your Sent folder
5. Increase `MAX_OUTREACH_PER_RUN` for production runs

### Web UI (Streamlit)

For a more user-friendly experience, use the Streamlit web interface:

```bash
streamlit run ui/app.py
```

The web UI provides:
- **Generate Emails**: Process contacts with web-based preview and confirmation
- **Upload Contacts**: Upload JSON files directly through the browser
- **View Log**: Real-time viewing of outreach_log.csv with statistics
- **Settings**: View current configuration

The web UI includes the same safety features as the CLI (dry-run mode, volume caps, human review).

## Input Format

Create a `contacts.json` file with your outreach targets:

```json
[
  {
    "recipient_name": "John Doe",
    "recipient_email": "john@example.com",
    "company": "Acme Corp",
    "role": "Software Engineer",
    "job_url": "https://acme.com/jobs/engineer",
    "personalization_note": "Company recently launched AI product",
    "candidate_name": "Your Name",
    "candidate_background": "Python developer with ML experience",
    "portfolio_url": "https://github.com/yourname",
    "linkedin_url": "https://linkedin.com/in/yourname",
    "resume_link": "https://drive.google.com/your-resume"
  }
]
```

### Required Fields
- `recipient_email`: Email address
- `company`: Company name
- `role`: Job role/title
- `candidate_name`: Your name
- `candidate_background`: Your background for personalization

### Optional Fields
- `recipient_name`: Recipient's name
- `job_url`: Job posting URL
- `personalization_note`: Custom note for personalization
- `portfolio_url`: Your portfolio link
- `linkedin_url`: Your LinkedIn profile
- `resume_link`: Resume/CV link

## Safety Features

- **Dry-Run Mode**: Default setting prevents accidental sends
- **Volume Cap**: `MAX_OUTREACH_PER_RUN` limits emails per batch
- **Human Review**: Each email requires explicit confirmation
- **Audit Log**: All attempts logged to `outreach_log.csv`
- **Error Handling**: Clear error messages for authentication/network issues

## Output

### Log File

All outreach attempts are logged to `outreach_log.csv`:

```csv
timestamp,recipient_email,company,role,subject,status,error_message,word_count,job_url
2024-06-18T12:00:00,john@example.com,Acme Corp,Software Engineer,Quick note on the Software Engineer role at Acme Corp,sent,,67,https://acme.com/jobs/engineer
```

### Status Values
- `generated`: Email created (dry-run mode)
- `sent`: Email successfully delivered
- `drafted`: Email saved as draft
- `skipped`: User chose to skip
- `failed`: Delivery failed (see error_message)

## Troubleshooting

### SMTP Authentication Error
- Ensure 2-Factor Authentication is enabled
- Use Gmail App Password (not regular password)
- Verify `SMTP_USER` matches your Gmail address

### Connection Timeout
- Check internet connection
- Verify `SMTP_HOST` and `SMTP_PORT` settings
- Ensure firewall allows SMTP connections

### Import Errors
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Check Python version (requires 3.10+)

## Project Structure

```
the-closer/
├── src/
│   ├── __init__.py
│   ├── models.py          # Data models
│   ├── config.py          # Configuration loader
│   ├── input_loader.py    # Contact loader
│   ├── email_generator.py # Email generation
│   ├── preview.py         # Preview and confirmation
│   ├── email_sender.py    # Email delivery
│   └── logger.py          # Audit logging
├── main.py                # CLI entry point
├── contacts.json          # Input data
├── requirements.txt       # Dependencies
├── .env.example           # Configuration template
├── .env                   # Your credentials (not tracked)
└── outreach_log.csv       # Audit log (not tracked)
```

## Safety Verification Checklist

Before sending live emails:

- [ ] Test with `DRY_RUN=true` first
- [ ] Set `MAX_OUTREACH_PER_RUN=1` for initial test
- [ ] Send test email to your own address
- [ ] Verify email appears in Sent folder
- [ ] Check `outreach_log.csv` for correct status
- [ ] Review each email before confirming
- [ ] Keep volume cap reasonable (≤5 for first run)
- [ ] Monitor log file during production run
- [ ] Verify sender identity is not spoofed

## License

MIT License
