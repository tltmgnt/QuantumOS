# Evidence-reference manifest CLI

Create a `references.json` object with exactly four keys: `registration_authenticity`, `reviewer_independence`, `label_provenance`, and `scientific_validity`. Each value is a list of records with `locator`, `description`, and `sha256`. For unverified categories, empty lists are allowed.

Create a manifest:

```sh
python -m quantum_omega.gap_audit_evidence_refs_cli create --bundle audit-bundle.json --signoff signoff.json --references references.json --output evidence-refs.json
```

Verify the saved manifest:

```sh
python -m quantum_omega.gap_audit_evidence_refs_cli verify --bundle audit-bundle.json --signoff signoff.json --manifest evidence-refs.json
```

Creation never overwrites an existing file. Verification checks deterministic checksums and binding to the bundle and sign-off. It **does not** fetch referenced evidence or establish that the underlying evidence is authentic.
