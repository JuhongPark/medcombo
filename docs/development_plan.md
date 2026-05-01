# MedCombo Development Plan

## Goal

Build MedCombo as a consumer-first healthcare AI system for medication safety
review.

The first working product should let a consumer enter a medication list, see
structured medication information, review source-linked safety signals, and
generate questions or summaries for a pharmacist or clinician.

## Product Assumptions

- The primary user is a consumer or caregiver, not a clinician.
- The system category is healthcare AI.
- The initial workflow is medication-combination safety review.
- The system surfaces review signals, not final medication decisions.
- Professional review remains the decision path for medication changes.
- Source traceability is a core product requirement, not a nice-to-have.
- AI is used for intake, structuring, explanation, and summarization before it is
  used for safety-critical reasoning.

## Initial System Boundary

The MVP should handle a small curated medication set well instead of attempting
wide medication coverage too early.

Supported in MVP:

- Typed medication list entry.
- Normalized medication candidates.
- Active ingredient display.
- Duplicate ingredient signals.
- Therapeutic class overlap signals.
- Curated interaction signals.
- Consumer-readable explanations.
- Pharmacist or clinician question generation.
- Shareable review summary.
- Source and rule identifiers.

Not supported in MVP:

- Medication start, stop, or change instructions.
- Dosage adjustment recommendations.
- Diagnostic claims.
- Emergency triage.
- Full supplement coverage.
- Real patient-specific safety determination.
- EHR integration.
- Storage of identifiable health information without a privacy and security
  implementation.

## Recommended Repository Structure

The first implementation can use a small Python backend and a simple consumer UI.

```text
medcombo/
  __init__.py
  models.py
  normalize.py
  knowledge.py
  rules.py
  explain.py
  summary.py
  safety_language.py
data/
  demo/
    medications.json
    interactions.json
    sources.json
docs/
  initial_project_ideas.md
  development_plan.md
tests/
  test_normalize.py
  test_rules.py
  test_explain.py
  test_safety_language.py
app/
  streamlit_app.py
```

This structure keeps the safety engine testable before the interface becomes
complex.

## Core Data Model

The MVP should define these objects before adding UI complexity.

### MedicationInput

User-entered medication text.

Fields:

- `raw_text`
- `input_source`
- `user_notes`
- `created_at`

### NormalizedMedication

A matched medication candidate.

Fields:

- `input_text`
- `display_name`
- `normalized_name`
- `rxcui`
- `match_status`
- `match_confidence`
- `active_ingredients`
- `drug_classes`
- `source_ids`

### Ingredient

An active ingredient associated with one or more products.

Fields:

- `name`
- `ingredient_id`
- `source_ids`

### DrugClass

A therapeutic or pharmacologic class.

Fields:

- `name`
- `class_id`
- `class_source`
- `source_ids`

### SafetySignal

A review-worthy medication safety signal.

Fields:

- `signal_id`
- `signal_type`
- `review_priority`
- `medication_ids`
- `ingredient_ids`
- `plain_language_explanation`
- `professional_question`
- `source_ids`
- `rule_id`
- `data_version`
- `confidence`

### SourceReference

A source used to produce or explain a signal.

Fields:

- `source_id`
- `title`
- `publisher`
- `url`
- `retrieved_or_version_date`
- `source_type`

## Review Priority Model

Use review-priority labels instead of definitive safety labels.

Suggested labels:

- `urgent_review`: The user should seek immediate professional guidance or
  emergency help if symptoms or urgent conditions are present.
- `prompt_review`: The user should ask a pharmacist or clinician soon before
  making medication changes.
- `routine_review`: The user should discuss the item during a normal medication
  review.
- `information`: The item is useful context, not a safety signal by itself.
- `unknown`: The system could not verify the product or signal.

Avoid labels such as `safe`, `unsafe`, `approved`, or `contraindicated` unless a
future validated regulatory and clinical framework supports that usage.

## Phase 0: Product And Safety Foundation

Deliverables:

- Product requirements document.
- Intended-use statement.
- Safety boundary document.
- Initial regulatory assumptions.
- Privacy and data-handling assumptions.
- Safety language guide.

Exit criteria:

