# RxNorm Experiment

Purpose:

- Evaluate RxNorm as the primary normalization backbone for prescription and
  many OTC drug names.

Initial experiment:

- Run local lookup scripts or notebooks outside the product path.
- Compare results against `data/benchmarks/normalization_cases.json`.
- Preserve ambiguous and out-of-scope states.

Required output fields:

- source metadata
- RXCUI when available
- display name
- normalized name
- active ingredients when available
- mapping confidence
- out-of-scope reason
- review status
