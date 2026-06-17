# Implementation Plan: The Closer — Phase-Wise Build

This document outlines a phase-wise implementation plan for **The Closer** cold email writer and send bot, derived from [architecture.md](./architecture.md) and [problemStatement.md](./problemStatement.md).

**Build Strategy:** Vertical slices - each phase delivers a working, testable component that builds toward the complete system.

---

## Phase 1: Foundation — Project Setup, Data Models, and Configuration

**Goal:** Establish project structure, define data models, and set up configuration management.

### Tasks

1. **Project Structure Setup**
   - Create repository root directory
   - Set up Python virtual environment
   - Create folder structure per architecture §10
   - Initialize `.gitignore` (exclude `.env`, `outreach_log.csv`, `__pycache__`)

2. **Dependencies**
   - Create `requirements.txt` with:
     - `python-dotenv` (environment variable loading)
   - Install dependencies

3. **Data Models** (`models.py`)
   - Define `Contact` dataclass with all fields from architecture §6.1
   - Define `EmailDraft` dataclass (subject, body, word_count)
   - Define `LogEntry` dataclass (timestamp, recipient_email, company, role, subject, status, error_message)
   - Add type hints and docstrings

4. **Configuration** (`config.py`)
   - Create `AppConfig` dataclass
   - Implement `load_config()` function using `python-dotenv`
   - Define environment variables from architecture §5.7:
     - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`
     - `SENDER_NAME`, `DRY_RUN`, `SEND_MODE`, `MAX_OUTREACH_PER_RUN`, `INPUT_PATH`
   - Create `.env.example` file with defaults
   - Add validation for required fields when send mode is active

### Deliverables

- `models.py` with Contact, EmailDraft, LogEntry dataclasses
- `config.py` with AppConfig and load_config()
- `.env.example` template
- `requirements.txt`
- `.gitignore`

### Acceptance Criteria

- Can import dataclasses without errors
- `load_config()` reads from `.env` file
- Missing required env vars raise clear error messages
- `DRY_RUN` defaults to `true`

### Verification

```python
# Manual test
from config import load_config
from models import Contact, EmailDraft, LogEntry

config = load_config()
assert config.dry_run == True
assert config.max_outreach_per_run == 5
```

---

## Phase 2: Data Layer — Input Loader and Sample Data

**Goal:** Implement FR1 - load outreach targets from local files with validation.

### Tasks

1. **Sample Data Creation** (`contacts.json`)
   - Create 3-5 sample contact records matching problem statement §5
   - Include all required fields (recipient_email, company, role, candidate_name, candidate_background)
   - Include optional fields (recipient_name, personalization_note, portfolio_url, job_url)
   - Ensure realistic, varied data for testing

2. **Input Loader** (`input_loader.py`)
   - Implement `load_targets(path: str | None = None) -> list[Contact]`
   - Support JSON file loading
   - Add field validation per architecture §5.2:
     - Email format validation
     - Required field presence checks
     - Non-empty string validation
   - Handle missing/invalid records with clear error messages
   - Return only valid contacts (skip invalid ones with warnings)

3. **Hardcoded Fallback**
   - Add fallback to hardcoded list if no path provided
   - Useful for live demo and testing

### Deliverables

- `contacts.json` with 3-5 sample records
- `input_loader.py` with load_targets() function
- Validation logic for all required fields

### Acceptance Criteria

- `load_targets()` returns list of Contact objects
- Invalid records are skipped with console warnings
- Missing required fields cause record rejection
- Email format is validated
- Can load from both JSON and hardcoded fallback

### Verification

```python
# Manual test
from input_loader import load_targets

contacts = load_targets("contacts.json")
assert len(contacts) >= 3
assert all(c.recipient_email for c in contacts)
assert all(c.company and c.role for c in contacts)
```

---

## Phase 3: Generation Layer — Email Generator with Templates

**Goal:** Implement FR2 - generate personalized cold emails following the six-part anatomy.

### Tasks

1. **Email Generator** (`email_generator.py`)
   - Implement `generate_email(contact: Contact, config: AppConfig) -> EmailDraft`
   - Create template following problem statement §7 (email anatomy):
     - Subject line (role/company specific)
     - Personalization hook (company/role or personalization_note)
     - Introduction (candidate_name, candidate_background)
     - Value/fit statement
     - One clear ask
     - Sign-off with optional portfolio link
   - Use Python f-strings or `string.Template` for MVP
   - Implement word count calculation
   - Add word count validation (≤150 words)
   - Handle missing optional fields gracefully (defaults)

2. **Template Logic**
   - Subject: `f"Quick note on the {role} role"` or company variant
   - Body template with conditional sections
   - Fallback for missing `recipient_name` ("Hi there" or "Hi")
   - Fallback for missing `personalization_note` (derive from company + role)

3. **Guardrails**
   - Enforce word count limit
   - Warn if personalization is too generic
   - Ensure no hallucinated facts (template-only interpolation)

### Deliverables

- `email_generator.py` with generate_email() function
- Email template following six-part anatomy
- Word count validation
- Fallback logic for optional fields

### Acceptance Criteria

- `generate_email()` returns EmailDraft with subject, body, word_count
- Word count ≤ 150 for all generated emails
- Subject lines are role/company specific
- Body includes all six email anatomy sections
- Missing optional fields use sensible defaults
- No hallucinated facts (only template interpolation)

### Verification

```python
# Manual test
from email_generator import generate_email
from input_loader import load_targets
from config import load_config