- The product can be described consistently as a consumer-first healthcare AI
  system.
- The system boundary avoids direct medication decisions.
- The MVP scope is narrow enough to test.

## Phase 1: Curated Knowledge Base

Deliverables:

- `data/demo/medications.json`
- `data/demo/interactions.json`
- `data/demo/sources.json`
- Data schema documentation.

Minimum data coverage:

- 20 to 50 common prescription or OTC products.
- A few combination products.
- Several known duplicate-ingredient examples.
- Several class-overlap examples.
- Several interaction examples with source references.
- Unknown-product test cases.

Exit criteria:

- Every medication record has active ingredients.
- Every safety signal can cite a source or rule.
- The dataset is small enough to manually review.

## Phase 2: Core Safety Engine

Deliverables:

- Medication normalization module.
- Knowledge lookup module.
- Duplicate ingredient rule.
- Therapeutic class overlap rule.
- Curated interaction rule.
- Safety signal model.
- Unit tests for each rule.

Exit criteria:

- The engine accepts a medication list and returns structured safety signals.
- Unknown and ambiguous matches are handled explicitly.
- Tests cover positive, negative, ambiguous, and edge cases.

## Phase 3: Consumer Explanation Layer

Deliverables:

- Plain-language explanation templates.
- Safety-language guardrails.
- Pharmacist question generator.
- Clinician summary generator.
- Tests for prohibited phrases and unsafe wording.

Exit criteria:

- Every signal includes a consumer-readable explanation.
- The language avoids direct start, stop, or change instructions.
- Every explanation preserves the source or rule behind the signal.

## Phase 4: Consumer Interface

Deliverables:

- Simple web interface.
- Medication list entry.
- Review results page.
- Signal detail view.
- Exportable pharmacist or clinician summary.
- Prominent product status and safety boundary copy.

Exit criteria:

- A consumer can complete the end-to-end workflow without reading developer
  instructions.
- The UI separates information, review signals, and unknown items.
- The user can bring a concise summary to a pharmacist or clinician.

## Phase 5: Evidence And Data Pipeline

Deliverables:

- RxNorm lookup experiment.
- RxClass lookup experiment.
- DailyMed source-linking experiment.
- Data freshness metadata.
- Source reliability notes.

Exit criteria:

- Public source integration is separated from curated demo data.
- Source versions and retrieval dates are captured.
- The system can fall back safely when external data is missing or ambiguous.

## Phase 6: Privacy, Security, And Audit

Deliverables:

- Local-only mode or no-PHI demo mode.
- Data retention policy.
- Audit log design.
- Access-control assumptions.
- Sensitive data handling notes.

Exit criteria:

- The project has a clear answer for what data is stored, where it is stored, and
  how it can be deleted.
- Any future cloud deployment has privacy and security requirements before
  implementation starts.

## Phase 7: Validation And Regulatory Readiness

Deliverables:

- Validation test set.
- Pharmacist or clinician adjudication plan.
- False negative and false positive analysis plan.
- Regulatory classification memo.
- Clinical evaluation plan.

Exit criteria:

- The team can distinguish a software demo from a clinically validated system.
- The intended use, users, claims, and outputs are documented.
- The validation plan tests both safety and consumer comprehension.

## Near-Term Build Order

The next concrete engineering steps should be:

1. Create the Python package structure.
2. Define data models.
3. Create the curated demo dataset.
4. Implement normalization against the curated dataset.
5. Implement duplicate ingredient detection.
6. Implement class overlap detection.
7. Implement curated interaction detection.
8. Implement explanation and question generation.
9. Add unit tests.
10. Add a simple Streamlit or FastAPI-based UI.

## Definition Of Done For The MVP

The MVP is done when:

- A user can enter at least three medications.
- The system returns normalized medication records where possible.
- Duplicate ingredient, class overlap, and curated interaction signals work.
- Unknown medications are displayed as unresolved review items.
- Every signal has a source or rule identifier.
- Every signal has a consumer-readable explanation.
- The output includes pharmacist or clinician questions.
- Unit tests cover the core rules.
- The README explains how to run the prototype.
- The product status clearly says the system is not yet clinically validated or
  cleared for real-world medication decisions.
