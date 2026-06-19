# Deployment Plan: The Closer - Cold Email Parser

## Executive Summary

The Closer project is well-suited for Streamlit deployment, as it already includes a fully functional Streamlit web interface (`ui/app.py`). This deployment plan outlines multiple deployment strategies, with Streamlit Cloud being the recommended option for ease of use and cost-effectiveness.

## Current Project Status

**✅ Ready for Deployment:**
- Streamlit UI implemented (`ui/app.py`)
- Core functionality complete (email generation, preview, sending)
- Configuration management via environment variables
- Audit logging system
- Safety features (dry-run mode, volume caps)

**Dependencies:**
- `python-dotenv==1.0.0` - Environment variable management
- `groq==0.5.0` - AI/ML capabilities
- `streamlit==1.58.0` - Web UI framework
- `pandas` - Data handling (implied from CSV operations)

---

## Deployment Options Comparison

### Option 1: Streamlit Cloud (Recommended)

**Pros:**
- Free tier available
- Zero configuration required
- Automatic SSL/HTTPS
- Built-in authentication (optional)
- Easy deployment from GitHub
- Automatic updates on git push
- Managed infrastructure

**Cons:**
- Limited resources on free tier
- Vendor lock-in
- Limited customization
- Data persistence limitations

**Cost:** Free (up to certain limits), then $10/month for Pro

**Best For:** Quick deployment, testing, small-scale usage

### Option 2: Self-Hosted VPS (DigitalOcean, AWS, etc.)

**Pros:**
- Full control over environment
- Unlimited customization
- Better performance for larger datasets
- Complete data control
- Can scale vertically

**Cons:**
- Requires server management
- Manual SSL setup
- Higher maintenance overhead
- Cost increases with resources

**Cost:** $5-20/month for basic VPS

**Best For:** Production use, custom requirements, data privacy

### Option 3: Docker Container Deployment

**Pros:**
- Consistent environment
- Easy scaling
- Portability
- Version control
- Easy rollback

**Cons:**
- Requires Docker knowledge
- Additional complexity
- Resource overhead

**Cost:** Depends on hosting platform

**Best For:** Enterprise deployments, multi-environment setups

---

## Recommended Deployment: Streamlit Cloud

### Prerequisites

1. **GitHub Repository**
   - Push code to GitHub (already done based on git presence)
   - Ensure `.env` is in `.gitignore` (already done)
   - Verify all dependencies in `requirements.txt`

2. **Streamlit Account**
   - Sign up at https://streamlit.io/cloud
   - Connect GitHub account

3. **Environment Variables**
   - Prepare SMTP credentials
   - Document all required environment variables

### Step-by-Step Deployment

#### 1. Update requirements.txt

Add missing dependencies:
```txt
python-dotenv==1.0.0
groq==0.5.0
streamlit==1.58.0
pandas>=2.0.0
```

#### 2. Create Streamlit Configuration File

Create `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#2563eb"
backgroundColor = "#f8f9fa"
secondaryBackgroundColor = "#ffffff"
textColor = "#1e293b"
font = "sans serif"

[client]
showErrorDetails = true
maxUploadSize = 200

[logger]
level = "info"
```

#### 3. Create Deployment Script

Create `deploy.sh`:
```bash
#!/bin/bash
# Deployment script for Streamlit Cloud

echo "Preparing for Streamlit Cloud deployment..."

# Verify requirements
if [ ! -f "requirements.txt" ]; then
    echo "Error: requirements.txt not found"
    exit 1
fi

# Verify Streamlit app
if [ ! -f "ui/app.py" ]; then
    echo "Error: ui/app.py not found"
    exit 1
fi

# Create .streamlit directory if not exists
mkdir -p .streamlit

echo "Ready for deployment!"
echo "Next steps:"
echo "1. Push to GitHub"
echo "2. Go to https://share.streamlit.io"
echo "3. Connect your repository"
echo "4. Configure environment variables"
echo "5. Deploy!"
```

