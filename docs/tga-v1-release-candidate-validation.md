# v1.0 software release candidate validation

The final planned development milestone adds a machine-readable local acceptance report. It does **not** publish a release, create a version tag, or attest to external scientific or security review.

Run from a clean checkout of the intended candidate commit with `cryptography` installed:

```sh
python -m unittest discover -s tests -v
python -m quantum_omega.gap_v1_release_candidate --repository .
```

The validator records the current commit, checks for a clean Git working tree, and runs the end-to-end acceptance, reproducibility/security, and release-guide suites. Skipped acceptance tests and failed tests block the local software readiness flag. Use `--output report.json` to write a new report file (create-only); write outside the repository to avoid making the tree dirty before validation.

## Final release decision

- [ ] Both CI workflows green for the **exact** final candidate commit.
- [ ] Full Python test suite green in a fresh environment, with optional cryptography installed.
- [ ] Local release candidate report passes with no skipped acceptance tests.
- [ ] Security checklist and unresolved issues reviewed by a human maintainer.
- [ ] Version number, supported platforms, release notes, and provenance recorded.
- [ ] Only then decide whether to tag and publish a **research software prototype v1.0** release.

A locally successful report **does not** establish CI status, external evidence authenticity, reviewer identity, reviewer independence, a completed independent security audit, or scientific validity. These fields remain false by design.
