# MedCombo Research Plan Template

## Purpose

Use this document as a reusable plan for investigating MedCombo's system
limitations across multiple research focuses.

Each research run should answer one narrow question with traceable evidence,
not attempt to settle the whole product strategy at once. A good run produces a
clear limitation statement, supporting sources, product implications, and a
short list of decisions or follow-up work.

## When To Use This Plan

Use this plan when evaluating:

- Current MVP limitations.
- Data and knowledge-source coverage.
- Medication normalization quality.
- Drug-drug interaction signal quality.
- Consumer medication-list reliability.
- AI explanation and summarization safety.
- Regulatory classification risk.
- Privacy, security, consent, and retention obligations.
- Clinical validation requirements.
- Human factors and overreliance risk.

## Research Run Template

### Research Focus

Write one sentence.

Example:

```text
Evaluate whether public data sources are sufficient for clinical-grade
drug-drug interaction detection in a consumer medication review product.
```

### Decision This Run Should Support

Define the decision that the research should inform.

Examples:

- Keep a feature in the MVP.
- Narrow or rewrite a product claim.
- Add a new validation requirement.
- Replace or supplement a data source.
- Mark a capability as out of scope.
- Create a regulatory or privacy review item.

### System Snapshot

Refresh this section at the start of each run.

- Current branch and commit.
- Current data version.
- Medication, ingredient, class, interaction, and source counts.
- Current supported inputs.
- Current unsupported inputs.
- Current user-facing claims.
- Current safety-boundary language.
- Current tests relevant to the focus.

Useful local checks:

```bash
git status --short
python -m unittest discover
```

For the demo knowledge base, count the current data objects before making
coverage claims.

### Research Questions

Use three to seven questions. Keep them answerable.

Examples:

- What limitation exists in the current system?
- Is this limitation caused by product scope, data coverage, rule logic, model
  behavior, UI wording, regulatory boundary, or validation gap?
- What evidence supports the limitation?
- What evidence argues the limitation is acceptable for the MVP?
- What user harm or product risk could occur if the limitation is hidden?
- What mitigation is feasible in the next one or two development phases?
- What remains uncertain after this run?

### Evidence Standards

Prefer primary and high-quality sources.

Source priority:

1. Official regulatory guidance and government documentation.
2. Peer-reviewed systematic reviews, reporting guidelines, and consensus
   statements.
3. Peer-reviewed empirical studies.
4. Official source documentation for data products and APIs.
5. Commercial white papers only when they describe market structure, available
   datasets, or implementation constraints.
6. Blog posts and vendor material only as leads, not final authority.

For each source, record:

- Title.
- Publisher or journal.
- Date.
- URL or DOI.
- Source type.
- Key claim.
- How it applies to MedCombo.
- Limitations or conflicts of interest.
- Retrieval date.

### Evidence Ledger

Use this table in each research output.

| Claim | Evidence | Source Type | Confidence | Product Implication |
| --- | --- | --- | --- | --- |
| Public normalization data does not fully cover supplements. | RxNorm scope excludes dietary supplements. | Official documentation | High | Supplement handling should remain limited or use another source. |

Confidence labels:

- `high`: Supported by official guidance, repeated findings, or direct code/data
  evidence.
- `medium`: Supported by credible sources but may be context-dependent.
- `low`: Plausible but based on limited, indirect, or early evidence.

### Analysis Frame

Classify each limitation into one or more categories.

- `scope_limit`: The product intentionally does not support the capability yet.
- `data_limit`: The source data is incomplete, stale, ambiguous, licensed, or
  not structured enough.
- `logic_limit`: Rules do not capture real clinical complexity.
- `model_limit`: AI output may be ungrounded, inconsistent, biased, or hard to
  validate.
- `ux_limit`: The interface or wording can cause misunderstanding,
  overreliance, anxiety, or missed escalation.
- `validation_limit`: No clinical, user, or benchmark evidence exists yet.
- `regulatory_limit`: Intended use, claims, or risk level may trigger review.
- `privacy_limit`: Sensitive data handling is not yet production-ready.
- `operational_limit`: Update, monitoring, audit, incident response, or
  maintenance processes are missing.

### Risk Rating

Rate each limitation.

| Rating | Meaning |
| --- | --- |
| `critical` | Could plausibly cause serious user harm or create a major regulatory/privacy blocker if shipped. |
| `high` | Could mislead users, miss important safety signals, or materially weaken clinical trust. |
| `medium` | Important for product quality but can be managed with scope limits or warnings. |
| `low` | Mostly documentation, polish, or future-readiness. |

