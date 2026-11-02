# External study-package intake

Supply a directory containing **exactly** six UTF-8 JSON files:

- `protocol.json` — frozen evaluation protocol
- `priority.json` — frozen priority report
- `evidence.json` — evidence manifest and label checksum
- `labels.json` — original frozen pairwise labels
- `reviewers.json` — original reviewer votes and adjudications
- `study.json` — study metadata, reviewer identifiers and claimed chronology

Invoke `quantum_omega.gap_study_package.validate_study_package(path)`. The validator rejects missing or extra files, symlinks, invalid JSON, inconsistent records, tampered labels and unresolved reviewer/label disagreement. It returns the full provenance-gated replay result.

The intake format is a software validation contract. It **does not** prove that claimed registration timestamps are genuine, that reviewers are independent, or that labels are scientifically correct. Preserve signed attestations and original external records separately for independent audit. The synthetic example generator emits `evaluation.json` as well; remove that generated output before submitting its six input files as a package.
