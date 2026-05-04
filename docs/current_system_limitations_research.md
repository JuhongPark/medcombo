# Research Run: Current System Limitations

## Summary

This research run evaluates the current MedCombo MVP as of May 3, 2026. The
system is best described as a traceable medication-review prototype, not a
clinical-grade medication safety system. Its strongest design choice is the
explicit safety boundary: it surfaces review-worthy signals and avoids direct
medication commands. Its largest risk is that a clean consumer workflow could
make a very small, unvalidated rule and data layer appear more complete than it
is.

The current evidence supports keeping MedCombo narrow, source-linked, and
professional-review oriented while building a validation and data-source plan
before stronger safety claims or real-user deployment.

## Decision Supported

Use this research to decide whether the next phase should focus on feature
expansion or risk reduction. Recommendation: prioritize risk reduction through
claim control, data-source evaluation, normalization benchmarks, interaction
rule validation, consumer input verification, and privacy/regulatory review.

## Current System Snapshot

- Date: 2026-05-03.
- Commit: `b9f65ba`.
- Working tree: `docs/research_plan_template.md` was already untracked before
  this research output was created.
- Demo data version: `demo-2026-05-01`.
- Demo data size: 34 medications, 29 ingredients, 20 drug classes, 10
  interactions, 4 sources.
- Tests: `python -m unittest discover` ran 18 tests successfully.
- Relevant code:
  - `medcombo/knowledge.py` loads only `data/demo`.
  - `medcombo/normalize.py` uses demo aliases and `difflib.get_close_matches`.
  - `medcombo/rules.py` emits unknown, ambiguous, duplicate ingredient,
    therapeutic class overlap, curated interaction, and context-recorded
    signals.
  - `medcombo/safety_language.py` blocks a small set of prohibited phrases.
  - `medcombo/summary.py` includes the important warning that no generated
    signal does not mean no risk.
- Observable sample checks:
  - `Tylenol`, `NyQuil`, `Zoloft` generated 3 signals:
    duplicate active ingredient, possible interaction, and class overlap.
  - `Unlisted Herb`, `Metoprolol` generated unknown and ambiguous product
    signals.
  - `Lisinopril` plus age, kidney disease, and dizziness generated only an
    informational health-context signal, not personalized clinical risk scoring.

## Findings

| Finding | Evidence | Risk | Confidence | Implication |
| --- | --- | --- | --- | --- |
| MedCombo is currently a demo-data prototype, not clinical-grade coverage. | Local demo data has 34 medications and 10 interactions. README states it is not clinically validated or FDA-cleared and that demo data is not clinical-grade. | high | high | Product claims must stay at "review signal prototype" level. |
| Medication normalization is limited to curated aliases and fuzzy matching. | `normalize.py` uses `alias_index` and `get_close_matches`; no live RxNorm, NDC, dose, route, strength, image, OCR, or label parsing is implemented. RxNorm itself excludes dietary supplements and other categories. | high | high | Build a normalization benchmark and source strategy before expanding inputs. |
| Public data alone is unlikely to provide complete DDI coverage. | RxNav announced removal of its Drug-Drug Interaction API. Literature reports no single complete public PDDI source and low agreement among DDI compendia. | high | high | Treat DDI as a curated evidence product, not a simple API lookup. |
| Current interaction rules lack patient-specific context. | `rules.py` records health context but explicitly says the MVP does not use it for personalized clinical risk scoring. DDI alert literature identifies missing patient-specific characteristics as a false-positive driver. | high | high | Do not add stronger interaction claims until context requirements are defined. |
| Consumer-entered medication lists are a primary failure point. | Patient-completed lists often omit or add medications. One study found only 36.3% made no errors compared with pharmacy lists. Another found 56% incomplete personal lists and 94% with at least one discrepancy. | high | high | Intake should ask for labels, bottles, dose, frequency, formulation, and confidence. |
| OTC combination products need special handling. | FDA says acetaminophen appears in hundreds of OTC and prescription drugs and warns against using more than one acetaminophen-containing product at a time. Current MedCombo can detect duplicate acetaminophen only when both products are recognized in demo data. | high | high | Duplicate-ingredient checks should become a first-class benchmark area. |
| AI-generated explanations would require controls beyond the current regex. | Current text is deterministic and checked against a small prohibited-phrase list. DECIDE-AI, CONSORT-AI, FDA transparency principles, and NIST AI RMF all point toward human factors, input/output handling, error analysis, and transparent limitations. | medium | high | Keep safety-critical signal generation deterministic until an AI validation protocol exists. |
| Regulatory and privacy posture is not production-ready. | FDA 2026 CDS guidance applies digital health policy to functions that meet device definitions, including patient or caregiver functions. HHS and FTC health app guidance point to HIPAA, FTC Act, HBNR, FD&C Act, COPPA, and information blocking analysis. | high | high | Complete intended-use, claim, data inventory, retention, consent, and breach-response reviews before real deployment. |

