# Intake Agent Follow-Up Work

## Purpose

This document lists the next development work after the first deterministic
medication intake agent.

The current agent is a development-stage slot-filling state machine. It can
start a session, ask active clarification questions, accept one answer at a
time, update structured intake fields, and avoid re-asking answered questions.

The next work should turn that foundation into a usable multi-turn workflow
while keeping safety-critical reasoning deterministic and source-linked.

## Current Baseline

Implemented:

- Agent session and turn models.
- Deterministic active question generation.
- Answer handling for identity, information source, strength, dose, frequency,
  and formulation.
- Unknown or unsure answer handling.
- Browser-side answer submission for the next active question.
- Development-only in-memory multi-turn web session state.
- Updated intake quality panel after each answer.
- Conversation history display in the web demo.
- Review packet regeneration from the current agent session.
- Unit tests for core session behavior, scenario coverage, web rendering, and
  demo data integrity.

Not implemented yet:

- Persistent session storage.
- LLM-assisted parsing.
- OCR or image intake.
- Clinical validation.
- Production privacy, retention, and audit controls.

## Immediate Next Work

### 1. Multi-Turn Web UI

Status:

- Implemented for the local development demo with in-memory session storage.
- Not production-ready persistence, privacy handling, or hosted session
  management.

Goal:

- Let users answer one active question in the browser and see the intake state
  update.

Deliverables:

- Hidden session payload or development-only in-memory session store.
- Answer form for the next active question.
- Updated intake quality panel after each answer.
- Conversation history panel.
- Review packet regenerated from the current session.

Exit criteria:

- A user can disambiguate `metoprolol` by answering `succinate`.
- The item changes from `ambiguous_needs_selection` to `matched_by_name`.
- The same identity question is not asked again.

### 2. Agent Scenario Fixtures

Status:

- Initial scenario coverage is implemented in `tests/test_agent_scenarios.py`.
- Additional real-world fixture expansion is still recommended.

Goal:

- Make the agent testable against realistic medication intake conversations.

Deliverables:

- Fixture cases for exact matches, ambiguous names, unknown products, OTC
  combination products, missing dose, missing frequency, and unsure answers.
- Expected final intake state for each scenario.
- Regression tests for question order and unresolved review needs.

Exit criteria:

- Fixture tests pass with deterministic output.
- Failure diffs clearly show which slot or question changed.

### 3. Review Packet Upgrade

Status:

- Implemented for verified items, uncertain items, missing details, user answer
  history, and a consolidated professional-review checklist.
- Further pharmacist or clinician feedback is still needed before treating the
  packet as validated.

Goal:

- Make the final packet more useful for pharmacist or clinician review.

Deliverables:

- Separate sections for verified items, uncertain items, missing details, and
  user answers.
- Turn-history summary.
- Explicit "not yet verified" status for unresolved items.
- One consolidated professional-review checklist.

Exit criteria:

- The packet remains useful when several answers are unknown.
- No packet wording implies that the list is fully screened or safe.

### 4. LLM-Assisted Parsing Prototype

Goal:

- Use an LLM only to parse messy user text into draft fields, not to create
  safety signals.

Deliverables:

- Strict JSON schema for draft extraction.
- Validation layer that rejects unsupported fields.
- User confirmation requirement before extracted fields become verified.
- Safety-language checks on generated text.

Exit criteria:

- LLM output cannot directly create or suppress a safety signal.
- Every extracted medication field is marked as extracted, confirmed, or
  unresolved.

### 5. Source And Evidence Expansion

Goal:

- Prepare for non-demo medication data without losing traceability.

Deliverables:

- Normalization benchmark fixture set.
- Data-source comparison memo for RxNorm, DailyMed, openFDA extraction,
  licensed compendia, and expert-curated rules.
- Evidence schema for interaction pairs, clinical concern, source freshness,
  patient-specific modifiers, and review priority.

Exit criteria:

- The team can compare source options without changing product claims.
- Unknown, ambiguous, and out-of-scope items remain first-class states.

### 6. Safety And Human Factors Review

Goal:

- Check whether the agent reduces confusion without creating overreliance.

Deliverables:

- Consumer comprehension scenarios.
- Overreliance wording review.
- Anxiety-producing wording review.
- Pharmacist or clinician feedback checklist.

Exit criteria:

- Users understand that no signal is not no risk.
- Users understand that unknown answers should be brought to a professional.
- Reviewers can identify misleading or incomplete agent behavior.

### 7. Privacy And Operations

Goal:

- Avoid treating development intake data as production-ready health data.

Deliverables:

- Data inventory.
- Local-only versus hosted deployment decision.
- Retention policy.
- Deletion workflow.
- Access control and audit assumptions.
- Breach-response review item.

Exit criteria:

- No hosted demo uses identifiable health information without a privacy and
  security plan.

## Recommended Order

1. Normalization benchmark fixtures.
2. Source and evidence expansion.
3. LLM-assisted parsing prototype.
4. Safety and human factors review.
5. Privacy and operations plan.
6. Persistent session storage if the demo moves beyond local development.

## Development Rule

Until validation and regulatory review are stronger, the agent should remain a
review-preparation assistant. It should collect and clarify facts, preserve
uncertainty, and prepare professional-review questions. It should not issue
medication decisions.
