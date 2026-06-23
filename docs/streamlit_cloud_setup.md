# Streamlit Cloud Environment Variables Setup Guide

## Required Environment Variables for Streamlit Cloud

To deploy the Cold Email Parser to Streamlit Cloud, you must configure these environment variables in the Streamlit Cloud Secrets section.

### Step-by-Step Setup

1. **Go to Streamlit Cloud Dashboard**
   - Navigate to https://share.streamlit.io
   - Click on your app (e.g., `cold-email-sender-gk`)
   - Go to the "Secrets" section in app settings

2. **Add Required Environment Variables**

Copy and paste these exact variables into the Secrets section:

```
# SMTP Configuration (Required even for dry-run mode)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password

# Sender Information
SENDER_NAME=Your Name

# Safety Configuration
DRY_RUN=true
SEND_MODE=draft
MAX_OUTREACH_PER_RUN=5

# Input Configuration
INPUT_PATH=contacts_sample.json
```

### Important Notes

#### SMTP_PASSWORD Setup
- **Do NOT use your regular Gmail password**
- You must use a Gmail App Password
- Enable 2-Factor Authentication on your Google Account first
- Generate App Password at: https://myaccount.google.com/apppasswords
- Select "Mail" and "Other (Custom name)"
- Enter "Cold Email Parser" or similar
- Copy the 16-character password
- Use this password as SMTP_PASSWORD

#### DRY_RUN Setting
- Keep `DRY_RUN=true` for testing
- Set `DRY_RUN=false` only when ready to send real emails
- Always test with dry-run first

#### INPUT_PATH Setting
- Use `contacts_sample.json` for initial testing
- Or upload your own contacts via the web interface
- The app will work even if this file doesn't exist (you can upload contacts)

### Optional Environment Variables

These are not required for basic functionality:

```
# Groq API Key (for LLM features - stretch goals)
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
```

### Troubleshooting

#### App Shows "Configuration Error"
- Check that all required environment variables are set
- Verify variable names match exactly (case-sensitive)
- Ensure no typos in variable names
- Restart the app after adding secrets

#### App Won't Start
- Check Streamlit Cloud logs for specific error messages
- Verify SMTP_PASSWORD is a valid App Password, not regular password
- Ensure SMTP_USER matches your Gmail address

#### SMTP Authentication Error
- Verify 2FA is enabled on Google Account
- Generate a new App Password
- Check that SMTP_USER is correct
- Ensure you're using the App Password, not regular password

### Testing Your Setup

1. **After setting environment variables:**
   - The app should automatically redeploy
   - Wait 1-2 minutes for redeployment to complete
   - Check the app URL to see if it loads

2. **Test with dry-run mode:**
   - Keep `DRY_RUN=true`
   - Upload a test contact
   - Generate an email
   - Verify it works without actually sending

3. **Test live sending (carefully):**
   - Set `MAX_OUTREACH_PER_RUN=1`
   - Set `DRY_RUN=false`
   - Send to your own email first
   - Verify email arrives
   - Check your Sent folder in Gmail

### Security Best Practices

1. **Never commit secrets to git**
   - `.env` file should be in `.gitignore`
   - Never include actual passwords in code
   - Use Streamlit Cloud Secrets only

2. **Use App Passwords**
   - Never use regular Gmail passwords
   - Generate unique App Passwords for each application
   - Revoke App Passwords if compromised

3. **Limit Access**
   - Use the minimum required permissions
   - Keep volume caps low (MAX_OUTREACH_PER_RUN=5 or less)
   - Monitor for unusual activity

### Quick Reference

**Minimum Required Variables:**
- SMTP_HOST
- SMTP_PORT  
- SMTP_USER
- SMTP_PASSWORD
- SENDER_NAME
- DRY_RUN
- SEND_MODE
- MAX_OUTREACH_PER_RUN
- INPUT_PATH

**Common Issues:**
- Missing environment variables → Add all required variables
- Wrong SMTP_PASSWORD → Use Gmail App Password, not regular password
- App crashes silently → Check Streamlit Cloud logs
- Import errors → Verify main file path is `ui/app.py`

### Support

If you encounter issues:
1. Check Streamlit Cloud logs
2. Verify all environment variables are set
3. Review the troubleshooting guide
4. Check the main deployment documentation
