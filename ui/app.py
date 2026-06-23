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

# Custom CSS - Dark theme with high contrast and modern typography
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Global dark theme styles */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        min-height: 100vh;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main content area with dark glass effect */
    .main .block-container {
        background: rgba(15, 15, 35, 0.85);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 2.5rem;
        margin: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.05);
        animation: fadeIn 0.8s ease-in;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Header styling with neon gradient text */
    .main-header {
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00d4ff 0%, #7c3aed 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        text-align: center;
        animation: slideIn 1s ease-out;
        letter-spacing: -0.02em;
        text-shadow: 0 0 40px rgba(124, 58, 237, 0.3);
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-50px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .subtitle {
        font-size: 1.5rem;
        color: #94a3b8;
        text-align: center;
        margin-bottom: 2.5rem;
        font-weight: 400;
        animation: fadeInUp 1s ease-out 0.3s both;
        letter-spacing: -0.01em;
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Card styling with dark theme */
    .card {
        background: linear-gradient(145deg, #1e1e3f 0%, #252550 100%);
        border-radius: 20px;
        padding: 1.75rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.08);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .card:hover {
        transform: translateY(-8px);
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.4);
        border-color: rgba(124, 58, 237, 0.3);
    }
    
    /* Email preview styling with neon effects */
    .email-preview {
        background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.05);
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
        border-radius: 20px;
        padding: 2px;
        background: linear-gradient(135deg, #00d4ff 0%, #7c3aed 50%, #f472b6 100%);
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
    }
    
    @keyframes pulse {
        0%, 100% { box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 20px rgba(124, 58, 237, 0.2); }
        50% { box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 30px rgba(124, 58, 237, 0.4); }
    }
    
    .email-preview h3 {
        background: linear-gradient(135deg, #00d4ff 0%, #7c3aed 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 1.75rem;
        margin-bottom: 1.5rem;
        font-weight: 700;
        letter-spacing: -0.01em;
    }
    
    .email-preview p {
        color: #e2e8f0;
        font-size: 1.05rem;
        line-height: 1.8;
        margin: 0.75rem 0;
        font-weight: 400;
    }
    
    .email-preview strong {
        color: #f8fafc;
        font-weight: 700;
    }
    
    .email-preview hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #7c3aed, transparent);
        margin: 1.5rem 0;
    }
    
    .email-preview pre {
        background: linear-gradient(145deg, #0f0f23 0%, #1a1a2e 100%);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        font-size: 1.05rem;
        line-height: 1.7;
        color: #e2e8f0;
        white-space: pre-wrap;
        word-wrap: break-word;
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* Success box with dark theme */
    .success-box {
        background: linear-gradient(135deg, #064e3b 0%, #065f46 100%);
        border: 2px solid #10b981;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #d1fae5;
        animation: slideInRight 0.5s ease-out;
        box-shadow: 0 8px 32px rgba(16, 185, 129, 0.2);
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(50px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    /* Warning box with dark theme */
    .warning-box {
        background: linear-gradient(135deg, #78350f 0%, #92400e 100%);
        border: 2px solid #f59e0b;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #fef3c7;
        animation: slideInRight 0.5s ease-out;
        box-shadow: 0 8px 32px rgba(245, 158, 11, 0.2);
    }
    
    /* Info box with dark theme */
    .info-box {
        background: linear-gradient(135deg, #0c4a6e 0%, #075985 100%);
        border: 2px solid #0ea5e9;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #e0f2fe;
        animation: slideInRight 0.5s ease-out;
        box-shadow: 0 8px 32px rgba(14, 165, 233, 0.2);
    }
    
    /* Error box with dark theme */
    .error-box {
        background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%);
        border: 2px solid #ef4444;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #fee2e2;
        animation: shake 0.5s ease-in-out;
        box-shadow: 0 8px 32px rgba(239, 68, 68, 0.2);
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-10px); }
        75% { transform: translateX(10px); }
    }
    
    /* Button styling with neon gradient */
    .stButton > button {
        background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
        color: white;
        border: none;
        border-radius: 16px;
        padding: 1rem 2.5rem;
        font-size: 1.05rem;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 32px rgba(124, 58, 237, 0.4);
        position: relative;
        overflow: hidden;
        font-family: 'Inter', sans-serif;
        letter-spacing: -0.01em;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-4px);
        box-shadow: 0 16px 48px rgba(124, 58, 237, 0.6);
    }
    
    .stButton > button:active {
        transform: translateY(-2px);
    }
    
    /* Metric styling with dark theme */
    .metric-card {
        background: linear-gradient(145deg, #1e1e3f 0%, #252550 100%);
        border-radius: 20px;
        padding: 2.5rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    .metric-card:hover {
        transform: scale(1.05);
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.4);
        border-color: rgba(124, 58, 237, 0.3);
    }
    
    .metric-card h3 {
        color: #94a3b8;
        font-size: 0.875rem;
        font-weight: 500;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    
    .metric-card p {
        color: #f8fafc;
        font-weight: 700;
    }
    
    /* Sidebar styling with dark gradient */
    .css-1d391kg {
        background: linear-gradient(180deg, #0f0f23 0%, #1a1a2e 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    /* Section headers with neon underline */
    .section-header {
        font-size: 2.25rem;
        font-weight: 700;
        color: #f8fafc;
        margin: 2.5rem 0 1.5rem 0;
        padding-bottom: 1rem;
        position: relative;
        animation: fadeIn 0.8s ease-out;
        letter-spacing: -0.02em;
    }
    
    .section-header::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #00d4ff 0%, #7c3aed 50%, #f472b6 100%);
        border-radius: 2px;
    }
    
    /* Contact card with dark theme */
    .contact-card {
        background: linear-gradient(145deg, #1e1e3f 0%, #252550 100%);
        border-radius: 16px;
        padding: 1.75rem;
        margin: 1rem 0;
        border-left: 5px solid;
        border-image: linear-gradient(180deg, #00d4ff 0%, #7c3aed 50%, #f472b6 100%) 1;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .contact-card:hover {
        transform: translateX(12px);
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.4);
    }
    
    /* Progress bar styling with neon */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #00d4ff 0%, #7c3aed 50%, #f472b6 100%);
    }
    
    /* File uploader styling with dark theme */
    .stFileUploader {
        border: 2px dashed #7c3aed;
        border-radius: 16px;
        padding: 2.5rem;
        background: rgba(124, 58, 237, 0.05);
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        background: rgba(124, 58, 237, 0.1);
        border-color: #a855f7;
    }
    
    /* Expander styling with dark theme */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #1e1e3f 0%, #252550 100%);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        color: #f8fafc;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    /* Dataframe styling with dark theme */
    .stDataFrame {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    /* Radio button styling with dark theme */
    .stRadio > div {
        background: rgba(30, 30, 63, 0.8);
        padding: 1.25rem;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    /* Select box styling with dark theme */
    .stSelectbox > div > div {
        background: rgba(30, 30, 63, 0.8);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: #f8fafc;
    }
    
    /* Text input styling with dark theme */
    .stTextInput > div > div > input {
        background: rgba(30, 30, 63, 0.8);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 0.875rem;
        color: #f8fafc;
    }
    
    /* Text area styling with dark theme */
    .stTextArea > div > div > textarea {
        background: rgba(30, 30, 63, 0.8);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 0.875rem;
        color: #f8fafc;
    }
    
    /* Loading animation with neon */
    .stSpinner {
        color: #7c3aed;
    }
    
    /* Typography improvements */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        letter-spacing: -0.02em;
    }
    
    p, span, div {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* High contrast text colors */
    .stMarkdown, .stText {
        color: #e2e8f0;
    }
    
    /* Code styling */
    code {
        font-family: 'JetBrains Mono', monospace;
        background: rgba(124, 58, 237, 0.1);
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        color: #a855f7;
    }
    
    /* Link styling */
    a {
        color: #00d4ff;
        text-decoration: none;
        transition: color 0.3s ease;
    }
    
    a:hover {
        color: #7c3aed;
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
        
        # Animated stats cards (moved after contacts loading)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📧 Ready to Send</h3>
                <p style="font-size: 2.5rem; font-weight: 800; margin: 0.5rem 0;">{len(contacts)}</p>
                <p>Contacts Available</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📊 Volume Cap</h3>
                <p style="font-size: 2.5rem; font-weight: 800; margin: 0.5rem 0;">{config.max_outreach_per_run}</p>
                <p>Max Per Run</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🔒 Mode</h3>
                <p style="font-size: 2rem; font-weight: 800; margin: 0.5rem 0;">{'DRY RUN' if config.dry_run else 'LIVE'}</p>
                <p>Current Status</p>
            </div>
            """, unsafe_allow_html=True)
        
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
