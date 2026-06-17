# Evaluation Criteria: The Closer — Phase-by-Phase Assessment

This document provides evaluation criteria for each implementation phase. Use this checklist to verify completion, quality, and adherence to requirements before moving to the next phase.

---

## Phase 1: Foundation — Project Setup, Data Models, and Configuration

### Deliverable Checklist

- [ ] Project structure created per architecture §10
- [ ] Python virtual environment initialized
- [ ] `requirements.txt` created with `python-dotenv`
- [ ] Dependencies installed successfully
- [ ] `.gitignore` created (excludes `.env`, `outreach_log.csv`, `__pycache__`)
- [ ] `models.py` created with Contact, EmailDraft, LogEntry dataclasses
- [ ] `config.py` created with AppConfig and load_config()
- [ ] `.env.example` created with all documented variables
- [ ] All files are valid Python (no syntax errors)

### Code Quality Checks

**models.py:**
- [ ] Contact dataclass has all fields from architecture §6.1
- [ ] EmailDraft has subject, body, word_count fields
- [ ] LogEntry has timestamp, recipient_email, company, role, subject, status, error_message
- [ ] All fields have proper type hints
- [ ] Optional fields use `str | None` or default values
- [ ] Docstrings present for each dataclass

**config.py:**
- [ ] AppConfig dataclass matches environment variables from architecture §5.7
- [ ] load_config() uses python-dotenv
- [ ] Default values documented (DRY_RUN=true, MAX_OUTREACH_PER_RUN=5)
- [ ] Validation for required fields when send mode active
- [ ] Clear error messages for missing required env vars
- [ ] Type conversion for int/bool env vars (not just strings)

### Functional Tests

```python
# Test 1: Import all models
from models import Contact, EmailDraft, LogEntry
# Expected: No ImportError

# Test 2: Create Contact instance
contact = Contact(
    recipient_email="test@example.com",
    company="Test Co",
    role="Test Role",
    candidate_name="Test User",
    candidate_background="Python developer"
)
# Expected: No errors, all fields accessible

# Test 3: Load config
from config import load_config
config = load_config()
# Expected: Config object with all fields, DRY_RUN=true by default

# Test 4: Missing .env handling
# Remove .env temporarily, run load_config()
# Expected: Uses defaults or shows clear warning
```

### Edge Cases Covered

- [ ] Missing .env file handled gracefully
- [ ] Invalid env var types (string instead of int/bool)
- [ ] Missing required env vars when DRY_RUN=false
- [ ] Extra whitespace in env var values

### Success Criteria

- All imports work without errors
- Config loads from .env file
- Defaults are sensible (DRY_RUN=true)
- Dataclasses are properly typed
- No syntax errors in any file

### Phase Score: ___/10

---

## Phase 2: Data Layer — Input Loader and Sample Data

### Deliverable Checklist

- [ ] `contacts.json` created with 3-5 sample records
- [ ] `input_loader.py` created with load_targets() function
- [ ] All required fields present in sample data
- [ ] Optional fields included in some records
- [ ] Field validation implemented
- [ ] Error handling for invalid records
- [ ] Hardcoded fallback implemented

### Code Quality Checks

**contacts.json:**
- [ ] Valid JSON syntax
- [ ] At least 3 contact records
- [ ] All required fields present in each record
- [ ] Email addresses are valid format
- [ ] Company and role are non-empty
- [ ] Realistic, varied data (different companies, roles)

**input_loader.py:**
- [ ] load_targets() accepts optional path parameter
- [ ] JSON parsing with error handling
- [ ] Email format validation (regex or library)
- [ ] Required field validation
- [ ] Non-empty string validation
- [ ] Invalid records skipped with warnings
- [ ] Returns list[Contact]
- [ ] Hardcoded fallback when no path provided

### Functional Tests

