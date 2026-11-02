# Reviewer handoff acknowledgment

A receiving reviewer can create a checksum-bound acknowledgment after replaying the portable signed handoff with their **own** trusted-key pin and independently confirmed fingerprint.

```sh
python -m quantum_omega.gap_reviewer_handoff_acknowledgment_cli create handoff/ --package reviewer-package.json --pinned-key recipient-trusted-key.json --expected-sha256 INDEPENDENTLY_CONFIRMED_SHA256 --reviewer-id reviewer-B --reviewed-at 2026-11-02 --notes "Signed software replay only" --output reviewer-ack.json
```

Recheck the acknowledgment against the original package and handoff:

```sh
python -m quantum_omega.gap_reviewer_handoff_acknowledgment_cli verify handoff/ --package reviewer-package.json --pinned-key recipient-trusted-key.json --expected-sha256 INDEPENDENTLY_CONFIRMED_SHA256 --acknowledgment reviewer-ack.json
```

The output is create-only and contains checksums linking the package, fingerprint, and replay result. **Reviewer ID, date, and notes are self-declared and editable by someone who can regenerate the checksum.** This acknowledgment is not digitally signed, timestamp-attested, or proof of reviewer identity or independence. Do not treat successful software replay as external evidence authenticity or scientific validity.
