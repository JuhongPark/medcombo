# MedCombo Validation Plan From Literature

## Purpose

This plan turns the literature findings into validation work. It is not a
clinical validation report. It defines the evidence needed before MedCombo can
make stronger claims.

## Validation Principles

- Validate intake before validating safety output.
- Validate source coverage before expanding claims.
- Validate consumer comprehension before public deployment.
- Validate professional usefulness before professional workflow claims.
- Keep AI-generated parsing separate from deterministic safety signals.

## Stage 1: Offline Scenario Validation

Goal:

- Measure whether MedCombo preserves and structures consumer medication input
  without hiding uncertainty.

Dataset:

- 100 to 150 synthetic but realistic consumer-style inputs.
- Categories:
  - exact brand names
  - generic ingredients
  - OTC combination products
  - common abbreviations such as APAP
  - strength/dose/frequency embedded in text
  - misspellings
  - ambiguous names
  - supplements
  - unknown products
  - memory-entered partial descriptions

Metrics:

- match status accuracy
- correct medication ID when matched
- correct ambiguous candidate set
- unknown preservation rate
- extracted strength/dose/frequency accuracy
- inappropriate match rate

Exit criteria:

- No high-risk unknown product is silently matched to the wrong medication.
- Ambiguous entries remain ambiguous until user selection.
- Missing fields are visible in the review packet.

## Stage 2: Interaction Rule Review

Goal:

- Determine whether curated review signals are appropriate, explainable, and
  neither too strong nor too weak.

Reviewers:

- At least one pharmacist or medication safety expert for initial review.
- More reviewers before any clinical or public safety claim.

Materials:

- Interaction evidence records.
- Product combinations that should trigger signals.
- Product combinations that should not trigger a signal.
- Current plain-language explanation.
- Professional-review question.

Metrics:

- signal appropriateness
- explanation clarity
- review priority agreement
- missing patient-specific context
- false positive concern
- false negative concern

Exit criteria:

- Every interaction rule has evidence metadata.
- Every high-priority signal has a professional-review question.
- Reviewers can identify the rule and source behind each signal.
- No explanation implies that MedCombo has made a medication decision.

## Stage 3: Consumer Comprehension Study

Goal:

- Check whether users understand MedCombo's uncertainty and limits.

Test concepts:

- matched
- ambiguous
- unknown
- review-worthy signal
- no demo signal
- source limitation
- professional-review question

Tasks:

- Show users medication review packets.
- Ask what they think the system has and has not concluded.
- Ask whether they would stop, start, or change medication based on the output.
- Ask whether they know what to bring to a pharmacist or clinician.

Success criteria:

- Users understand that no signal does not mean no risk.
- Users understand unknown products need professional review.
- Users do not interpret review signals as medication instructions.
- Users can identify at least one question to ask a professional.

## Stage 4: Human Factors And Overreliance Review

Goal:

- Reduce overreliance, anxiety, and false reassurance.

Review areas:

- product status notice
- no-signal language
- interaction explanation wording
- source freshness display
- evidence metadata display
- emergency and urgent-care boundary
- summary export wording

Methods:

- Expert review.
- Moderated usability sessions.
- Error-case walkthroughs.
- Heuristic review against FDA transparency principles and NIST AI RMF.

Exit criteria:

- No page implies comprehensive safety clearance.
- No generated text tells users to start, stop, combine, or change medication.
- Source limitations are visible near results, not buried in docs.

## Stage 5: LLM-Assisted Intake Validation

Only begin this stage after deterministic intake and benchmark validation are
stronger.

Allowed role:

- Draft extraction of medication names and fields from messy text.
- Plain-language rewriting under safety-language checks.

Not allowed:

- Creating safety signals.
- Suppressing safety signals.
- Producing medication decisions.
- Marking extracted fields as verified without user confirmation.

Validation requirements:

- strict JSON schema
- rejected unsupported fields
- extracted versus confirmed state
- hallucination test cases
- regression tests against benchmark fixtures
- human-visible confidence and source trace

## Stage 6: Privacy And Operational Readiness

Before hosted deployment:

- data inventory
- no-PHI demo mode
- retention policy
- deletion workflow
- access-control assumptions
- audit log design
- breach-response process
- HIPAA, FTC Act, HBNR, FD&C Act, and state law review

Exit criteria:

- The project can answer what data is collected, where it is stored, how long it
  is retained, who can access it, and how a user can delete it.

## Minimum Evidence Before Stronger Claims

| Claim | Minimum evidence |
| --- | --- |
| "Helps organize medication lists" | Offline scenario validation plus consumer comprehension |
| "Improves medication review preparation" | Consumer study and pharmacist review of packets |
| "Detects duplicate active ingredients" | Expanded OTC benchmark and expert review |
| "Flags interaction concerns" | Pharmacist-adjudicated interaction set |
| "Reduces medication errors" | Prospective clinical evaluation |
| "Improves outcomes" | Controlled clinical study |

## Immediate Next Tasks

1. Expand normalization benchmark to at least 50 cases.
2. Add interaction scenario fixtures with expected signal IDs.
3. Draft pharmacist review rubric.
4. Draft consumer comprehension questions.
5. Add no-signal language tests for UI and summary.
6. Create a privacy data inventory before persistent sessions.