```python
# Test 1: Load from JSON
from input_loader import load_targets
contacts = load_targets("contacts.json")
# Expected: List of 3-5 Contact objects

# Test 2: Validate loaded data
assert len(contacts) >= 3
assert all(c.recipient_email for c in contacts)
assert all(c.company and c.role for c in contacts)
assert all(c.candidate_name and c.candidate_background for c in contacts)

# Test 3: Invalid email handling
# Add invalid email to contacts.json, reload
# Expected: Invalid record skipped, warning shown

# Test 4: Missing required field
# Remove required field from one record, reload
# Expected: Invalid record skipped, warning shown

# Test 5: Hardcoded fallback
contacts = load_targets(None)
# Expected: Returns hardcoded list of contacts
```

### Edge Cases Covered

- [ ] Invalid JSON syntax
- [ ] Empty contacts.json ([])
- [ ] File not found
- [ ] Invalid email format
- [ ] Missing required fields
- [ ] Empty string fields
- [ ] Null/None values
- [ ] Duplicate recipients

### Success Criteria

- Loads 3-5 valid contacts from JSON
- Invalid records are skipped with warnings
- Email validation works
- Required field validation works
- Hardcoded fallback works
- No crashes on malformed input

### Phase Score: ___/10

---

## Phase 3: Generation Layer — Email Generator with Templates

### Deliverable Checklist

- [ ] `email_generator.py` created
- [ ] generate_email() function implemented
- [ ] Email template follows six-part anatomy
- [ ] Word count calculation implemented
- [ ] Word count validation (≤150 words)
- [ ] Fallback logic for optional fields
- [ ] No hallucinated facts (template-only)

### Code Quality Checks

**email_generator.py:**
- [ ] generate_email() signature matches architecture §5.3
- [ ] Returns EmailDraft with subject, body, word_count
- [ ] Subject line is role/company specific
- [ ] Body includes all six sections:
  - [ ] Personalization hook
  - [ ] Introduction
  - [ ] Value/fit statement
  - [ ] One clear ask
  - [ ] Sign-off
- [ ] Word count calculated correctly
- [ ] Word count ≤ 150 enforced
- [ ] Missing recipient_name handled (default greeting)
- [ ] Missing personalization_note handled (company+role fallback)
- [ ] Template uses only provided fields (no hallucination)

### Functional Tests

```python
# Test 1: Generate email
from email_generator import generate_email
from input_loader import load_targets
from config import load_config

contacts = load_targets("contacts.json")
config = load_config()
draft = generate_email(contacts[0], config)

# Test 2: Validate output
assert draft.subject
assert draft.body
assert draft.word_count <= 150
assert draft.word_count > 0

# Test 3: Check email anatomy
assert "Hi" in draft.body or "Hello" in draft.body
assert contacts[0].candidate_name in draft.body
assert contacts[0].company in draft.body or contacts[0].role in draft.body

# Test 4: Word count enforcement
# Create contact with very long background
# Expected: Word count ≤ 150 or warning shown

# Test 5: Missing optional fields
contact_no_name = Contact(
    recipient_email="test@example.com",
    company="Test Co",
    role="Test Role",
    candidate_name="Test User",
    candidate_background="Python dev",
    recipient_name=None
)
draft = generate_email(contact_no_name, config)
# Expected: Uses default greeting
```

### Edge Cases Covered

- [ ] Word count exceeds 150
- [ ] Missing personalization_note
- [ ] Missing recipient_name
- [ ] Missing portfolio/resume links
- [ ] Special characters in fields
- [ ] Extremely long fields
- [ ] Template variable not found
- [ ] Generic personalization detection

### Success Criteria

- Generates valid EmailDraft for all contacts
- Word count ≤ 150 for all emails
- Subject lines are specific
- Body includes all six sections
- Optional fields handled gracefully
- No hallucinated facts
- Template interpolation works correctly

### Phase Score: ___/10

---

## Phase 4: Interaction Layer — Preview and Confirmation

### Deliverable Checklist

- [ ] `preview.py` created (or functions in main.py)
- [ ] preview_email() function implemented
- [ ] prompt_action() function implemented
- [ ] Formatted terminal output
- [ ] Input validation with re-prompting
- [ ] Safe default (skip on empty input)

