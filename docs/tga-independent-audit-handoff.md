# Independent TGA-Ω study audit handoff

This procedure is for independent reviewers receiving a six-file external study submission. Passing software checks **does not** prove preregistration, reviewer independence, empirical accuracy, or scientific validity.

## 1. Assemble the immutable input set

Put exactly these six JSON files in a new directory, with no additional files or symlinks:

- `protocol.json`
- `priority.json`
- `evidence.json`
- `labels.json`
- `reviewers.json`
- `study.json`

Retain the original byte sequences and document who supplied them, by what channel, and when. Keep audit outputs **outside** this directory.

## 2. Validate and export audit artifacts

```sh
python -m quantum_omega.gap_study_package_cli STUDY_DIR --output full-evaluation.json
python -m quantum_omega.gap_study_package_cli STUDY_DIR --summary --output review-summary.json
python -m quantum_omega.gap_study_inventory_cli create STUDY_DIR --output inventory.json
python -m quantum_omega.gap_audit_bundle_cli export STUDY_DIR --output audit-bundle.json
```

Each output is create-only: use fresh filenames, not existing output paths. Record the exact QuantumOS Git commit and Python runtime used. Record SHA-256 hashes of exported artifacts through a separately retained channel.

## 3. Exchange and verify

Transmit the six input files, the audit bundle, and separately recorded digests to the auditor using an agreed transfer mechanism. The auditor should independently compute checksums, compare them with the independently transmitted digest record, and run:

```sh
python -m quantum_omega.gap_audit_bundle_cli verify STUDY_DIR --bundle audit-bundle.json
python -m quantum_omega.gap_study_inventory_cli verify STUDY_DIR --inventory inventory.json
python -m quantum_omega.gap_audit_bundle_cli verify-offline --bundle audit-bundle.json
```

The `verify` command revalidates the supplied study package. `verify-offline` checks only the saved bundle's internal structure and hashes; it does **not** replay the inputs.

## 4. Independent evidence review (outside software checks)

A qualified external reviewer must independently inspect:

1. Preregistration existence and trusted timestamp evidence, from the registry itself.
2. Reviewer identities, independence, conflicts, and eligibility, using external records.
3. Origin and collection process for held-out labels and adjudications.
4. Whether the study was prospectively specified, with deviations disclosed.
5. Scientific relevance of comparisons, baseline methods, sample size, uncertainty, and reproducibility.

Document every unsupported or unresolved claim. A self-reported registration timestamp or reviewer ID is not independently verified evidence.

## 5. Sign-off record

Record the study identifier, evaluation set identifier, exact commit SHA, original file digests, audit-bundle digest, independent verifier name/organization, date, verification steps, exceptions, and separate scientific assessment. If authenticity or scientific review is incomplete, label it **unverified** rather than **passed**.

**Security boundary:** SHA-256 digests are not signatures or trusted timestamps. An attacker able to replace both a bundle and its digest can make internally consistent replacements. A separately trusted digest record or authenticated signature is needed for stronger handoff integrity.
