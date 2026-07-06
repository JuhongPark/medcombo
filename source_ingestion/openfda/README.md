# openFDA Experiment

Purpose:

- Evaluate openFDA drug labeling data for machine-readable label retrieval.

Initial experiment:

- Compare retrieved labeling against DailyMed and demo source references.
- Track source freshness and API limitations.
- Do not use openFDA output for medical-care decisions or user-facing safety
  signals without curation.

Required output fields:

- source metadata
- source record identifier
- display name
- linked normalized identifier if available
- mapping confidence
- out-of-scope or limitation notes
- review status
