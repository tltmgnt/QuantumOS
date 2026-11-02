# Reviewer public-key pinning

A signature is only as trustworthy as the public key used to verify it. **Obtain and authenticate the expected SHA-256 fingerprint independently of the received handoff**, for example through a previously verified organizational channel. Never copy the expected fingerprint from the same untrusted package as the key.

Install optional Ed25519 support:

```sh
python -m pip install cryptography
```

After independently comparing the fingerprint, pin the raw Ed25519 public key in a separate file:

```sh
python -m quantum_omega.gap_trusted_key_pin_cli pin --public-key-hex KEY_HEX --expected-sha256 INDEPENDENTLY_CONFIRMED_SHA256 --output trusted-key.json
```

The command checks the 32-byte key against the independently supplied SHA-256 and refuses to overwrite an existing pin.

Verify the portable handoff using that saved key:

```sh
python -m quantum_omega.gap_trusted_key_pin_cli verify handoff/ --inventory handoff-inventory.json --signature handoff-signature.json --pinned-key trusted-key.json
```

Store `trusted-key.json` outside the received handoff directory. Protect it against unauthorized replacement and retain a separate record of how the fingerprint was authenticated. The pinned-key file itself is **not** a certificate or proof of identity. The software cannot tell whether a reviewer actually performed out-of-band identity checks; successful verification establishes key possession and input-backed consistency only.
