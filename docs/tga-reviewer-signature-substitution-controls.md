# Adversarial reviewer signature substitution controls

The suite exercises a complete synthetic two-signer handoff and demonstrates the distinction between **valid Ed25519 signatures** and **independently authenticated signer identity**.

Run:

```sh
python -m pip install cryptography
python -m unittest tests.test_gap_reviewer_signature_substitution -v
```

Controls include a new attacker Ed25519 key re-signing the original acknowledgment, coordinated replacement of the local reviewer pin and stored checksum, altered reviewer ID with regenerated acknowledgment checksum, and signature-envelope metadata manipulation.

A forged acknowledgment signed with an attacker key **fails** when checked against the original independently expected reviewer fingerprint. Deliberately supplying the attacker's fingerprint instead allows the signature to verify, but the result still marks real-world identity and reviewer independence as unverified. That positive attacker-key control is a demonstration of a missing external trust anchor, **not** evidence of identity authentication.

In real reviews, obtain the expected reviewer key fingerprint through an independently authenticated channel and retain a separate custody record. Signature verification alone cannot establish reviewer independence, affiliation, date authenticity, or scientific validity.
