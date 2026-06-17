# Edge Cases: The Closer — Cold Email Writer + Send Bot

This document catalogs all edge cases and failure scenarios that **The Closer** should handle gracefully. Each edge case includes expected behavior and implementation guidance.

---

## 1. Input Validation Edge Cases

### 1.1 Missing Required Fields

**Scenario:** Contact record missing required field (recipient_email, company, role, candidate_name, candidate_background)

**Expected Behavior:**
- Skip the invalid record
- Log warning with specific field name
- Continue processing remaining contacts
- Do not abort entire batch

**Implementation:**
```python
# In input_loader.py
if not contact.recipient_email:
    print(f"WARNING: Skipping record - missing recipient_email")
    continue
```

---

### 1.2 Invalid Email Format

**Scenario:** Email address doesn't match valid format (no @, no domain, special characters)

**Examples:**
- `invalid-email`
- `@example.com`
- `user@`
- `user @example.com`

**Expected Behavior:**
- Validate using regex or `email-validator` library
- Skip record with invalid email
- Show specific error: "Invalid email format: {email}"
- Continue processing

**Implementation:**
```python
import re

def is_valid_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
```

---

### 1.3 Empty String Fields

**Scenario:** Required field is present but empty string or whitespace only

**Expected Behavior:**
- Treat empty strings as missing
- Strip whitespace before validation
- Skip record with clear warning

**Implementation:**
```python
if not contact.company.strip():
    print(f"WARNING: Skipping record - company is empty")
    continue
```

---

### 1.4 Null/None Values

**Scenario:** Field is explicitly None instead of empty string

**Expected Behavior:**
- Handle None gracefully
- Use default values for optional fields
- Reject None for required fields

**Implementation:**
```python
recipient_name = contact.recipient_name or "there"
```

---

### 1.5 Malformed JSON

**Scenario:** `contacts.json` has syntax errors (missing commas, unmatched brackets)

**Expected Behavior:**
- Catch JSONDecodeError
- Show specific error message with line number
- Abort with clear guidance: "Fix contacts.json syntax"
- Do not proceed with partial data

**Implementation:**
```python
import json

try:
    with open(path) as f:
        data = json.load(f)
except json.JSONDecodeError as e:
    print(f"ERROR: Invalid JSON in {path}: {e}")
    sys.exit(1)
```

---

### 1.6 Empty Input File

**Scenario:** `contacts.json` exists but is empty array `[]`

**Expected Behavior:**
- Handle gracefully
- Show message: "No contacts found in input file"
- Exit without error (nothing to do)

---

### 1.7 File Not Found

**Scenario:** Specified input file doesn't exist

**Expected Behavior:**
- Show clear error: "File not found: {path}"
- Fall back to hardcoded list if available
- Or abort with guidance

---

### 1.8 CSV Parsing Errors

**Scenario:** CSV file has mismatched columns, quoted strings with commas, encoding issues

**Expected Behavior:**
- Use `csv` module with proper error handling
- Skip malformed rows with warnings
- Show row number for debugging
- Continue with valid rows

---

### 1.9 Duplicate Recipients

**Scenario:** Same email appears multiple times in input

**Expected Behavior:**
- Detect duplicates
- Warn user: "Duplicate recipient: {email}"
- Option to skip duplicates or process all
- Log decision

---

## 2. Email Generation Edge Cases

### 2.1 Word Count Exceeds Limit

**Scenario:** Generated email exceeds 150 words

**Expected Behavior:**
- Warn in preview: "Word count: {count} (limit: 150)"
- Option to auto-trim or regenerate
- Or block send with error
- Log as warning

**Implementation:**
```python
if draft.word_count > 150:
    print(f"WARNING: Email exceeds 150 words ({draft.word_count})")
    # Option: trim to last complete sentence under limit
```

---

### 2.2 Missing Personalization Note

**Scenario:** `personalization_note` is None or empty

**Expected Behavior:**
- Use fallback: derive from company + role
- Example: "I noticed {company} is hiring for {role}"
- If still too generic, warn user
- Allow user to skip or edit

---

### 2.3 Missing Recipient Name

**Scenario:** `recipient_name` is None or empty

**Expected Behavior:**
- Use default greeting: "Hi there" or "Hi"
- Do not fail
- Log that default was used

---

### 2.4 Missing Portfolio/Resume Links

**Scenario:** Optional URLs (portfolio_url, resume_link, linkedin_url) are missing

**Expected Behavior:**
- Omit from sign-off
- Don't show broken links
- Template handles gracefully with conditional sections

