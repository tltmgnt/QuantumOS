# Machine-readable signed reviewer verification receipt

The receipt records which portable inventory, signature envelope, and independently fingerprint-checked Ed25519 public key were successfully verified. It is deterministic and SHA-256-bound to the verification result.

Create it only after full signed-handoff replay:

```sh
python -m quantum_omega.gap_reviewer_verification_receipt_cli create handoff/ --inventory handoff-inventory.json --signature handoff-signature.json --pinned-key trusted-key.json --expected-sha256 INDEPENDENTLY_CONFIRMED_SHA256 --output reviewer-receipt.json
```

Verify a saved receipt against the **original inputs**:

```sh
python -m quantum_omega.gap_reviewer_verification_receipt_cli verify handoff/ --inventory handoff-inventory.json --signature handoff-signature.json --pinned-key trusted-key.json --expected-sha256 INDEPENDENTLY_CONFIRMED_SHA256 --receipt reviewer-receipt.json
```

The output file is create-only; it will not silently overwrite an existing receipt. A successful verification means the receipt matches a newly replayed handoff and valid signature under the independently supplied expected key fingerprint.

**Limitations:** The receipt is a reproducible software verification record, **not** a separately signed or timestamped attestation. It does not authenticate the source of the expected fingerprint, the real-world signer identity, external evidence, reviewer independence, or scientific conclusions. A fully coordinated rewrite by an attacker with the signing key and control of trust inputs is outside these checks.
