# Conversational Medication Intake Plan

## Product Direction

MedCombo should first become a consumer medication-intake and review-preparation
assistant.

The near-term product should help users provide better medication information,
identify missing or uncertain details, surface first-pass review signals, and
prepare questions for a pharmacist or clinician. It should not independently
decide whether a medication combination is safe or tell users to start, stop, or
change medication use.

## Strategy

Use a two-layer product strategy.

### Layer 1: Intake-Based Review Advice

The first product layer receives medication information and returns structured
review guidance.

Core behavior:

- Accept messy consumer inputs such as typed names, copied pharmacy lists, OTC
  product names, supplements, and notes from memory.
- Normalize recognized products to known medication candidates when possible.
- Mark unknown, ambiguous, and incomplete products as review needs.
- Display missing details such as strength, dose, route, frequency, last dose,
  formulation, and source of the information.
- Run deterministic first-pass screening only on sufficiently identified items.
- Generate professional-review questions instead of medication commands.
- Export a medication review packet for a pharmacist or clinician.

Primary output:

- Verified or likely medication candidates.
- Missing information checklist.
- Unknown or ambiguous product list.
- Duplicate ingredient signals.
- Curated interaction signals.
- Therapeutic class overlap signals.
- Questions for pharmacist or clinician review.
- Clear limitation language.

Safety boundary:

- Say "review signal", "possible concern", or "needs verification".
- Do not say "safe", "unsafe", "all clear", "contraindicated", or "do not
  take" unless a future validated clinical and regulatory framework supports
  that usage.
- For potential emergency or overdose scenarios, route users to urgent medical
  help or poison control instead of attempting app-based resolution.

### Layer 2: Conversational Clarification

The second product layer should make intake conversational. The goal is not to
make the assistant more medically authoritative. The goal is to reduce the
burden on ordinary users by asking one missing-detail question at a time.

Core behavior:

- Ask targeted follow-up questions when a medication entry is incomplete.
- Ask disambiguation questions when multiple products match.
- Ask memory-triggering questions for OTC drugs, vitamins, supplements,
  inhalers, creams, eye drops, patches, and as-needed products.
- Ask how the user knows the information: bottle label, pharmacy list, medical
  visit summary, photo, caregiver memory, or personal memory.
- Preserve the user's original wording next to the normalized candidate.
- Let users answer "I do not know" without blocking the workflow.
- Convert unknown answers into professional-review questions.
- Stop asking once the remaining uncertainty is better handled by a pharmacist
  or clinician.

Example dialogue goals:

- "Is this metoprolol succinate or metoprolol tartrate?"
- "Does the label say extended release, ER, XR, XL, or CD?"
- "How many milligrams are listed on the bottle?"
- "How often do you take it?"
- "Are you also taking any cold, sleep, allergy, pain, or stomach medicines?"
- "Did you copy this from a label, a pharmacy list, or memory?"
- "Would you like this item marked as unsure for pharmacist review?"

## User Workflow

1. User starts with a medication list, a pharmacy list, product labels, or typed
   names.
2. MedCombo creates a draft medication list with confidence states.
3. The conversational intake asks only for missing or ambiguous details.
4. Each item receives a verification status.
5. The deterministic review engine runs on identified items.
6. The system generates review signals and missing-information warnings.
7. The user receives a medication review packet for a pharmacist or clinician.

## Confidence States

Every medication item should have a visible confidence state.

Suggested states:

- `verified_from_label`
- `verified_from_pharmacy_list`
- `matched_by_name`
- `matched_with_user_confirmation`
- `ambiguous_needs_selection`
- `unknown_product`
- `missing_strength`
- `missing_dose`
- `missing_frequency`
- `memory_entered`
- `supplement_or_out_of_scope`

The review engine should use these states when explaining result confidence.
Low-confidence items should not be silently ignored.

## Data Model Additions

Add or extend a medication-intake model with these fields.

### MedicationIntakeItem

- `raw_text`
- `source_type`
- `source_confidence`
- `candidate_medications`
- `selected_medication_id`
- `match_status`
- `verification_status`
- `strength`
- `dose`
- `route`
- `frequency`
- `formulation`
- `last_dose_taken`
- `actual_use_notes`
- `missing_fields`
- `professional_review_questions`

### ConversationTurn

- `turn_id`
- `item_id`
- `question_type`
- `question_text`
- `user_answer`
- `extracted_fields`
- `remaining_uncertainty`
- `created_at`

## Conversation Policy

The conversational system should follow strict rules.

- Ask for facts, not clinical decisions.
- Prefer one question per turn.
- Show uncertainty instead of hiding it.
- Keep the user's exact wording.
- Never invent medication identity, dose, frequency, or interaction evidence.
- Confirm before replacing a user's medication entry with a normalized product.
- Turn unknown answers into review questions.
- Use deterministic rules for safety signals.
- Use LLMs only for intake parsing, question selection, summarization, and plain
  language drafting under safety-language checks.

## First Build Milestones

### Milestone 1: Intake Item State

Deliverables:

- Intake item model.
- Verification status labels.
- Missing-field detection.
- UI display for raw text, candidate match, and confidence state.

Exit criteria:

- Unknown and ambiguous inputs are visible.
- Missing strength, dose, frequency, and formulation are visible.
- No item is treated as safely screened unless it has enough identity.

### Milestone 2: Deterministic Follow-Up Questions

Deliverables:

- Rule-based question generator.
- Question types for missing strength, dose, frequency, formulation, OTC status,
  supplement status, and source confidence.
- Tests for common missing-field scenarios.

Exit criteria:

- The system can ask useful follow-up questions without an LLM.
- A user can answer "I do not know" and still receive a review packet.

### Milestone 3: Conversational Intake Loop

Deliverables:

- Chat-style intake flow.
- Per-item question queue.
- Conversation history.
- Stop conditions for uncertainty that requires professional review.

Exit criteria:

- The app can guide users through medication clarification one item at a time.
- The conversation produces structured medication-intake data.

### Milestone 4: Review Packet

Deliverables:

- Consumer-facing medication review packet.
- Section for verified medications.
- Section for uncertain medications.
- Section for missing information.
- Section for review signals.
- Section for pharmacist or clinician questions.

Exit criteria:

- The packet is useful even when many details are unknown.
- The packet does not imply that no signal means no risk.

### Milestone 5: LLM-Assisted Intake

Deliverables:

- LLM parser for pasted text or messy descriptions.
- Deterministic schema validation after parsing.
- Safety-language check for generated summaries.
- Human-visible confidence and source trace.

Exit criteria:

- LLM output never directly creates a safety signal.
- Parsed fields are marked as extracted or user-confirmed.
- Users can correct every extracted field.

## Research Support

The research supports this direction, but with different confidence levels.

| Claim | Evidence | Confidence | Product Implication |
| --- | --- | --- | --- |
| Medication reconciliation is inherently a process of obtaining, verifying, documenting, and comparing medication information. | AHRQ MATCH Toolkit describes medication reconciliation as a complex process that obtains and verifies prescription drugs, OTC drugs, vitamins, supplements, herbals, and dosing information. | high | MedCombo should focus first on intake and verification, not only interaction alerts. |
| Patient interviews should use probing questions to trigger memory and collect medication details. | AHRQ interview tips recommend asking about prescriptions, OTC drugs, vitamins, herbals, supplements, inhalers, and full dosing details such as name, strength, formulation, dose, route, frequency, and last dose. | high | A conversational interface maps well to the real medication-history interview pattern. |
| Patient-entered medication lists are often incomplete or discrepant. | Meyer et al. found only 36.3% of patient-completed lists matched pharmacy-prescribed drugs. Lee et al. found 56% of evaluated personal medication lists incomplete and 94% with at least one discrepancy. | high | The product should assume incomplete input and design for clarification. |
| Electronic tools can reduce medication discrepancies, especially omissions, but evidence is heterogeneous. | Mekonnen et al. systematic review and meta-analysis found electronic medication reconciliation reduced omission errors, while other outcomes were less consistent. | medium | Build electronic intake support, but validate it locally instead of assuming clinical benefit. |
| Patient portal medication reconciliation can engage patients and save clinician time in some settings. | Ebbens et al. randomized noninferiority study found portal reconciliation noninferior to pharmacy technician reconciliation on discrepancies and saved time in a preoperative setting. | medium | Patient-facing intake can be viable, but implementation should account for user characteristics and setting. |
| A conversational AI medication reconciliation agent is technically plausible. | A 2025 medRxiv preprint describes AMREC, a conversational agent that verifies, corrects, removes, and adds medications through dialogue. This is preprint and company-affiliated evidence. | low to medium | Conversational intake is promising, but MedCombo should start with deterministic question flows and treat LLM assistance as later-stage. |

## Reference Sources

- AHRQ MATCH Toolkit:
  https://www.ahrq.gov/patient-safety/settings/hospital/match/index.html
- AHRQ tips for conducting a patient medication interview:
  https://www.ahrq.gov/patient-safety/settings/hospital/match/figure-9.html
- Meyer et al., 2012, patient-completed medication reconciliation forms:
  https://pubmed.ncbi.nlm.nih.gov/21855261/
- Lee et al., 2014, self-reported personal medication lists:
  https://pubmed.ncbi.nlm.nih.gov/24259649/
- Mekonnen et al., 2016, electronic medication reconciliation systematic review:
  https://bmcmedinformdecismak.biomedcentral.com/articles/10.1186/s12911-016-0353-9
- Ebbens et al., 2021, patient portal medication reconciliation:
  https://pubmed.ncbi.nlm.nih.gov/33905738/
- Deo et al., 2025, conversational AI medication reconciliation preprint:
  https://www.medrxiv.org/content/10.1101/2025.06.16.25329719v1

## Product Decision

Proceed with a conversational medication-intake strategy.

The first useful version should not try to maximize the number of detected
interactions. It should maximize the quality, transparency, and reviewability of
the medication list. First-pass screening should be included, but it should be
secondary to accurate intake and professional-review preparation.
