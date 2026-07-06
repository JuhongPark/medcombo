# MedCombo Data Source Strategy

## Decision

MedCombo should separate data-source ingestion from the curated demo knowledge
base before expanding medication coverage. `data/demo` should remain a small,
manually reviewable test set. External data should enter through a separate
pipeline with explicit source freshness, licensing, mapping confidence, and
failure states.

## Source Roles

| Source | Best use | Main limits | MedCombo role |
| --- | --- | --- | --- |
| RxNorm | Normalized drug names, RXCUIs, brand/generic mapping, ingredient relationships | Excludes supplements, foods, devices, homeopathics, and ambiguous out-of-scope names | Primary normalization backbone |
| RxClass | Drug class relationships | Class semantics depend on source and use case | Class-overlap features and display |
| DailyMed | Structured labeling and source-linked product information | Labeling text is not a complete reasoning engine | Source-linked ingredient, warning, and label references |
| openFDA drug label API | Machine-readable SPL-derived label access | API warns against medical-care decisions, labels may not match current distributed products, OTC limitations exist | Label retrieval experiment and source freshness metadata |
| Licensed compendia | Curated interaction and severity knowledge | Cost, license limits, black-box differences, compendia disagreement | Candidate for clinical-grade DDI expansion |
| Expert-curated rules | Narrow, auditable review signals | Requires maintenance and expert review | MVP and validation-friendly safety rules |

## Architecture Direction

Add a source layer before changing rule logic:

```text
data/demo/
  manually curated fixtures

data/benchmarks/
  normalization and scenario expectations

source_ingestion/
  rxnorm/
  rxclass/
  dailymed/
  openfda/

medcombo/
  knowledge.py
  normalize.py
  rules.py
  evidence.py
```

The ingestion layer should output normalized intermediate records rather than
directly changing review behavior.

## Required Metadata

Every non-demo medication, ingredient, class, and interaction record should
carry:

- source name
- source URL or identifier
- source version or retrieval date
- license or use restriction note
- mapping confidence
- normalized identifier if available
- source freshness
- out-of-scope reason if unresolved
- review status: imported, curated, expert-reviewed, or deprecated

## Normalization Strategy

Phase 1:

- Keep current demo alias matching.
- Expand `data/benchmarks/normalization_cases.json` to 50 to 100 cases.
- Categorize cases by exact brand, generic ingredient, OTC combination,
  strength/dose in text, typo, ambiguous name, supplement, and unknown.

Phase 2:

- Add RxNorm lookup experiment behind a feature flag or offline script.
- Compare benchmark pass rate against demo-only normalization.
- Keep ambiguous and out-of-scope states visible.

Phase 3:

- Add DailyMed/openFDA label linking only after normalization IDs are stable.
- Add confidence and source freshness to UI and summaries.

## Interaction Strategy

Current demo interactions should remain curated. Future interactions should be
modeled as evidence records, not simple pairs.

Recommended fields:

- ingredient pair or product pair
- clinical concern
- mechanism if source-supported
- evidence source
- evidence type
- review priority
- patient-specific modifiers
- exclusion or de-escalation conditions
- source freshness
- expert review status

The rule engine should only emit a user-facing signal when the record has enough
evidence metadata to explain why the signal appeared.

## Source Comparison Questions

For each source:

- What entities does it cover?
- What does it explicitly exclude?
- How often is it updated?
- Can the source be redistributed?
- Does it provide stable identifiers?
- Does it expose ingredients and combination products?
- Does it provide classes, warnings, interactions, or only labels?
- How should MedCombo show source freshness?
- What failure modes would mislead a consumer?

## Near-Term Implementation Tasks

1. Expand the normalization benchmark.
2. Create an offline RxNorm lookup experiment.
3. Create a DailyMed/openFDA label retrieval memo.
4. Add an `evidence.py` model for interaction evidence records.
5. Add tests that fail when imported records lack source metadata.
6. Keep public claims tied to the curated demo dataset until source coverage is
   measured.