#### 4. Deploy to Streamlit Cloud

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Streamlit Cloud deployment"
   git push origin main
   ```

2. **Connect to Streamlit Cloud**
   - Go to https://share.streamlit.io
   - Click "New app"
   - Select your GitHub repository
   - Select branch: `main`
   - Main file path: `ui/app.py`
   - Click "Deploy"

3. **Configure Environment Variables**
   In Streamlit Cloud dashboard, add these secrets:
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

4. **Test Deployment**
   - Access your app at `https://your-app-name.streamlit.app`
   - Test dry-run mode first
   - Verify all features work
   - Test with live SMTP (set DRY_RUN=false)

#### 5. Data Persistence Strategy

Streamlit Cloud has limitations for file persistence. Implement this strategy:

**Option A: Streamlit Cloud File System**
- Use temporary file system
- Upload contacts via web interface
- Download logs manually
- **Limitation:** Files reset on redeploy

**Option B: Cloud Storage Integration**
- Add Google Drive / Dropbox / S3 integration
- Store contacts.json in cloud storage
- Store outreach_log.csv in cloud storage
- **Implementation:** Add to requirements.txt:
  ```txt
  gdown>=4.0.0  # For Google Drive
  ```

**Option C: Database Integration (Recommended for Production)**
- Add SQLite/PostgreSQL for persistent storage
- Replace CSV logging with database
- **Implementation:** Add to requirements.txt:
  ```txt
  sqlalchemy>=2.0.0
  ```

---

## Self-Hosted Deployment (Alternative)

### Prerequisites

- VPS with Ubuntu 20.04+ (DigitalOcean, AWS EC2, Linode)
- Domain name (optional)
- Basic Linux knowledge

### Step-by-Step Deployment

#### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install Nginx
sudo apt install nginx -y

# Install Git
sudo apt install git -y
```

#### 2. Application Setup

```bash
# Clone repository
cd /var/www
sudo git clone <your-repo-url> cold-email-parser
cd cold-email-parser

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
nano .env  # Add your credentials
```

#### 3. Systemd Service

Create `/etc/systemd/system/cold-email-parser.service`:
```ini
[Unit]
Description=Streamlit Cold Email Parser
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/cold-email-parser
Environment="PATH=/var/www/cold-email-parser/venv/bin"
ExecStart=/var/www/cold-email-parser/venv/bin/streamlit run ui/app.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start service:
```bash
sudo systemctl enable cold-email-parser
sudo systemctl start cold-email-parser
sudo systemctl status cold-email-parser
```

#### 4. Nginx Reverse Proxy

Create `/etc/nginx/sites-available/cold-email-parser`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/cold-email-parser /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 5. SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## Security Considerations

### Environment Variable Management

**Never commit sensitive data:**
- `.env` file must be in `.gitignore` (already done)
- Use Streamlit Cloud secrets for deployment
- For self-hosted, use `.env` with proper permissions

**Required Environment Variables:**
```env
# SMTP Configuration (HIGH SECURITY)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password  # Use Gmail App Password

# Sender Configuration
SENDER_NAME=Your Name

# Safety Configuration
DRY_RUN=true  # Set to false only after testing
SEND_MODE=draft
MAX_OUTREACH_PER_RUN=5

# Data Configuration
INPUT_PATH=contacts.json
```

### SMTP Security Best Practices

1. **Use App Passwords, Not Regular Passwords**
   - Enable 2FA on Gmail
   - Generate App Password at https://myaccount.google.com/apppasswords
   - Never use regular Gmail password

2. **Limit Email Volume**
   - Keep `MAX_OUTREACH_PER_RUN` low (5-10)
   - Gmail has sending limits (500/day for free accounts)
   - Monitor for spam flags

3. **Rate Limiting**
   - Implement delays between sends
   - Consider adding exponential backoff
   - Monitor bounce rates

### Application Security

1. **Authentication (Optional for Streamlit Cloud)**
   - Add basic authentication in Streamlit
   - Implement user management if needed
   - Consider OAuth integration

