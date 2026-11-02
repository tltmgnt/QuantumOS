# Independent-audit sign-off CLI

Prepare a JSON declaration with exactly these fields: `auditor`, `organization`, `reviewed_at`, `repository_commit` (full 40-character lowercase Git SHA), `evidence_statuses`, and `notes`. Evidence statuses must include `registration_authenticity`, `reviewer_independence`, `label_provenance`, and `scientific_validity`, each set to `unverified`, `verified`, or `rejected`.

Create a sign-off file (never overwrites):

```sh
python -m quantum_omega.gap_audit_signoff_cli create --bundle audit-bundle.json --declaration declaration.json --output signoff.json
```

Verify the saved record's checksum and binding to the bundle:

```sh
python -m quantum_omega.gap_audit_signoff_cli verify --bundle audit-bundle.json --signoff signoff.json
```

**Caution:** Verification only checks consistency of self-reported declarations. It does not authenticate the auditor, digitally sign the record, validate a registry timestamp, or establish scientific validity. Retain external evidence separately.
