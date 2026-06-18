"""
Email Generator for The Closer - Cold Email Writer + Send Bot

This module generates personalized cold emails following the six-part email anatomy.
"""

from src.models import Contact, EmailDraft
from src.config import AppConfig


def count_words(text: str) -> int:
    """
    Count the number of words in a text string.
    
    Args:
        text: Text to count words in
        
    Returns:
        Number of words
    """
    return len(text.split())


def generate_email(contact: Contact, config: AppConfig) -> EmailDraft:
    """
    Generate a personalized cold email following the six-part email anatomy.
    
    Email anatomy:
    1. Subject line (role/company specific)
    2. Personalization hook (company/role or personalization_note)
    3. Introduction (candidate_name, candidate_background)
    4. Value/fit statement
    5. One clear ask
    6. Sign-off with optional portfolio link
    
    Args:
        contact: Contact information for the recipient
        config: Application configuration
        
    Returns:
        EmailDraft with subject, body, and word count
    """
    # Generate subject line
    subject = f"Quick note on the {contact.role} role at {contact.company}"
    
    # Determine greeting
    if contact.recipient_name:
        greeting = f"Hi {contact.recipient_name},"
    else:
        greeting = "Hi there,"
    
    # Generate personalization hook
    if contact.personalization_note:
        personalization_hook = contact.personalization_note
    else:
        # Fallback: derive from company + role
        personalization_hook = f"I noticed {contact.company} is hiring for the {contact.role} position."
    
    # Build email body following six-part anatomy
    body = f"""{greeting}

{personalization_hook}

I'm {contact.candidate_name}, and I've been building projects around {contact.candidate_background}. The role stood out because it connects closely with my interest in practical automation and product-focused engineering.

Would you be open to a quick look at my profile or pointing me to the right person?

Best,
{contact.candidate_name}"""

    # Add portfolio link if available
    if contact.portfolio_url:
        body += f"\n{contact.portfolio_url}"
    
    # Calculate word count
    word_count = count_words(body)
    
    # Enforce word count limit (warn if exceeds 150)
    if word_count > 150:
        print(f"WARNING: Generated email exceeds 150 words ({word_count}). Consider trimming.")
    
    # Check for generic personalization
    if not contact.personalization_note:
        print(f"INFO: Using generic personalization hook for {contact.company}. Consider adding a personalization_note.")
    
    return EmailDraft(
        subject=subject,
        body=body,
        word_count=word_count
    )
