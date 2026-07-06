# MedCombo Privacy Data Inventory

## Purpose

This inventory documents the data MedCombo can collect in the local MVP and the
privacy decisions required before any hosted or persistent deployment.

MedCombo currently runs as a local development demo. This document does not
authorize hosted collection of medication lists or health context.

## Current Runtime Boundary

Current mode:

- Local Python standard-library web server.
- No database.
- No file-backed user session store.
- Development-only in-memory web session state.
- Demo knowledge base loaded from repository JSON files.

Current persistence:

- User-entered review data is not intentionally written to disk by the app.
- Multi-turn intake answers are stored in process memory only.
- Data disappears when the local process stops.

Important limitation:

- The app does not yet implement production privacy controls, access controls,
  consent, retention, deletion, audit logging, or breach-response workflows.

## Data Categories

| Category | Examples | Current handling | Sensitivity |
| --- | --- | --- | --- |
| Medication entries | Product names, prescriptions, OTC products, typed list | Parsed in memory for review | Sensitive health-related data |
| Supplements | Vitamin D, fish oil, herbal products | Parsed in memory for context signal | Sensitive health-related data |
| Demographics | Age range, sex, pregnancy status if entered | Included in context and summary | Sensitive personal or health data |
| Body information | Weight, kidney or liver notes, blood pressure context | Included in context and summary | Sensitive health data |
| Conditions or history | Chronic conditions, allergies if typed | Included in context and summary | Sensitive health data |
| Current symptoms | User-entered symptoms or concerns | Included in context and summary | Sensitive health data |
| Intake source | Manual, label, pharmacy list, medical summary, memory, photo | Stored in intake state | Contextual sensitivity |
| Agent turns | Follow-up question, answer, extracted field, status | Stored in process memory | Sensitive health-related data |
| Generated signals | Review-worthy signal, source IDs, rule IDs, evidence metadata | Generated in memory | Derived health-related data |
| Review summary | Combined medication list, context, signals, questions | Rendered to browser | Sensitive derived data |

## Data Not Currently Implemented

The local MVP does not currently implement:

- user accounts
- authentication
- authorization
- persistent sessions
- cloud storage
- analytics
- telemetry
- uploaded image storage
- OCR
- EHR import
- FHIR import or export
- email, SMS, or sharing workflows

If any of these are added, this inventory must be updated before implementation.

## No-PHI Demo Boundary

Recommended public demo posture:

- Use synthetic sample lists only.
- Do not ask users to enter real medication lists.
- Avoid free-text health context in hosted demos unless privacy controls exist.
- Label the demo as local-only or synthetic-data-only.
- Keep sample data out of real patient or personal health information.

## Hosted Deployment Gates

Before a hosted demo or persistent session feature:

1. Define intended use and claims.
2. Decide whether real medication or health context is allowed.
3. Create consent and notice language.
4. Define retention duration.
5. Implement deletion workflow.
6. Implement access controls.
7. Implement audit logging.
8. Review HIPAA, FTC Act, Health Breach Notification Rule, FD&C Act, COPPA,
   state privacy laws, and app-store requirements as applicable.
9. Define breach-response process.
10. Add security testing and dependency review.

## Retention Decision Placeholder

Current decision:

- Local development demo: process memory only.
- Hosted demo: not approved for identifiable medication or health information.

Future decisions needed:

- Whether to allow real medication lists.
- Whether summaries can be downloaded.
- Whether users can save sessions.
- How long saved sessions persist.
- Who can access saved sessions.
- How users delete saved sessions.
- Whether logs can contain medication names or symptoms.

## Engineering Requirements Before Persistence

If persistent storage is added:

- Centralize session serialization.
- Exclude raw health text from default logs.
- Add structured deletion tests.
- Add data inventory tests or checks for new fields.
- Add audit metadata for created, viewed, updated, and deleted records.
- Encrypt data at rest and in transit for hosted deployment.
- Keep demo fixtures separate from any user-entered data.

## Product Wording Requirements

User-facing text should continue to say:

- MedCombo is in development.
- MedCombo is not clinically validated or FDA-cleared.
- MedCombo does not replace pharmacist or clinician judgment.
- No demo signal is not a complete medication safety screen.
- Real sensitive personal information requires privacy and security controls.

Avoid:

- implying hosted data is safe to enter before controls exist
- implying real medication review can be stored
- asking users to upload labels or photos before OCR privacy handling exists

## Immediate Follow-Up Tasks

1. Add a no-PHI hosted demo mode if deployment is needed.
2. Add tests that logging does not include raw medication input by default.
3. Draft deletion workflow requirements before persistent sessions.
4. Review whether downloadable summaries create local storage risk.
5. Revisit this inventory when source ingestion or image intake is implemented.
