# Architecture and implementation boundaries
The supplied paper states twelve principal subsystems but enumerates fifteen specialist agents. This repository treats agents as roles within broader services; subsystem boundaries remain a design decision.

| Service | Proposed responsibility | Current implementation |
|---|---|---|
| Ingestion | Measurements, literature, citations, constraints | Strict local JSON source/claim/relation bundle import |
| Knowledge | Claims, ontology, evidence, epistemic labels | Claim records, labels, controlled source domains, and persistent typed claim relationships |
| TGA-Ω | Typed state graph, weighted transitions, gap metrics | Read-only unweighted dependency paths and cycle components |
| Gap engine | Classify missing mathematical/physical/evidential links | Structural review prompts: isolates, dependency cycles, asserted contradictions |
| Agent orchestration | Fifteen specialist research roles | Bounded local workflow; specialist AI agents remain unimplemented |
| Theory factory | Assumptions, models, predictions, falsifiers | Exact-rational polynomial factory with bounded search |
| Validation | Mathematics, quantum, gravity, independent review | Sequential stages, Q[x] checks, exact finite density/unitary and declared Laurent-limit checks; general quantum/GR and independent review pending |
| Computation | Symbolic, numerical, circuit, tensor adapters | Exact polynomial evaluation and coefficient-removal simulations |
| Criticism | Red-team and counterfactual analysis | Exact sample counterexamples, assumption-removal probes, persisted rejection |
| Competition/planner | Rank theories and next actions | Complexity ranking, frozen holdout scores, budgeted action policy |
| Experiment interface | Distinguishing tests under budget | Uniform-prior distinguishing probe proposals; no execution |
| Memory/ledger | Versioned history and provenance | In-memory ledger plus transactional SQLite event history |

Proposed event envelope: event ID, run ID, claim ID, actor identity, timestamp, event type, input artifact hashes, output artifact hashes, software/model versions, epistemic status, and human authorization reference when required. This envelope is a target interface, not implemented serialization.

The graph must distinguish a weighted concept graph from a mathematical topology. Specify the state space, admissible transitions, distance or pseudometric, units, uncertainty estimates, and validation procedure before treating gap scores as meaningful.

Planner estimates require calibrated units or normalized scales. Cost and risk need a documented common scale. Information gain and uncertainty reduction may overlap; avoid double-counting. Reject non-finite estimates and a zero denominator. Tie-breaking in the prototype uses input order.

Independent verification should run in a separate environment with independent methods and blinded inputs where practical. No cloud calls, external model invocation, or experiment execution occur in this scaffold.

The integrated local workflow spans these interfaces in a restricted domain. See RESEARCH_WORKFLOW.md for its sequencing and MILESTONES.md for original acceptance criteria that remain unmet.
