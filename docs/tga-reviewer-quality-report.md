# Unified reviewer-quality evaluation

Call `build_reviewer_quality_report(submissions, adjudications=(), confidence=0.95)` from `quantum_omega.gap_quality_report`.

Inputs use the reviewer judgment and adjudication formats documented in the corresponding Python modules. The output contains descriptive pairwise agreement, illustrative Wilson intervals, all disputed pair votes, optional adjudication rationales, and a deterministic SHA-256 of the report payload.

**Do not mistake this for an independent evaluation dataset.** No real reviewer data ships with the package. Collect and retain external judgments under the frozen protocol and evidence-manifest workflow before using this report in a study.

Reviewer identity, chronological provenance, conflict disclosures, and reviewer independence require external verification. Wilson intervals are not calibrated for repeated claim pairs or shared reviewers. Adjudication is recorded separately and does not rewrite initial labels.
