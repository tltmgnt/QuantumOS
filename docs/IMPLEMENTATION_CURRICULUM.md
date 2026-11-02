# QuantumOS end-to-end implementation curriculum

**Format:** GitHub-native, documentation-only, self-paced learning path. **Audience:** Python developers, computational researchers, technical reviewers. **Prerequisites:** Python 3.11+, Git, virtual environments, JSON, basic testing and hashing. Cryptographic reviewer exercises require `cryptography`.

**Outcome:** Understand and reproduce the implemented research-software workflow, explain its trust boundaries, and design defensible extensions. This is not a course in established quantum-gravity discovery and does not certify scientific validity.

## Learning route (12 modules, approximately 6–10 weeks)

| Module | Topic | Hands-on deliverable | Completion gate |
|---|---|---|---|
| 00 | Repository orientation and environment | Recorded commit, Python environment, baseline tests | Commands reproducible on clean checkout |
| 01 | Epistemic governance and architecture | Claim-stage and service-boundary map | Distinguish software evidence from scientific acceptance |
| 02 | Ingestion and provenance | Import example bundle and inspect source IDs | Explain source trust and duplicate handling |
| 03 | Scientific memory and knowledge graph | Create claim/relation and verify history | Identify assertion vs inferred proof |
| 04 | Structural gap and topology concepts | Annotated topology design exercise | Separate proposed design from implemented behavior |
| 05 | Theory generation and criticism | Run polynomial research example | Explain candidate retention and rejection |
| 06 | Planning, benchmarks, and holdouts | Trace decision and holdout evidence | Avoid leakage and unsupported discovery claims |
| 07 | Quantum and classical-limit validators | Run both exact-check demos | Explain constraints vs physical validation |
| 08 | Reproducible evaluation and audit chain | Verify a run and inspect artifact integrity | Distinguish digest matching from authenticity |
| 09 | Signed portable reviewer handoff | Generate synthetic two-signer handoff | Pin independent expected keys and reject substitutions |
| 10 | Reviewer evidence and adversarial controls | Execute end-to-end and negative tests | Document fail-closed cases and identity limits |
| 11 | Release candidate and responsible publication | Produce local acceptance report and release decision memo | All software gates documented; external gates separately tracked |

Use [module-by-module labs](IMPLEMENTATION_LABS.md) and the [assessment rubric](IMPLEMENTATION_ASSESSMENT.md). Modules are ordered; advanced users can skip lectures but must satisfy gates.

## Recommended GitHub workflow

1. Fork or clone the repository; create a learning branch and record `git rev-parse HEAD`.
2. Read each module's referenced docs **before** running commands. Write observations in a personal lab notebook or draft PR; no changes to production code are required.
3. Keep generated artifacts in ignored or external scratch directories. Most example commands require **new** output directories.
4. For each module, submit a short evidence note: exact commit, environment, command, exit status, key output paths, limitations, and one negative control.
5. Review the note against the rubric. Do not merge claims of external reviewer independence or scientific proof into software acceptance.

## Quick-start lab environment

```sh
git clone https://github.com/tltmgnt/QuantumOS.git
cd QuantumOS
git rev-parse HEAD
python --version
python -m venv .venv
. .venv/bin/activate
python -m pip install cryptography
python -m unittest discover -s tests -v
```

For Windows, activate with `.venv\\Scripts\\activate`. Follow root [README](../README.md) for canonical CLI examples and current prerequisites.

## Curriculum scope

The repository describes a broader proposed agentic operating system than the bounded implemented reference workflow. In particular, topology-governed discovery and general quantum-gravity inference are research directions, not established outputs of this course. The signed reviewer workflow uses synthetic keys and self-declared anchors; passing signatures does not independently establish human identity or reviewer independence.

## Primary source map

- [Architecture](ARCHITECTURE.md), [roadmap](ROADMAP.md), [milestones](MILESTONES.md), [governance](GOVERNANCE.md)
- [Research workflow](RESEARCH_WORKFLOW.md), [ingestion](INGESTION.md), [topology](TOPOLOGY.md)
- [Quantum validation](QUANTUM_VALIDATION.md), [classical limits](CLASSICAL_LIMITS.md)
- [Independent reviewer quickstart](tga-independent-reviewer-quickstart.md), [signed reviewer demo](tga-signed-reviewer-ack-demo.md)
- [End-to-end acceptance](tga-v1-end-to-end-acceptance.md), [reproducibility/security audit](tga-v1-reproducibility-security-audit.md)
- [Release guide](tga-v1-release-guide.md), [candidate validation](tga-v1-release-candidate-validation.md)

**Success standard:** A learner can trace a result from input to verification, reproduce checks, identify what each proof does *not* prove, and state what external evidence would be needed to support stronger scientific claims.
