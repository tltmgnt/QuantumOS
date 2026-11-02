# Consolidated audit-chain report CLI

Export a deterministic JSON report after verifying the audit bundle, sign-off, evidence-reference manifest and all referenced local evidence files:

```sh
python -m quantum_omega.gap_audit_chain_report_cli --bundle audit-bundle.json --signoff signoff.json --manifest evidence-refs.json --evidence-dir evidence/ --output audit-chain-report.json
```

The command fails with nonzero exit status for malformed inputs, missing files, checksum mismatches, or an existing output path. Keep outputs outside the exact six-file study directory.

The report includes per-category declared status, reference counts, checked local file counts and checksum bindings. `external_authenticity_verified` and `scientific_validity_independently_verified` remain false: a successful run is **not** an independent authenticity or scientific validation result.
