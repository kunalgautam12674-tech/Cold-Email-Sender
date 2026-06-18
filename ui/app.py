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

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .email-preview {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def load_config_safe():
    """Load configuration with error handling."""
    try:
        return load_config()
    except Exception as e:
        st.error(f"Failed to load configuration: {e}")
        return None


def display_email_preview(draft: EmailDraft, contact: Contact):
    """Display email preview in a formatted box."""
    st.markdown(f"""
    <div class="email-preview">
        <h3>📧 Email Preview</h3>
        <p><strong>To:</strong> {contact.recipient_email}</p>
        <p><strong>Name:</strong> {contact.recipient_name or 'N/A'}</p>
        <p><strong>Company:</strong> {contact.company}</p>
        <p><strong>Role:</strong> {contact.role}</p>
        <hr>
        <p><strong>Subject:</strong> {draft.subject}</p>
        <hr>
        <p><strong>Body:</strong></p>
        <pre style="white-space: pre-wrap; font-family: Arial, sans-serif;">{draft.body}</pre>
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
            st.subheader("📊 Outreach Log")
            st.dataframe(df, use_container_width=True)
            
            # Summary statistics
            st.subheader("📈 Summary Statistics")
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
            st.warning(f"Could not read log file: {e}")
    else:
        st.info("No log file found yet. Send some emails to see the log.")


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">📧 The Closer</h1>', unsafe_allow_html=True)
    st.markdown("Cold Email Writer + Send Bot")
    
    # Load configuration
    config = load_config_safe()
    if not config:
        st.stop()
    
    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Display current config
        st.subheader("Current Configuration")
        st.info(f"""
        - **Dry Run:** {config.dry_run}
        - **Send Mode:** {config.send_mode}
        - **Max Outreach:** {config.max_outreach_per_run}
        - **Input Path:** {config.input_path or 'None (use upload)'}
        """)
        
        if config.dry_run:
            st.warning("⚠️ Dry Run Mode - No emails will be sent")
        else:
            st.success("✅ Live Mode - Emails will be sent")
        
        st.divider()
        
        # Navigation
        st.header("📋 Navigation")
        page = st.radio(
            "Select Page",
            ["Generate Emails", "Upload Contacts", "View Log", "Settings"],
            label_visibility="collapsed"
        )
    
    # Page: Generate Emails
    if page == "Generate Emails":
        st.header("📝 Generate Emails")
        
        # Load contacts
        if config.input_path and os.path.exists(config.input_path):
            contacts = load_targets(config.input_path)
            st.success(f"✅ Loaded {len(contacts)} contacts from {config.input_path}")
        else:
            st.info("No input file configured. Please upload contacts in the 'Upload Contacts' page.")
            contacts = []
        
        if not contacts:
            st.warning("No contacts available. Please upload contacts first.")
            st.stop()
        
        # Apply volume cap
        max_contacts = min(len(contacts), config.max_outreach_per_run)
        if max_contacts < len(contacts):
            st.info(f"Volume cap: Processing {max_contacts} of {len(contacts)} contacts")
        
        contacts_to_process = contacts[:max_contacts]
        
        # Process contacts
        if st.button("🚀 Start Processing", type="primary"):
            progress_bar = st.progress(0)
            results = []
            
            for idx, contact in enumerate(contacts_to_process):
                progress_bar.progress((idx + 1) / max_contacts)
                
                # Generate email
                draft = generate_email(contact, config)
                
                # Display preview
                st.divider()
                st.subheader(f"Contact {idx + 1}/{max_contacts}: {contact.recipient_email}")
                display_email_preview(draft, contact)
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    send_btn = st.button("📤 Send", key=f"send_{idx}")
                with col2:
                    draft_btn = st.button("📝 Draft", key=f"draft_{idx}")
                with col3:
                    skip_btn = st.button("⏭️ Skip", key=f"skip_{idx}")
                
                # Handle action
                if send_btn:
                    if config.dry_run:
                        st.info("⚠️ Dry run mode - skipping actual delivery")
                        status = "generated"
                    else:
                        result = deliver_email(draft, contact, config, "send")
                        status = result.status
                        if result.status == "sent":
                            st.success(f"✅ Email sent to {contact.recipient_email}")
                        else:
                            st.error(f"❌ Failed to send: {result.error}")
                
                elif draft_btn:
                    if config.dry_run:
                        st.info("⚠️ Dry run mode - skipping actual delivery")
                        status = "generated"
                    else:
                        result = deliver_email(draft, contact, config, "draft")
                        status = result.status
                        if result.status == "drafted":
                            st.success(f"✅ Email drafted for {contact.recipient_email}")
                        else:
                            st.error(f"❌ Failed to draft: {result.error}")
                
                elif skip_btn:
                    st.info(f"⏭️ Skipped {contact.recipient_email}")
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
                
                st.divider()
            
            # Summary
            st.subheader("📊 Batch Summary")
            summary_df = pd.DataFrame(results)
            st.dataframe(summary_df, use_container_width=True)
            
            sent_count = sum(1 for r in results if r["status"] == "sent")
            st.success(f"✅ Processed {len(results)} contacts: {sent_count} sent")
    
    # Page: Upload Contacts
    elif page == "Upload Contacts":
        st.header("📤 Upload Contacts")
        
        st.info("""
        Upload a JSON file with contact information. The file should contain an array of contact objects.
        
        Required fields:
        - recipient_email
        - company
        - role
        - candidate_name
        - candidate_background
        
        Optional fields:
        - recipient_name
        - job_url
        - personalization_note
        - portfolio_url
        - linkedin_url
        - resume_link
        """)
        
        uploaded_file = st.file_uploader(
            "Choose a JSON file",
            type="json",
            help="Upload contacts.json file"
        )
        
        if uploaded_file:
            try:
                contacts = json.load(uploaded_file)
                st.success(f"✅ Loaded {len(contacts)} contacts")
                
                # Display contacts
                st.subheader("📋 Contacts Preview")
                for idx, contact in enumerate(contacts[:5]):
                    with st.expander(f"Contact {idx + 1}: {contact.get('recipient_email', 'N/A')}"):
                        st.json(contact)
                
                if len(contacts) > 5:
                    st.info(f"... and {len(contacts) - 5} more contacts")
                
                # Option to save
                if st.button("💾 Save as contacts.json"):
                    with open("contacts.json", "w") as f:
                        json.dump(contacts, f, indent=2)
                    st.success("✅ Saved to contacts.json")
                    
            except Exception as e:
                st.error(f"❌ Error loading file: {e}")
    
    # Page: View Log
    elif page == "View Log":
        st.header("📊 Outreach Log")
        display_log_file()
    
    # Page: Settings
    elif page == "Settings":
        st.header("⚙️ Settings")
        
        st.subheader("Configuration")
        st.json({
            "smtp_host": config.smtp_host,
            "smtp_port": config.smtp_port,
            "smtp_user": config.smtp_user,
            "sender_name": config.sender_name,
            "dry_run": config.dry_run,
            "send_mode": config.send_mode,
            "max_outreach_per_run": config.max_outreach_per_run,
            "input_path": config.input_path
        })
        
        st.warning("⚠️ To change settings, edit the .env file and restart the app.")


if __name__ == "__main__":
    main()
