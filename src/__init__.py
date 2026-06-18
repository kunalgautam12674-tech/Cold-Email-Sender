"""
The Closer - Cold Email Writer + Send Bot

A Python CLI tool for generating and sending personalized cold emails.
"""

from src.models import Contact, EmailDraft, LogEntry
from src.config import load_config, AppConfig
from src.input_loader import load_targets
from src.email_generator import generate_email
from src.preview import preview_email, prompt_action
from src.email_sender import deliver_email, DeliveryResult
from src.logger import append_log

__all__ = ["Contact", "EmailDraft", "LogEntry", "load_config", "AppConfig", "load_targets", "generate_email", "preview_email", "prompt_action", "deliver_email", "DeliveryResult", "append_log"]