Also record:

- User affected.
- Trigger scenario.
- Failure mode.
- Existing mitigation.
- Missing mitigation.
- Evidence strength.
- Owner or next action.

## Standard Research Tracks

### Track 1: Intended Use And Safety Boundary

Goal:

- Define what MedCombo may safely claim and what it must not claim.

Core questions:

- Is MedCombo presenting review-worthy signals or medication decisions?
- Could wording imply that the regimen is safe if no signal appears?
- Does the target user include patients, caregivers, clinicians, or all three?
- Does any feature move from general wellness or non-device CDS toward device
  software?

Primary sources:

- FDA Clinical Decision Support Software guidance.
- FDA General Wellness guidance.
- FTC, HHS, FDA Mobile Health Apps Interactive Tool.

Expected output:

- Intended-use statement.
- Prohibited-claims list.
- Claim-risk table.
- Required safety-language updates.

### Track 2: Medication Normalization Coverage

Goal:

- Determine whether current name matching can support the planned user workflow.

Core questions:

- Which inputs can be normalized reliably?
- Which inputs are ambiguous because of brand names, formulations, strengths,
  routes, or combination products?
- Which inputs are out of scope for RxNorm or current public sources?
- How should the app represent unknown and ambiguous products?

Primary sources:

- RxNorm overview and technical documentation.
- RxNorm and RxNav API documentation.
- DailyMed labeling and mapping resources.
- RxClass API documentation.

Expected output:

- Coverage matrix.
- Ambiguity taxonomy.
- Normalization benchmark set.
- Product copy for unknown and ambiguous products.

### Track 3: Drug Interaction And Rule Quality

Goal:

- Evaluate whether current rules can safely support interaction review signals.

Core questions:

- Which interaction types can be supported with traceable public evidence?
- Which interaction pairs require licensed or expert-curated knowledge bases?
- How inconsistent are interaction severity labels across sources?
- Which patient-specific factors are needed to reduce false positives?
- What false negatives are unacceptable even in an MVP?

Primary sources:

- Drug-drug interaction clinical decision support studies.
- Drug interaction compendia concordance studies.
- DailyMed label sections on interactions, contraindications, warnings, and
  precautions.
- Licensed knowledge-base documentation when available.

Expected output:

- Interaction-source decision memo.
- Minimum viable interaction rule set.
- Severity and review-priority mapping.
- False-positive and false-negative test scenarios.

### Track 4: Consumer Input Reliability

Goal:

- Understand how often consumer-entered medication lists are incomplete,
  inaccurate, or misleading.

Core questions:

- How accurate are patient-generated medication lists compared with pharmacy or
  clinical records?
- Which errors matter most for MedCombo?
- How should the app ask users to verify product labels, pill bottles, dose,
  route, timing, and active ingredients?
- What UI patterns reduce omission and duplicate-entry risk?

Primary sources:

- Medication reconciliation studies.
- Patient-generated medication list studies.
- Health literacy and OTC medication-use studies.
- Acetaminophen and combination-product misuse studies.

Expected output:

- Input-risk taxonomy.
- Intake redesign recommendations.
- Required verification prompts.
- Scenario test set for missing and misleading inputs.

### Track 5: AI Explanation And Summarization Safety

Goal:

- Define how AI-generated explanations can be used without inventing evidence
  or issuing medication instructions.

Core questions:

- Which content must be rule-generated instead of model-generated?
- How should AI text cite sources and preserve uncertainty?
- What prohibited language should be blocked?
- What evaluation is needed for plain-language accuracy, readability,
  overreliance, and clinical appropriateness?

Primary sources:

- DECIDE-AI.
- SPIRIT-AI.
- CONSORT-AI.
- FDA Good Machine Learning Practice.
- NIST AI Risk Management Framework.

Expected output:

- AI role boundary.
- Explanation-generation requirements.
- Safety-language test suite.
- Human review and audit requirements.

### Track 6: Privacy, Security, Consent, And Retention

Goal:

- Determine the data-handling requirements before real user deployment.

Core questions:

- Does the product collect identifiable health information?
- Does HIPAA apply directly, indirectly, or not at all?
- Does the FTC Health Breach Notification Rule apply?
- What consent, retention, deletion, access, audit, and breach-response
  controls are required?
