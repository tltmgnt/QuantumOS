# Signed reviewer acknowledgment verification

A reviewer acknowledgment can be **optionally** signed with a detached Ed25519 signature. The signature covers the full canonical acknowledgment JSON with domain separation (`QUANTUM-OMEGA reviewer acknowledgment Ed25519 v1\\0`). The signature envelope has exactly six fields: `schema_version: 1`, `kind: tga_reviewer_acknowledgment_signature`, `algorithm: Ed25519`, `acknowledgment_sha256`, `reviewer_public_key_sha256`, and `signature_base64`.

A signing application holding the reviewer's private key must produce `signature_base64` by signing `signed_acknowledgment_payload(record)` from `quantum_omega.gap_signed_reviewer_acknowledgment`. This repository's verification CLI **does not accept or persist private keys**.

The recipient must separately authenticate and pin **both** the handoff signer key and the reviewer signer key, and independently confirm both expected SHA-256 fingerprints:

```sh
python -m quantum_omega.gap_signed_reviewer_acknowledgment_cli handoff/ --package reviewer-package.json --acknowledgment reviewer-ack.json --signature reviewer-ack-signature.json --handoff-pinned-key handoff-trusted-key.json --handoff-expected-sha256 INDEPENDENT_HANDOFF_FINGERPRINT --reviewer-pinned-key reviewer-trusted-key.json --reviewer-expected-sha256 INDEPENDENT_REVIEWER_FINGERPRINT
```

The command replays the signed handoff and acknowledgment before verifying the reviewer signature. A valid signature establishes possession of the reviewer's private key, **not** the reviewer's real-world identity, independence, timestamp authenticity, or scientific validity. Key provenance and authorization require external evidence.