## Evidence Notes

### Local System Evidence

- README positions MedCombo as a consumer-first healthcare AI system, but says
  it is not clinically validated, FDA-cleared, or a replacement for professional
  judgment.
- README states that real clinical-grade interaction coverage may eventually
  require licensed commercial knowledge bases or expert-curated content.
- The current knowledge base is loaded from `data/demo` and has no live update
  path.
- The current rule engine has useful traceability: every signal has a
  `rule_id`, `data_version`, source IDs, priority, explanation, and professional
  question.
- The current system already avoids a dangerous "all clear" claim in generated
  summaries: "No demo-dataset safety signals were generated. This does not mean
  the medication list has no risk."

### Regulatory And Public-Source Evidence

- FDA Clinical Decision Support Software guidance, January 2026:
  https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-decision-support-software
  - FDA says the guidance clarifies non-device CDS criteria and that digital
    health policies still apply to device software functions, including patient
    or caregiver functions.
- FDA General Wellness guidance, January 2026:
  https://www.fda.gov/regulatory-information/search-fda-guidance-documents/general-wellness-policy-low-risk-devices
  - Software for maintaining or encouraging a healthy lifestyle unrelated to
    diagnosis, cure, mitigation, prevention, or treatment of disease is outside
    the device definition. MedCombo's medication safety review is not obviously
    in this wellness-only lane.
- RxNorm Overview:
  https://www.nlm.nih.gov/research/umls/rxnorm/overview.html
  - RxNorm supports normalized names and identifiers for prescription and many
    OTC drugs in the United States. It excludes dietary supplements,
    homeopathics, medical devices, foods, and other categories.
  - RxNorm reports that only about 60% of source vocabulary drug names receive
    normalized names, with others out of scope or ambiguous.
- RxNav:
  https://lhncbc.nlm.nih.gov/RxNav/
  - RxNav APIs are updated monthly with RxNorm releases. RxNav announced that
    the Drug-Drug Interaction API would be discontinued on or about January 2,
    2024.
- DailyMed:
  https://dailymed-beta.nlm.nih.gov/dailymed/about-dailymed.cfm
  - DailyMed contains FDA-submitted labeling for approved prescription and OTC
    products and additional regulated products. It is useful for source-linked
    labeling, but it is not the same as a ready-made interaction reasoning
    engine.
- FDA Acetaminophen information:
  https://www.fda.gov/drugs/information-drug-class/acetaminophen-information
  - FDA states that acetaminophen is found in hundreds of OTC and prescription
    drugs and warns consumers not to use more than one acetaminophen-containing
    product at a time.

### Literature Evidence

- Van De Sijpe et al., "Overall performance of a drug-drug interaction clinical
  decision support system," BMC Medical Informatics and Decision Making, 2022:
  https://link.springer.com/article/10.1186/s12911-022-01783-z
  - The study found 38,409 very severe DDI alerts, 88.2% overridden, and
    false positives linked to broad screening windows and missing
    patient-specific characteristics.
- Felisberto et al., "Override rate of drug-drug interaction alerts in clinical
  decision support systems," 2024:
  https://journals.sagepub.com/doi/10.1177/14604582241263242
  - Systematic review and meta-analysis reporting high DDI alert override
    rates. This supports treating alert specificity and trust as core product
    requirements.
- Abarca et al., "Concordance of severity ratings provided in four drug
  interaction compendia," 2004:
  https://pubmed.ncbi.nlm.nih.gov/15098847/
  - Found low agreement among major DDI compendia. Only 9 of 406 major DDIs
    were listed in all four compendia.
- Ayvaz et al., "Toward a complete dataset of drug-drug interaction information
  from publicly available sources," Journal of Biomedical Informatics, 2015:
  https://pubmed.ncbi.nlm.nih.gov/25917055/
  - Reports that no single complete public source of potential DDI information
    exists.
- Meyer et al., "How reliable are patient-completed medication reconciliation
  forms compared with pharmacy lists?", American Journal of Emergency Medicine,
  2012:
  https://pubmed.ncbi.nlm.nih.gov/21855261/
  - In 315 patients, 33% had omission errors, 12.7% addition errors, 18.1% both,
    and 36.3% no errors.
- Lee et al., "Predictors of completeness of patients' self-reported personal
  medication lists and discrepancies with clinic medication lists," Annals of
  Pharmacotherapy, 2014:
  https://pubmed.ncbi.nlm.nih.gov/24259649/
  - Among evaluated personal medication lists, 56% were incomplete and 94% had
    at least one discrepancy with clinic lists.