### Code Quality Checks

**preview.py:**
- [ ] preview_email() shows recipient, company, role, subject, body, word count
- [ ] Clear formatting with separators
- [ ] Body is readable (line breaks preserved)
- [ ] prompt_action() accepts "send", "draft", "skip"
- [ ] Accepts common variations (y/yes, d/draft, s/skip/no)
- [ ] Re-prompts on invalid input
- [ ] Defaults to "skip" on empty input
- [ ] Returns Literal["send", "draft", "skip"]

### Functional Tests

```python
# Test 1: Preview display
from preview import preview_email
from email_generator import generate_email
from input_loader import load_targets
from config import load_config

contacts = load_targets("contacts.json")
config = load_config()
draft = generate_email(contacts[0], config)

preview_email(draft, contacts[0])
# Expected: All info displayed clearly

# Test 2: Action prompt (manual test)
from preview import prompt_action
action = prompt_action()
# Expected: Returns "send", "draft", or "skip"
# Test with various inputs: "yes", "y", "send", "draft", "d", "skip", "s", "no"

# Test 3: Invalid input handling
# Enter "maybe", should re-prompt
# Enter empty string, should default to "skip"
```

### Edge Cases Covered

- [ ] Invalid user input
- [ ] Empty input (default to skip)
- [ ] Keyboard interrupt
- [ ] Terminal too narrow
- [ ] Non-interactive environment

### Success Criteria

- Preview shows all relevant information
- Subject and body clearly visible
- Word count displayed
- User can choose send/draft/skip
- Invalid input triggers re-prompt
- Default to skip on empty input
- No crashes on any input

### Phase Score: ___/10

---

## Phase 5: Delivery Layer — Email Sender with Dry-Run Mode

### Deliverable Checklist

- [ ] `email_sender.py` created
- [ ] DeliveryResult dataclass defined
- [ ] deliver_email() function implemented
- [ ] DryRunEmailSender implemented
- [ ] SmtpEmailSender implemented
- [ ] Adapter pattern/factory for sender selection
- [ ] Error handling for auth failures
- [ ] Error handling for network errors

### Code Quality Checks

**email_sender.py:**
- [ ] DeliveryResult has status, provider_message_id, error fields
- [ ] deliver_email() signature matches architecture §5.5
- [ ] DryRunEmailSender returns success without network calls
- [ ] SmtpEmailSender uses smtplib with STARTTLS
- [ ] SMTP credentials loaded from config
- [ ] Port 587 used (or configurable)
- [ ] Authentication errors caught with clear messages
- [ ] Network errors caught and reported
- [ ] DRY_RUN=true routes to dry-run sender
- [ ] Consistent interface across all senders

### Functional Tests

```python
# Test 1: Dry-run sender
from email_sender import deliver_email
from email_generator import generate_email
from input_loader import load_targets
from config import load_config

contacts = load_targets("contacts.json")
config = load_config()  # DRY_RUN=true
draft = generate_email(contacts[0], config)

result = deliver_email(draft, contacts[0], config, "send")
assert result.status in ["sent", "dry_run", "generated"]
assert result.error is None

# Test 2: SMTP sender (with real credentials)
# Set DRY_RUN=false, provide real SMTP credentials
# Send to own email address
# Expected: Email arrives, status="sent"

# Test 3: Auth failure
# Use wrong password
# Expected: Clear error message, status="failed"

# Test 4: Network error
# Disconnect network
# Expected: Timeout or connection error, status="failed"
```

### Edge Cases Covered

- [ ] SMTP authentication failure
- [ ] Network timeout
- [ ] SMTP server unreachable
- [ ] TLS/SSL errors
- [ ] Rate limiting
- [ ] Email rejected by recipient server
- [ ] Dry-run mode active
- [ ] Missing credentials in send mode
- [ ] Sender email mismatch

### Success Criteria

- Dry-run sender works without network
- SMTP sender sends emails successfully
- Authentication failures show clear errors
- Network errors are caught and reported
- DRY_RUN flag respected
- All senders return consistent result
- No silent failures

