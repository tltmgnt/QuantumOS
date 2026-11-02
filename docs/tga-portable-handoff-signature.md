# Optional Ed25519 portable-handoff signature verification

Install the optional dependency:

```sh
python -m pip install cryptography
```

This verifier accepts an externally created **detached Ed25519 signature** over the canonical portable inventory. The signed bytes are:

```python
b"QUANTUM-OMEGA portable handoff manifest Ed25519 v1\\x00" + json.dumps(inventory, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
```

The literal Python byte-string above ends in a NUL separator (the `\\x00` escape). The JSON signature envelope must have exactly:

```json
{
  "schema_version": 1,
  "kind": "tga_portable_manifest_signature",
  "algorithm": "Ed25519",
  "manifest_sha256": "<inventory sha256>",
  "public_key_sha256": "<SHA256 of raw 32-byte Ed25519 public key>",
  "signature_base64": "<base64 of raw 64-byte Ed25519 signature>"
}
```

Verify with a raw 32-byte public key (64 hex characters) acquired through a **separately authenticated channel**:

```sh
python -m quantum_omega.gap_portable_handoff_signature_cli handoff/ --inventory handoff-inventory.json --signature handoff-signature.json --trusted-public-key-hex YOUR_TRUSTED_PUBLIC_KEY_HEX
```

The command first performs full study/audit replay and byte checks, then validates the detached signature against the supplied key. It exits nonzero for mismatches. The verifier never generates or stores private keys.

**Trust boundary:** A valid signature proves that the signer controlled the private key corresponding to the pinned public key. It does **not** establish who that person is, whether they are independent, whether registration or evidence is genuine, or whether scientific claims are valid. A public key supplied by the same untrusted handoff is not independently trusted.
