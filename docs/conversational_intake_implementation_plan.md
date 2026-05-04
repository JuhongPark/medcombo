# Conversational Intake Implementation Plan

## Goal

Implement MedCombo's next phase as a guided medication-intake and review packet
workflow.

The implementation should make uncertainty visible before adding broader
interaction coverage. It should ask users for missing or ambiguous medication
details, then produce structured review guidance for a pharmacist or clinician.

## Scope

In scope:

- Medication intake item state.
- Missing-field detection.
- Confidence and verification status labels.
- Deterministic follow-up question generation.
- Chat-style clarification display.
- Review packet sections for verified, uncertain, and missing information.
- Tests for intake state and follow-up question behavior.

Out of scope for this phase:

- Real clinical validation.
- FDA/regulatory classification resolution.
- Live RxNorm, NDC, pharmacy, EHR, or OCR integration.
- LLM-generated safety signals.
- LLM extraction of pasted text.
- Storing identifiable health information.

## Implementation Sequence

### Step 1: Intake Models

Add structured models for medication intake and conversational prompts.

Expected objects:

- `MedicationIntakeItem`
- `ConversationQuestion`

Each intake item should preserve:

- Raw user text.
- Source type.
- Source confidence.
- Normalized medication candidate.
- Match status.
- Verification status.
- Missing fields.
- Professional-review questions.

### Step 2: Intake Builder

Create an intake module that converts raw medication lines into intake items.

Expected behavior:

- Matched products receive `matched_by_name`.
- Ambiguous products receive `ambiguous_needs_selection`.
- Unknown products receive `unknown_product`.
- Inputs without strength, dose, frequency, or formulation are marked with
  missing fields.
- Low-confidence items remain visible.

### Step 3: Deterministic Question Generator

Generate follow-up questions from intake state without using an LLM.

Question types:

- `identify_unknown_product`
- `select_ambiguous_product`
- `confirm_information_source`
- `confirm_strength`
- `confirm_dose`
- `confirm_frequency`
- `confirm_formulation`

Rules:

- Ask about unknown or ambiguous identity before dose details.
- Ask for information source when the source is memory or generic manual entry.
- Ask only one field per question.
- Let unresolved items become professional-review questions.

### Step 4: Review Packet

Extend the summary layer to include intake quality.

Sections:

- Medication entries.
- Intake quality and missing information.
- Uncertain items.
- Review-worthy signals.
- Pharmacist or clinician questions.
- Source references.

### Step 5: Web Demo Update

Update the dependency-free web demo.

UI changes:

- Rename the primary workflow around medication intake and review preparation.
- Show confidence states in normalized medication cards.
- Add a chat-style clarification section.
- Add a "conversation starter" panel with follow-up questions.
- Keep all safety boundary language visible.

### Step 6: Tests

Add focused tests.

Minimum coverage:

- Matched medication creates an intake item.
- Unknown product creates an unknown verification state and identity question.
- Ambiguous medication creates candidate-selection question.
- Missing strength, dose, frequency, and formulation are detected.
- Review packet includes missing information and follow-up questions.
- Existing rule and summary tests continue to pass.

## Acceptance Criteria

- Running `python -m unittest discover` passes.
- The default demo flow still shows Tylenol, NyQuil, and Zoloft review signals.
- Unknown and ambiguous items are visible as review needs.
- The app shows at least one chat-style follow-up prompt after review.
- No result screen implies that the medication list is safe or fully screened.
- LLMs are not required for this implementation.

## Next Phase After This Plan

After this phase, the next development increment should add one of:

- Pasted pharmacy-list parsing into draft intake items.
- User-confirmed answers that update intake state across turns.
- OCR or label-photo intake prototype.
- Normalization benchmark fixture set.
- Licensed or curated DDI source evaluation.