---

### 2.5 Special Characters in Fields

**Scenario:** Fields contain quotes, newlines, emojis, unicode characters

**Examples:**
- Company: "O'Reilly & Associates"
- Background: "Python/JavaScript developer"
- Name with accents: "José García"

**Expected Behavior:**
- Handle in templates without breaking
- Escape properly for email headers
- Preserve unicode in body
- Test with various character sets

---

### 2.6 Extremely Long Fields

**Scenario:** `candidate_background` is 500+ words

**Expected Behavior:**
- Truncate or summarize
- Warn user: "Background too long, truncating"
- Use first 2-3 sentences
- Log truncation

---

### 2.7 Template Variable Not Found

**Scenario:** Template references field that doesn't exist in Contact

**Expected Behavior:**
- Use default value or empty string
- Log warning: "Missing field: {field_name}"
- Don't crash

---

### 2.8 Generic Personalization Detection

**Scenario:** Generated hook is too generic (e.g., "I'm interested in this role")

**Expected Behavior:**
- Detect generic phrases
- Warn user: "Personalization seems generic"
- Suggest adding `personalization_note`
- Option to skip or edit

---

## 3. Email Sending Edge Cases

### 3.1 SMTP Authentication Failure

**Scenario:** Wrong username/password, account locked, 2FA required

**Expected Behavior:**
- Catch authentication error
- Show clear message: "SMTP authentication failed. Check credentials."
- Suggest using Gmail App Password
- Log as failed with error details
- Do not retry indefinitely

**Implementation:**
```python
try:
    server.login(smtp_user, smtp_password)
except smtplib.SMTPAuthenticationError:
    print("ERROR: Authentication failed. Use Gmail App Password.")
    return DeliveryResult(status="failed", error="Authentication failed")
```

---

### 3.2 Network Timeout

**Scenario:** SMTP server doesn't respond within timeout

**Expected Behavior:**
- Catch timeout exception
- Show: "Connection timeout. Check network."
- Log as failed
- Allow retry on next run
- Don't hang indefinitely

---

### 3.3 SMTP Server Unreachable

**Scenario:** Can't connect to SMTP host (wrong host, firewall, DNS issue)

**Expected Behavior:**
- Show: "Cannot connect to SMTP server: {host}:{port}"
- Suggest checking network/firewall
- Log as failed
- Continue with next contact

---

### 3.4 TLS/SSL Errors

**Scenario:** STARTTLS fails, certificate invalid

**Expected Behavior:**
- Show specific TLS error
- Suggest checking SMTP port (587 vs 465)
- Log as failed
- Don't send unencrypted

---

### 3.5 Rate Limiting

**Scenario:** SMTP provider blocks after too many emails

**Expected Behavior:**
- Detect rate limit error (4xx response)
- Show: "Rate limited. Waiting or stopping."
- Implement exponential backoff (optional)
- Or stop batch and log
- Volume cap should prevent this

---

### 3.6 Email Rejected by Recipient Server

**Scenario:** Recipient's server rejects email (unknown user, spam filter)

**Expected Behavior:**
- Log rejection with server response
- Show: "Email rejected by recipient server: {reason}"
- Mark as failed in log
- Continue with next contact

---

### 3.7 Dry-Run Mode Active

**Scenario:** `DRY_RUN=true` but user tries to send

**Expected Behavior:**
- Skip actual network call
- Return success without sending
- Log status as "dry_run" or "generated"
- Still run preview/confirmation for testing

---

### 3.8 Missing Credentials in Send Mode

**Scenario:** `DRY_RUN=false` but SMTP_USER/SMTP_PASSWORD not set

**Expected Behavior:**
- Abort before attempting send
- Show: "ERROR: SMTP credentials required when DRY_RUN=false"
- Suggest setting env vars or using DRY_RUN=true
- Do not attempt connection

---

### 3.9 Sender Email Mismatch

**Scenario:** SENDER_NAME doesn't match SMTP_USER

