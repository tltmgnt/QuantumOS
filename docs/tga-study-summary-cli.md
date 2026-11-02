# Compact external-study review summary

Run:

```sh
python -m quantum_omega.gap_study_package_cli /path/to/study --summary
```

Use `--summary --output review-summary.json` to write a new, create-only audit summary file. Without `--summary`, the CLI continues to output the full provenance-gated replay result.

The summary reports internal protocol/label/reviewer consistency and always marks independent registration authenticity, reviewer independence, and scientific validity as **unverified**. Invalid or tampered packages fail with a nonzero exit code.
