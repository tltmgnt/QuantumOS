# Frozen replay with reviewer quality

Use `replay_with_reviewer_quality(protocol, priority_report, evidence_manifest, label_bytes, reviewer_bytes, reviewer_sha256)` from `quantum_omega.gap_quality_replay`.

The frozen evaluation is verified through the existing evidence replay. Reviewer submissions are a **separate** UTF-8 JSON object containing exactly `submissions` and `adjudications`, checksum-bound to the supplied SHA-256 of their original bytes. The result includes evaluation scores, reviewer agreement, illustrative uncertainty, disputed votes, adjudications, and a deterministic combined report digest.

**Important:** This does not establish that the reviewer judgments are the same data as the frozen evaluation labels. It also does not verify reviewer independence, registration chronology, or scientific correctness. An external auditor must reconcile the reviewer records with the actual labels and provenance before making study claims.