### Phase Score: ___/10

---

## Phase 6: Audit Layer — Logger Implementation

### Deliverable Checklist

- [ ] `logger.py` created
- [ ] append_log() function implemented
- [ ] CSV schema defined
- [ ] Header creation logic
- [ ] Append-only behavior
- [ ] All status values supported

### Code Quality Checks

**logger.py:**
- [ ] append_log() accepts LogEntry and optional path
- [ ] Creates file with header if missing
- [ ] Appends mode (never overwrites)
- [ ] CSV columns match architecture §5.6:
  - [ ] timestamp
  - [ ] recipient_email
  - [ ] company
  - [ ] role
  - [ ] subject
  - [ ] status
  - [ ] error_message
  - [ ] word_count (optional)
  - [ ] job_url (optional)
- [ ] Status values: generated, drafted, sent, skipped, failed
- [ ] Timestamp in ISO-8601 format
- [ ] Error messages logged when present
- [ ] Handles file permission errors gracefully

### Functional Tests

```python
# Test 1: Create log file
from logger import append_log
from models import LogEntry
from datetime import datetime

entry = LogEntry(
    timestamp=datetime.now().isoformat(),
    recipient_email="test@example.com",
    company="Test Co",
    role="Test Role",
    subject="Test Subject",
    status="generated"
)

append_log(entry, "test_log.csv")
# Expected: File created with header + 1 row

# Test 2: Append multiple entries
for i in range(3):
    entry = LogEntry(
        timestamp=datetime.now().isoformat(),
        recipient_email=f"test{i}@example.com",
        company="Test Co",
        role="Test Role",
        subject="Test Subject",
        status="generated"
    )
    append_log(entry, "test_log.csv")
# Expected: Header + 4 rows total

# Test 3: Read and verify
import csv
with open("test_log.csv") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
assert len(rows) == 4
```

### Edge Cases Covered

- [ ] Log file permission denied
- [ ] Disk full
- [ ] Log file corrupted
- [ ] Concurrent write attempts
- [ ] Missing log header
- [ ] CSV encoding issues
- [ ] Extremely long subject in log

### Success Criteria

- Log file created with header on first write
- Each outreach appends new row
- All required columns present
- Status values match expected enum
- Errors logged with messages
- File never overwritten
- CSV is valid and readable

### Phase Score: ___/10

---

## Phase 7: Integration — Orchestrator and End-to-End Testing

### Deliverable Checklist

- [ ] `main.py` created
- [ ] run_outreach_pipeline() implemented
- [ ] All modules integrated
- [ ] Per-contact state machine implemented
- [ ] Volume cap enforced
- [ ] Batch summary printed
- [ ] Error handling throughout
- [ ] CLI entry point working

### Code Quality Checks

**main.py:**
- [ ] Loads configuration at startup
- [ ] Loads contacts with input loader
- [ ] Applies guardrails (volume cap, validation)
- [ ] Loops through contacts (respects MAX_OUTREACH_PER_RUN)
- [ ] For each contact:
  - [ ] Generates email
  - [ ] Previews email
  - [ ] Prompts for action
  - [ ] Delivers email (or skips)
  - [ ] Logs result
