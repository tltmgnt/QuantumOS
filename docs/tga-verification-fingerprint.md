# Verify a pinned key against an independent fingerprint every time

The `verify` command now **requires** `--expected-sha256`. Obtain this 64-character lowercase SHA-256 fingerprint from a separately authenticated source, not from the pin record or received handoff:

```sh
python -m quantum_omega.gap_trusted_key_pin_cli verify handoff/ --inventory handoff-inventory.json --signature handoff-signature.json --pinned-key trusted-key.json --expected-sha256 INDEPENDENTLY_CONFIRMED_SHA256
```

The command compares the independently supplied fingerprint with the raw public key loaded from the local pin **before** signature verification. This catches a replacement where an attacker changes both the key and the fingerprint stored in the pin file.

**Limit:** The CLI cannot determine whether the supplied expected fingerprint was truly authenticated out of band. If an attacker controls both the pin and the user's expected fingerprint, cryptographic validation alone cannot identify the substitution. Maintain independent fingerprint custody and review identity evidence separately.
