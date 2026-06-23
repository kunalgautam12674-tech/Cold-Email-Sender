# Streamlit Cloud Deployment Troubleshooting

## Issue: App not deploying at https://cold-email-sender-test2.streamlit.app

## Common Streamlit Cloud Deployment Issues

### 1. Main File Path Configuration

**Problem:** Streamlit Cloud can't find the main app file.

**Solution:** 
- In Streamlit Cloud dashboard, ensure main file path is set to: `ui/app.py`
- Not `app.py` or `main.py`

### 2. Missing Dependencies

**Problem:** Dependencies not installed in cloud environment.

**Solution:**
- Verify `requirements.txt` is in repository root
- Check all dependencies are listed:
  ```
  python-dotenv==1.0.0
  groq==0.5.0
  streamlit==1.58.0
  pandas>=2.0.0
  ```

### 3. Environment Variables Not Set

**Problem:** App fails to load configuration due to missing environment variables.

**Solution:**
- Go to Streamlit Cloud dashboard
- Click on your app
- Go to "Secrets" section
- Add these environment variables:
  ```
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

### 4. Import Errors

**Problem:** Python imports failing in cloud environment.

**Solution:**
- Check deployment logs in Streamlit Cloud dashboard
- Common issues:
  - Relative import paths
  - Missing `__init__.py` files
  - Case sensitivity in imports

### 5. File Structure Issues

**Problem:** Streamlit Cloud can't access required files.

**Solution:**
- Verify file structure:
  ```
  repository-root/
  ├── ui/
  │   └── app.py          # Main Streamlit app
  ├── src/
  │   ├── __init__.py
  │   ├── config.py
  │   ├── models.py
  │   ├── input_loader.py
  │   ├── email_generator.py
  │   ├── email_sender.py
  │   ├── logger.py
  │   └── preview.py
  ├── requirements.txt
  ├── .streamlit/
  │   ├── config.toml
  │   └── credentials.toml
  └── contacts.json
  ```

### 6. Runtime Errors

**Problem:** App starts but crashes during execution.

**Solution:**
- Check deployment logs for specific error messages
- Common runtime errors:
  - Missing `contacts.json` file
  - SMTP authentication failures
  - CSV file access issues
  - Memory limits

## Immediate Troubleshooting Steps

### Step 1: Check Streamlit Cloud Dashboard

1. Go to https://share.streamlit.io
2. Click on your app: `cold-email-sender-test2`
3. Check the "Logs" tab for error messages
4. Look for red error indicators

### Step 2: Verify Configuration

1. Check main file path: Should be `ui/app.py`
2. Check branch: Should be `main`
3. Verify repository is connected correctly

### Step 3: Check Environment Variables

1. Go to app settings
2. Click "Secrets"
3. Verify all required environment variables are set
4. Check for typos in variable names

### Step 4: Review Deployment Logs

Look for these specific errors:
- `ModuleNotFoundError`: Missing dependencies
- `ImportError`: Import path issues
- `FileNotFoundError`: Missing files
- `KeyError`: Missing environment variables
- `AuthenticationError`: SMTP credentials issues

### Step 5: Test Locally with Cloud Configuration

1. Set environment variables locally to match cloud
2. Test with: `python -m streamlit run ui/app.py`
3. Verify app works with cloud-like configuration

## Specific Fixes for This Project

### Fix 1: Ensure contacts.json exists

Streamlit Cloud may not have `contacts.json` by default. Add sample data:

```bash
# Create sample contacts.json if missing
cat > contacts.json << 'EOF'
[
  {
    "recipient_email": "test@example.com",
    "company": "Test Company",
    "role": "Software Engineer",
    "candidate_name": "Your Name",
    "candidate_background": "Python developer with ML experience"
  }
]
EOF
```

### Fix 2: Add fallback for missing files

Modify `ui/app.py` to handle missing files gracefully:

```python
# In the main function, add fallback
if not os.path.exists("contacts.json"):
    st.warning("No contacts.json found. Please upload contacts in the Upload Contacts page.")
    contacts = []
else:
    contacts = load_targets("contacts.json")
```

### Fix 3: Add error handling for configuration

```python
# In load_config_safe(), add better error handling
def load_config_safe():
    """Load configuration with error handling."""
    try:
        return load_config()
    except Exception as e:
        st.error(f"Configuration error: {e}")
        st.info("Please ensure all environment variables are set in Streamlit Cloud Secrets.")
        return None
```

## Deployment Checklist

Before deploying to Streamlit Cloud:

- [ ] Main file path set to `ui/app.py`
- [ ] `requirements.txt` in repository root
- [ ] All dependencies listed in requirements.txt
- [ ] `.streamlit/config.toml` committed
- [ ] `.streamlit/credentials.toml` committed
- [ ] Environment variables set in Streamlit Cloud Secrets
- [ ] `contacts.json` exists or upload functionality works
- [ ] All `__init__.py` files present in Python packages
- [ ] No hardcoded paths (use relative paths)
- [ ] App tested locally with `DRY_RUN=true`

## Getting Help

If the app still doesn't deploy:

1. **Check Streamlit Cloud Status:** https://status.streamlit.io
2. **Review Documentation:** https://docs.streamlit.io/streamlit-cloud
3. **Check Community Forum:** https://discuss.streamlit.io
4. **Contact Support:** Through Streamlit Cloud dashboard

## Common Error Messages and Solutions

### "ModuleNotFoundError: No module named 'src'"

**Cause:** Import path issue or missing `__init__.py`

**Solution:** 
- Ensure `src/__init__.py` exists
- Check import statements use correct relative paths
- Verify file structure matches local setup

### "KeyError: 'SMTP_HOST'"

**Cause:** Environment variable not set in Streamlit Cloud

**Solution:**
- Add SMTP_HOST to Streamlit Cloud Secrets
- Restart the app after adding secrets

### "FileNotFoundError: contacts.json"

**Cause:** contacts.json not in repository or not accessible

**Solution:**
- Add contacts.json to repository
- Or implement file upload functionality
- Or add fallback for missing file

### "AuthenticationError: (535, b'5.7.8 Username and Password not accepted')"

**Cause:** SMTP credentials incorrect or using regular password instead of App Password

**Solution:**
- Use Gmail App Password, not regular password
- Enable 2FA on Google Account
- Generate new App Password at https://myaccount.google.com/apppasswords

## Next Steps

1. Check Streamlit Cloud deployment logs
2. Verify main file path is `ui/app.py`
3. Ensure all environment variables are set
4. Test locally with cloud configuration
5. Review specific error messages in logs
6. Apply appropriate fix based on error type