2. **Input Validation**
   - Validate email formats
   - Sanitize user inputs
   - Limit file upload sizes

3. **HTTPS Only**
   - Always use HTTPS in production
   - Streamlit Cloud provides automatic SSL
   - Use Let's Encrypt for self-hosted

---

## Data Persistence Strategy

### Current State

- `contacts.json` - Input data (user-provided)
- `outreach_log.csv` - Audit log (application-generated)

### Streamlit Cloud Limitations

- File system resets on redeploy
- No persistent storage by default
- Need alternative solution for production

### Recommended Solutions

#### Option 1: Cloud Storage Integration (Quick Fix)

Add Google Drive integration:
```python
# Add to requirements.txt
gdown>=4.0.0
pydrive>=1.3.1
```

Implement in code:
```python
# In input_loader.py
def load_targets_from_gdrive(file_id: str) -> list[Contact]:
    """Load contacts from Google Drive."""
    import gdown
    url = f'https://drive.google.com/uc?id={file_id}'
    output = 'contacts.json'
    gdown.download(url, output, quiet=False)
    return load_targets(output)
```

#### Option 2: Database Integration (Production-Ready)

Add SQLite for persistence:
```python
# Add to requirements.txt
sqlalchemy>=2.0.0
```

Create database models:
```python
# In src/database.py
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class ContactDB(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    recipient_email = Column(String)
    company = Column(String)
    role = Column(String)
    # ... other fields

class LogEntryDB(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    recipient_email = Column(String)
    status = Column(String)
    # ... other fields
```

#### Option 3: User-Managed Files (Simplest)

- Require users to upload contacts each session
- Provide download button for logs
- Add clear documentation about data persistence
- **Best for:** Streamlit Cloud free tier

---

## Monitoring and Maintenance

### Logging

**Current:** CSV-based logging
**Enhancement:** Add structured logging

```python
# Add to requirements.txt
structlog>=23.0.0
```

Implement:
```python
import structlog

log = structlog.get_logger()
log.info("email_sent", recipient=contact.recipient_email, status="sent")
```

### Health Checks

