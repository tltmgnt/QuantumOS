# Audit-handoff receipt CLI

Create a checksum-bound reviewer receipt after replaying the original six-file study and checking all audit-chain artifacts:

```sh
python -m quantum_omega.gap_audit_handoff_receipt_cli create --study-dir STUDY_DIR --bundle audit-bundle.json --signoff signoff.json --manifest evidence-refs.json --evidence-dir evidence/ --report audit-chain-report.json --output receipt.json
```

Verify the saved receipt against the original inputs:

```sh
python -m quantum_omega.gap_audit_handoff_receipt_cli verify --study-dir STUDY_DIR --bundle audit-bundle.json --signoff signoff.json --manifest evidence-refs.json --evidence-dir evidence/ --report audit-chain-report.json --receipt receipt.json
```

Create mode never overwrites an existing receipt. Verification fails on altered receipt fields or underlying study/evidence changes. Store all artifacts outside the exact six-file study directory.

A successful receipt is a reproducible local integrity record, **not** an authenticated auditor signature, verified external provenance, or independent scientific endorsement.
