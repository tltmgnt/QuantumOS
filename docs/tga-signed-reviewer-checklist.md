# Independent reviewer checklist: signed portable TGA audit handoff

This checklist is for a reviewer evaluating an externally supplied, **potentially untrusted** portable handoff. Passing software checks establishes internal consistency and, when used, possession of a particular signing key. It does **not** independently establish real-world reviewer identity, registration authenticity, independence, evidence provenance, or scientific validity.

## 1. Prepare the review environment

- [ ] Use a controlled Python 3.11+ environment and install the repository from a reviewed commit.
- [ ] If verifying signatures, install the optional `cryptography` dependency.
- [ ] Keep the received `handoff/` separate from locally trusted key records.
- [ ] Record the repository commit and commands used for review.

## 2. Confirm the unsigned baseline

- [ ] Inspect the six `handoff/study/*.json` inputs and the saved inventory.
- [ ] Run full portable replay, not checksum-only/offline bundle verification:

```sh
python -m quantum_omega.gap_portable_handoff_verify_cli handoff/ --inventory handoff-inventory.json
```

- [ ] Require successful exit and check `study_inputs_replayed` and `portable_handoff_bytes_match` in the output.
- [ ] Treat the external-authenticity and independent-scientific-validation flags as **false**, even after successful replay.

## 3. Establish a trusted public-key fingerprint independently

- [ ] Obtain the expected SHA-256 fingerprint of the raw 32-byte Ed25519 public key from an authenticated channel **outside** the received handoff.
- [ ] Record who provided the fingerprint, by what channel, and how their authority was verified.
- [ ] Do not use a public key or fingerprint included in the received package as its own trust anchor.
- [ ] Store the key pin in a reviewer-controlled directory, outside `handoff/`:

```sh
python -m quantum_omega.gap_trusted_key_pin_cli pin --public-key-hex KEY_HEX --expected-sha256 INDEPENDENTLY_CONFIRMED_SHA256 --output trusted-key.json
```

The pinning command refuses to overwrite an existing pin. Protect the file and containing directory from unauthorized replacement.

## 4. Verify the signed handoff with the independent fingerprint

- [ ] Verify the complete handoff using the pinned key and **re-enter** the independently confirmed fingerprint:

```sh
python -m quantum_omega.gap_trusted_key_pin_cli verify handoff/ --inventory handoff-inventory.json --signature handoff-signature.json --pinned-key trusted-key.json --expected-sha256 INDEPENDENTLY_CONFIRMED_SHA256
```

- [ ] Require successful exit and `manifest_signature_valid: true`.
- [ ] Verify the fingerprint is the one authenticated in step 3, not copied from the local pin record.
- [ ] Stop and investigate any mismatch; do not silently replace the trusted pin.

## 5. Complete independent, non-software review

- [ ] Authenticate the signer's real-world identity and authority separately.
- [ ] Investigate reviewer independence, affiliations, and conflicts of interest.
- [ ] Confirm registration claims and dates with the external registry, if applicable.
- [ ] Validate external evidence provenance and scientific conclusions through appropriate independent review.
- [ ] Record unresolved questions and the provenance of each external verification.

## 6. Preserve the review record

- [ ] Save the command outputs, inventory, signature envelope, expected fingerprint and independent source record, software commit, and review date.
- [ ] Preserve a clear distinction between `manifest_signature_valid` and **identity authenticated**.
- [ ] Do not publish a successful signature check as proof of scientific validity.

## Synthetic rehearsal

Use `python -m quantum_omega.gap_signed_reviewer_demo /tmp/tga-signed-demo` to rehearse the workflow. Its `DEMO-public-key.hex` is generated and delivered with the demonstration, so **it is not independently trusted**. A successful rehearsal verifies only the software path.

Related guides: `docs/tga-independent-reviewer-quickstart.md`, `docs/tga-portable-handoff-signature.md`, `docs/tga-trusted-key-pinning.md`, `docs/tga-verification-fingerprint.md`, and `docs/tga-signature-trust-boundaries.md`.
