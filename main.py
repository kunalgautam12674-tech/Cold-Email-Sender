"""
The Closer - Cold Email Writer + Send Bot

Main orchestrator that wires all modules together for the outreach pipeline.
"""

import sys
from datetime import datetime
from src.config import load_config
from src.input_loader import load_targets
from src.email_generator import generate_email
from src.preview import preview_email, prompt_action
from src.email_sender import deliver_email
from src.logger import append_log
from src.models import LogEntry


def run_outreach_pipeline() -> None:
    """
    Run the complete outreach pipeline.
    
    Pipeline:
    1. Load configuration
    2. Load contacts
    3. For each contact (respecting volume cap):
       - Generate email
       - Preview email
       - Prompt for action
       - Deliver or skip
       - Log result
    4. Print batch summary
    """
    print("=" * 60)
    print("THE CLOSER - Cold Email Writer + Send Bot")
    print("=" * 60)
    
    # Load configuration
    print("\nLoading configuration...")
    try:
        config = load_config()
        print(f"✓ Configuration loaded")
        print(f"  - Dry run: {config.dry_run}")
        print(f"  - Send mode: {config.send_mode}")
        print(f"  - Max outreach per run: {config.max_outreach_per_run}")
        print(f"  - Input path: {config.input_path or 'hardcoded fallback'}")
    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        sys.exit(1)
    
    # Load contacts
    print("\nLoading contacts...")
    try:
        contacts = load_targets(config.input_path)
        if not contacts:
            print("✗ No contacts loaded. Exiting.")
            sys.exit(1)
        print(f"✓ Loaded {len(contacts)} contacts")
    except Exception as e:
        print(f"✗ Failed to load contacts: {e}")
        sys.exit(1)
    
    # Apply volume cap
    max_contacts = min(len(contacts), config.max_outreach_per_run)
    if max_contacts < len(contacts):
        print(f"\n⚠ Volume cap: Processing {max_contacts} of {len(contacts)} contacts")
    contacts_to_process = contacts[:max_contacts]
    
    # Initialize counters
    sent_count = 0
    drafted_count = 0
    skipped_count = 0
    failed_count = 0
    
    # Process each contact
    print("\n" + "=" * 60)
    print("PROCESSING CONTACTS")
    print("=" * 60)
    
    for idx, contact in enumerate(contacts_to_process, 1):
        print(f"\n[{idx}/{max_contacts}] Processing: {contact.recipient_email}")
        
        try:
            # Generate email
            draft = generate_email(contact, config)
            print(f"✓ Email generated ({draft.word_count} words)")
            
            # Preview email
            preview_email(draft, contact)
            
            # Prompt for action
            action = prompt_action()
            print(f"✓ Action: {action}")
            
            # Handle action
            if action == "skip":
                # Log skip
                log_entry = LogEntry(
                    timestamp=datetime.now().isoformat(),
                    recipient_email=contact.recipient_email,
                    company=contact.company,
                    role=contact.role,
                    subject=draft.subject,
                    status="skipped",
                    error_message=""
                )
                append_log(log_entry)
                skipped_count += 1
                continue
            
            # Handle dry run
            if config.dry_run:
                print("⚠ Dry run mode: Skipping actual delivery")
                log_entry = LogEntry(
                    timestamp=datetime.now().isoformat(),
                    recipient_email=contact.recipient_email,
                    company=contact.company,
                    role=contact.role,
                    subject=draft.subject,
                    status="generated",
                    error_message=""
                )
                append_log(log_entry)
                skipped_count += 1
                continue
            
            # Deliver email
            result = deliver_email(draft, contact, config, action)
            
            if result.status == "sent":
                print(f"✓ Email sent successfully")
                sent_count += 1
            elif result.status == "drafted":
                print(f"✓ Email drafted successfully")
                drafted_count += 1
            else:
                print(f"✗ Email delivery failed: {result.error}")
                failed_count += 1
            
            # Log result
            log_entry = LogEntry(
                timestamp=datetime.now().isoformat(),
                recipient_email=contact.recipient_email,
                company=contact.company,
                role=contact.role,
                subject=draft.subject,
                status=result.status,
                error_message=result.error or ""
            )
            append_log(log_entry)
            
        except KeyboardInterrupt:
            print("\n\n⚠ Operation cancelled by user")
            break
        except Exception as e:
            print(f"✗ Error processing contact: {e}")
            failed_count += 1
            
            # Log error
            log_entry = LogEntry(
                timestamp=datetime.now().isoformat(),
                recipient_email=contact.recipient_email,
                company=contact.company,
                role=contact.role,
                subject="",
                status="failed",
                error_message=str(e)
            )
            append_log(log_entry)
    
    # Print batch summary
    print("\n" + "=" * 60)
    print("BATCH SUMMARY")
    print("=" * 60)
    print(f"Total contacts processed: {idx}")
    print(f"Sent: {sent_count}")
    print(f"Drafted: {drafted_count}")
    print(f"Skipped: {skipped_count}")
    print(f"Failed: {failed_count}")
    print("=" * 60)
    
    if config.dry_run:
        print("\n⚠ Dry run mode - no emails were actually sent")
        print("Set DRY_RUN=false in .env to send real emails")


if __name__ == "__main__":
    try:
        run_outreach_pipeline()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        sys.exit(1)
