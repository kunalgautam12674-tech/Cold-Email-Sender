"""
Configuration management for The Closer - Cold Email Writer + Send Bot

This module handles loading configuration from environment variables using python-dotenv.
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv


@dataclass
class AppConfig:
    """
    Application configuration loaded from environment variables.
    
    Attributes:
        smtp_host: SMTP server hostname (default: smtp.gmail.com)
        smtp_port: SMTP server port (default: 587)
        smtp_user: SMTP username/sender email (required for send mode)
        smtp_password: SMTP password/app password (required for send mode)
        sender_name: Display name for sender
        dry_run: If true, skip actual email delivery (default: true)
        send_mode: Delivery mode - 'draft' or 'send' (default: draft)
        max_outreach_per_run: Maximum contacts to process per run (default: 5)
        input_path: Path to contacts.json file (optional)
        groq_api_key: Groq API key for LLM features (optional, for stretch goals)
    """
    smtp_host: str
    smtp_port: int
    smtp_user: Optional[str]
    smtp_password: Optional[str]
    sender_name: Optional[str]
    dry_run: bool
    send_mode: str
    max_outreach_per_run: int
    input_path: Optional[str]
    groq_api_key: Optional[str]


def load_config() -> AppConfig:
    """
    Load configuration from environment variables.
    
    Loads from .env file if present, then overrides with system environment variables.
    Provides sensible defaults for optional values.
    
    Returns:
        AppConfig: Configuration object with all settings loaded
        
    Raises:
        ValueError: If required environment variables are missing when send mode is active
    """
    # Load from .env file if it exists
    load_dotenv()
    
    # Load SMTP configuration
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender_name = os.getenv("SENDER_NAME")
    
    # Load safety and behavior configuration
    dry_run_str = os.getenv("DRY_RUN", "true").lower()
    dry_run = dry_run_str in ("true", "1", "yes")
    
    send_mode = os.getenv("SEND_MODE", "draft").lower()
    if send_mode not in ("draft", "send"):
        raise ValueError(f"SEND_MODE must be 'draft' or 'send', got: {send_mode}")
    
    max_outreach_per_run = int(os.getenv("MAX_OUTREACH_PER_RUN", "5"))
    
    # Validate volume cap is reasonable
    if max_outreach_per_run <= 0:
        raise ValueError("MAX_OUTREACH_PER_RUN must be positive")
    if max_outreach_per_run > 50:
        print(f"WARNING: MAX_OUTREACH_PER_RUN capped at 50 for safety (was {max_outreach_per_run})")
        max_outreach_per_run = 50
    
    # Load input configuration
    input_path = os.getenv("INPUT_PATH")
    
    # Load Groq API key for LLM features (optional)
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    # Validate required fields for send mode
    if not dry_run and send_mode == "send":
        if not smtp_user:
            raise ValueError("SMTP_USER is required when DRY_RUN=false and SEND_MODE=send")
        if not smtp_password:
            raise ValueError("SMTP_PASSWORD is required when DRY_RUN=false and SEND_MODE=send")
    
    return AppConfig(
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_user=smtp_user,
        smtp_password=smtp_password,
        sender_name=sender_name,
        dry_run=dry_run,
        send_mode=send_mode,
        max_outreach_per_run=max_outreach_per_run,
        input_path=input_path,
        groq_api_key=groq_api_key
    )
