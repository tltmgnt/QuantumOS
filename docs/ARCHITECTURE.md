# Architecture and implementation boundaries
The supplied paper states twelve principal subsystems but enumerates fifteen specialist agents. This repository treats agents as roles within broader services; subsystem boundaries remain a design decision.

| Service | Proposed responsibility | Current implementation |
|---|---|---|
| Ingestion | Measurements, literature, citations, constraints | Strict local JSON source/claim/relation bundle import |
| Knowledge | Claims, ontology, evidence, epistemic labels | Claim records, labels, controlled source domains, and persistent typed claim relationships |
| TGA-Ω | Typed state graph, weighted transitions, gap metrics | Read-only unweighted dependency paths and cycle components |
| Gap engine | Classify missing mathematical/physical/evidential links | Structural review prompts: isolates, dependency cycles, asserted contradictions |
| Agent orchestration | Fifteen specialist research roles | Not implemented |
| Theory factory | Assumptions, models, predictions, falsifiers | Specification only |
| Validation | Mathematics, quantum, gravity, independent review | Sequential stage checks only |
| Computation | Symbolic, numerical, circuit, tensor adapters | Not implemented |
| Criticism | Red-team and counterfactual analysis | Not implemented |
| Competition/planner | Rank theories and next actions | Action ranking only |
| Experiment interface | Distinguishing tests under budget | Not implemented |
| Memory/ledger | Versioned history and provenance | In-memory ledger plus transactional SQLite event history |

Proposed event envelope: event ID, run ID, claim ID, actor identity, timestamp, event type, input artifact hashes, output artifact hashes, software/model versions, epistemic status, and human authorization reference when required. This envelope is a target interface, not implemented serialization.

The graph must distinguish a weighted concept graph from a mathematical topology. Specify the state space, admissible transitions, distance or pseudometric, units, uncertainty estimates, and validation procedure before treating gap scores as meaningful.

Planner estimates require calibrated units or normalized scales. Cost and risk need a documented common scale. Information gain and uncertainty reduction may overlap; avoid double-counting. Reject non-finite estimates and a zero denominator. Tie-breaking in the prototype uses input order.

Independent verification should run in a separate environment with independent methods and blinded inputs where practical. No cloud calls, external model invocation, or experiment execution occur in this scaffold.
