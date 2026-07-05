# MedCombo

## Overview

MedCombo is a consumer-first healthcare AI system for medication-combination
safety review. It is designed to help people understand their medication lists,
identify review-worthy medication safety signals, and communicate more
effectively with pharmacists and clinicians.

The primary user is the consumer: a person who may not know whether a product
name is a brand, an active ingredient, a combination drug, an over-the-counter
medicine, or a supplement. MedCombo should turn that messy real-world input into
structured, source-linked safety intelligence.

MedCombo is not positioned as an education-only prototype. It is a healthcare AI
product concept in pre-market development. It is not yet clinically validated,
FDA-cleared, or intended to replace professional medical judgment.

## Product Thesis

Medication safety problems often begin before a person reaches a clinic or
pharmacy counter. People may combine prescriptions from multiple clinicians,
over-the-counter products, cold medicines, supplements, and combination drugs
without understanding duplicated ingredients, therapeutic overlap, or interaction
signals.

MedCombo starts from the idea that a healthcare AI system can help consumers
organize medication information, understand safety signals in plain language, and
prepare better questions for a pharmacist or clinician. The system should support
safer review behavior without telling users to start, stop, combine, or change
medications on their own.

## Intended Users

The first product experience is built for consumers and caregivers.

- People taking multiple prescription, over-the-counter, or supplement products.
- Caregivers helping a family member organize a medication list.
- Consumers preparing for a pharmacy visit, clinic visit, or medication review.
- People trying to understand whether two product names contain the same active
  ingredient.

Professional use is an important expansion path, not the starting point. Future
versions may support pharmacists, clinicians, medication safety teams, and care
navigation workflows through professional review dashboards, audit trails, and
EHR or FHIR integrations.

## Core Workflow

The intended consumer workflow is:

1. Enter medications, supplements, or product names by typing, uploading a photo,
   scanning a label, or importing a list.
2. Normalize names against reliable drug data when possible.
3. Resolve active ingredients, combination products, and therapeutic classes.
4. Detect review-worthy safety signals such as duplicate active ingredients,
   possible drug-drug interactions, therapeutic class overlap, allergy-related
   concerns, or context-sensitive warnings.
5. Explain each signal in plain language with source references.
6. Generate questions and a concise summary that the user can bring to a
   pharmacist or clinician.

## Safety Boundary

MedCombo should not:

- Prescribe medication.
- Diagnose a condition.
- Tell a user to start, stop, combine, or change a medication.
- Tell a user that a medication regimen is safe.
- Replace a pharmacist, physician, nurse, or other licensed professional.
- Provide emergency medical advice.
- Hide uncertainty or source limitations.

MedCombo should:

- Surface review-worthy signals.
- Explain why a signal appeared.
- Show sources and data freshness where available.
- Use cautious, consumer-readable language.
- Encourage professional review before medication decisions.
- Escalate urgent warning patterns to appropriate emergency or professional care
  language.

## Initial AI System Capabilities

The first MVP should prioritize a narrow but serious healthcare AI workflow:

- Consumer medication list intake.
- Medication name normalization.
- Active ingredient resolution.
- Duplicate active ingredient detection.
- Basic drug-drug interaction signal detection.
- Therapeutic class overlap detection.
- Consumer-readable explanation generation.
- Pharmacist or clinician question generation.
- Shareable medication review summary.
- Source, rule, and data-version traceability for every safety signal.

AI should be used first for intake, structuring, language simplification, and
explanation. Safety-critical signal generation should rely on deterministic
rules, validated knowledge sources, and traceable evidence before using
predictive models.

## Data And Knowledge Strategy

The system should start with public, well-documented sources and a curated
prototype knowledge base.

