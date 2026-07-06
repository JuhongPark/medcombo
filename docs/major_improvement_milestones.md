# MedCombo Major Improvement Milestones

## Purpose

This plan records the next major product shift for MedCombo. The project should
move away from sounding like a broad consumer interaction checker and toward a
pharmacist-ready medication review preparation system.

The core product should not be "is this combination safe?" The core product
should be "what needs to be clarified, verified, and professionally reviewed?"

## Strategic Repositioning

Target position:

> MedCombo helps consumers and caregivers prepare a pharmacist-ready medication
> review packet by organizing medication lists, preserving uncertainty,
> surfacing limited source-linked review signals, and generating
> professional-review questions.

This position is more defensible than a consumer-facing medication safety
checker because it:

- treats uncertainty as a product feature
- keeps pharmacists and clinicians in the decision path
- reduces coverage illusion
- fits the current evidence base
- allows benchmark-first development
- avoids unsupported clinical outcome claims

## Product Principles

- Review preparation over medication decisions.
- Medication list quality before interaction coverage.
- Evidence records before broad rule expansion.
- Professional-review packet before consumer conclusions.
- Benchmark-first development before source ingestion.
- No-signal wording must never imply a complete safety screen.
- LLMs, if added, should parse or draft only behind schema validation and user
  confirmation.

## Milestone 1: Product Repositioning

Goal:

- Align README, UI copy, docs, and tests around review preparation rather than
  broad medication-combination safety checking.

Deliverables:

- README overview rewritten around medication review preparation.
- UI headings and helper text updated from "safety review" framing to
  "review packet" and "professional review" framing.
- Claim-boundary language cross-checked against
  `docs/research/medcombo_research_claims.md`.
- Tests that fail if user-facing copy implies a complete safety check.

Exit criteria:

- The product reads as a pharmacist-ready review packet builder.
- Public-facing text avoids unsupported "checker", "all clear", and
  clinical-grade language.

Suggested commit:

```text
docs: reposition product around review preparation
```

## Milestone 2: Structured Pharmacist Review Packet

Goal:

- Replace ad hoc summary assembly with a structured packet model designed for
  pharmacist or clinician review.

Deliverables:

- `medcombo/review_packet.py`.
- Packet dataclasses for sections and items.
- Packet builder from review result, intake items, conversation turns, and
  evidence signals.
- Summary string generator backed by the packet model.
- Web rendering based on packet sections.

Target sections:

1. Review Snapshot.
2. Verified Medication Items.
3. Needs Identity Confirmation.
4. Missing Dose, Frequency, Route, or Formulation.
5. Duplicate Active Ingredient Signals.
6. Curated Interaction Review Signals.
7. Supplements and Out-of-Scope Items.
8. Context To Ask About.
9. Pharmacist Questions.
10. Evidence Appendix.

Exit criteria:

- Every packet section is testable.
- Unknown and ambiguous items are visible review items.
- Evidence and source limitations are near the signals they support.
- Packet wording does not imply medication decisions.

Suggested commit:

```text
feat: add structured pharmacist review packet
```

## Milestone 3: Medication List Readiness

Goal:

- Add an intake completeness and review-readiness summary without creating a
  safety score.

Deliverables:

- `MedicationListReadiness` dataclass.
- Counts for verified, ambiguous, unknown, out-of-scope, missing fields, and
  source confidence.
- Readiness labels such as `needs_identity_review`, `missing_details`, and
  `ready_for_professional_review`.
- UI and packet display.

Non-goals:

- No safety score.
- No risk score.
- No "safe", "unsafe", or "all clear" status.

Exit criteria:

- Users can see what information is missing before professional review.
- Readiness never implies medication safety.

Suggested commit:

```text
feat: add medication list readiness summary
```

## Milestone 4: Pharmacist Feedback Loop

Goal:

- Turn the review packet into something that can be evaluated by pharmacists or
  medication safety reviewers.

Deliverables:

- `docs/research/pharmacist_review_rubric.md`.
- Packet evaluation criteria:
  - useful or not useful
  - misleading wording
  - missing clinical context
  - inappropriate priority
  - unclear source
  - follow-up question quality
- `data/benchmarks/pharmacist_packet_cases.json`.
- Tests for expected packet sections and professional-review questions.

Exit criteria:

- Reviewers can evaluate packet usefulness consistently.
- Packet fixtures capture expected sections and unsafe wording guardrails.

Suggested commit:

```text
test: add pharmacist packet review fixtures
```

## Milestone 5: Evidence Registry

Goal:

- Promote evidence from rule metadata to a first-class registry that governs
  whether a signal can be emitted.

Deliverables:

- `EvidenceRecord` and `EvidenceRegistry`.
- Evidence statuses:
  - `imported`
  - `curated`
  - `expert_reviewed`
  - `deprecated`
- Signal generation eligibility checks.
- Source freshness metadata.
- Reviewer note field.
- Tests that block user-facing signals from unreviewed or deprecated evidence.

Exit criteria:

- Interaction signals come from eligible evidence records.
- Deprecated or unreviewed evidence cannot silently create user-facing signals.

Suggested commit:

```text
feat: add evidence registry for review signals
```

## Milestone 6: Source Ingestion Experiments

Goal:

- Evaluate public source ingestion offline without mixing imported records into
  the curated demo knowledge base.

Deliverables:

- RxNorm normalization experiment.
- DailyMed label-linking experiment.
- openFDA labeling limitation memo or retrieval experiment.
- Benchmark comparison report.
- Source freshness and mapping-confidence tests.

Exit criteria:

- Imported records remain separate from `data/demo`.
- Source ingestion is measured against benchmark fixtures.
- Ambiguous and out-of-scope states remain visible.

Suggested commits:

```text
feat: add rxnorm normalization experiment
docs: document dailymed and openfda ingestion findings
```

## Milestone 7: No-PHI Hosted Demo Mode

Goal:

- Make the project demoable without inviting users to enter real medication or
  health information.

Deliverables:

- Sample-only mode.
- Synthetic examples.
- Health-context free text disabled or clearly marked in hosted mode.
- No raw medication input in logs by default.
- Documentation tied to `docs/research/privacy_data_inventory.md`.

Exit criteria:

- Hosted demo can run without collecting real medication lists.
- Privacy boundary is visible in the UI.

Suggested commit:

```text
feat: add no-phi hosted demo mode
```

## Success Criteria

MedCombo is meaningfully better when:

- a pharmacist can use the packet as a review starting point
- a consumer understands that MedCombo has not cleared the medication list
- unknown, ambiguous, and out-of-scope products are visible and actionable
- source and evidence limits are visible near review signals
- every new source or rule is measured against benchmark fixtures
- product copy matches the evidence and claim-boundary documents

## Recommended Next Sprint

Build these in order:

1. Product repositioning in README and UI.
2. Structured pharmacist review packet.
3. Medication list readiness summary.

This sprint changes the product from a demo safety checker into a review
preparation workflow.
