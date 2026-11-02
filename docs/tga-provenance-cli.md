# Provenance-gated TGA CLI

Run:

```sh
python -m quantum_omega.gap_provenance_cli \\
  --protocol protocol.json --report priority.json \\
  --evidence evidence.json --labels labels.json \\
  --reviewers reviewers.json --study study.json \\
  --output evaluation.json
```

All inputs are local JSON files. The label and reviewer files are read as original bytes for checksum validation. Output paths use create-only mode to avoid overwriting existing evaluation records. An invalid input or inconsistent provenance returns a nonzero exit code.

The CLI enforces consistency across self-reported records and reviewer-to-label reconciliation. It does **not** independently verify external registration, reviewer identities, or scientific validity.