contacts = load_targets("contacts.json")
config = load_config()

for contact in contacts[:3]:
    draft = generate_email(contact, config)
    assert draft.word_count <= 150
    assert draft.subject
    assert draft.body
    print(f"Subject: {draft.subject}")
    print(f"Word count: {draft.word_count}")
```

---

## Phase 4: Interaction Layer — Preview and Confirmation

**Goal:** Implement FR3 - human-in-the-loop gate before email delivery.

### Tasks

1. **Preview Module** (`preview.py` or inline in main.py)
   - Implement `preview_email(draft: EmailDraft, contact: Contact) -> None`
   - Pretty-print email preview with:
     - Recipient email and name
     - Company and role
     - Subject line
     - Email body (formatted)
     - Word count
   - Use clear formatting with separators

2. **Confirmation Prompt**
   - Implement `prompt_action() -> Literal["send", "draft", "skip"]`
   - Display prompt: "Send this email? (send/draft/skip):"
   - Validate user input (accept variations: y/yes/send, d/draft, s/skip/no)
   - Re-prompt on invalid input
   - Default to "skip" on empty input (safe default)

3. **Edit Mode (Stretch)**
   - Optional: allow user to edit email before sending
   - Re-display preview after edit

### Deliverables

- `preview.py` with preview_email() and prompt_action() functions
- Formatted terminal output
- Input validation with re-prompting

### Acceptance Criteria

- Preview displays all relevant email information
- Subject and body are clearly visible
- Word count is shown
- User can choose send, draft, or skip
- Invalid input triggers re-prompt
- Default to skip on empty input (safe)

### Verification

```python
# Manual test (interactive)
from preview import preview_email, prompt_action
from email_generator import generate_email
from input_loader import load_targets
from config import load_config

contacts = load_targets("contacts.json")
config = load_config()
draft = generate_email(contacts[0], config)

preview_email(draft, contacts[0])
action = prompt_action()
assert action in ["send", "draft", "skip"]
```

---

## Phase 5: Delivery Layer — Email Sender with Dry-Run Mode

**Goal:** Implement FR4 - abstract email delivery behind pluggable interface with safety-first approach.

### Tasks

1. **Email Sender Interface** (`email_sender.py`)
   - Define `DeliveryResult` dataclass (status, provider_message_id, error)
   - Define protocol/interface for EmailSender
   - Implement `deliver_email(draft, contact, config, mode) -> DeliveryResult`

2. **Dry Run Sender**
   - Implement `DryRunEmailSender` class
   - Skip all network I/O
   - Return success without actual delivery
   - Log status as "dry_run" or "generated"

3. **SMTP Sender** (`SmtpEmailSender`)
   - Implement SMTP delivery using `smtplib`
   - Support STARTTLS on port 587
   - Load credentials from config
   - Handle authentication failures with clear error messages
   - Support both "send" and "draft" modes (draft mode may use Gmail API as stretch)

4. **Adapter Pattern**
   - Create sender factory based on config
   - Route to appropriate sender (dry-run vs real)
   - Ensure consistent interface across all senders

5. **Error Handling**
   - Catch SMTP authentication errors
   - Catch network errors
   - Provide actionable error messages (e.g., "Use Gmail App Password")
   - Never silently fail on user-confirmed send

### Deliverables

- `email_sender.py` with sender interface and implementations
- `DryRunEmailSender` for safe testing
- `SmtpEmailSender` for real delivery
- Error handling with clear messages

### Acceptance Criteria

- `DryRunEmailSender` returns success without network calls
- `SmtpEmailSender` sends emails via SMTP
- Authentication failures show clear error messages
- Network errors are caught and reported
- `DRY_RUN=true` routes to dry-run sender
- All senders return consistent `DeliveryResult`

### Verification

```python
# Manual test with dry-run
from email_sender import deliver_email
from email_generator import generate_email
from input_loader import load_targets
from config import load_config

