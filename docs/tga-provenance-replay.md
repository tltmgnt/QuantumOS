# Provenance-gated frozen evaluation replay

Call `replay_with_provenance(protocol, priority_report, evidence_manifest, label_bytes, reviewer_bytes, study)` from `quantum_omega.gap_provenance_replay`.

This fail-closed entry point first checks study metadata against the frozen protocol, evidence manifest, label source, original label bytes, and reviewer identifiers. It then invokes the existing frozen evaluation and reviewer-quality replay, which checks label reconciliation, reviewer agreement, uncertainty, and adjudications. Any inconsistent record raises `ValueError`.

The returned report has a deterministic SHA-256 digest and retains explicit `False` flags for independently authenticated registration and reviewer independence. Matching self-reported metadata is **not** proof of external provenance or scientific validity.
