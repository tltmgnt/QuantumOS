# v1 end-to-end software acceptance criteria

The automated acceptance suite runs a synthetic two-signer reviewer workflow end to end. It creates a portable signed handoff, verifies the original handoff and reviewer acknowledgment using separately pinned handoff and reviewer keys, and checks locally stored evidence bytes against a checksum-bound reviewer evidence index.

```sh
python -m pip install cryptography
python -m unittest tests.test_gap_v1_end_to_end_acceptance -v
```

## Required software acceptance gates

1. Synthetic handoff and reviewer signatures verify against supplied independent fingerprint inputs.
2. Reviewer acknowledgment matches replayed package and original study/evidence inputs.
3. At least one synthetic reviewer evidence file matches its indexed SHA-256.
4. Changed handoff evidence, altered local evidence, missing evidence, and wrong reviewer fingerprints fail verification.
5. Every result keeps external evidence authenticity, reviewer identity, and reviewer independence explicitly unverified.

**Not a scientific acceptance test:** All keys and records are generated locally for software testing. These tests cannot establish actual external key authentication, reviewer identity or independence, registration chronology, authentic source evidence, or scientific validity. Those require separate real-world verification.