Add health check endpoint:
```python
# In ui/app.py
@st.cache_data
def health_check():
    """Check application health."""
    try:
        config = load_config()
        return {"status": "healthy", "config_loaded": True}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

### Error Monitoring

Consider adding error tracking:
```python
# Add to requirements.txt
sentry-sdk>=1.0.0
```

### Backup Strategy

**For Streamlit Cloud:**
- Manual download of logs
- Export contacts regularly
- Use cloud storage integration

**For Self-Hosted:**
- Automated database backups
- File system backups
- Off-site backup storage

---

## Scaling Considerations

### Current Limitations

- Single-user design
- No concurrent processing
- File-based data storage
- SMTP rate limits

### Scaling Options

#### 1. Horizontal Scaling

- Deploy multiple instances
- Load balancer (Nginx)
- Shared database storage
- Queue system for email sending

#### 2. Vertical Scaling

- Upgrade server resources
- Optimize database queries
- Implement caching
- Use async processing

#### 3. Email Service Integration

Replace SMTP with email API:
```python
# Add to requirements.txt
sendgrid>=6.0.0
# or
mailgun>=1.0.0
```

Benefits:
- Better deliverability
- Higher rate limits
- Built-in analytics
- Webhook support

---

## Cost Analysis

### Streamlit Cloud

**Free Tier:**
- Community support
- Limited resources
- Suitable for testing/small usage

**Pro Tier ($10/month):**
- Priority support
- More resources
- Custom domains
- Better performance

### Self-Hosted VPS

**DigitalOcean:**
- Basic: $5/month (1GB RAM, 1 CPU)
- Standard: $10/month (2GB RAM, 1 CPU)
- Premium: $20/month (4GB RAM, 2 CPU)

**AWS EC2:**
- t3.micro: $8/month (1GB RAM, 2 CPU)
- t3.small: $16/month (2GB RAM, 2 CPU)

**Additional Costs:**
- Domain: $10-15/year
- SSL: Free (Let's Encrypt)
- Email service: $0-30/month (if using API)

---

## Deployment Checklist

### Pre-Deployment

- [ ] Update `requirements.txt` with all dependencies
- [ ] Create `.streamlit/config.toml`
- [ ] Test application locally with dry-run mode
- [ ] Test with live SMTP (send to own email)
- [ ] Verify `.env` is in `.gitignore`
- [ ] Document all environment variables
- [ ] Prepare deployment documentation

### Streamlit Cloud Deployment

- [ ] Push code to GitHub
- [ ] Create Streamlit Cloud account
- [ ] Connect GitHub repository
- [ ] Configure app settings
- [ ] Add environment variables in secrets
- [ ] Deploy application
- [ ] Test all features
- [ ] Verify dry-run mode works
- [ ] Test live sending (carefully)

### Self-Hosted Deployment

- [ ] Provision VPS
- [ ] Configure DNS (if using domain)
- [ ] Set up server security (SSH, firewall)
- [ ] Install dependencies
- [ ] Clone repository
- [ ] Configure environment variables
- [ ] Set up systemd service
- [ ] Configure Nginx reverse proxy
- [ ] Set up SSL certificate
- [ ] Test application
- [ ] Set up monitoring
- [ ] Configure backups

### Post-Deployment

- [ ] Monitor application health
- [ ] Check email deliverability
- [ ] Review audit logs
- [ ] Test user workflows
- [ ] Document any issues
- [ ] Set up alerting
- [ ] Plan regular maintenance

---

## Troubleshooting

### Streamlit Cloud Issues

**App won't start:**
- Check requirements.txt for missing dependencies
- Verify main file path is correct
- Check Streamlit Cloud logs

**Environment variables not loading:**
- Verify secrets are set in Streamlit Cloud dashboard
- Check variable names match exactly
- Restart application after changing secrets

**File upload issues:**
- Check file size limits
- Verify file format (JSON)
- Check Streamlit Cloud logs

### Self-Hosted Issues

**Service won't start:**
- Check systemd logs: `sudo journalctl -u cold-email-parser`
- Verify Python environment is activated
- Check file permissions

**Nginx 502 Bad Gateway:**
- Check if Streamlit is running on port 8501
- Verify Nginx configuration
- Check firewall settings

**SMTP authentication fails:**
- Verify App Password is correct
- Check 2FA is enabled
- Verify SMTP_USER matches Gmail address

---

## Rollback Plan

### Streamlit Cloud

1. Revert to previous commit in GitHub
2. Streamlit Cloud auto-redeploys on push
3. Or use "Rollback" feature in Streamlit Cloud dashboard

### Self-Hosted

1. Keep previous version in separate directory
2. Switch git branch: `git checkout previous-version`
3. Restart systemd service
4. Or restore from backup

---

## Next Steps

### Immediate (Week 1)

1. Update `requirements.txt` with missing dependencies
2. Create `.streamlit/config.toml`
3. Test Streamlit Cloud deployment
4. Configure environment variables
5. Test dry-run mode in production

### Short-term (Week 2-4)

1. Implement data persistence strategy
2. Add authentication (if needed)
3. Set up monitoring
4. Document deployment process
5. Create user guide

### Long-term (Month 2+)

1. Consider database integration
2. Add email service API integration
3. Implement scaling strategy
4. Add analytics
5. Optimize performance

---

## Conclusion

**Streamlit Cloud is the recommended deployment option** for The Closer project because:

1. **Zero Configuration:** Deploy directly from GitHub
2. **Free Tier Available:** No cost for testing/small usage
3. **Automatic SSL:** HTTPS by default
4. **Easy Updates:** Redeploy on git push
5. **Managed Infrastructure:** No server maintenance

The project is already well-structured for Streamlit deployment with a functional web interface. The main consideration is data persistence, which can be addressed with cloud storage integration or user-managed file uploads.

For production use with higher volume requirements, consider self-hosted deployment with database integration for better data persistence and scalability.