contacts = load_targets("contacts.json")
config = load_config()  # DRY_RUN=true
draft = generate_email(contacts[0], config)

result = deliver_email(draft, contacts[0], config, "send")
assert result.status in ["sent", "dry_run", "failed"]
```

---

## Phase 6: Audit Layer — Logger Implementation

**Goal:** Implement FR5 - append-only audit log for all outreach attempts.

### Tasks

1. **Logger Module** (`logger.py`)
   - Implement `append_log(entry: LogEntry, path: str = "outreach_log.csv") -> None`
   - Create CSV file with header if missing
   - Append mode (never overwrite)
   - Handle concurrent access (basic file lock optional for stretch)

2. **Log Schema**
   - Columns per architecture §5.6:
     - timestamp (ISO-8601)
     - recipient_email
     - company
     - role
     - subject
     - status (generated, drafted, sent, skipped, failed)
     - error_message
     - word_count (optional)
     - job_url (optional)

3. **Integration Points**
   - Log every email generation attempt
   - Log user decisions (send, draft, skip)
   - Log delivery results (success/failure)
   - Log errors with full error messages

4. **Log Integrity**
   - Ensure header created only once
   - Ensure all rows have same column count
   - Handle file permission errors gracefully

### Deliverables

- `logger.py` with append_log() function
- CSV schema definition
- Header creation logic
- Append-only behavior

### Acceptance Criteria

- Log file created with header on first write
- Each outreach attempt appends a new row
- All required columns present
- Status values match expected enum
- Errors are logged with messages
- File is never overwritten

### Verification

```python
# Manual test
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
# Verify file exists and has header + 1 row
```

---

## Phase 7: Integration — Orchestrator and End-to-End Testing

**Goal:** Implement `main.py` orchestrator to wire all modules together and test complete pipeline.

### Tasks

1. **Orchestrator** (`main.py`)
   - Implement `run_outreach_pipeline()` per architecture §5.1 pseudocode
   - Load configuration
   - Load contacts with input loader
   - Apply guardrails (volume cap, validation)
   - Loop through contacts (respect MAX_OUTREACH_PER_RUN)
   - For each contact:
     - Generate email
     - Preview email
     - Prompt for action
     - Deliver email (or skip)
     - Log result
   - Print batch summary (sent/drafted/skipped/failed counts)

2. **Per-Contact State Machine**
   - Implement state transitions per architecture §5.1
   - Handle each state: Loaded → Generated → Previewed → Delivering/Skipped → Sent/Drafted/Failed
   - Ensure clean state transitions

3. **Guardrails in Orchestrator**
   - Enforce MAX_OUTREACH_PER_RUN cap
   - Check DRY_RUN flag before real delivery
   - Validate config before sending
   - Handle errors gracefully without stopping entire batch

4. **CLI Entry Point**
   - Add `if __name__ == "__main__":` block
   - Call `run_outreach_pipeline()`
   - Handle keyboard interrupts gracefully

5. **End-to-End Testing**
   - Test with DRY_RUN=true
   - Test with 3-5 contacts
   - Verify all log entries created
   - Verify batch summary accuracy
   - Test error scenarios (invalid contact, send failure)

### Deliverables

- `main.py` with complete orchestrator
- Working end-to-end pipeline
- Batch summary reporting
- Error handling throughout

### Acceptance Criteria

- Pipeline runs from start to finish without errors
- All modules integrate correctly
- Volume cap is enforced
- Dry-run mode works end-to-end
- Log file populated with all attempts
- Batch summary shows accurate counts
- Errors don't crash entire pipeline

### Verification

```bash
# End-to-end test
python main.py
# Verify:
# - 3-5 emails processed
# - Preview shown for each
# - User prompted for each
# - outreach_log.csv created with entries
# - Summary printed at end
```

---

## Phase 8: Production — Live Send with Safety Verification

**Goal:** Transition from dry-run to live sending with safety verification and proof of work.

### Tasks

1. **Credential Setup**
   - Configure real SMTP credentials in `.env`
   - Use Gmail App Password (document in README)
   - Test authentication separately
   - Verify sender email matches SMTP_USER

2. **Safe Live Test**
   - Set DRY_RUN=false
   - Set MAX_OUTREACH_PER_RUN=1
   - Send test email to own address first
   - Verify email arrives in Sent folder
   - Verify log entry shows "sent" status

3. **Production Run**
   - Send to 3-5 real contacts
   - Maintain human review for each
   - Monitor log file in real-time
   - Verify each email in Sent/Drafts folder

4. **Proof Collection**
   - Take screenshots of Sent/Drafts folder
   - Export `outreach_log.csv`
   - Verify log matches actual emails sent
   - Document sending method used

5. **Safety Verification**
   - Confirm volume cap respected
   - Confirm all emails were previewed
   - Confirm no accidental bulk send
   - Confirm identity not spoofed

6. **Documentation**
   - Update README with setup instructions
   - Document Gmail App Password setup
   - Add troubleshooting section
   - Document safety features

### Deliverables

- Working live email delivery
- Screenshots of sent/drafted emails
- Complete `outreach_log.csv`
- Updated README with setup guide
- Safety verification checklist

### Acceptance Criteria

- At least 5 personalized emails sent/drafted
- All emails visible in Sent/Drafts folder
- Log file matches actual delivery
- No accidental bulk sends
- All emails were human-reviewed
- Screenshots collected as proof

### Verification

```bash
# Production run
# 1. Set DRY_RUN=false in .env
# 2. Set MAX_OUTREACH_PER_RUN=5
# 3. Run: python main.py
# 4. Verify each email in Gmail
# 5. Check outreach_log.csv
# 6. Take screenshots
```

---

## Stretch Goals (Post-MVP)

After completing Phase 8, consider these enhancements:

### Gmail API Integration
- Implement `GmailApiEmailSender` for draft creation
- OAuth2 authentication flow
- Draft mode creates Gmail drafts instead of sending

### CSV Upload Support
- Extend `input_loader.py` to parse CSV files
- Map CSV columns to Contact fields
- Handle various CSV formats

### Streamlit UI
- Create `ui/app.py` with Streamlit
- Web-based preview and confirmation
- File upload for contacts
- Real-time log viewing

### LLM Email Rewriter
- Implement `LLMEmailGenerator` class
- Use OpenAI/Claude API for tone improvement
- Add post-generation validation
- Quality scoring before preview

### Email Quality Checker
- Spam risk analysis
- Readability scoring
- Personalization strength check
- Multiple subject line suggestions

### Follow-up Generator
- New module `followup_generator.py`
- Generate follow-up emails based on log history
- Link follow-ups to original emails via parent_id

### Deduplication
- `RecipientRegistry` to track contacted emails
- Filter out already-contacted recipients
- Respect opt-out list from `do_not_contact.csv`

---

## Implementation Timeline Estimate

| Phase | Estimated Time | Dependencies |
|-------|----------------|--------------|
| Phase 1: Foundation | 1-2 hours | None |
| Phase 2: Data Layer | 1-2 hours | Phase 1 |
| Phase 3: Generation | 2-3 hours | Phase 1, 2 |
| Phase 4: Interaction | 1-2 hours | Phase 1, 3 |
| Phase 5: Delivery | 2-3 hours | Phase 1 |
| Phase 6: Audit | 1 hour | Phase 1 |
| Phase 7: Integration | 2-3 hours | All previous |
| Phase 8: Production | 1-2 hours | All previous |
| **Total MVP** | **11-18 hours** | |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| SMTP authentication fails | Document Gmail App Password setup; provide clear error messages |
| Word count exceeds limit | Implement auto-trim or regeneration; warn in preview |
| Generic personalization | Add guardrail to reject empty/generic hooks |
| Accidental bulk send | DRY_RUN default; volume cap; human confirmation required |
| Email marked as spam | Keep volume low; use personalization; avoid spammy language |
| Lost credentials | Use `.env` never committed; document setup process |

---

## Success Criteria

The implementation is successful when:

1. **Functional Requirements Met**
   - FR1: Loads outreach targets from JSON/CSV ✓
   - FR2: Generates personalized emails ✓
   - FR3: Previews before sending ✓
   - FR4: Sends or drafts emails ✓
   - FR5: Logs all attempts ✓

2. **Non-Functional Requirements Met**
   - Simple and explainable ✓
   - Safe by default ✓
   - Modular design ✓
   - Configurable via env vars ✓
   - Clear error messages ✓

3. **Safety Requirements Met**
   - Human review required ✓
   - Low-volume sending ✓
   - Personalization required ✓
   - No deceptive identity ✓
   - No fake claims ✓

4. **Acceptance Criteria Met**
   - 5+ personalized emails generated ✓
   - Subject + body for each ✓
   - Company/role personalization ✓
   - Preview before send ✓
   - Send/draft successful ✓
   - Log entries created ✓
   - Proof via screenshots ✓

---

## Next Steps

1. Begin with Phase 1 (Foundation)
2. Complete each phase sequentially
3. Test each phase before moving to next
4. Document any deviations from this plan
5. Collect proof at Phase 8 completion