- Which data should not be stored in the MVP?

Primary sources:

- HHS HIPAA health app developer resources.
- FTC Health Breach Notification Rule guidance.
- FTC Act health privacy enforcement guidance.
- NIST security and privacy frameworks as needed.

Expected output:

- Data inventory.
- Privacy boundary memo.
- Storage and retention decision.
- Security requirements for production readiness.

### Track 7: Clinical Validation And Human Factors

Goal:

- Define what evidence is needed before stronger safety or clinical claims.

Core questions:

- What offline tests are enough for MVP development?
- What pharmacist or clinician review is needed?
- What user study is needed for comprehension and overreliance?
- What prospective or real-world evaluation would be required later?
- How should performance be measured for the human-AI team, not just the
  algorithm?

Primary sources:

- DECIDE-AI for early-stage clinical AI evaluation.
- CONSORT-AI and SPIRIT-AI for trial reporting and protocols.
- FDA human factors and usability guidance.
- Medication safety alert fatigue literature.

Expected output:

- Validation roadmap.
- Scenario benchmark.
- Expert-review protocol.
- Consumer comprehension study plan.
- Human factors risk register.

## Standard Deliverables

Each completed research run should create or update:

- Limitation statement.
- Evidence ledger.
- Risk register entries.
- Product implications.
- Engineering implications.
- Validation implications.
- Regulatory or privacy implications.
- Open questions.
- Recommended next actions.

## Output Template

```markdown
# Research Run: <focus>

## Summary

<Three to five sentences.>

## Decision Supported

<Decision this research informs.>

## Current System Snapshot

- Commit:
- Data version:
- Relevant files:
- Relevant tests:

## Findings

| Finding | Evidence | Risk | Confidence | Implication |
| --- | --- | --- | --- | --- |

## Evidence Notes

<Annotated source notes.>

## Product Implications

<Claims, UX, copy, workflow, and scope changes.>

## Engineering Implications

<Data, rules, tests, logging, audit, and architecture changes.>

## Validation Implications

<Benchmarks, expert review, user study, or clinical evaluation.>

## Regulatory And Privacy Implications

<CDS, SaMD, HIPAA, FTC, HBNR, consent, retention, breach response.>

## Open Questions

<What remains unresolved.>

## Next Actions

<Prioritized follow-up work.>
```

## Seed Reference List

Refresh these links before making current claims.

- FDA Clinical Decision Support Software:
  https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-decision-support-software
- FDA Good Machine Learning Practice:
  https://www.fda.gov/medical-devices/software-medical-device-samd/good-machine-learning-practice-medical-device-development-guiding-principles
- NIST AI Risk Management Framework:
  https://www.nist.gov/itl/ai-risk-management-framework
- HHS Resources for Mobile Health Apps Developers:
  https://www.hhs.gov/hipaa/for-professionals/special-topics/health-apps/index.html
- FTC Health Breach Notification Rule:
  https://www.ftc.gov/business-guidance/resources/health-breach-notification-rule-basics-business
- RxNorm Overview:
  https://www.nlm.nih.gov/research/umls/rxnorm/overview.html
- RxNav:
  https://lhncbc.nlm.nih.gov/RxNav/
- RxClass API:
  https://lhncbc.nlm.nih.gov/RxNav/APIs/RxClassAPIs.html
- DailyMed:
  https://dailymed.nlm.nih.gov/dailymed/
- DECIDE-AI:
  https://www.nature.com/articles/s41591-022-01772-9
- SPIRIT-AI:
  https://www.nature.com/articles/s41591-020-1037-7
- CONSORT-AI:
  https://www.nature.com/articles/s41591-020-1034-x
- Drug-drug interaction alert performance study:
  https://link.springer.com/article/10.1186/s12911-022-01783-z
- Patient-completed medication reconciliation reliability:
  https://pubmed.ncbi.nlm.nih.gov/21855261/
- Acetaminophen nonprescription overdose risk:
  https://psnet.ahrq.gov/issue/risk-unintentional-overdose-non-prescription-acetaminophen-products

## Maintenance Notes

- Update the system snapshot before each new research run.
- Re-check regulatory and API documentation because these sources can change.
- Do not treat absence of a signal as evidence of safety.
- Keep consumer-facing claims weaker than the validated evidence.
- Prefer narrow, traceable, well-tested capability over broad unsupported
  coverage.
