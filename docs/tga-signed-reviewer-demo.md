# Signed independent-reviewer demonstration (synthetic)

Install the optional signature-verification dependency:

```sh
python -m pip install cryptography
```

Create a disposable demonstration package:

```sh
python -m quantum_omega.gap_signed_reviewer_demo /tmp/tga-signed-demo
```

This builds the complete synthetic portable handoff and inventory, generates a fresh **ephemeral Ed25519 private key in memory**, signs the inventory, and verifies the resulting signature. The private key is **never written to disk**.

The output contains `handoff/`, `handoff-inventory.json`, `handoff-signature.json`, and `DEMO-public-key.hex`. To replay the signature check:

```sh
python -m quantum_omega.gap_portable_handoff_signature_cli /tmp/tga-signed-demo/handoff --inventory /tmp/tga-signed-demo/handoff-inventory.json --signature /tmp/tga-signed-demo/handoff-signature.json --trusted-public-key-hex "$(cat /tmp/tga-signed-demo/DEMO-public-key.hex)"
```

**Important:** The public key in this synthetic demonstration is distributed alongside the signature and therefore is **not independently trusted**. It only exercises cryptographic correctness. For a real review, obtain the expected public key through an authenticated, out-of-band channel, and separately verify the signer's identity, independence, evidence provenance, and scientific claims.

A valid demo signature never means that the signer's real-world identity or the scientific conclusions were verified.
