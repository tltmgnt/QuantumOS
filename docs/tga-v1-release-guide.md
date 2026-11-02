# QUANTUM-Ω / TGA-Ω research software prototype v1.0 release guide

**Status:** Release candidate preparation, not a published v1.0 release. Follow the checklist below and verify the final candidate commit before assigning a version tag.

## Scope

The v1 software prototype provides synthetic reviewer handoff generation, replayable input verification, Ed25519 signed handoffs, separately signed reviewer acknowledgments, portable verification receipts, and a local SHA-256 reviewer evidence index. These are software verification tools. They do not prove scientific hypotheses or authenticate real-world reviewer identity.

## Installation and reproducible checks

In a fresh checkout at a recorded commit, create an isolated Python environment and install the optional signature dependency:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install cryptography
python -m unittest discover -s tests -v
```

Record `python --version`, `python -m pip show cryptography`, `git rev-parse HEAD`, and the CI workflow conclusions for the exact candidate commit. Follow any additional dependency installation instructions in the repository's root README.

Run the synthetic signed reviewer demo and its acceptance controls:

```sh
python -m quantum_omega.gap_signed_reviewer_ack_demo /tmp/tga-v1-synthetic-review
python -m unittest tests.test_gap_v1_end_to_end_acceptance tests.test_gap_v1_reproducibility_security -v
```

The demo uses disposable keys generated in memory. **Do not use demo public keys or locally generated fingerprints as real-world trusted identity anchors.**

## Release acceptance checklist

- [ ] Confirm a clean checkout and record the exact candidate commit SHA.
- [ ] Verify both Python CI workflows pass on that exact commit.
- [ ] Run the full test suite in a fresh supported Python environment.
- [ ] Run the v1 end-to-end acceptance and reproducibility/security tests.
- [ ] Confirm verification fails for modified handoff inputs, altered evidence bytes, wrong expected fingerprints, and forged authenticity claims.
- [ ] Review outstanding issues, dependencies, packaging, license, supported Python versions, and security disclosures.
- [ ] Confirm no private keys, confidential reviewer identity files, or restricted evidence were committed.
- [ ] Review the [security audit checklist](tga-v1-reproducibility-security-audit.md), [reviewer custody checklist](tga-reviewer-key-custody-checklist.md), and [evidence integrity limits](tga-reviewer-evidence-files.md).
- [ ] Clearly distinguish software test completion from external evidence authentication, reviewer independence, and scientific validation.
- [ ] Record release notes, version/tag, and candidate SHA only after the final checks pass.

## Trust boundaries and unresolved external work

The software can verify signatures against **supplied** pinned keys and expected fingerprints, replay recorded inputs, and compare evidence-file bytes with index digests. It cannot independently establish where expected fingerprints came from, whether a named person controls a signing key, whether two keys belong to separate people, whether reviewers are independent, whether evidence originates from a genuine institution, or whether the scientific claims are valid.

A release may be labeled **research software prototype v1.0** after the software release gates pass. It must not be labeled independently scientifically validated without separate documented external review and empirical evidence.
