# MedCombo Literature Map

## Scope

Date: 2026-07-06.

This scoping research pack supports MedCombo's current product direction: a
consumer-first medication review preparation assistant that organizes medication
information, preserves uncertainty, surfaces source-linked review signals, and
generates pharmacist or clinician questions.

This is not a clinical validation report or a complete systematic review. It is
a product evidence map built from peer-reviewed anchor papers, public official
data-source documentation, and AI or digital health reporting guidance. Preprint
and non-peer-reviewed sources are treated as lower-confidence directional
evidence.

## Main Conclusion

The literature supports MedCombo's current boundary. The system should help
consumers prepare better medication review conversations, not decide whether a
regimen is safe. The strongest support is for structured intake, source-linked
normalization, duplicate-ingredient awareness, uncertainty preservation,
professional-review questions, and careful validation before stronger safety
claims.

The biggest product risk is coverage illusion: a clean interface can make a
small demo knowledge base look like complete medication safety screening.

## Research Themes

### Medication List Accuracy

Consumer-entered medication lists are a high-risk input. Studies comparing
patient-completed lists or personal medication lists against pharmacy or clinic
records report frequent omissions, additions, and discrepancies.

Implication for MedCombo:

- Treat "unknown" and "ambiguous" as first-class review states.
- Ask for information source, strength, dose, frequency, route, formulation,
  and actual use notes.
- Prefer review preparation language over completion language.
- Do not show "all clear" when no signal is generated.

Anchor sources:

- Meyer et al., patient-completed medication reconciliation forms versus
  pharmacy lists: https://pubmed.ncbi.nlm.nih.gov/21855261/
- Lee et al., completeness of patient self-reported medication lists:
  https://pubmed.ncbi.nlm.nih.gov/24259649/

### OTC And Duplicate Ingredient Risk

OTC products create medication safety risk because brand names can hide active
ingredients, especially in combination cold and pain products. FDA consumer
guidance emphasizes that acetaminophen appears in hundreds of prescription and
OTC products and warns against using multiple acetaminophen-containing products
at the same time.

Implication for MedCombo:

- Duplicate active ingredient detection is an appropriate early MVP rule.
- The benchmark set should include OTC combination products and abbreviations
  such as APAP.
- Product labels and active-ingredient display should be treated as core UX,
  not secondary detail.

Anchor sources:

- FDA acetaminophen consumer guidance:
  https://www.fda.gov/drugs/safe-use-over-counter-pain-relievers-and-fever-reducers/acetaminophen
- King et al., consumer-centered nonprescription acetaminophen labeling:
  https://pubmed.ncbi.nlm.nih.gov/21565649/

### Drug Normalization And Public Data Sources

RxNorm is the correct public anchor for normalized drug names and identifiers in
the United States, but its scope is not universal. NLM states that RxNorm covers
prescription and many OTC drugs, while dietary supplements, homeopathics, foods,
devices, and other categories are out of scope. NLM also notes that only about
60 percent of source vocabulary drug names receive RxNorm normalized names,
while the rest are out of scope or ambiguous.

DailyMed and openFDA labeling can support source-linked drug facts, but neither
is a ready-made clinical reasoning system. openFDA explicitly warns against
using its API to make medical care decisions and notes limits around labeling
currency, FDA verification, and OTC approval status.

Implication for MedCombo:

- Build a normalization benchmark before adding source ingestion.
- Separate `data/demo` from any live or imported source pipeline.
- Treat supplement and unknown entries as review needs rather than failed
  product flows.
- Show source freshness and source limitations.

Anchor sources:

- RxNorm Overview:
  https://www.nlm.nih.gov/research/umls/rxnorm/overview.html
- DailyMed:
  https://dailymed.nlm.nih.gov/dailymed/
- openFDA Drug Labeling API:
  https://open.fda.gov/apis/drug/label/

### Drug-Drug Interaction Evidence And Alert Fatigue

DDI evidence is not a simple lookup problem. Compendia may disagree, public
sources are incomplete, and clinical decision support systems can generate high
override rates when alerts ignore patient-specific context.

