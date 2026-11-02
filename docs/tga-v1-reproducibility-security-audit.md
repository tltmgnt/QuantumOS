# v1 reproducibility and security audit

## Automated controls

Run the end-to-end acceptance and reproducibility regression tests with the optional Ed25519 dependency installed:

```sh
python -m pip install cryptography
python -m unittest tests.test_gap_v1_end_to_end_acceptance tests.test_gap_v1_reproducibility_security -v
```

The tests generate two independent disposable-key demos and confirm each verifies, that their key fingerprints differ, and that private keys are not intentionally emitted as files. They also exercise CLI failure on an incorrect reviewer fingerprint, reject a rehashed false authenticity claim, and verify that zero evidence references never imply authenticated evidence.

## Human audit gates before v1 release

- [ ] Record Python and `cryptography` versions, OS, and exact repository commit; rerun tests in a fresh environment.
- [ ] Confirm all supported CI jobs pass on the exact release-candidate commit.
- [ ] Review key handling and ensure private keys never enter source control, logs, demo artifacts, or command-line arguments.
- [ ] Review path handling for symlinks, traversal, hardlinks, and concurrent filesystem changes; local evidence checking assumes a trusted, stable filesystem snapshot.
- [ ] Review denial-of-service risks from untrusted JSON and large evidence files; apply resource limits at the caller or sandbox boundary.
- [ ] Confirm pinned fingerprints originate from separately authenticated external channels in any real review.
- [ ] Preserve evidence custody and conflicts documentation outside the public repository.
- [ ] Record unresolved security findings and release-blocking failures.

## Audit interpretation

Automated tests are **regression checks, not an independent security audit**. Randomized demo keys mean output fingerprints are intentionally different between runs; reproducibility means the same verification invariants and pass/fail behavior, not byte-identical demo artifacts. No automated test here establishes reviewer identity, real-world independence, source authenticity, chronology, or scientific validity.