- King et al., "Developing consumer-centered, nonprescription drug labeling: a
  study in acetaminophen," American Journal of Preventive Medicine, 2011:
  https://pubmed.ncbi.nlm.nih.gov/21565649/
  - Reports acetaminophen overdose as a major consumer safety issue and shows
    limited consumer awareness of active ingredients.
- DECIDE-AI:
  https://www.nature.com/articles/s41591-022-01772-9
  - Notes that many AI-based decision support systems show promising in silico
    performance but few have demonstrated real patient-care benefit, and
    emphasizes early clinical performance, safety, and human factors.
- CONSORT-AI:
  https://www.nature.com/articles/s41591-020-1034-x
  - Recommends clear reporting of AI intervention instructions, integration
    setting, input/output handling, human-AI interaction, and error cases.
- FDA Transparency for Machine Learning-Enabled Medical Devices:
  https://www.fda.gov/medical-devices/software-medical-device-samd/transparency-machine-learning-enabled-medical-devices-guiding-principles
  - Emphasizes audience-specific information, human-centered design, workflow
    timing, known limitations, and ongoing monitoring.
- NIST AI Risk Management Framework:
  https://www.nist.gov/itl/ai-risk-management-framework
  - Provides a voluntary framework to incorporate trustworthiness into AI
    design, development, use, and evaluation.

## Product Implications

- Keep the primary claim as "helps consumers organize medication information and
  prepare review questions" rather than "checks whether combinations are safe."
- Make the phrase "demo dataset" highly visible anywhere a result could be read
  as complete safety screening.
- Strengthen no-signal wording in UI and exports. The summary already includes
  good caution language; the main UI should match that level of caution.
- Treat unknown and ambiguous products as review needs, not as failed UX states.
- Add explicit prompts for dose, strength, route, frequency, timing, and whether
  the user copied from a bottle, label, pharmacy list, memory, or photo.
- Keep professional-review questions as a first-class output.

## Engineering Implications

- Add a data-source abstraction before expanding beyond `data/demo`.
- Add a normalization benchmark with expected outcomes for exact, misspelled,
  ambiguous, combination, OTC, supplement, and unknown inputs.
- Add fixture categories for high-risk duplicate ingredients, especially
  acetaminophen-containing products.
- Add a DDI evidence schema that separates:
  - interacting ingredient or product pair,
  - clinical effect,
  - evidence source,
  - review priority,
  - patient-specific modifiers,
  - source freshness,
  - exclusion or suppression conditions.
- Add tests that fail if any result screen or export implies "safe", "all
  clear", or "no risk."
- Add logging and data-version display for every generated signal.

## Validation Implications

Minimum next validation work:

- Offline scenario set with at least 100 consumer-style inputs.
- Normalization accuracy measurement by input class.
- Interaction rule review by a pharmacist or medication safety expert.
- Consumer comprehension study for "unknown", "ambiguous", "review-worthy", and
  "no signal" language.
- False-negative review for a small list of never-miss MVP scenarios.
- Human factors review for overreliance and anxiety-producing wording.

Do not present benchmark results as clinical validation. The first validation
goal is repeatable development evidence, not proof of patient outcome benefit.

## Regulatory And Privacy Implications

- MedCombo should not assume it fits general wellness policy because medication
  safety review is related to treatment and risk mitigation.
- The exact intended use, user population, output type, and claim language
  should be reviewed against FDA CDS guidance before public release.
- If the product stores or transmits identifiable health information, it needs a
  data inventory, consent model, retention policy, deletion workflow, access
  controls, audit logging, and breach-response plan.
- HIPAA applicability depends on business relationships with covered entities
  or business associates. A direct-to-consumer app may still face FTC health
  privacy and Health Breach Notification Rule obligations.
- No real-user deployment should proceed on the current "development use"
  sensitive-data notice alone.

## Open Questions

- Which public and licensed knowledge sources are acceptable for the first
  non-demo medication and DDI dataset?
- What minimum pharmacist review is needed for MVP interaction rules?
- What review-priority taxonomy should be used when sources disagree on
  severity?
- Should supplements remain "recorded for review only" in the next version, or
  should a separate supplement knowledge source be evaluated?
- What deployment model is intended: local-only demo, hosted consumer app,
  pharmacy-assisted workflow, or clinician-facing workflow?
- Will any AI model generate user-facing medical explanations, or will AI only
  support intake and draft text under deterministic constraints?

## Next Actions

1. Write an intended-use and prohibited-claims memo.
2. Create a normalization benchmark fixture set.
3. Create a DDI source decision memo comparing DailyMed/openFDA extraction,
   licensed compendia, and expert-curated rules.
4. Add explicit UI copy for "demo coverage", "unknown product", "ambiguous
   product", and "no signal is not no risk."
5. Add first pharmacist-review checklist for curated demo interactions.
6. Create a privacy and data-retention decision before any hosted demo.
7. Convert this run into reusable risk-register entries.
