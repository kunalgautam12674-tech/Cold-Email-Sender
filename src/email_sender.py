"""
Email Sender for The Closer - Cold Email Writer + Send Bot

This module handles email delivery with dry-run mode and SMTP support.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Literal
from dataclasses import dataclass
from src.models import Contact, EmailDraft
from src.config import AppConfig


@dataclass
class DeliveryResult:
    """
    Result of an email delivery attempt.
    
    Attributes:
        status: Delivery status (sent, drafted, failed, dry_run)
        provider_message_id: Message ID from provider (if available)
        error: Error message if delivery failed
    """
    status: Literal["sent", "drafted", "failed", "dry_run"]
    provider_message_id: str | None = None
    error: str | None = None


class DryRunEmailSender:
    """Sender that simulates delivery without actual network calls."""
    
    def deliver(self, draft: EmailDraft, contact: Contact, config: AppConfig, mode: Literal["send", "draft"]) -> DeliveryResult:
        """
        Simulate email delivery without sending.
        
        Args:
            draft: Email draft to deliver
            contact: Contact information
            config: Application configuration
            mode: Delivery mode (send or draft)
            
        Returns:
            DeliveryResult with dry_run status
        """
        return DeliveryResult(
            status="dry_run",
            provider_message_id=None,
            error=None
        )


class SmtpEmailSender:
    """Sender that delivers emails via SMTP."""
    
    def deliver(self, draft: EmailDraft, contact: Contact, config: AppConfig, mode: Literal["send", "draft"]) -> DeliveryResult:
        """
        Deliver email via SMTP.
        
        Args:
            draft: Email draft to deliver
            contact: Contact information
            config: Application configuration
            mode: Delivery mode (send or draft)
            
        Returns:
            DeliveryResult with delivery status
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = config.smtp_user
            msg['To'] = contact.recipient_email
            msg['Subject'] = draft.subject
            
            # Add body
            msg.attach(MIMEText(draft.body, 'plain'))
            
            # Connect to SMTP server
            server = smtplib.SMTP(config.smtp_host, config.smtp_port)
            server.starttls()
            
            # Login
            server.login(config.smtp_user, config.smtp_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(config.smtp_user, contact.recipient_email, text)
            
            # Quit
            server.quit()
            
            return DeliveryResult(
                status="sent",
                provider_message_id=None,  # SMTP doesn't always return message ID
                error=None
            )
            
        except smtplib.SMTPAuthenticationError:
            return DeliveryResult(
                status="failed",
                provider_message_id=None,
                error="SMTP authentication failed. Check your credentials and use Gmail App Password if using Gmail."
            )
        except smtplib.SMTPException as e:
            return DeliveryResult(
                status="failed",
                provider_message_id=None,
                error=f"SMTP error: {str(e)}"
            )
        except Exception as e:
            return DeliveryResult(
                status="failed",
                provider_message_id=None,
                error=f"Unexpected error: {str(e)}"
            )


def deliver_email(
    draft: EmailDraft,
    contact: Contact,
    config: AppConfig,
    mode: Literal["send", "draft"]
) -> DeliveryResult:
    """
    Deliver email using appropriate sender based on configuration.
    
    Args:
        draft: Email draft to deliver
        contact: Contact information
        config: Application configuration
        mode: Delivery mode (send or draft)
        
    Returns:
        DeliveryResult with delivery status
    """
    # Use dry-run sender if DRY_RUN is enabled
    if config.dry_run:
        sender = DryRunEmailSender()
        return sender.deliver(draft, contact, config, mode)
    
    # Use SMTP sender for real delivery
    sender = SmtpEmailSender()
    return sender.deliver(draft, contact, config, mode)
