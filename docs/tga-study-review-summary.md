# Machine-readable independent-study review summary

Call `quantum_omega.gap_study_review.summarize_study_package(path)` on a six-file study package. The function runs the full fail-closed provenance-gated evaluation and returns a deterministic SHA-256-bound JSON-compatible summary.

The `checks` section records **internal** protocol, label, reviewer, timestamp-string and adjudication consistency. The `external_verification` section always marks registration authenticity, reviewer independence, and scientific validity as `false`. These claims require independent evidence beyond the submitted JSON files.

This summary is a compact audit aid, not a certificate of empirical validation. Invalid packages raise `ValueError` rather than generating a passing summary.
