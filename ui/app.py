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

# Custom CSS - Modern, animated design with gradients and effects
st.markdown("""
<style>
    /* Global styles with animated gradient background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Main content area with glass effect */
    .main .block-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        animation: fadeIn 0.8s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Header styling with gradient text */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        text-align: center;
        animation: slideIn 1s ease-out;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-50px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .subtitle {
        font-size: 1.5rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 500;
        animation: fadeInUp 1s ease-out 0.3s both;
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Card styling with hover effects */
    .card {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.5);
        transition: all 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    /* Email preview styling with animated border */
    .email-preview {
        background: linear-gradient(145deg, #ffffff 0%, #f0f4ff 100%);
        padding: 2rem;
        border-radius: 16px;
        margin: 1.5rem 0;
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2);
        border: 2px solid transparent;
        background-clip: padding-box;
        position: relative;
        animation: pulse 2s infinite;
    }
    
    .email-preview::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border-radius: 16px;
        padding: 2px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
    }
    
    @keyframes pulse {
        0%, 100% { box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2); }
        50% { box-shadow: 0 8px 40px rgba(102, 126, 234, 0.4); }
    }
    
    .email-preview h3 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 1.75rem;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    
    .email-preview p {
        color: #374151;
        font-size: 1.05rem;
        line-height: 1.7;
        margin: 0.75rem 0;
    }
    
    .email-preview strong {
        color: #1e293b;
        font-weight: 700;
    }
    
    .email-preview hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 1.5rem 0;
    }
    
    .email-preview pre {
        background: linear-gradient(145deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid #dee2e6;
        font-size: 1.05rem;
        line-height: 1.7;
        color: #374151;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    
    /* Success box with animation */
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 2px solid #28a745;
        border-radius: 12px;
        padding: 1.25rem;
        margin: 1rem 0;
        color: #155724;
        animation: slideInRight 0.5s ease-out;
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(50px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    /* Warning box with animation */
    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeeba 100%);
        border: 2px solid #ffc107;
        border-radius: 12px;
        padding: 1.25rem;
        margin: 1rem 0;
        color: #856404;
        animation: slideInRight 0.5s ease-out;
    }
    
    /* Info box with animation */
    .info-box {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border: 2px solid #17a2b8;
        border-radius: 12px;
        padding: 1.25rem;
        margin: 1rem 0;
        color: #0c5460;
        animation: slideInRight 0.5s ease-out;
    }
    
    /* Error box with animation */
    .error-box {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border: 2px solid #dc3545;
        border-radius: 12px;
        padding: 1.25rem;
        margin: 1rem 0;
        color: #721c24;
        animation: shake 0.5s ease-in-out;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-10px); }
        75% { transform: translateX(10px); }
    }
    
    /* Button styling with gradient and hover effects */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.875rem 2rem;
        font-size: 1.05rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
    }
    
    .stButton > button:active {
        transform: translateY(-1px);
    }
    
    /* Metric styling with gradient cards */
    .metric-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border: 1px solid rgba(255,255,255,0.5);
    }
    
    .metric-card:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    /* Sidebar styling with gradient */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Section headers with gradient underline */
    .section-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
        margin: 2rem 0 1.5rem 0;
        padding-bottom: 0.75rem;
        position: relative;
        animation: fadeIn 0.8s ease-out;
    }
    
    .section-header::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 2px;
    }
    
    /* Contact card with animated border */
    .contact-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid;
        border-image: linear-gradient(180deg, #667eea 0%, #764ba2 100%) 1;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .contact-card:hover {
        transform: translateX(10px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* File uploader styling */
    .stFileUploader {
        border: 2px dashed #667eea;
        border-radius: 12px;
        padding: 2rem;
        background: rgba(102, 126, 234, 0.05);
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        background: rgba(102, 126, 234, 0.1);
        border-color: #764ba2;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 8px;
        padding: 0.75rem 1rem;
        color: white;
        font-weight: 600;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Radio button styling */
    .stRadio > div {
        background: rgba(255,255,255,0.9);
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Select box styling */
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.9);
        border-radius: 8px;
        border: 1px solid #dee2e6;
    }
    
    /* Text input styling */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #dee2e6;
        padding: 0.75rem;
    }
    
    /* Text area styling */
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 1px solid #dee2e6;
        padding: 0.75rem;
    }
    
    /* Loading animation */
    .stSpinner {
        color: #667eea;
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
    try:
        # Header
        st.markdown('<h1 class="main-header">📧 The Closer</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Cold Email Writer + Send Bot</p>', unsafe_allow_html=True)
        
        # Load configuration
        config = load_config_safe()
        if not config:
            st.error("Failed to load configuration. Please check environment variables.")
            st.stop()
    except Exception as e:
        st.error(f"Startup error: {e}")
        import traceback
        st.error(traceback.format_exc())
        st.stop()
    
    # Sidebar for settings with enhanced styling
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        # Animated welcome message
        st.markdown("""
        <div style="text-align: center; padding: 1rem; margin-bottom: 1rem;">
            <h4 style="color: white; margin: 0;">🚀 Welcome!</h4>
            <p style="color: rgba(255,255,255,0.8); font-size: 0.9rem; margin: 0.5rem 0 0 0;">
                Your AI-powered email assistant
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display current config with enhanced card
        st.markdown("#### Current Configuration")
        st.markdown(f"""
        <div class="card">
            <p style="margin: 0.5rem 0;"><strong>🔒 Dry Run:</strong> {config.dry_run}</p>
            <p style="margin: 0.5rem 0;"><strong>📤 Send Mode:</strong> {config.send_mode}</p>
            <p style="margin: 0.5rem 0;"><strong>📊 Max Outreach:</strong> {config.max_outreach_per_run}</p>
            <p style="metric: 0.5rem 0;"><strong>📁 Input Path:</strong> {config.input_path or 'None (use upload)'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Animated status indicator
        if config.dry_run:
            st.markdown("""
            <div class="warning-box" style="animation: pulse 2s infinite;">
                ⚠️ Dry Run Mode - No emails will be sent
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="success-box" style="animation: pulse 2s infinite;">
                ✅ Live Mode - Emails will be sent
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation with custom styling
        st.markdown("### 📋 Navigation")
        page = st.radio(
            "Select Page",
            ["📝 Generate Emails", "📤 Upload Contacts", "📊 View Log", "⚙️ Settings"],
            label_visibility="collapsed"
        )
    
    # Page: Generate Emails
    if page == "📝 Generate Emails":
        st.markdown('<h2 class="section-header">📝 Generate Emails</h2>', unsafe_allow_html=True)
        
        # Animated stats cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; color: #667eea;">📧 Ready to Send</h3>
                <p style="font-size: 2rem; font-weight: 700; margin: 0.5rem 0; color: #1e293b;">{len(contacts) if config.input_path and os.path.exists(config.input_path) else 0}</p>
                <p style="margin: 0; color: #64748b;">Contacts Available</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; color: #764ba2;">📊 Volume Cap</h3>
                <p style="font-size: 2rem; font-weight: 700; margin: 0.5rem 0; color: #1e293b;">{config.max_outreach_per_run}</p>
                <p style="margin: 0; color: #64748b;">Max Per Run</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="margin: 0; color: #667eea;">🔒 Mode</h3>
                <p style="font-size: 1.5rem; font-weight: 700; margin: 0.5rem 0; color: #1e293b;">{'DRY RUN' if config.dry_run else 'LIVE'}</p>
                <p style="margin: 0; color: #64748b;">Current Status</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Load contacts with enhanced messaging
        if config.input_path and os.path.exists(config.input_path):
            try:
                contacts = load_targets(config.input_path)
                st.markdown(f"""
                <div class="success-box" style="animation: slideInRight 0.5s ease-out;">
                    ✅ Successfully loaded {len(contacts)} contacts from {config.input_path}
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f'<div class="error-box">❌ Error loading contacts: {e}</div>', unsafe_allow_html=True)
                contacts = []
        else:
            st.markdown('<div class="info-box">ℹ️ No input file configured. Please upload contacts in the "Upload Contacts" page.</div>', unsafe_allow_html=True)
            contacts = []
        
        if not contacts:
            st.markdown("""
            <div class="warning-box" style="text-align: center; padding: 2rem;">
                <h3 style="margin: 0 0 1rem 0;">⚠️ No Contacts Available</h3>
                <p style="margin: 0;">Please upload contacts first to get started.</p>
            </div>
            """, unsafe_allow_html=True)
            st.stop()
        
        # Apply volume cap with enhanced messaging
        max_contacts = min(len(contacts), config.max_outreach_per_run)
        if max_contacts < len(contacts):
            st.markdown(f"""
            <div class="info-box" style="animation: fadeInUp 0.5s ease-out;">
                ℹ️ Volume cap active: Processing {max_contacts} of {len(contacts)} contacts
            </div>
            """, unsafe_allow_html=True)
        
        contacts_to_process = contacts[:max_contacts]
        
        # Process contacts with enhanced button
        if st.button("🚀 Start Processing", type="primary", width='stretch', help="Begin generating personalized emails"):
            progress_bar = st.progress(0)
            results = []
            
            for idx, contact in enumerate(contacts_to_process):
                progress_bar.progress((idx + 1) / max_contacts)
                
                # Generate email
                draft = generate_email(contact, config)
                
                # Display preview with enhanced styling
                st.markdown("---")
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); 
                           padding: 1.5rem; border-radius: 12px; margin: 1rem 0;">
                    <h3 style="margin: 0 0 0.5rem 0; color: #667eea;">
                        📧 Contact {idx + 1}/{max_contacts}: {contact.recipient_email}
                    </h3>
                    <p style="margin: 0; color: #64748b;">{contact.company} • {contact.role}</p>
                </div>
                """, unsafe_allow_html=True)
                display_email_preview(draft, contact)
                
                # Action buttons with enhanced styling
                col1, col2, col3 = st.columns(3)
                with col1:
                    send_btn = st.button("📤 Send", key=f"send_{idx}", width='stretch', help="Send this email now")
                with col2:
                    draft_btn = st.button("📝 Draft", key=f"draft_{idx}", width='stretch', help="Save as draft")
                with col3:
                    skip_btn = st.button("⏭️ Skip", key=f"skip_{idx}", width='stretch', help="Skip this contact")
                
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
            
            # Enhanced summary with celebration animation
            st.markdown('<h2 class="section-header">📊 Batch Summary</h2>', unsafe_allow_html=True)
            summary_df = pd.DataFrame(results)
            st.dataframe(summary_df, width='stretch')
            
            sent_count = sum(1 for r in results if r["status"] == "sent")
            st.markdown(f"""
            <div class="success-box" style="animation: slideInRight 0.5s ease-out; text-align: center; padding: 1.5rem;">
                <h3 style="margin: 0 0 0.5rem 0;">✅ Processing Complete!</h3>
                <p style="margin: 0;">Processed {len(results)} contacts: {sent_count} sent successfully</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Page: Upload Contacts
    elif page == "📤 Upload Contacts":
        st.markdown('<h2 class="section-header">📤 Upload Contacts</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box" style="animation: fadeInUp 0.5s ease-out;">
            <h4 style="margin: 0 0 1rem 0;">📝 Upload Instructions</h4>
            <p style="margin: 0 0 1rem 0;">Upload a JSON file with contact information. The file should contain an array of contact objects.</p>
            <hr>
            <p style="margin: 0.5rem 0;"><strong>Required fields:</strong></p>
            <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                <li>recipient_email</li>
                <li>company</li>
                <li>role</li>
                <li>candidate_name</li>
                <li>candidate_background</li>
            </ul>
            <hr>
            <p style="margin: 0.5rem 0;"><strong>Optional fields:</strong></p>
            <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
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
            "📁 Choose a JSON file",
            type="json",
            help="Upload your contacts.json file here",
            label_visibility="visible"
        )
        
        if uploaded_file:
            try:
                contacts = json.load(uploaded_file)
                st.markdown(f"""
                <div class="success-box" style="animation: slideInRight 0.5s ease-out; text-align: center; padding: 1.5rem;">
                    <h3 style="margin: 0 0 0.5rem 0;">✅ File Uploaded Successfully!</h3>
                    <p style="margin: 0;">Loaded {len(contacts)} contacts from your file</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Display contacts with enhanced styling
                st.markdown('<h3 style="animation: fadeIn 0.5s ease-out;">📋 Contacts Preview</h3>', unsafe_allow_html=True)
                for idx, contact in enumerate(contacts[:5]):
                    with st.expander(f"👤 Contact {idx + 1}: {contact.get('recipient_email', 'N/A')}", expanded=False):
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
    elif page == "📊 View Log":
        st.markdown('<h2 class="section-header">📊 Outreach Log</h2>', unsafe_allow_html=True)
        display_log_file()
    
    # Page: Settings
    elif page == "⚙️ Settings":
        st.markdown('<h2 class="section-header">⚙️ Settings</h2>', unsafe_allow_html=True)
        
        st.markdown('<h3 style="animation: fadeIn 0.5s ease-out;">🔧 Configuration</h3>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="card" style="animation: fadeInUp 0.5s ease-out;">
            <p style="margin: 0.5rem 0;"><strong>🌐 SMTP Host:</strong> {config.smtp_host}</p>
            <p style="margin: 0.5rem 0;"><strong>🔌 SMTP Port:</strong> {config.smtp_port}</p>
            <p style="margin: 0.5rem 0;"><strong>📧 SMTP User:</strong> {config.smtp_user or 'Not configured'}</p>
            <p style="margin: 0.5rem 0;"><strong>👤 Sender Name:</strong> {config.sender_name or 'Not configured'}</p>
            <p style="margin: 0.5rem 0;"><strong>🔒 Dry Run:</strong> {config.dry_run}</p>
            <p style="margin: 0.5rem 0;"><strong>📤 Send Mode:</strong> {config.send_mode}</p>
            <p style="margin: 0.5rem 0;"><strong>📊 Max Outreach:</strong> {config.max_outreach_per_run}</p>
            <p style="margin: 0.5rem 0;"><strong>📁 Input Path:</strong> {config.input_path or 'Not configured'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box" style="animation: fadeInUp 0.5s ease-out 0.2s both;">
            <h4 style="margin: 0 0 0.5rem 0;">💡 How to Change Settings</h4>
            <p style="margin: 0;">Edit the .env file and restart the app to apply changes.</p>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
