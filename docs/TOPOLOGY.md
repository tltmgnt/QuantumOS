# Structural gap analysis

This initial TGA-Ω component operates on a single verified event-log snapshot. It does not implement a scientific state-space metric, mathematical topology, physical gap taxonomy, or autonomous research prioritization.

| Report field | Meaning |
|---|---|
| claim_count | All registered claims |
| relation_count | All retained relations, including rejected assertions |
| isolated_claims | Claims incident to no non-rejected relation of any type |
| dependency_cycle_components | Strongly connected dependency groups with more than one node |
| asserted_contradictions | Non-rejected contradicts relation IDs |
| dependency_path | Optional directed shortest path and hop count |

Dependency traversal follows source → target for depends_on and derived_from assertions only. Rejected relations are excluded; other labels, including speculative assertions, remain traversable. A prediction derived_from a model therefore points toward the model. Supports and contradicts are not dependency steps. Paths do not prove derivability or support, and a recorded contradiction need not be a real inconsistency.

BFS uses lexicographically sorted neighbors for deterministic shortest-path ties. Unreachable targets return null path and null hop count. A node to itself returns a one-node path with zero hops. Unknown endpoints and incomplete source/target pairs are errors. Iterative strongly connected component analysis avoids recursion-depth limits. A component is a cycle group, not an enumeration of every simple cycle.

The CLI requires an existing database and opens SQLite in read-only mode. Integrity or schema failures exit nonzero. ScientificMemory.snapshot returns immutable record tuples from one verified replay; the analysis API does not mutate them. Other writers may commit after a snapshot, so results describe that snapshot rather than a continuously current graph. Existing hash-chain limits apply.

Run the complete local workflow from the repository root with a new database path:

```sh
python -m quantum_omega.ingestion examples/research_bundle.json --database research-import.sqlite3
python -m quantum_omega.topology --database research-import.sqlite3 --source toy-prediction --target toy-model
python -m unittest discover -s tests -v
```

The fixture produces a one-hop dependency path; it makes no physical discovery claim. State-transition dynamics, weighted gap metrics, agent routing, theory generation, and empirical verification remain future work.
