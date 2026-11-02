# Local reviewer evidence-file integrity verification

This command checks that files referenced by the [reviewer evidence index](tga-reviewer-evidence-index.md) exist under a local evidence directory and match their recorded SHA-256 digests:

```sh
python -m quantum_omega.gap_reviewer_evidence_files_cli --acknowledgment reviewer-acknowledgment.json --index reviewer-evidence-index.json --evidence-dir /private/reviewer-evidence
```

Locators must be relative paths with no traversal, symlinks, or special files. The checker rejects mismatching or missing files and reports the number of references checked.

**Important:** Matching a file to a digest stored in a self-declared index establishes only consistency of local bytes with that index. It does not authenticate the original source, establish the reviewer's identity or independence, or prove the evidence is genuine. Zero references produce a vacuous byte-match result with `checked_reference_count: 0`, not evidence of completed review. Keep confidential identity and conflict records in access-controlled storage, not the public repository.

For high-assurance environments, run on a trusted, immutable snapshot: concurrent changes to directory components are outside this simple local-file verifier's threat model.
