"""
Input Loader for The Closer - Cold Email Writer + Send Bot

This module handles loading outreach targets from JSON files with validation.
"""

import json
import re
import sys
from typing import Optional
from src.models import Contact


def is_valid_email(email: str) -> bool:
    """
    Validate email format using regex.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email format is valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def load_targets(path: Optional[str] = None) -> list[Contact]:
    """
    Load outreach targets from a JSON file or use hardcoded fallback.
    
    Args:
        path: Path to contacts.json file. If None, uses hardcoded fallback.
        
    Returns:
        List of valid Contact objects. Invalid records are skipped with warnings.
    """
    # Hardcoded fallback for demo/testing
    hardcoded_contacts = [
        Contact(
            recipient_email="priya.sharma@example.com",
            company="Acme AI",
            role="Backend Engineering Intern",
            candidate_name="Your Name",
            candidate_background="Python developer interested in automation and AI agents",
            recipient_name="Priya Sharma",
            personalization_note="Company recently launched an AI workflow automation product",
            portfolio_url="https://github.com/yourname"
        ),
        Contact(
            recipient_email="john.chen@techstartup.io",
            company="TechStartup",
            role="Full Stack Developer",
            candidate_name="Your Name",
            candidate_background="Full-stack developer with React and Python experience",
            recipient_name="John Chen",
            personalization_note="Building a modern SaaS platform for remote teams",
            portfolio_url="https://github.com/yourname"
        ),
        Contact(
            recipient_email="sarah.j@innovatecorp.com",
            company="InnovateCorp",
            role="Software Engineer",
            candidate_name="Your Name",
            candidate_background="Software engineer focused on cloud-native applications",
            recipient_name="Sarah Johnson",
            personalization_note="Expanding their cloud infrastructure team",
            portfolio_url="https://github.com/yourname"
        )
    ]
    
    # If no path provided, return hardcoded contacts
    if path is None:
        print("INFO: Using hardcoded contact list (no input file provided)")
        return hardcoded_contacts
    
    # Try to load from JSON file
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"WARNING: File not found: {path}. Using hardcoded fallback.")
        return hardcoded_contacts
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {path}: {e}")
        print("Using hardcoded fallback.")
        return hardcoded_contacts
    
    # Validate and convert to Contact objects
    contacts = []
    for idx, record in enumerate(data):
        try:
            # Validate required fields
            recipient_email = record.get("recipient_email", "").strip()
            company = record.get("company", "").strip()
            role = record.get("role", "").strip()
            candidate_name = record.get("candidate_name", "").strip()
            candidate_background = record.get("candidate_background", "").strip()
            
            # Check required fields
            if not recipient_email:
                print(f"WARNING: Skipping record {idx + 1} - missing recipient_email")
                continue
            
            if not is_valid_email(recipient_email):
                print(f"WARNING: Skipping record {idx + 1} - invalid email: {recipient_email}")
                continue
            
            if not company:
                print(f"WARNING: Skipping record {idx + 1} - missing company")
                continue
            
            if not role:
                print(f"WARNING: Skipping record {idx + 1} - missing role")
                continue
            
            if not candidate_name:
                print(f"WARNING: Skipping record {idx + 1} - missing candidate_name")
                continue
            
            if not candidate_background:
                print(f"WARNING: Skipping record {idx + 1} - missing candidate_background")
                continue
            
            # Create Contact object
            contact = Contact(
                recipient_email=recipient_email,
                company=company,
                role=role,
                candidate_name=candidate_name,
                candidate_background=candidate_background,
                recipient_name=record.get("recipient_name"),
                job_url=record.get("job_url"),
                portfolio_url=record.get("portfolio_url"),
                personalization_note=record.get("personalization_note"),
                linkedin_url=record.get("linkedin_url"),
                resume_link=record.get("resume_link")
            )
            
            contacts.append(contact)
            
        except Exception as e:
            print(f"WARNING: Skipping record {idx + 1} - error: {e}")
            continue
    
    if not contacts:
        print("WARNING: No valid contacts found in input file. Using hardcoded fallback.")
        return hardcoded_contacts
    
    print(f"INFO: Loaded {len(contacts)} valid contacts from {path}")
    return contacts