**Expected Behavior:**
- Warning: "Sender name may not match authenticated email"
- Allow proceed (user's choice)
- Log the mismatch
- Prevent spoofing attempts

---

## 4. Logging Edge Cases

### 4.1 Log File Permission Denied

**Scenario:** Can't write to `outreach_log.csv` (permissions, read-only filesystem)

**Expected Behavior:**
- Catch permission error
- Show: "Cannot write to log file. Check permissions."
- Continue without logging (or abort)
- Suggest fixing permissions

---

### 4.2 Disk Full

**Scenario:** No disk space to write log

**Expected Behavior:**
- Catch disk full error
- Show: "Disk full. Cannot write log."
- Continue without logging
- Alert user to free space

---

### 4.3 Log File Corrupted

**Scenario:** Existing `outreach_log.csv` has malformed rows

**Expected Behavior:**
- Detect corruption on read
- Show: "Log file corrupted. Starting new log."
- Backup old file
- Create fresh log with header
- Don't lose data

---

### 4.4 Concurrent Write Attempts

**Scenario:** Multiple processes try to write to log simultaneously

**Expected Behavior:**
- Use file locking (optional for MVP)
- Or append mode is safe enough for single-process
- Log warning if conflict detected
- Ensure no data loss

---

### 4.5 Missing Log Header

**Scenario:** Log file exists but has no header row

**Expected Behavior:**
- Detect missing header
- Add header if file is empty
- If file has data but no header, warn user
- Don't corrupt existing data

---

### 4.6 CSV Encoding Issues

**Scenario:** Log contains unicode characters that break CSV parsing

**Expected Behavior:**
- Use UTF-8 encoding consistently
- Handle encoding errors gracefully
- Use `errors='replace'` or `'ignore'` if needed
- Log encoding issues

---

### 4.7 Extremely Long Subject in Log

**Scenario:** Subject line is very long, breaks CSV formatting

**Expected Behavior:**
- Truncate subject in log if needed
- Or quote properly in CSV
- Ensure CSV remains valid
- Log truncation

---

## 5. User Interaction Edge Cases

### 5.1 Invalid User Input

**Scenario:** User enters invalid choice at confirmation prompt

**Examples:**
- "maybe"
- "yes please"
- "1"
- Empty string

**Expected Behavior:**
- Show: "Invalid choice. Please enter: send, draft, or skip"
- Re-prompt
- Default to "skip" on empty input (safe)
- Accept common variations (y/yes/send, d/draft, s/skip/no)

---

### 5.2 Keyboard Interrupt

**Scenario:** User presses Ctrl+C during operation

**Expected Behavior:**
- Catch KeyboardInterrupt
- Show: "Operation cancelled by user"
- Log current state
- Exit gracefully
- Don't leave partial state

**Implementation:**
```python
try:
    # main loop
except KeyboardInterrupt:
    print("\nOperation cancelled by user")
    sys.exit(0)
```

---

### 5.3 User Skips All Emails

**Scenario:** User chooses "skip" for every contact

**Expected Behavior:**
- Process all skips
- Log each as "skipped"
- Show summary: "0 sent, 0 drafted, 5 skipped"
- This is valid behavior

---

### 5.4 User Wants to Edit Email

**Scenario:** User wants to modify generated email before sending (stretch feature)

**Expected Behavior:**
- Offer edit option in prompt
- Open text editor or re-prompt for edits
- Regenerate with edits
- Show new preview
- Continue with confirmation

---

### 5.5 User Changes Mind Mid-Batch

**Scenario:** User sends 2 emails, then wants to stop

**Expected Behavior:**
- Add "quit" option to prompt
- Stop processing remaining contacts
- Log completed attempts
- Show partial summary
- Exit gracefully

---

### 5.6 Terminal Too Narrow

**Scenario:** Preview text wraps poorly on narrow terminal

**Expected Behavior:**
- Use textwrap for formatting
- Don't assume fixed width
- Handle gracefully
- Or suggest wider terminal

---

### 5.7 Non-Interactive Environment

**Scenario:** Running in CI/CD or non-interactive terminal

**Expected Behavior:**
- Detect non-TTY
- Either abort with error
- Or use DRY_RUN mode automatically
- Document behavior

---

## 6. Configuration Edge Cases

### 6.1 Missing .env File

**Scenario:** `.env` file doesn't exist

**Expected Behavior:**
- Use defaults where possible
- Show warning: ".env file not found, using defaults"
- Abort if required credentials missing
- Suggest creating from `.env.example`

---

### 6.2 Invalid Environment Variable Values

**Scenario:** Env vars have wrong types (string instead of int, invalid boolean)

**Examples:**
- `MAX_OUTREACH_PER_RUN=abc` (should be int)
- `DRY_RUN=yes` (should be boolean true/false)
- `SMTP_PORT=invalid` (should be int)

**Expected Behavior:**
- Validate on load
- Show: "Invalid value for {VAR}: {value}. Using default: {default}"
- Use safe defaults
- Log validation errors

---

### 6.3 Required Env Var Missing

**Scenario:** Required variable not set (SMTP_USER when DRY_RUN=false)

**Expected Behavior:**
- Abort with clear error
- Show: "Required env var missing: SMTP_USER"
- Suggest adding to .env
- Don't proceed with invalid config

---

### 6.4 Conflicting Configuration

**Scenario:** Conflicting settings (e.g., DRY_RUN=false but SEND_MODE=draft)

**Expected Behavior:**
- Detect conflicts
- Show warning: "Conflicting config: DRY_RUN=false but SEND_MODE=draft"
- Resolve with precedence rules
- Document precedence

---

### 6.5 Port Number Out of Range

**Scenario:** SMTP_PORT is invalid (negative, >65535)

**Expected Behavior:**
- Validate port range (1-65535)
- Show: "Invalid port: {port}. Using default: 587"
- Use default

---

### 6.6 Malformed .env File

**Scenario:** `.env` has syntax errors (no equals, invalid characters)

**Expected Behavior:**
- Catch parse errors
- Show: "Error parsing .env: {error}"
- Abort or use partial config
- Suggest fixing syntax

---

## 7. Safety Edge Cases

### 7.1 Volume Cap Exceeded

**Scenario:** Input has 10 contacts but MAX_OUTREACH_PER_RUN=5

**Expected Behavior:**
- Process only first 5
- Show: "Volume cap: processing 5 of 10 contacts"
- Log that cap was applied
- Don't silently ignore extras

---

### 7.2 Duplicate Email in Same Batch

**Scenario:** Same recipient appears twice in input

**Expected Behavior:**
- Detect duplicate
- Warn: "Duplicate recipient: {email} (appears multiple times)"
- Option to skip second occurrence
- Log decision

---

### 7.3 Email Already Sent Previously

**Scenario:** Recipient was already contacted (check log history)

**Expected Behavior:**
- Check `outreach_log.csv` for previous sends
- Warn: "Already contacted {email} on {date}"
- Option to skip or proceed
- Log decision

---

### 7.4 Opt-Out List

**Scenario:** Recipient is in `do_not_contact.csv`

**Expected Behavior:**
- Load opt-out list
- Skip opted-out recipients
- Show: "Skipping {email} - opted out"
- Log as "skipped_opt_out"
- Respect opt-outs strictly

---

### 7.5 Suspicious Activity Detection

**Scenario:** Pattern looks like spam (same template, many recipients)

**Expected Behavior:**
- Warn if personalization is identical across emails
- Suggest adding variety
- Don't block but alert user
- Log warning

---

### 7.6 Identity Spoofing Attempt

**Scenario:** User tries to send from email they don't own

**Expected Behavior:**
- Validate SMTP_USER matches authenticated account
- Block if mismatch detected
- Show: "Cannot send from unauthenticated email"
- Prevent spoofing

---

### 7.7 Bulk Send Attempt

**Scenario:** User sets MAX_OUTREACH_PER_RUN=1000

**Expected Behavior:**
- Enforce hard maximum (e.g., 50)
- Show: "MAX_OUTREACH_PER_RUN capped at 50 for safety"
- Override user setting
- Log override

---

## 8. System Edge Cases

### 8.1 Python Version Incompatibility

**Scenario:** Running on Python <3.10

**Expected Behavior:**
- Check Python version on startup
- Show: "Requires Python 3.10+. Current: {version}"
- Abort with clear message
- Document requirements

---

### 8.2 Missing Dependencies

**Scenario:** Required package not installed

**Expected Behavior:**
- Show: "Missing dependency: {package}"
- Suggest: `pip install -r requirements.txt`
- Abort gracefully
- Don't crash with ImportError

---

### 8.3 Filesystem Case Sensitivity

**Scenario:** Code references `Contacts.json` but file is `contacts.json`

**Expected Behavior:**
- Use consistent casing
- Or handle case-insensitive on Windows
- Document case sensitivity
- Test on both platforms

---

### 8.4 Line Ending Differences

**Scenario:** Files have CRLF (Windows) vs LF (Unix)

**Expected Behavior:**
- Handle both line endings
- Use universal newline mode
- Don't break parsing

---

### 8.5 Timezone Issues

**Scenario:** Log timestamps in different timezones

**Expected Behavior:**
- Use UTC for consistency
- Or use local time with timezone offset
- Document timezone choice
- Be consistent

---

### 8.6 Memory Issues with Large Input

**Scenario:** Loading 10,000 contacts into memory

**Expected Behavior:**
- MVP: Not expected (volume cap prevents)
- Stretch: Stream processing instead of loading all
- Warn if input is unusually large

---

## 9. Integration Edge Cases

### 9.1 Module Import Failure

**Scenario:** Can't import one of the modules

**Expected Behavior:**
- Show: "Failed to import {module}: {error}"
- Check file exists and is valid Python
- Abort with clear guidance
- Don't continue with broken state

---

### 9.2 Circular Dependencies

**Scenario:** Modules import each other circularly

**Expected Behavior:**
- Design to avoid circular imports
- If detected, show error
- Refactor to break cycle
- Use dependency injection pattern

---

### 9.3 State Inconsistency

**Scenario:** Email marked as sent in log but actually failed

**Expected Behavior:**
- Log before send, update after
- Or use transactional logging
- Handle partial failures
- Allow manual correction

---

### 9.4 Orphaned Drafts

**Scenario:** Draft created but user never sends

**Expected Behavior:**
- Log as "drafted" (not sent)
- This is valid state
- User can manually send later
- No action needed

---

## 10. Error Recovery Edge Cases

### 10.1 Partial Batch Failure

**Scenario:** 3 emails sent, 2 failed, 1 skipped

**Expected Behavior:**
- Continue processing after failures
- Log each individually
- Show accurate summary: "3 sent, 2 failed, 1 skipped"
- Don't stop on first failure

---

### 10.2 Retry Logic

**Scenario:** Transient error (network blip) on one email

**Expected Behavior:**
- MVP: Fail and log, user retries manually
- Stretch: Implement retry with exponential backoff
- Limit retry attempts (e.g., 3)
- Log retry attempts

---

### 10.3 State Recovery After Crash

**Scenario:** Process crashes mid-batch

**Expected Behavior:**
- Log shows partial progress
- User can re-run (duplicates detected)
- Or implement resume capability (stretch)
- Document crash recovery

---

### 10.4 Manual Log Correction

**Scenario:** User needs to fix log entry manually

**Expected Behavior:**
- Log is plain CSV, editable
- Document format
- Warn about manual edits
- Validate after edit

---

## Priority Matrix

| Edge Case | Priority | Likelihood | Impact |
|-----------|----------|------------|--------|
| Missing required fields | High | High | High |
| Invalid email format | High | High | High |
| SMTP authentication failure | High | Medium | High |
| Word count exceeds limit | Medium | Medium | Medium |
| Missing .env file | High | Medium | High |
| Invalid user input | Medium | High | Low |
| Keyboard interrupt | Medium | Low | Low |
| Duplicate recipients | Medium | Medium | Medium |
| Log file permission denied | Low | Low | High |
| Network timeout | Medium | Low | Medium |

---

## Testing Strategy

### Unit-Level Edge Case Testing

```python
# Test invalid email
assert not is_valid_email("invalid-email")
assert not is_valid_email("@example.com")

# Test missing fields
contact = Contact(recipient_email="", company="Test", ...)
assert should_skip(contact) == True

# Test word count
draft = generate_email(long_background_contact)
assert draft.word_count <= 150 or handle_overflow(draft)
```

### Integration-Level Edge Case Testing

```bash
# Test with malformed JSON
echo '{"invalid": json}' > contacts.json
python main.py  # Should fail gracefully

# Test with missing .env
rm .env
python main.py  # Should use defaults or abort

# Test with DRY_RUN=true
DRY_RUN=true python main.py  # Should complete without sending
```

### Manual Edge Case Testing Checklist

- [ ] Empty contacts.json
- [ ] Contact with missing email
- [ ] Contact with invalid email
- [ ] Contact with empty company
- [ ] Contact with extremely long background
- [ ] Missing .env file
- [ ] Invalid SMTP credentials
- [ ] Network disconnected
- [ ] Keyboard interrupt during batch
- [ ] Skip all emails
- [ ] Send to self first
- [ ] Volume cap exceeded
- [ ] Duplicate recipients

---

## Summary

**The Closer** should handle edge cases with these principles:

1. **Fail loudly** - Clear error messages with actionable guidance
2. **Continue when possible** - Don't abort entire batch for single record failure
3. **Log everything** - All edge cases should be logged for debugging
4. **Safe defaults** - When in doubt, choose the safer option (skip vs send)
5. **User control** - Let user decide how to handle ambiguous situations
6. **No silent failures** - Every failure should be visible in terminal or log
