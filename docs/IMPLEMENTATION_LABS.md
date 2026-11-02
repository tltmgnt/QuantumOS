# Implementation labs: guided end-to-end exercises

Run commands from repository root. Use a fresh scratch path for each invocation; paths below are examples and may need unique suffixes. Record exact commit and command outputs. Exercises intentionally use supplied fixtures, not real-world scientific validation.

## 00 — Setup and baseline (half day)

**Read:** [README](../README.md), [milestones](MILESTONES.md). **Do:** `python --version`, `git rev-parse HEAD`, `python -m unittest discover -s tests -v`. Install `cryptography` first to avoid silently skipped cryptographic tests. **Artifact:** environment manifest and full test result. **Gate:** explain why skipped tests cannot count as release evidence.

## 01 — Architecture and scientific governance (half day)

**Read:** [architecture](ARCHITECTURE.md), [governance](GOVERNANCE.md), [roadmap](ROADMAP.md). **Do:** draw a dataflow from ingestion to claim, model, criticism, evaluation, reviewer handoff. Label proposed services versus implemented components. **Artifact:** one-page service/epistemic boundary map. **Gate:** accurately distinguish D0 claims from validated discoveries.

## 02 — Ingestion and source provenance (half day)

**Read:** [ingestion](INGESTION.md). **Do:**
```sh
python -m quantum_omega.ingestion examples/research_bundle.json --database /tmp/quantumos-curriculum-import.sqlite3
```
Use a new database path; rerun on the same database to observe duplicate rejection. **Artifact:** source-ID and failure-mode table. **Gate:** explain why a stored source reference is not an authenticated source.

## 03 — Memory and knowledge graph (one day)

**Read:** README sections on persistent memory and claim graph. **Do:** follow the README's `ScientificMemory`, `Claim`, `Relation`, and `Stage` snippets in a fresh scratch database. Inspect `history`, `relations`, and `verify`. **Artifact:** two claims, one relation, and replay notes. **Gate:** describe how an asserted edge differs from a proven deduction.

## 04 — Structural gaps and topology (one day)

**Read:** [topology](TOPOLOGY.md), [architecture](ARCHITECTURE.md). **Do:** annotate a hypothetical gap between two supported claims; specify graph inputs, edge semantics, candidate ranking criterion, baseline, and a falsifiable benchmark. **Artifact:** design note with assumptions and counterexample. **Gate:** explicitly mark unimplemented ideas and avoid claiming topology improves ranking without a comparative result.

## 05 — Theory generation and criticism (one day)

**Read:** [research workflow](RESEARCH_WORKFLOW.md). **Do:**
```sh
python -m quantum_omega run examples/polynomial_research.json --output /tmp/quantumos-curriculum-research
python -m quantum_omega verify-run /tmp/quantumos-curriculum-research
```
Inspect the report, artifact manifest, and retained failed candidates. **Artifact:** model lineage and rejection summary. **Gate:** explain exact-rational polynomial domain limits and why surviving holdouts do not imply quantum-gravity discovery.

## 06 — Planning, benchmark, and holdout discipline (half day)

**Read:** [research workflow](RESEARCH_WORKFLOW.md), [evaluation example](tga-evaluation-example.md). **Do:** trace how budgeted actions, holdouts, and candidate scoring appear in the demo outputs; design a leakage negative control on paper. **Artifact:** evaluation matrix (input, holdout, metric, expected failure). **Gate:** identify at least one way the result could be overinterpreted.

## 07 — Quantum and classical-limit checks (one day)

**Read:** [quantum validation](QUANTUM_VALIDATION.md), [classical limits](CLASSICAL_LIMITS.md). **Do:**
```sh
python -m quantum_omega validate-quantum examples/quantum_constraints.json --output /tmp/quantumos-curriculum-quantum
python -m quantum_omega verify-run /tmp/quantumos-curriculum-quantum
python -m quantum_omega validate-limits examples/classical_limits.json --output /tmp/quantumos-curriculum-limits
python -m quantum_omega verify-run /tmp/quantumos-curriculum-limits
```
**Artifact:** pass/fail examples and scope statement. **Gate:** distinguish finite exact matrix/asymptotic checks from experimental physics validation.

## 08 — Reproducibility and audit integrity (one day)

**Read:** [provenance replay](tga-provenance-replay.md), [audit chain verification](tga-audit-chain-verify.md), [study inventory](tga-study-file-inventory.md). **Do:** inspect the research-run manifest, compare recorded hashes and verification results, and describe what a mutated artifact should cause. **Artifact:** provenance chain diagram and threat model. **Gate:** distinguish tamper detection from proof of source authenticity.

## 09 — Signed reviewer workflow (one day)

**Read:** [signed demo](tga-signed-reviewer-ack-demo.md), [key pinning](tga-trusted-key-pinning.md), [signature trust boundaries](tga-signature-trust-boundaries.md). **Do:**
```sh
python -m quantum_omega.gap_signed_reviewer_ack_demo /tmp/quantumos-curriculum-signed-review
```
Use only synthetic demo keys. Review handoff signature, separate reviewer acknowledgment, and expected public-key fingerprints. **Artifact:** annotated verification sequence. **Gate:** explain why two signatures do not establish two independent real-world people.

## 10 — Evidence and adversarial acceptance (one day)

**Read:** [evidence files](tga-reviewer-evidence-files.md), [evidence index](tga-reviewer-evidence-index.md), [end-to-end acceptance](tga-v1-end-to-end-acceptance.md). **Do:**
```sh
python -m unittest tests.test_gap_v1_end_to_end_acceptance tests.test_gap_v1_reproducibility_security -v
```
Inspect tests for wrong fingerprints, altered evidence, signer substitution, and self-declared authenticity. **Artifact:** negative-control checklist with observed results. **Gate:** state why file hash matching is not evidence origin authentication.

## 11 — Release candidate (one day)

**Read:** [release guide](tga-v1-release-guide.md), [candidate validation](tga-v1-release-candidate-validation.md). **Do:** run full suite, then:
```sh
python -m quantum_omega.gap_v1_release_candidate --repository .
```
Run from a clean checkout with `cryptography` installed; an untracked local notebook may make the working tree dirty. **Artifact:** candidate JSON report plus human go/no-go memo. **Gate:** verify CI on the *same final commit* separately; document outstanding external audits and do not create a tag or release as a course exercise.

## Capstone

Prepare a reviewable GitHub pull request containing **documentation only**: lab evidence notes, source-to-artifact trace, one negative-control analysis, a proposed TGA-Ω baseline comparison, and a release readiness decision. No secrets, private keys, confidential evidence, or unsupported scientific claims.
