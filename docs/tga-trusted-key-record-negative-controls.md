# Trusted-key record negative controls and custody

Run:

```sh
python -m unittest tests.test_gap_trusted_key_record_negative_controls -v
```

The tests reject malformed pin schemas, invalid key encodings, incorrect fingerprints, unexpected fields, and false claims of software-authenticated identity.

**Important limitation:** A pin file is not an immutable external trust anchor. If an attacker can replace both the public key and its matching fingerprint in the pin record, the record can remain internally valid. The test explicitly demonstrates this boundary. Store pins in reviewer-controlled locations, protect the file and its containing directory, and retain an **independently authenticated fingerprint** outside the handoff. Recheck that fingerprint before accepting a changed pin or when compromise is suspected.

The software cannot authenticate the real-world signer or guarantee the custody of a local trust file.
