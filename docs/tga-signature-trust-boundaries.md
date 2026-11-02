# Signed-handoff adversarial trust-boundary tests

Run with the optional Ed25519 dependency:

```sh
python -m pip install cryptography
python -m unittest tests.test_gap_signature_trust_boundaries -v
```

The tests create a synthetic signed portable handoff and cover:

- Attacker-generated replacement keys and signatures.
- Signatures over unrelated messages.
- Altered signature envelope metadata and invalid base64.
- Changed study inputs, local evidence, and signed inventory data.

**Pinned-key security property:** A replacement signature generated with an attacker's private key must fail against the previously pinned public key, even when the attacker updates the signature envelope. A deliberately separate control confirms that supplying the attacker's own public key can make the forged signature cryptographically valid. That control is intentional: a valid signature is not an identity check when the trust anchor is attacker-controlled.

These tests do not establish real-world reviewer identity, independent affiliation, registration authenticity, or scientific validity. Production trust anchors must be authenticated independently of the received package.
