"""
Streamlit UI for The Closer - Cold Email Writer + Send Bot

Web-based interface for generating, previewing, and sending cold emails.
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import load_config, AppConfig
from src.input_loader import load_targets
from src.email_generator import generate_email
from src.email_sender import deliver_email
from src.logger import append_log
from src.models import Contact, EmailDraft, LogEntry


# Page configuration
st.set_page_config(
    page_title="The Closer - Cold Email Bot",
    page_icon="📧",
    layout="wide"
)

# Custom CSS - Modern, clean design with better visibility
st.markdown("""
<style>
    /* Global styles */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Header styling */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #2563eb;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .subtitle {
        font-size: 1.25rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Card styling */
    .card {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #e5e7eb;
    }
    
    /* Email preview styling */
    .email-preview {
        background-color: white;
        padding: 2rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 2px solid #3b82f6;
    }
    
    .email-preview h3 {
        color: #1e40af;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .email-preview p {
        color: #374151;
        font-size: 1rem;
        line-height: 1.6;
        margin: 0.5rem 0;
    }
    
    .email-preview strong {
        color: #1f2937;
        font-weight: 600;
    }
    
    .email-preview hr {
        border: none;
        border-top: 2px solid #e5e7eb;
        margin: 1rem 0;
    }
    
    .email-preview pre {
        background-color: #f9fafb;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        font-size: 1rem;
        line-height: 1.6;
        color: #374151;
    }
    
    /* Success box */
    .success-box {
        background-color: #dcfce7;
        border: 2px solid #22c55e;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #166534;
    }
    
    /* Warning box */
    .warning-box {
        background-color: #fef3c7;
        border: 2px solid #f59e0b;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #92400e;
    }
    
    /* Info box */
    .info-box {
        background-color: #dbeafe;
        border: 2px solid #3b82f6;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #1e40af;
    }
    
    /* Error box */
    .error-box {
        background-color: #fee2e2;
        border: 2px solid #ef4444;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #991b1b;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #2563eb;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #1d4ed8;
        transform: translateY(-1px);
    }
    
    /* Metric styling */
    .metric-card {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: white;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.75rem;
        font-weight: 600;
        color: #1e293b;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #3b82f6;
    }
    
    /* Contact card */
    .contact-card {
        background-color: white;
        border-radius: 10px;
        padding: 1.25rem;
        margin: 0.75rem 0;
        border-left: 4px solid #3b82f6;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)


def load_config_safe():
    """Load configuration with error handling."""
    try:
        return load_config()
    except Exception as e:
        st.error(f"Configuration error: {e}")
        st.info("Please ensure all environment variables are set in Streamlit Cloud Secrets.")
        st.info("Required variables: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SENDER_NAME")
        return None


def display_email_preview(draft: EmailDraft, contact: Contact):
    """Display email preview in a formatted box."""
    st.markdown(f"""
    <div class="email-preview">
        <h3>📧 Email Preview</h3>
        <div style="background-color: #f8fafc; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <p><strong>To:</strong> {contact.recipient_email}</p>
            <p><strong>Name:</strong> {contact.recipient_name or 'N/A'}</p>
            <p><strong>Company:</strong> {contact.company}</p>
            <p><strong>Role:</strong> {contact.role}</p>
        </div>
        <hr>
        <p><strong>Subject:</strong> {draft.subject}</p>
        <hr>
        <p><strong>Body:</strong></p>
        <pre style="white-space: pre-wrap; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 1.05rem; line-height: 1.7;">{draft.body}</pre>
        <hr>
        <p><strong>Word Count:</strong> {draft.word_count}</p>
    </div>
    """, unsafe_allow_html=True)


def display_log_file():
    """Display the outreach log file if it exists."""
    log_path = "outreach_log.csv"
    if os.path.exists(log_path):
        try:
            df = pd.read_csv(log_path)
            st.markdown('<h3>📊 Outreach Log</h3>', unsafe_allow_html=True)
            st.dataframe(df, width='stretch')
            
            # Summary statistics
            st.markdown('<h3>📈 Summary Statistics</h3>', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Attempts", len(df))
            with col2:
                sent_count = len(df[df['status'] == 'sent'])
                st.metric("Sent", sent_count)
            with col3:
                skipped_count = len(df[df['status'] == 'skipped'])
                st.metric("Skipped", skipped_count)
            with col4:
                failed_count = len(df[df['status'] == 'failed'])
                st.metric("Failed", failed_count)
        except Exception as e:
            st.markdown(f'<div class="warning-box">Could not read log file: {e}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box">ℹ️ No log file found yet. Send some emails to see the log.</div>', unsafe_allow_html=True)


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">📧 The Closer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Cold Email Writer + Send Bot</p>', unsafe_allow_html=True)
    
    # Load configuration
    config = load_config_safe()
    if not config:
        st.stop()
    
    # Sidebar for settings
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        # Display current config
        st.markdown("#### Current Configuration")
        st.markdown(f"""
        <div class="card">
            <p><strong>Dry Run:</strong> {config.dry_run}</p>
            <p><strong>Send Mode:</strong> {config.send_mode}</p>
            <p><strong>Max Outreach:</strong> {config.max_outreach_per_run}</p>
            <p><strong>Input Path:</strong> {config.input_path or 'None (use upload)'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if config.dry_run:
            st.markdown('<div class="warning-box">⚠️ Dry Run Mode - No emails will be sent</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-box">✅ Live Mode - Emails will be sent</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### 📋 Navigation")
        page = st.radio(
            "Select Page",
            ["Generate Emails", "Upload Contacts", "View Log", "Settings"],
            label_visibility="collapsed"
        )
    
    # Page: Generate Emails
    if page == "Generate Emails":
        st.markdown('<h2 class="section-header">📝 Generate Emails</h2>', unsafe_allow_html=True)
        
        # Load contacts
        if config.input_path and os.path.exists(config.input_path):
            try:
                contacts = load_targets(config.input_path)
                st.markdown(f'<div class="success-box">✅ Loaded {len(contacts)} contacts from {config.input_path}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f'<div class="error-box">❌ Error loading contacts: {e}</div>', unsafe_allow_html=True)
                contacts = []
        else:
            st.markdown('<div class="info-box">ℹ️ No input file configured. Please upload contacts in the "Upload Contacts" page.</div>', unsafe_allow_html=True)
            contacts = []
        
        if not contacts:
            st.markdown('<div class="warning-box">⚠️ No contacts available. Please upload contacts first.</div>', unsafe_allow_html=True)
            st.stop()
        
        # Apply volume cap
        max_contacts = min(len(contacts), config.max_outreach_per_run)
        if max_contacts < len(contacts):
            st.markdown(f'<div class="info-box">ℹ️ Volume cap: Processing {max_contacts} of {len(contacts)} contacts</div>', unsafe_allow_html=True)
        
        contacts_to_process = contacts[:max_contacts]
        
        # Process contacts
        if st.button("🚀 Start Processing", type="primary", width='stretch'):
            progress_bar = st.progress(0)
            results = []
            
            for idx, contact in enumerate(contacts_to_process):
                progress_bar.progress((idx + 1) / max_contacts)
                
                # Generate email
                draft = generate_email(contact, config)
                
                # Display preview
                st.markdown("---")
                st.markdown(f"### Contact {idx + 1}/{max_contacts}: {contact.recipient_email}")
                display_email_preview(draft, contact)
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    send_btn = st.button("📤 Send", key=f"send_{idx}", width='stretch')
                with col2:
                    draft_btn = st.button("📝 Draft", key=f"draft_{idx}", width='stretch')
                with col3:
                    skip_btn = st.button("⏭️ Skip", key=f"skip_{idx}", width='stretch')
                
                # Handle action
                if send_btn:
                    if config.dry_run:
                        st.markdown('<div class="warning-box">⚠️ Dry run mode - skipping actual delivery</div>', unsafe_allow_html=True)
                        status = "generated"
                    else:
                        result = deliver_email(draft, contact, config, "send")
                        status = result.status
                        if result.status == "sent":
                            st.markdown(f'<div class="success-box">✅ Email sent to {contact.recipient_email}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="error-box">❌ Failed to send: {result.error}</div>', unsafe_allow_html=True)
                
                elif draft_btn:
                    if config.dry_run:
                        st.markdown('<div class="warning-box">⚠️ Dry run mode - skipping actual delivery</div>', unsafe_allow_html=True)
                        status = "generated"
                    else:
                        result = deliver_email(draft, contact, config, "draft")
                        status = result.status
                        if result.status == "drafted":
                            st.markdown(f'<div class="success-box">✅ Email drafted for {contact.recipient_email}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="error-box">❌ Failed to draft: {result.error}</div>', unsafe_allow_html=True)
                
                elif skip_btn:
                    st.markdown(f'<div class="info-box">⏭️ Skipped {contact.recipient_email}</div>', unsafe_allow_html=True)
                    status = "skipped"
                else:
                    status = "skipped"
                
                # Log result
                log_entry = LogEntry(
                    timestamp=datetime.now().isoformat(),
                    recipient_email=contact.recipient_email,
                    company=contact.company,
                    role=contact.role,
                    subject=draft.subject,
                    status=status,
                    error_message=""
                )
                append_log(log_entry)
                results.append({
                    "email": contact.recipient_email,
                    "company": contact.company,
                    "status": status
                })
                
                st.markdown("---")
            
            # Summary
            st.markdown('<h2 class="section-header">📊 Batch Summary</h2>', unsafe_allow_html=True)
            summary_df = pd.DataFrame(results)
            st.dataframe(summary_df, width='stretch')
            
            sent_count = sum(1 for r in results if r["status"] == "sent")
            st.markdown(f'<div class="success-box">✅ Processed {len(results)} contacts: {sent_count} sent</div>', unsafe_allow_html=True)
    
    # Page: Upload Contacts
    elif page == "Upload Contacts":
        st.markdown('<h2 class="section-header">📤 Upload Contacts</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
            <h4>📝 Upload Instructions</h4>
            <p>Upload a JSON file with contact information. The file should contain an array of contact objects.</p>
            <hr>
            <p><strong>Required fields:</strong></p>
            <ul>
                <li>recipient_email</li>
                <li>company</li>
                <li>role</li>
                <li>candidate_name</li>
                <li>candidate_background</li>
            </ul>
            <hr>
            <p><strong>Optional fields:</strong></p>
            <ul>
                <li>recipient_name</li>
                <li>job_url</li>
                <li>personalization_note</li>
                <li>portfolio_url</li>
                <li>linkedin_url</li>
                <li>resume_link</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose a JSON file",
            type="json",
            help="Upload contacts.json file",
            label_visibility="visible"
        )
        
        if uploaded_file:
            try:
                contacts = json.load(uploaded_file)
                st.markdown(f'<div class="success-box">✅ Loaded {len(contacts)} contacts</div>', unsafe_allow_html=True)
                
                # Display contacts
                st.markdown('<h3>📋 Contacts Preview</h3>', unsafe_allow_html=True)
                for idx, contact in enumerate(contacts[:5]):
                    with st.expander(f"Contact {idx + 1}: {contact.get('recipient_email', 'N/A')}"):
                        st.json(contact)
                
                if len(contacts) > 5:
                    st.markdown(f'<div class="info-box">... and {len(contacts) - 5} more contacts</div>', unsafe_allow_html=True)
                
                # Option to save
                if st.button("💾 Save as contacts.json", width='stretch'):
                    with open("contacts.json", "w") as f:
                        json.dump(contacts, f, indent=2)
                    st.markdown('<div class="success-box">✅ Saved to contacts.json</div>', unsafe_allow_html=True)
                    
            except Exception as e:
                st.markdown(f'<div class="error-box">❌ Error loading file: {e}</div>', unsafe_allow_html=True)
    
    # Page: View Log
    elif page == "View Log":
        st.markdown('<h2 class="section-header">📊 Outreach Log</h2>', unsafe_allow_html=True)
        display_log_file()
    
    # Page: Settings
    elif page == "Settings":
        st.markdown('<h2 class="section-header">⚙️ Settings</h2>', unsafe_allow_html=True)
        
        st.markdown('<h3>Configuration</h3>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="card">
            <p><strong>SMTP Host:</strong> {config.smtp_host}</p>
            <p><strong>SMTP Port:</strong> {config.smtp_port}</p>
            <p><strong>SMTP User:</strong> {config.smtp_user}</p>
            <p><strong>Sender Name:</strong> {config.sender_name}</p>
            <p><strong>Dry Run:</strong> {config.dry_run}</p>
            <p><strong>Send Mode:</strong> {config.send_mode}</p>
            <p><strong>Max Outreach:</strong> {config.max_outreach_per_run}</p>
            <p><strong>Input Path:</strong> {config.input_path}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="warning-box">⚠️ To change settings, edit the .env file and restart the app.</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
