# QUANTUM-Ω
## A Topology-Governed Agentic Operating System for Quantum-Gravity Discovery, Explanatory Reasoning, and Scientific Verification

**Research Architecture v1.0 · Reference Software v0.2.2**

> Do not optimize for answers. Optimize for verified explanatory knowledge.

QUANTUM-Ω proposes a research operating system for discovering, formalizing, criticizing, simulating, verifying, and comparing candidate explanations. It does not claim to solve quantum gravity.

This repository contains a dependency-free end-to-end reference implementation in a bounded exact-rational polynomial domain, alongside a condensed technical specification based on the supplied white paper. It connects source ingestion, knowledge graphs, structural gap analysis, theory generation, exact algebra and criticism, budgeted action planning, holdout evaluation, experiment proposals, and persistent scientific memory.

The reference workflow is a software demonstration. It does not implement a general quantum-gravity solver, independently verified scientific discovery, general theorem proving, or laboratory execution. [Milestone status](docs/MILESTONES.md) distinguishes implemented interfaces from scientific acceptance that remains pending.

### Quick start
Requires Python 3.11 or later. From this directory:

```sh
python -m quantum_omega run examples/polynomial_research.json --output research-runs/demo
python -m quantum_omega verify-run research-runs/demo
python -m unittest discover -s tests -v
```

The example generates 27 candidate models, retains failures, and produces a local research report, SQLite ledger, and artifact manifest. The simpler pre-holdout model deliberately fails; the surviving quadratic is retained at D4, without a discovery claim. Output directories must be new. Run `python -m quantum_omega` for the original short governance demo.

See the [workflow guide](docs/RESEARCH_WORKFLOW.md) for inputs, outputs, expected results, and limits.

### Quantum matrix validation

```sh
python -m quantum_omega validate-quantum examples/quantum_constraints.json --output research-runs/quantum-demo
python -m quantum_omega verify-run research-runs/quantum-demo
```

Checks Hermiticity, trace, and positive semidefiniteness of density matrices, and unitarity of square operators. Dimensions 1–4 and exact rational complex entries are supported. Results include exact minors or residuals, source fingerprints, and persistent rejection records. Mathematical constraint failures exit with status 1; malformed input exits with status 2. Passing these checks does not validate a physical theory. See [format and scope](docs/QUANTUM_VALIDATION.md).

### Declared classical-limit checks

```sh
python -m quantum_omega validate-limits examples/classical_limits.json --output research-runs/limit-demo
python -m quantum_omega verify-run research-runs/limit-demo
```

Checks exact finite Laurent expressions as a positive dimensionless parameter tends to zero or infinity. Reports preserve cancellations, finite reference mismatches, and divergent leading terms. This checks supplied asymptotic expressions; it does not demonstrate recovery of Einstein's equations. See [limit-check semantics](docs/CLASSICAL_LIMITS.md).

### Contents
- [Technical specification](docs/WHITE_PAPER.md): condensed version of the supplied research architecture, preserving its 37-section structure.
- [Architecture](docs/ARCHITECTURE.md): proposed services, interfaces, and implementation boundaries.
- [Roadmap](docs/ROADMAP.md): eight phases and acceptance criteria.
- [Scientific governance](docs/GOVERNANCE.md): epistemic status, evidence, independent review, and limitations.
- `quantum_omega/`: ingestion, graph analysis, theory factory, verification, planner, benchmark, experiment design, and workflow modules.
- `tests/`: governance and planner regression checks.

### Persistent scientific memory
The optional SQLite store preserves claims, source identifiers, and stage-transition evidence across restarts, with transactional writes and a hash-linked event history.

```python
from quantum_omega import Claim, Stage
from quantum_omega.memory import ScientificMemory

with ScientificMemory("research.sqlite3") as memory:
    memory.register(Claim("example-001", "Illustrative conjecture", ("local:notes",)))
    memory.advance("example-001", Stage.CONJECTURE, "local:assumptions", "reviewer", "author")
    print(memory.get("example-001"))
    assert memory.verify()
```

Run the example once per new database; duplicate IDs are rejected. Source and artifact references are recorded, not downloaded or validated. The store replays retained events on each operation and is intended for small research logs. Tail truncation, full database rewrites, authenticated identity, and external immutable anchoring are not covered. Back up the database separately.

### Claim knowledge graph
Directed relationships are persisted in the same verified event history:

```python
from quantum_omega import Claim, Relation, RelationType
from quantum_omega.memory import ScientificMemory

with ScientificMemory("graph.sqlite3") as memory:
    memory.register(Claim("model", "Illustrative model claim", ("local:model-notes",)))
    memory.register(Claim("prediction", "Illustrative prediction claim", ("local:prediction-notes",)))
    memory.link(Relation("link-001", "prediction", "model",
                         RelationType.DERIVED_FROM, ("local:derivation",)))
    print(memory.relations("prediction", direction="outgoing"))
    print(memory.history("model"))
```

Relations are user-supplied assertions, not inferred scientific facts. Supported types are `supports`, `contradicts`, `depends_on`, and `derived_from`. Queries return direct edges in insertion order and can filter by `RelationType`. Self-links, missing endpoints, duplicate relation IDs, and missing evidence references are rejected. Cycles between distinct claims are permitted and do not prove valid derivations. Existing databases remain readable; old software cannot replay newly written link events. Ontology ingestion, inference, and topological gap analysis remain future work.

### Structured source ingestion
Import a local, versioned JSON bundle into a new database:

```sh
python -m quantum_omega.ingestion examples/research_bundle.json --database research-import.sqlite3
```

The sample contains illustrative fixtures, not scientific evidence. Reimporting duplicate IDs is rejected. Bundles atomically register source metadata, D0 claims, and typed relations. Claim sources and relation evidence must resolve to registered source IDs; references may reuse sources imported earlier. Unknown fields, source types, domain tags, statuses, and schema versions are rejected. No network requests occur.

Source kinds: `literature`, `observation`, `experiment`, `simulation`, `derivation`. Controlled domains: `mathematics`, `quantum`, `gravity`, `information`, `computation`. This is an initial vocabulary, not a complete physics ontology.

Sources require `id`, `title`, `locator`, `kind`, `domains`, and `content_sha256`. The hash is a supplied fingerprint, not an independently verified download. Retrieve metadata with `memory.get_source(source_id)`. See [ingestion format](docs/INGESTION.md) for validation and compatibility details.

### Structural gap analysis (TGA-Ω prototype)
After importing the example bundle, analyze it without writing to the database:

```sh
python -m quantum_omega.topology --database research-import.sqlite3 --source toy-prediction --target toy-model
```

The JSON report includes isolated claims, dependency cycle components, asserted contradiction IDs, and an optional directed shortest dependency path. Only `depends_on` and `derived_from` edges participate in paths and cycles; rejected edges are excluded. Hop counts measure unweighted graph structure, not explanatory distance or scientific merit. See [analysis semantics](docs/TOPOLOGY.md).

### Research loop
Reality → evidence → representation → gap → conjecture → explanation → criticism → prediction → verification → experiment → knowledge.

### Scientific status
Planner values are supplied estimates, not measured scientific utility. Graph distance alone is not a definition of explanatory progress. A local checksum establishes content integrity only; it does not prove truth, independent replication, or tamper resistance against a privileged writer.

### License
No license has been selected. No third-party use permissions beyond applicable law are granted by this repository. Select a license before distributing it as open source.
