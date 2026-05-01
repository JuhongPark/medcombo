# MedCombo Initial Project Ideas

## Purpose

MedCombo is a healthcare AI system built for consumers. It helps people
understand medication combinations, identify review-worthy medication safety
signals, and prepare better conversations with pharmacists and clinicians.

The project is not framed as an education-only prototype. It is a consumer-first
healthcare AI product concept that should be developed with clinical safety,
traceability, regulatory awareness, and privacy protection from the beginning.

MedCombo should not make medication decisions for users. Its purpose is to help
people notice when professional review may be needed and understand what to ask.

## Refined Product Definition

MedCombo is a consumer-oriented healthcare AI system for medication safety
review.

- Category: healthcare AI system.
- Primary user: consumer or caregiver.
- Primary problem: medication confusion in everyday life.
- Primary output: understandable safety intelligence and professional-review
  prompts.
- Professional role: pharmacists and clinicians validate, advise, and act on
  medication decisions.
- Product boundary: MedCombo does not prescribe, diagnose, or independently
  determine whether a regimen is safe.

The main product experience should feel approachable to consumers, but the
underlying system should be built with healthcare-grade rigor.

## Consumer Problem

Consumers often manage medication information in fragmented, informal ways.
Common situations include:

- Taking prescriptions from more than one clinician.
- Adding over-the-counter medicines such as cold, pain, allergy, or sleep
  products.
- Taking supplements alongside prescription medications.
- Receiving combination drugs without realizing they contain multiple active
  ingredients.
- Seeing brand names and ingredient names as unrelated products.
- Not knowing which medication questions to ask a pharmacist or clinician.
- Forgetting dosage, timing, or context when discussing medication use.

These problems are not only information-retrieval problems. They are safety,
communication, and decision-support problems.

## Core Product Idea

MedCombo should convert a consumer's messy medication list into structured,
reviewable safety intelligence.

The system should:

1. Accept medication names, product labels, prescription lists, and informal user
   descriptions.
2. Normalize recognized products to reliable medication identifiers where
   possible.
3. Identify active ingredients and combination products.
4. Detect duplicated active ingredients.
5. Detect possible drug-drug interaction signals.
6. Detect therapeutic class overlap.
7. Consider limited user context when available, such as allergies, pregnancy,
   age, kidney or liver concerns, alcohol use, or driving risk.
8. Explain each signal in consumer language.
9. Provide questions and summaries for pharmacist or clinician review.

The system should communicate uncertainty clearly. Unknown or unverified inputs
should be treated as review needs, not silently ignored.

## Why This Is Healthcare AI

MedCombo is healthcare AI because it works with medication-related health data,
uses AI to structure and explain medication information, and supports medication
safety review workflows.

The AI role should be carefully scoped:

- Intake AI: parse typed text, OCR outputs, product photos, or prescription-list
  text into structured medication candidates.
- Matching AI: help resolve misspellings, aliases, brand names, and ambiguous
  products, while keeping confidence and alternatives visible.
- Explanation AI: translate technical safety signals into plain language.
- Conversation AI: generate pharmacist or clinician questions.
- Summarization AI: create concise medication review summaries.

Safety-critical signal generation should begin with deterministic rules,
validated knowledge sources, and source-linked evidence. AI-generated text should
not invent evidence, hide uncertainty, or produce direct medication instructions.

## Product Principles

MedCombo should follow these principles:

- Consumer first, healthcare grade.
- Explain signals, do not issue medication commands.
- Keep every safety signal traceable to a source, rule, or data version.
- Make uncertainty visible.
- Prefer a narrower reliable system over broad unsupported coverage.
- Design for professional review, not professional replacement.
- Protect health data as sensitive by default.
- Evaluate false negatives and false positives, not only user engagement.

## Initial MVP Scope

The first MVP should include:

- Manual medication list entry.
- Basic medication name normalization.
- Active ingredient lookup from a curated dataset.
- Duplicate active ingredient detection.
- Therapeutic class overlap detection.
- Basic interaction signal detection from a curated interaction dataset.
- Plain-language consumer explanations.
- Source references for each signal.
- Pharmacist or clinician question generation.
- A shareable medication review summary.
- Clear safety boundary language.

The MVP should avoid broad clinical claims. It should demonstrate the end-to-end
workflow with a small, well-tested medication set.

## Not In Scope For The First MVP

The first MVP should not:

- Tell users to start, stop, combine, or change medications.
- Tell users a medication combination is safe.
- Provide dosage adjustment recommendations.
- Diagnose conditions.
- Provide emergency medical advice.
- Handle all possible medications or supplements.
- Infer patient-specific safety without adequate context.
- Use AI-generated interaction claims without source grounding.
- Store identifiable health information unless privacy and security controls are
  in place.

