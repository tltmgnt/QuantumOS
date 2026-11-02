# Assessment, deliverables, and GitHub review rubric

This curriculum is evaluated on reproducibility and clarity of epistemic boundaries, not on claims of scientific discovery.

## Standard lab evidence template

Copy into a learner-owned Markdown note or PR description:

```md
## Module NN — title
- Repository commit SHA:
- Python version / cryptography version:
- Environment and OS:
- Commands executed:
- Exit status and key observed output:
- Artifact paths and relevant hashes:
- Negative control / expected failure:
- What this establishes:
- What this does NOT establish:
- Open questions / proposed follow-up:
```

Do not commit generated databases, private keys, real reviewer credentials, or sensitive evidence. Prefer synthetic fixtures and paths under a disposable scratch directory.

## Review rubric (100 points)

| Criterion | Points | Evidence |
|---|---:|---|
| Reproducible setup and exact-commit provenance | 15 | environment manifest and test results |
| Architecture, governance, and trust boundaries | 15 | system map and explicit limitations |
| Ingestion, memory, and graph reasoning | 15 | replay and assertion/proof distinction |
| Model generation, evaluation, and validators | 20 | trace, holdout discipline, scoped results |
| Signed handoff and evidence integrity | 15 | key separation, digest and signature interpretation |
| Negative controls and fail-closed behavior | 10 | mutation/substitution observations |
| Release readiness and responsible reporting | 10 | software go/no-go with external gates separated |

**Suggested passing threshold:** 80/100, with no critical safety/trust-boundary error. A score is an internal learning assessment, not an external accreditation.

## Required capstone package

1. An end-to-end diagram linking source ingestion, candidate evaluation, artifact verification, reviewer receipt, and release report.
2. A command log on one pinned commit, including failures and skipped-test count.
3. A reproducibility table identifying inputs, outputs, checksums, and expected changes under mutation.
4. A comparison proposal for topology-governed ranking: explicit baseline, dataset, ranking metric, ablation, null hypothesis, and failure criterion. Do **not** invent performance results.
5. A reviewer trust-boundary note explaining identity, independence, evidence authenticity, and key-custody gaps.
6. A release go/no-go memo distinguishing passed local software gates from unperformed external reviews.

## Suggested GitHub issue / PR structure

- Issue title: `Curriculum module NN: <topic>`
- PR title: `docs: complete QuantumOS curriculum module NN`
- PR scope: Markdown documentation only.
- Review checklist: commands reproducible; links resolve; no private keys; synthetic evidence labeled; scientific claims properly scoped; outstanding gaps explicit.
- Review outcome: accept learning evidence, request corrections, or defer if critical provenance is missing.

## Completion criteria

A learner can reconstruct the software verification story from a pinned input and commit, identify at least three fail-closed cases, and specify a defensible independent benchmark for TGA-Ω. Completion does **not** imply that the benchmark has been executed or that quantum gravity has been solved.
