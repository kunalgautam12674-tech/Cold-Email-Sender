"""
Data models for The Closer - Cold Email Writer + Send Bot

This module defines the core data structures used throughout the application.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Contact:
    """
    Represents a contact/outreach target loaded from input data.
    
    Required fields:
        recipient_email: Email address of the recipient
        company: Company name
        role: Job role/title
        candidate_name: Name of the candidate/sender
        candidate_background: Background of the candidate for personalization
    
    Optional fields:
        recipient_name: Name of the recipient (defaults to "there" if missing)
        job_url: URL to the job posting
        portfolio_url: URL to candidate's portfolio
        personalization_note: Custom note for personalization
        linkedin_url: LinkedIn profile URL
        resume_link: Resume/CV link
    """
    recipient_email: str
    company: str
    role: str
    candidate_name: str
    candidate_background: str
    recipient_name: Optional[str] = None
    job_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    personalization_note: Optional[str] = None
    linkedin_url: Optional[str] = None
    resume_link: Optional[str] = None


@dataclass
class EmailDraft:
    """
    Represents a generated email draft.
    
    Attributes:
        subject: Email subject line
        body: Email body text
        word_count: Number of words in the body (for validation)
    """
    subject: str
    body: str
    word_count: int


@dataclass
class LogEntry:
    """
    Represents a single log entry for the outreach audit log.
    
    Attributes:
        timestamp: ISO-8601 timestamp of the attempt
        recipient_email: Email address of the recipient
        company: Company name
        role: Job role
        subject: Email subject line
        status: Status of the attempt (generated, drafted, sent, skipped, failed)
        error_message: Error message if status is failed (empty otherwise)
    """
    timestamp: str
    recipient_email: str
    company: str
    role: str
    subject: str
    status: str
    error_message: str = ""
