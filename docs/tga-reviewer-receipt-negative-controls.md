# Signed reviewer receipt adversarial controls

Run:

```sh
python -m pip install cryptography
python -m unittest tests.test_gap_reviewer_receipt_negative_controls -v
```

The suite replays a signed synthetic reviewer handoff and tests that:

- Changing receipt hashes, success flags, or identity/scientific-authenticity flags is rejected **even after recomputing the receipt's own checksum**.
- Replacing the signature envelope or the portable inventory fails full input-backed verification.
- Substituting both the pinned key and its stored fingerprint fails when the verifier still receives the independently expected original fingerprint.

The receipt is not a timestamped or separately signed independent attestation. A matching receipt proves only that the recorded software verification can be reproduced under the supplied trust inputs. Authenticating those inputs, real-world identity, reviewer independence, and scientific validity remains external.