- [RxNorm](https://www.nlm.nih.gov/research/umls/rxnorm/) for normalized drug
  names and identifiers.
- [RxClass](https://lhncbc.nlm.nih.gov/RxNav/APIs/RxClassAPIs.html) for drug
  class relationships.
- [DailyMed](https://dailymed.nlm.nih.gov/dailymed/) for structured product
  labeling and source-linked drug information.
- FDA labeling and safety communications where appropriate.
- Curated interaction and safety-rule datasets created for repeatable
  development and validation.

Public adverse-event datasets can support exploratory analysis, but they should
not be treated as proof that one medication caused a specific outcome. Real
clinical-grade interaction coverage may eventually require licensed commercial
knowledge bases or expert-curated content.

## Architecture Direction

MedCombo should be designed as a healthcare AI system with a consumer UX:

- Consumer interface for medication entry and review.
- AI intake layer for OCR, natural language parsing, and product-name cleanup.
- Medication normalization service.
- Knowledge graph or structured knowledge layer for ingredients, classes,
  interactions, warnings, and source metadata.
- Safety reasoning layer based on traceable rules and validated knowledge.
- Explanation layer that translates signals into consumer-readable language.
- Professional bridge for pharmacist or clinician summaries.
- Privacy, security, audit, and data-governance layer.

## Regulatory And Privacy Posture

Because MedCombo handles medication safety and consumer health information, it
must be developed with regulatory and privacy review from the beginning.

Relevant U.S. reference points include:

- FDA guidance on
  [Clinical Decision Support Software](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-decision-support-software).
- FDA guidance on
  [General Wellness: Policy for Low Risk Devices](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/general-wellness-policy-low-risk-devices).
- The FTC, HHS, and FDA
  [Mobile Health Apps Interactive Tool](https://www.ftc.gov/business-guidance/resources/mobile-health-apps-interactive-tool).

This repository does not make a final regulatory classification. The intended
use, claims, risk level, users, outputs, and clinical validation plan must be
reviewed before any real-world deployment.

## Development Roadmap

Near-term development should proceed in this order:

1. Define product requirements and safety boundaries.
2. Create a small curated medication knowledge base for repeatable testing.
3. Implement medication intake and normalization.
4. Implement duplicate ingredient and therapeutic overlap checks.
5. Add basic interaction signals with source-linked explanations.
6. Build a consumer-facing review interface.
7. Generate pharmacist or clinician question summaries.
8. Add tests for normalization, rules, explanations, and safety language.
9. Add privacy, audit, and data-version tracking.
10. Prepare validation and regulatory strategy documentation.

See [docs/development_plan.md](docs/development_plan.md) for the working
development plan.

## Run The MVP

The current MVP is dependency-free and uses the Python standard library.

The form requires at least one medication or product name. It also accepts
supplements, demographic information, body information, chronic conditions, and
current symptoms. Each non-medication section can be marked as no information
when the user does not have or does not want to provide that context.

After the first review, the guided clarification panel can ask targeted
follow-up questions about product identity, information source, strength, dose,
frequency, and formulation. The local demo keeps this multi-turn intake state in
process memory so answers can update the intake quality panel and regenerate the
review packet.

Sensitive personal information requires separate privacy, security, consent,
retention, and compliance handling before real deployment. In this development
environment, all entered data is used for development and demo processing.

Run tests:

```bash
python -m unittest discover
```

Start the local web demo:

```bash
python -m app.web_app --port 8010
```

Then open:

```text
http://127.0.0.1:8010
```

The demo starts with this sample list:

```text
Tylenol
NyQuil
Zoloft
```

That sample is intended to exercise duplicate-ingredient, interaction, and
therapeutic-overlap review signals against the curated demo knowledge base.
For guided clarification, try entering `metoprolol` and answering `succinate`
when the demo asks which product is intended.

## Current Implementation

The first implementation includes:

- A curated demo knowledge base in `data/demo/`.
- Core data models in `medcombo/models.py`.
- Medication normalization in `medcombo/normalize.py`.
- Traceable review rules in `medcombo/rules.py`.
- Additional intake fields for supplements, demographics, body information,
  chronic conditions, and current symptoms.
- A development-stage guided intake agent for deterministic follow-up questions.
- Consumer summary generation in `medcombo/summary.py`.
- Safety-language checks in `medcombo/safety_language.py`.
- A dependency-free multi-turn web demo in `app/web_app.py`.
- Unit tests and demo data integrity checks in `tests/`.
- GitHub Actions unit-test CI in `.github/workflows/test.yml`.

The demo data is not a clinical-grade medication knowledge base. It exists to
make the review workflow testable while the system architecture is developed.

## Current Status

MedCombo is in the early MVP implementation stage. The current system can run a
minimal consumer-facing medication review workflow backed by a curated, testable
knowledge base and a traceable safety-rule engine.
