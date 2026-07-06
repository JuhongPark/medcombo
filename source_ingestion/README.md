# Source Ingestion Experiments

This directory is for offline source-ingestion experiments. It intentionally
does not power the current demo knowledge base.

Current boundary:

- No network calls are implemented here.
- No source data is bundled here.
- Imported records must remain separate from `data/demo`.
- Every imported record must carry source metadata, mapping confidence, and
  review status before it can be considered for curated demo or product data.

Near-term experiments:

- RxNorm lookup experiment for normalized drug identity.
- DailyMed label-linking experiment for source references.
- openFDA label retrieval experiment for machine-readable labeling.

Do not use imported records for user-facing safety signals until they have been
validated, source-linked, and reviewed.
