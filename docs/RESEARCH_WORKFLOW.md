# End-to-end reference workflow

The implementation covers software interfaces across all eight roadmap phases in a deliberately restricted domain: deterministic dimensionless polynomials over exact rational numbers. It is a runnable research architecture demonstration, not a quantum-gravity solver or an accepted scientific discovery.

## Run and verify

From a checkout with Python 3.11 or later, using a new output directory:

```sh
python -m quantum_omega run examples/polynomial_research.json --output research-runs/demo
python -m quantum_omega verify-run research-runs/demo
python -m unittest discover -s tests -v
```

No third-party runtime packages, model API keys, cloud services, or network access are required. The existing ingestion and topology CLIs remain available. Reusing an output directory is rejected; existing data is never overwritten. Review experiment-proposal.json locally; nothing is sent to anyone or executed in a laboratory.

## Task schema

The root requires exactly schema_version, title, coefficient_values, max_degree, training, holdout, probes, action_budget, and experiment_budget. See the example JSON.

- schema_version is integer 1; title is nonempty text.
- coefficient_values is a nonempty grid of at most 32 integers or fraction strings, such as `"1/2"`; decimal floats are rejected.
- max_degree is an integer from 0 through 3. At most 512 coefficient combinations are allowed. Trailing zero coefficients are normalized.
- training and holdout each contain 1–128 `{ "x": ..., "y": ... }` records with rational literals. Repeated x values and overlapping split x values are rejected.
- probes contains 1–128 rational literals for counterfactual analysis and experiment design.
- Budgets are finite nonnegative values up to 1000 in configured demo units. Each selected workflow action costs one unit; source ingestion and bounded candidate enumeration are not charged to this action budget. This is not a wall-clock or laboratory budget.

Inputs are data, never Python expressions; there is no eval, shell execution, arbitrary plugin loading, or generated-code execution.

## Operating sequence

1. Validate the task and bounded search size before creating output.
2. Capture canonical task data, interpreter metadata, and source-module hashes.
3. Generate candidate polynomial records with assumptions, model, prediction semantics, falsification conditions, and computational representation.
4. Register task sources, hypotheses, and dependency edges in the scientific ledger; progress sequentially through D0, D1, and D2.
5. Select the next admissible local workflow action under the remaining budget; persist its proxy scores and decision. The current agenda is verification, experiment proposal, then holdout evaluation. This is a bounded scheduled policy, not a general autonomous scientist.
6. Verify training samples with exact arithmetic and two evaluation implementations. Check a restricted product-rule identity in Q[x] where supported. Preserve counterexamples and reject failed hypotheses. Evaluate coefficient-removal counterfactuals. Training-consistent hypotheses progress to D3/D4 with artifact references.
7. Propose a distinguishing probe by maximizing outcome entropy under a uniform candidate prior and a configured cost cap. Leave it awaiting_human_review. There is no execution adapter or automatic approval mechanism.
8. Persist candidate ranking and its hash before evaluating holdout observations. Preserve the initial champion's result. Any later selection based on those observations is explicitly adaptive and requires fresh data.
9. Reject contradicted hypotheses, record recovery requirements, analyze the resulting graph, and emit a milestone and discovery-criterion report.
10. Close SQLite and write an artifact manifest. verify-run checks retained event history, file checksums, tracked filenames, and registered source fingerprints.

## Expected example result

The factory enumerates 27 models. Training points (0,0) and (1,1) retain a linear and a quadratic model. The simpler pre-holdout champion is linear and fails at x=2 and x=3; that failure is intentionally retained. The quadratic remains a hypothesis at D4. One bit of distinguishing information is available from a suitable proposed noiseless probe under the uniform two-model prior. This proposal is never executed.

Expected report values: candidate_count=27, training_survivor_count=2, rejected_count=26, highest_stage=4, benchmark_champion_passed=false, scientific_discovery=false. Workflow completion means the software sequence completed, not that the scientific benchmark passed. A failed candidate or baseline is a valid research outcome.

## Artifacts and scientific boundaries

| Artifact | Purpose |
|---|---|
| task.json, runtime.json | Inputs, task fingerprint, runtime and code fingerprints |
| theories.json | Assumptions, models, predictions and falsifiers |
| plan-*.json | Bounded action decisions, proxy values and budgets |
| training-verification.json | Exact-sample checks, restricted certificates, counterexamples |
| simulation-counterfactuals.json | Coefficient-removal prediction changes |
| experiment-proposal.json | Distinguishing probe, assumptions, cost and pending review |
| pre-holdout-ranking.json | Candidate order committed before evaluation |
| benchmark.json | Holdout scores and failed baseline |
| recovery.json | Rejected candidates and fresh-evidence requirements |
| topology.json | Structural graph review prompts |
| memory.sqlite3 | Persistent claims, sources, links, stages and rejection history |
| report.json | Outcome, limits, milestones and explicit non-discovery status |
| manifest.json | Local checksums and threat model |

A zero action budget emits a partial report and no benchmark. No surviving models also yields a partial research outcome. Unexpected failures leave FAILED.json without a completed manifest. Timestamps and SQLite bytes can differ across equivalent runs; the semantic report and deterministic theory/benchmark artifacts are reproducible.

Polynomial coefficient identities are not a general theorem prover. Shared-author evaluators are not independent replication. Public synthetic holdouts are not Ω3 blind research. Algebraic fitting is not quantum or gravity validation. No D5/D6 promotion, empirical support, novelty, or solved-quantum-gravity claim is generated. External independent review and actual scientific discovery cannot be completed by marking software tasks passed.

The manifest and database are local and unsigned. An attacker who rewrites both coherently can defeat checks. Production deployment requires identity, access control, external trusted checkpoints, and independently controlled evaluation environments. Fingerprints capture source bytes but do not archive an entire interpreter or operating-system image.
