# Verify saved audit-chain reports

Recompute a saved report from its audit bundle, sign-off, evidence-reference manifest and local evidence files:

```sh
python -m quantum_omega.gap_audit_chain_verify_cli --bundle audit-bundle.json --signoff signoff.json --manifest evidence-refs.json --evidence-dir evidence/ --report audit-chain-report.json
```

The command returns nonzero if any input, local file checksum, or saved report field differs from the recomputed result. This is **input-backed** verification, not an offline-only check.

The output explicitly retains `external_authenticity_verified: false` and `scientific_validity_independently_verified: false`. Matching reports are not authenticated signatures or independent scientific endorsements.
