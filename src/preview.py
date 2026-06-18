"""
Preview and Confirmation for The Closer - Cold Email Writer + Send Bot

This module handles email preview display and user confirmation prompts.
"""

from typing import Literal
from src.models import Contact, EmailDraft


def preview_email(draft: EmailDraft, contact: Contact) -> None:
    """
    Display a formatted preview of the email draft.
    
    Args:
        draft: Email draft to preview
        contact: Contact information for context
    """
    separator = "=" * 60
    print(f"\n{separator}")
    print(f"EMAIL PREVIEW")
    print(f"{separator}")
    print(f"To: {contact.recipient_email}")
    if contact.recipient_name:
        print(f"Name: {contact.recipient_name}")
    print(f"Company: {contact.company}")
    print(f"Role: {contact.role}")
    print(f"{separator}")
    print(f"Subject: {draft.subject}")
    print(f"{separator}")
    print(f"Body:")
    print(f"{separator}")
    print(draft.body)
    print(f"{separator}")
    print(f"Word count: {draft.word_count}")
    print(f"{separator}\n")


def prompt_action() -> Literal["send", "draft", "skip"]:
    """
    Prompt user to choose an action for the email.
    
    Returns:
        User's choice: "send", "draft", or "skip"
    """
    while True:
        try:
            response = input("Send this email? (send/draft/skip): ").strip().lower()
            
            # Accept various valid inputs
            if response in ["send", "s", "yes", "y"]:
                return "send"
            elif response in ["draft", "d"]:
                return "draft"
            elif response in ["skip", "no", "n"]:
                return "skip"
            elif response == "":
                # Default to skip on empty input (safe default)
                return "skip"
            else:
                print("Invalid choice. Please enter: send, draft, or skip")
                
        except (EOFError, KeyboardInterrupt):
            # Handle Ctrl+C or EOF gracefully
            print("\nOperation cancelled by user")
            return "skip"