Van De Sijpe et al. found that a very severe DDI alert system produced 38,409
alerts, 88.2 percent of which were overridden. The authors linked false
positives to broad screening intervals and missing patient-specific
characteristics such as QTc values. Felisberto et al. provide broader systematic
review support for high override rates.

Implication for MedCombo:

- Keep interaction rules curated and evidence-linked.
- Store clinical concern, evidence basis, source freshness, and
  patient-specific modifiers.
- Avoid severity claims that imply clinical completeness.
- Treat patient context as "context to review" until clinical validation exists.

Anchor sources:

- Van De Sijpe et al., DDI CDSS evaluation:
  https://link.springer.com/article/10.1186/s12911-022-01783-z
- Felisberto et al., DDI alert override systematic review:
  https://journals.sagepub.com/doi/10.1177/14604582241263242
- Abarca et al., DDI compendia severity concordance:
  https://pubmed.ncbi.nlm.nih.gov/15098847/
- Ayvaz et al., public DDI source completeness:
  https://pubmed.ncbi.nlm.nih.gov/25917055/

### AI And Clinical Decision Support Evaluation

AI healthcare reporting guidelines support the current choice to keep
safety-critical logic deterministic while using AI, if added later, only for
bounded intake extraction or language assistance with validation.

DECIDE-AI emphasizes early-stage clinical evaluation, real workflow testing,
safety, and human factors. CONSORT-AI emphasizes transparent reporting of the
AI intervention, inputs and outputs, human-AI interaction, and error analysis.
FDA transparency principles and NIST AI RMF also point toward clear audience
information, limitations, human-centered design, and risk management.

Implication for MedCombo:

- Do not use LLMs to create or suppress safety signals.
- If LLM parsing is added, require strict schema validation and user
  confirmation.
- Track input source, confidence, extracted versus confirmed fields, and error
  cases.
- Add human factors testing before stronger consumer claims.

Anchor sources:

- DECIDE-AI:
  https://www.nature.com/articles/s41591-022-01772-9
- CONSORT-AI:
  https://www.nature.com/articles/s41591-020-1034-x
- FDA transparency for ML-enabled medical devices:
  https://www.fda.gov/medical-devices/software-medical-device-samd/transparency-machine-learning-enabled-medical-devices-guiding-principles
- NIST AI RMF:
  https://www.nist.gov/itl/ai-risk-management-framework

### Regulatory And Privacy Boundary

FDA CDS guidance confirms that patient or caregiver software can still fall
within digital health policy analysis depending on intended use and function.
FTC and HHS mobile health app guidance emphasize that apps collecting or
maintaining consumer health information may trigger privacy, security,
advertising, breach notification, and device-related obligations.

Implication for MedCombo:

- Keep the public claim as review preparation, not diagnosis, treatment, or
  medication decision support.
- Do not host identifiable medication or health context without privacy,
  retention, deletion, access-control, and breach-response decisions.
- Keep intended use, claims, outputs, and validation plan synchronized.

Anchor sources:

- FDA CDS guidance:
  https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-decision-support-software
- FTC Mobile Health Apps Interactive Tool:
  https://www.ftc.gov/business-guidance/resources/mobile-health-apps-interactive-tool
- HHS mobile health app resources:
  https://www.hhs.gov/hipaa/for-professionals/special-topics/health-apps/index.html

## Product Position Supported

Supported:

- Consumer medication review preparation.
- Structured medication list intake.
- Ingredient and class explanation.
- Duplicate active ingredient review signals.
- Curated interaction review signals with evidence metadata.
- Pharmacist or clinician questions.
- Explicit uncertainty and source limitation language.

Not supported yet:

- Claims that the system determines whether a medication regimen is safe.
- Claims of clinical-grade interaction coverage.
- Automated medication change advice.
- Patient-specific clinical risk scoring.
- Hosted PHI collection without privacy and security implementation.

## Next Research Pass

The next pass should focus on:

1. A formal data-source comparison memo for RxNorm, RxClass, DailyMed, openFDA,
   licensed compendia, and expert-curated rules.
2. A 50 to 100 case normalization benchmark expansion.
3. A pharmacist-adjudicated interaction scenario set.
4. Consumer comprehension testing for "unknown", "ambiguous",
   "review-worthy", and "no demo signal" language.
5. A privacy and regulatory memo tied to intended-use claims.