## Safety Signal Model

MedCombo should treat safety findings as review signals, not clinical decisions.

Example signal types:

- Duplicate active ingredient.
- Possible interaction.
- Therapeutic class overlap.
- Allergy-related concern.
- Condition-related warning.
- Age, pregnancy, kidney, liver, alcohol, sedation, or driving-related caution.
- Unknown product or ambiguous match.

Each signal should include:

- Signal type.
- Review priority.
- Affected medications.
- Plain-language explanation.
- Source reference or rule identifier.
- Data version or review date.
- Recommended professional-review question.
- Confidence or ambiguity indicator where useful.

## Consumer Experience

The consumer experience should reduce anxiety while increasing clarity.

The app should say things like:

- "These two products may contain the same active ingredient."
- "This combination may need pharmacist review."
- "Bring this summary to your pharmacist or clinician before changing how you
  take these medications."
- "This product could not be matched confidently. Please verify the label or ask
  a pharmacist."

The app should avoid saying:

- "This is safe."
- "This is unsafe."
- "Stop taking this medication."
- "You can take these together."
- "No risk exists."

## Professional Bridge

MedCombo should make it easy for consumers to involve professionals.

Near-term bridge features:

- Pharmacist question list.
- Clinician visit summary.
- Medication list export.
- Source-linked review summary.
- Clear notation of unknown, ambiguous, or user-entered data.

Future professional-facing features:

- Pharmacist review dashboard.
- Clinician dashboard.
- Rule override and rationale logging.
- EHR or FHIR import and export.
- Medication reconciliation workflow support.
- Organization-level safety analytics.

## Data Direction

The first data strategy should use public sources for normalization and labeling,
plus curated prototype datasets for repeatable safety-rule testing.

Candidate sources:

- RxNorm for medication names, identifiers, and normalization.
- RxClass for therapeutic class relationships.
- DailyMed for structured labeling and product information.
- FDA labeling and safety communications where appropriate.
- Curated medication and interaction datasets for MVP development.
- Licensed clinical knowledge bases in later versions if public data coverage is
  not sufficient for clinical-grade interaction support.

Data-source evaluation criteria:

- Licensing and permitted use.
- Update frequency.
- Coverage of prescription, OTC, supplement, and combination products.
- Identifier quality.
- Evidence quality.
- Ability to preserve source references.
- Fitness for consumer-facing explanations.

## Technical Direction

The first architecture can be simple but should be shaped like a real healthcare
AI system.

Core components:

- Consumer UI for medication entry and review.
- Medication intake and parsing service.
- Normalization service.
- Structured medication knowledge base.
- Safety-rule engine.
- Explanation generator.
- Professional summary generator.
- Source and audit metadata store.
- Test suite for rules, explanations, and safety boundaries.

The system should keep AI outputs constrained. Structured outputs should use
schemas, and generated explanations should be grounded in known signal objects.

## Evaluation Ideas

Early evaluation should focus on safety and clarity.

- Medication normalization accuracy.
- Duplicate ingredient detection accuracy.
- Interaction signal coverage against a known reference set.
- Therapeutic overlap precision.
- False negative analysis for severe signals.
- False positive and alert burden analysis.
- Explanation correctness.
- Consumer comprehension.
- Source traceability.
- Professional usefulness of generated summaries.

The project should not treat a working demo as clinical validation.

## Roadmap

Near-term work:

- Finalize product requirements and intended-use language.
- Define the initial data model.
- Build a curated medication and interaction demo dataset.
- Implement medication input and normalization.
- Implement duplicate ingredient detection.
- Implement therapeutic class overlap detection.
- Implement basic interaction signal detection.
- Add source-linked explanations.
- Generate pharmacist and clinician question summaries.
- Add tests for all safety rules.
- Add privacy and data-governance notes.
- Update the README with usage instructions once code exists.

Future work:

- Add OCR-based label and prescription intake.
- Add medication bottle or package recognition support.
- Add limited user context such as allergies and kidney or liver concerns.
- Add stronger source ingestion pipelines.
- Add professional review workflows.
- Add FHIR-compatible import and export.
- Build validation datasets with pharmacist or clinician adjudication.
- Prepare a formal regulatory strategy.

## Status

MedCombo is in early product-definition and system-design work. The immediate
goal is to build a small, consumer-facing healthcare AI MVP that demonstrates
medication-combination review, traceable safety-signal detection, and
professional-review support.
