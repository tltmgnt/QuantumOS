# Portable signed reviewer receipt package

The package combines the portable inventory, detached signature envelope, and replay-verifiable reviewer receipt in a single JSON file. **It does not embed a trusted public key or an expected fingerprint.** A recipient must obtain the fingerprint independently and retain a reviewer-controlled trusted-key pin.

Create after authenticating the expected fingerprint:

```sh
python -m quantum_omega.gap_portable_reviewer_receipt_package_cli create handoff/ --inventory handoff-inventory.json --signature handoff-signature.json --pinned-key trusted-key.json --expected-sha256 INDEPENDENTLY_CONFIRMED_SHA256 --output reviewer-package.json
```

Transfer `handoff/` and `reviewer-package.json` to another reviewer. The recipient independently authenticates the key fingerprint, creates their own local trusted-key pin, then verifies:

```sh
python -m quantum_omega.gap_portable_reviewer_receipt_package_cli verify handoff/ --package reviewer-package.json --pinned-key recipient-trusted-key.json --expected-sha256 INDEPENDENTLY_CONFIRMED_SHA256
```

Verification recomputes the package checksum and **replays the original handoff and detached signature**, rather than trusting the receipt's claims. The package checksum is not a signature or external timestamp. Real-world signer identity, reviewer independence, evidence provenance, and scientific validity still require external investigation.
