# Independent TGA-Ω evaluation study kit

This kit defines a **submission schema**, not a certification mechanism. No external judgments or real reviewer identities are included.

## Procedure

1. Choose an evaluation set of research claims and define review-priority judgments without consulting the TGA-Ω ranking. Document sampling, exclusions, reviewer recruitment, and conflicts.
2. Freeze the priority report and protocol using `freeze_protocol`. Publish the protocol digest and study design to an independently timestamped registry **before** collecting judgments.
3. Recruit at least two reviewers. Obtain their conflict declarations and record affiliations, but do not publish personal identifiers without consent.
4. Collect pairwise judgments using the `gap_external_eval` schema. Preserve the original UTF-8 JSON bytes.
5. Create the evidence manifest with the original label-file SHA-256, then run `python -m quantum_omega.gap_cli` with the protocol, report, manifest, and labels.
6. Report pairwise accuracy, alphabetical baseline, disagreements, sample size, excluded judgments, and all deviations from the registered protocol.
7. Have a person independent of the study verify registration timestamps, reviewer attestations, conflicts, and the chronology of label collection. Do not promote self-reported fields to verified evidence.

## Study submission metadata

Provide a JSON object with exactly these fields:

- `schema_version`: 1
- `study_id`: nonempty identifier
- `protocol_sha256`: lowercase 64-character digest
- `registered_at`, `labels_collected_at`: timezone-aware ISO-8601 timestamps
- `label_source_id`: identifier matching the label file
- `reviewers`: at least two records with `reviewer_id`, `affiliation`, and boolean `conflict_declared`

Call `validate_study_submission(submission)` for structural and claimed chronology checks. The returned flags explicitly state that external timestamp authenticity, reviewer independence, and label quality remain unverified.

**Scientific scope:** These evaluations test a structural review-priority heuristic, not quantum gravity, explanatory distance, or discovery.
