# MedCombo Research Claim Boundaries

## Purpose

This document translates the literature map into product claim boundaries for
MedCombo. It should be used before README updates, website copy, demos, grant
materials, research abstracts, or investor-facing descriptions.

## Claims Supported Now

### MedCombo helps consumers organize medication information for review.

Status: supported.

Evidence basis:

- Medication list discrepancies are common in patient-entered lists.
- RxNorm, DailyMed, and openFDA support structured drug identity and labeling
  work, with known limits.
- MedCombo currently preserves unknown and ambiguous entries instead of hiding
  them.

Allowed wording:

- "Helps organize medication information for pharmacist or clinician review."
- "Surfaces unresolved or ambiguous product names."
- "Records missing details such as strength, dose, frequency, and source."

Avoid:

- "Verifies a complete medication list."
- "Confirms the user's regimen."

### MedCombo surfaces review-worthy duplicate ingredient and interaction signals.

Status: partially supported for the curated demo dataset.

Evidence basis:

- OTC active-ingredient duplication, especially acetaminophen, is a known
  consumer safety issue.
- DDI alert literature supports the need for specificity, source linkage, and
  patient-specific context.
- Current MedCombo signals include rule IDs, source IDs, data version, and
  evidence metadata.

Allowed wording:

- "Surfaces review-worthy signals from the curated demo knowledge base."
- "Shows why a signal appeared and which source or rule was used."
- "Generates questions to bring to a pharmacist or clinician."

Avoid:

- "Detects all dangerous interactions."
- "Determines whether a combination is safe."
- "Provides clinical-grade DDI screening."

### MedCombo can support safer professional conversations.

Status: plausible but not validated.

Evidence basis:

- Medication reconciliation literature supports structured medication review.
- MedCombo produces professional-review questions and summary packets.
- No MedCombo-specific consumer or pharmacist validation has been completed.

Allowed wording:

- "Designed to help consumers prepare for medication review conversations."
- "Creates a shareable review summary."

Avoid:

- "Reduces medication errors."
- "Improves clinical outcomes."
- "Prevents adverse drug events."

## Claims Not Supported Yet

### Personalized clinical risk scoring

Do not claim that MedCombo estimates patient-specific risk based on age, weight,
conditions, symptoms, kidney function, pregnancy, or similar context. The current
system records context but does not validate personalized risk rules.

### Clinical validation

Do not claim clinical validation, FDA clearance, or demonstrated patient benefit.
DECIDE-AI and CONSORT-AI both point toward structured evaluation before claims
about clinical performance or benefit.

### Complete public-source DDI coverage

Do not imply that RxNorm, DailyMed, openFDA, or any single public source gives a
complete interaction knowledge base. Public source limitations and compendia
disagreement require curated evidence strategy.

### LLM safety reasoning

Do not claim that an LLM can determine medication safety. If LLMs are added,
their role should be limited to draft extraction or plain-language assistance
behind schema validation and user confirmation.

## Claim Review Checklist

Before publishing any external statement:

- Does the text say "review preparation" instead of "safety decision"?
- Does it mention curated demo data when referring to current signals?
- Does it avoid "safe", "all clear", "validated", and "clinical-grade"?
- Does it preserve the professional-review path?
- Does it avoid implying complete DDI or supplement coverage?
- Does it mention source limitations when describing evidence?
- Does it avoid storing or collecting health data claims before privacy work is
  implemented?

## Claim Status Table

| Claim | Status | Next evidence needed |
| --- | --- | --- |
| Organizes medication lists | Supported for MVP | Larger intake benchmark |
| Resolves known demo medications | Supported for demo data | RxNorm-backed normalization benchmark |
| Detects duplicate active ingredients | Supported for recognized products | Larger OTC combination product set |
| Surfaces curated interaction review signals | Supported for demo rules | Pharmacist-adjudicated interaction set |
| Helps users ask better questions | Plausible | Consumer comprehension study |
| Reduces medication errors | Not supported | Prospective clinical evaluation |
| Improves outcomes | Not supported | Controlled clinical study |
| Provides patient-specific safety assessment | Not supported | Validated clinical rule model and regulatory review |

## Recommended Product Position

MedCombo helps consumers prepare a safer medication review conversation by
organizing medication lists, preserving uncertainty, surfacing source-linked
review signals, and generating pharmacist or clinician questions.
