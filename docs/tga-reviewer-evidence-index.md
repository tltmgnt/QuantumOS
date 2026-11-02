# External reviewer custody evidence index

This index is a **self-declared reference register**, not proof that identity, independence, or external evidence has been verified. It links an acknowledgment to seven evidence categories: reviewer identity, reviewer authorization, reviewer independence, handoff-key authentication, reviewer-key authentication, conflict review, and key custody.

Each category has `status` (`unverified`, `claimed_verified`, or `rejected`) and `references` (a list of `{"locator": "...", "sha256": "64 lowercase hex"}`). A `claimed_verified` category requires at least one reference. The `locator` is an opaque pointer, **not** a path to open automatically. Store confidential supporting evidence outside public repositories.

Create a JSON evidence input with exactly those seven categories, then:

```sh
python -m quantum_omega.gap_reviewer_evidence_index_cli create --acknowledgment reviewer-acknowledgment.json --evidence reviewer-evidence-input.json --output reviewer-evidence-index.json
python -m quantum_omega.gap_reviewer_evidence_index_cli verify --acknowledgment reviewer-acknowledgment.json --index reviewer-evidence-index.json
```

The index checksum binds its content to the supplied acknowledgment. It **does not** retrieve evidence, compare actual evidence file bytes, authenticate external records, verify key custody, or prove a reviewer is a distinct independent person. An adversary able to regenerate the index checksum can also rewrite the self-declared statuses and references. Use the [independent reviewer custody checklist](tga-reviewer-key-custody-checklist.md) for required human verification.
