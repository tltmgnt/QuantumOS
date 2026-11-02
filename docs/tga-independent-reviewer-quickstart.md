# Independent reviewer quickstart (synthetic data only)

This quickstart exercises the **complete** portable handoff pipeline without presenting synthetic records as real-world validation.

From the repository root, create a new directory:

```sh
python -m quantum_omega.gap_reviewer_quickstart_example /tmp/tga-reviewer-demo
```

The generator creates `/tmp/tga-reviewer-demo/handoff/` containing the six study inputs, five audit records and a synthetic local evidence file. The separate `handoff-inventory.json` inventories every byte. Generation performs a complete input-backed verification before reporting success.

As a receiving reviewer, rerun the independent command:

```sh
python -m quantum_omega.gap_portable_handoff_verify_cli /tmp/tga-reviewer-demo/handoff --inventory /tmp/tga-reviewer-demo/handoff-inventory.json
```

For a negative control, change any byte in `handoff/evidence/synthetic-record.txt` and rerun verification; it must exit nonzero. Regenerate in a **new** directory to reset the example.

## Review interpretation

- `portable_handoff_bytes_match: true` means the local files match the saved portable manifest.
- `handoff_receipt_matches_inputs: true` means the six-file study and audit chain recompute consistently.
- `checked_reference_count` is a file-check count, **not** a count of authenticated external records.
- All sign-off statuses in this example are `unverified`; reviewer names, organization, timestamps, repository commit and evidence are fictional.
- `external_authenticity_verified: false` and `scientific_validity_independently_verified: false` are mandatory conservative limitations.

For real submissions, obtain evidence and registrations independently, assess reviewer conflicts and label provenance outside this software, and document any independent scientific assessment separately.