- [ ] Prints batch summary (sent/drafted/skipped/failed counts)
- [ ] State transitions: Loaded → Generated → Previewed → Delivering/Skipped → Sent/Drafted/Failed
- [ ] DRY_RUN flag checked before real delivery
- [ ] Config validated before sending
- [ ] Errors handled gracefully (don't crash entire batch)
- [ ] KeyboardInterrupt caught and handled
- [ ] if __name__ == "__main__": block present

### Functional Tests

```bash
# Test 1: End-to-end dry-run
# Set DRY_RUN=true in .env
python main.py
# Expected:
# - 3-5 contacts processed
# - Preview shown for each
# - User prompted for each
# - outreach_log.csv created
# - Summary printed

# Test 2: Volume cap
# Set MAX_OUTREACH_PER_RUN=2
# Have 5 contacts in contacts.json
python main.py
# Expected: Only 2 processed, message about cap

# Test 3: Skip all
# Choose "skip" for all contacts
# Expected: Summary shows 0 sent, 0 drafted, 5 skipped

# Test 4: Error handling
# Corrupt one contact record
# Expected: Invalid record skipped, others processed

# Test 5: Keyboard interrupt
# Press Ctrl+C mid-batch
# Expected: Graceful exit, partial summary shown
```

### Edge Cases Covered

- [ ] Empty contacts list
- [ ] All contacts invalid
- [ ] User skips all emails
- [ ] Keyboard interrupt
- [ ] Missing config
- [ ] Module import failure
- [ ] Partial batch failure

### Success Criteria

- Pipeline runs from start to finish without errors
- All modules integrate correctly
- Volume cap enforced
- Dry-run mode works end-to-end
- Log file populated with all attempts
- Batch summary shows accurate counts
- Errors don't crash entire pipeline
- KeyboardInterrupt handled gracefully

### Phase Score: ___/10

---

## Phase 8: Production — Live Send with Safety Verification

### Deliverable Checklist

- [ ] Real SMTP credentials configured
- [ ] Gmail App Password setup documented
- [ ] Test email sent to own address
- [ ] 3-5 real emails sent/drafted
- [ ] All emails verified in Sent/Drafts folder
- [ ] outreach_log.csv verified
- [ ] Screenshots collected
- [ ] README updated with setup instructions
- [ ] Safety verification completed

### Code Quality Checks

**Configuration:**
- [ ] .env has real SMTP credentials
- [ ] DRY_RUN=false for production
- [ ] MAX_OUTREACH_PER_RUN set appropriately
- [ ] SMTP_USER matches sender email
- [ ] Gmail App Password used (not regular password)

**Documentation:**
- [ ] README has setup instructions
- [ ] Gmail App Password setup documented
- [ ] Troubleshooting section added
- [ ] Safety features documented

**Verification:**
- [ ] Test email to self arrived successfully
- [ ] All 3-5 emails visible in Sent/Drafts
- [ ] Log file matches actual delivery
- [ ] No accidental bulk sends
- [ ] All emails were human-reviewed
- [ ] Screenshots taken as proof

### Functional Tests

```bash
# Test 1: Safe test to self
# Set MAX_OUTREACH_PER_RUN=1
# Set recipient to own email
# Set DRY_RUN=false
python main.py
# Expected: Email arrives in Sent folder

# Test 2: Production run
# Set MAX_OUTREACH_PER_RUN=5
# Use real contacts
python main.py
# Expected:
# - 5 emails processed
# - Each previewed and confirmed
# - All visible in Sent/Drafts
# - Log shows 5 sent/drafted

# Test 3: Verify log
cat outreach_log.csv
# Expected: 5 rows, status="sent" or "drafted"
```

### Safety Verification Checklist

- [ ] Volume cap respected (didn't exceed MAX_OUTREACH_PER_RUN)
- [ ] All emails were previewed before sending
- [ ] No accidental bulk sends
- [ ] Identity not spoofed (SMTP_USER matches sender)
- [ ] No fake claims in emails
- [ ] Personalization present in all emails
- [ ] Opt-outs respected (if applicable)

### Success Criteria

- 5+ personalized emails sent/drafted
- All emails visible in Sent/Drafts folder
- Log file matches actual delivery
- No accidental bulk sends
- All emails were human-reviewed
- Screenshots collected
- README complete
- Safety verification passed

### Phase Score: ___/10

---

## Overall Project Evaluation

### Functional Requirements Met

- [ ] FR1: Loads outreach targets from JSON/CSV
- [ ] FR2: Generates personalized emails
- [ ] FR3: Previews before sending
- [ ] FR4: Sends or drafts emails
- [ ] FR5: Logs all attempts

### Non-Functional Requirements Met

- [ ] Simple and explainable
- [ ] Safe by default
- [ ] Modular design
- [ ] Configurable via env vars
- [ ] Clear error messages

### Safety Requirements Met

- [ ] Human review required
- [ ] Low-volume sending
- [ ] Personalization required
- [ ] No deceptive identity
- [ ] No fake claims
- [ ] Opt-outs respected (if implemented)

### Acceptance Criteria Met

- [ ] 5+ personalized emails generated
- [ ] Subject + body for each
- [ ] Company/role personalization
- [ ] Preview before send
- [ ] Send/draft successful
- [ ] Log entries created
- [ ] Proof via screenshots

### Code Quality Metrics

- [ ] No syntax errors
- [ ] All imports work
- [ ] Type hints present
- [ ] Docstrings present
- [ ] Error handling comprehensive
- [ ] Edge cases handled
- [ ] Logging comprehensive
- [ ] Tests pass

### Documentation Quality

- [ ] README complete
- [ ] Setup instructions clear
- [ ] Architecture documented
- [ ] Edge cases documented
- [ ] Evaluation criteria documented

### Overall Project Score: ___/100

---

## Evaluation Process

### How to Use This Document

1. **Before starting each phase:** Review the deliverable checklist
2. **During implementation:** Refer to code quality checks
3. **After completing phase:** Run functional tests
4. **Before moving to next phase:** Verify edge cases and success criteria
5. **Score the phase:** Assign score based on completion

### Scoring Guidelines

**10/10 - Excellent:**
- All deliverables complete
- All code quality checks pass
- All functional tests pass
- All edge cases handled
- Exceeds expectations

**8-9/10 - Good:**
- All deliverables complete
- Most code quality checks pass
- All functional tests pass
- Most edge cases handled
- Meets expectations

**6-7/10 - Acceptable:**
- Most deliverables complete
- Some code quality issues
- Functional tests mostly pass
- Some edge cases unhandled
- Minor issues present

**4-5/10 - Needs Improvement:**
- Some deliverables missing
- Code quality issues
- Some functional tests fail
- Many edge cases unhandled
- Significant issues

**0-3/10 - Incomplete:**
- Many deliverables missing
- Major code quality issues
- Functional tests fail
- Edge cases not handled
- Not ready for next phase

### When to Proceed to Next Phase

- Phase score ≥ 6/10
- All critical deliverables complete
- All functional tests pass
- No blocking issues
- Edge cases either handled or documented

### When to Stop and Fix

- Phase score < 6/10
- Critical deliverables missing
- Functional tests failing
- Blocking issues present
- Safety concerns

---

## Final Submission Checklist

### Code Repository
- [ ] All phases completed
- [ ] No syntax errors
- [ ] All dependencies in requirements.txt
- [ ] .env.example present
- [ ] .gitignore properly configured
- [ ] README complete

### Documentation
- [ ] Problem statement documented
- [ ] Architecture documented
- [ ] Implementation plan documented
- [ ] Edge cases documented
- [ ] Evaluation criteria documented

### Proof of Work
- [ ] Screenshots of 5 sent/drafted emails
- [ ] outreach_log.csv file
- [ ] Log matches actual delivery
- [ ] Safety verification passed

### Submission Package
- [ ] GitHub repository or zipped code
- [ ] Screenshots of emails
- [ ] outreach_log.csv
- [ ] Short explanation of system
- [ ] Notes on sending method used

---

## Continuous Evaluation

### During Development

- Run functional tests after each module
- Check code quality before committing
- Test edge cases as they're discovered
- Update this document with new edge cases

### Before Demo

- Run full end-to-end test
- Verify all phases pass
- Check safety features
- Prepare demo data
- Test dry-run mode

### After Production Run

- Verify all emails delivered
- Check log accuracy
- Collect screenshots
- Document any issues
- Update edge cases if needed

---

## Notes

- This evaluation document should be updated as the project evolves
- New edge cases discovered during development should be added
- Scores are subjective but should be consistent
- The goal is quality, not just completion
- Safety is paramount—never compromise on safety features
