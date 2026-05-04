# Preliminary Research Summary: Medication Intake And Conversational Review

## Research Question

Should MedCombo's next development phase focus on first-pass medication
screening, or on helping consumers provide, verify, and clarify medication
information through a guided conversation?

## Conclusion

MedCombo should prioritize medication intake quality before expanding safety
screening breadth.

The research does not support treating consumer-entered medication names as
reliably complete clinical input. It supports a workflow that gathers medication
information, asks targeted follow-up questions, preserves uncertainty, and
turns unresolved items into pharmacist or clinician review questions.

First-pass screening should remain part of the product, but it should be
confidence-aware. The product should only present deterministic review signals
for sufficiently identified items and should clearly mark unknown, ambiguous, or
incomplete entries as review needs.

## Key Findings

| Finding | Evidence | Confidence | Product Implication |
| --- | --- | --- | --- |
| Medication reconciliation is not a single lookup. It is a process of collecting, verifying, documenting, and comparing medication information. | AHRQ MATCH Toolkit frames medication reconciliation as a complex process that obtains and verifies current medications across care settings. | high | MedCombo should be built around intake and verification, not only interaction detection. |
| A good medication history requires probing beyond prescription names. | AHRQ patient medication interview tips include prescriptions, OTC drugs, vitamins, herbals, supplements, inhalers, strength, formulation, dose, route, frequency, and last dose. | high | A conversational intake flow matches the real-world interview pattern better than a static form. |
| Patient-reported medication lists are often incomplete or discrepant. | Meyer et al. found only 36.3% of patient-completed reconciliation forms matched pharmacy-prescribed drugs. Lee et al. found 56% of evaluated personal medication lists incomplete and 94% with at least one discrepancy. | high | MedCombo should assume user input may be incomplete and should surface missing information. |
| Electronic medication reconciliation tools can reduce some medication discrepancies, especially omissions, but evidence is mixed. | Mekonnen et al. systematic review and meta-analysis found electronic reconciliation reduced omission errors, while other outcomes were less consistent. | medium | Build electronic intake support, then validate locally instead of claiming clinical impact. |
| Patient-facing medication reconciliation can work in some settings. | Ebbens et al. randomized noninferiority study found patient portal reconciliation noninferior to pharmacy technician reconciliation on discrepancies in a preoperative setting and saved time. | medium | A consumer-facing intake product is plausible, but success depends on usability and user characteristics. |
| Conversational AI for medication reconciliation is technically plausible but early. | A 2025 medRxiv preprint describes AMREC, a conversational medication reconciliation agent that verifies, corrects, removes, and adds medications through dialogue. It is preprint and company-affiliated evidence. | low to medium | MedCombo should start with deterministic question flows and add LLM assistance only behind validation and safety checks. |
| Drug identity normalization remains a coverage and ambiguity bottleneck. | RxNorm provides normalized names for many US prescription and OTC drugs, but some source vocabulary names are out of scope or ambiguous, including supplements and other non-drug categories. | high | Unknown, ambiguous, supplement, and out-of-scope entries should become first-class intake states. |

## Product Interpretation

The product should shift from:

```text
User enters medication names -> app checks interactions -> app returns warnings.
```

to:

```text
User provides messy medication information -> app clarifies missing facts ->
app marks confidence and uncertainty -> app runs first-pass review where
possible -> app creates a pharmacist or clinician review packet.
```

This is a safer and more evidence-aligned path because the main bottleneck is
not only drug-drug interaction knowledge. It is the quality, completeness, and
interpretability of the input medication list.

## Design Requirements Derived From Research

- Preserve the user's original text next to any normalized candidate.
- Track how each item was entered: label, pharmacy list, medical summary, photo,
  caregiver memory, or user memory.
- Ask one missing-detail question at a time.
- Let the user answer "I do not know" without blocking the workflow.
- Treat unknown and ambiguous entries as review needs, not as empty results.
- Do not screen low-confidence items as if they were fully identified.
- Include OTC products, vitamins, supplements, herbals, inhalers, creams,
  patches, eye drops, and as-needed products in the prompt strategy.
- Generate professional-review questions from missing or uncertain information.
- Keep safety-critical signal generation deterministic and source-linked.
- Use LLMs only for intake parsing, question selection, and plain-language
  drafting after schema validation and safety-language checks.

## References

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
- RxNorm overview:
  https://www.nlm.nih.gov/research/umls/rxnorm/overview.html
