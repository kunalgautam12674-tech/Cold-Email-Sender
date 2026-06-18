"""
Logger for The Closer - Cold Email Writer + Send Bot

This module handles append-only audit logging for all outreach attempts.
"""

import csv
from datetime import datetime
from src.models import LogEntry


def append_log(entry: LogEntry, path: str = "outreach_log.csv") -> None:
    """
    Append a log entry to the outreach audit log.
    
    Args:
        entry: LogEntry to append
        path: Path to the log file (default: outreach_log.csv)
    """
    # Define CSV columns
    fieldnames = [
        "timestamp",
        "recipient_email",
        "company",
        "role",
        "subject",
        "status",
        "error_message",
        "word_count",
        "job_url"
    ]
    
    # Check if file exists to determine if we need to write header
    file_exists = False
    try:
        with open(path, 'r', encoding='utf-8') as f:
            file_exists = True
    except FileNotFoundError:
        file_exists = False
    
    # Append entry to CSV
    try:
        with open(path, 'a', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            # Write header if file doesn't exist
            if not file_exists:
                writer.writeheader()
            
            # Write log entry
            writer.writerow({
                "timestamp": entry.timestamp,
                "recipient_email": entry.recipient_email,
                "company": entry.company,
                "role": entry.role,
                "subject": entry.subject,
                "status": entry.status,
                "error_message": entry.error_message,
                "word_count": "",  # Optional field
                "job_url": ""  # Optional field
            })
            
    except PermissionError:
        print(f"ERROR: Cannot write to log file {path}. Check permissions.")
    except Exception as e:
        print(f"ERROR: Failed to write to log file: {e}")
