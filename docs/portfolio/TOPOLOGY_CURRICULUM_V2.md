# Topology compatibility and curriculum v2 — QuantumOS

Version 2 adapts the explicit-molecular-graph teaching pattern to this repository's actual role. This is documentation and a learning/decision framework; it introduces no mathematical engine, runtime dependency or operational permission.

## Repository decision

| Question | Repository-specific answer |
| --- | --- |
| Architectural role | application research |
| Minimum useful mathematics | Typed claim graphs and stage transitions; defer new physical topology |
| Relationships to preserve | Claim sources, epistemic labels and governance stages |
| Concrete operation / capstone | Attempt to advance a synthetic claim with missing sources and explain the rejected transition or validation |
| Necessity and scope boundary | Governance stage names do not establish quantum-gravity results or empirical support |

The decision is a source-based recommendation, not measured proof that a new specialty improves this repository. Start with the existing implementation and compare any proposed abstraction against a simpler alternative.

## Six-criterion compatibility scorecard

Complete one scorecard per proposed candidate and per concrete operation. Leave unmeasured entries unknown. Scores are human judgments from 0 (no fit) to 5 (strong evidenced fit); unknown is not zero. Do not sum an incomplete card. A total out of 30 is a heuristic, not adoption approval, and feasibility or necessity can veto a high total.

| Criterion | Score | Required evidence |
| --- | --- | --- |
| Structural compatibility | Not yet scored | Map the repository objects and the relationships above without losing direction, labels, units or missingness. |
| Transformation support | Not yet scored | Demonstrate the capstone operation on accepted and rejected inputs. |
| Invariant preservation | Not yet scored | State the property preserved and supply a counterexample or perturbation. |
| Computational feasibility | Not yet scored | Measure size, time and memory on bounded fixtures; record limits. |
| Integration compatibility | Not yet scored | Verify existing schemas, APIs and neighboring contracts remain compatible. |
| Mathematical necessity | Not yet scored | Compare with typed claim graphs and stage transitions and explain the additional capability, if any. |

## Curriculum

Prerequisites: basic programming, sets, functions and graph vocabulary. Work in six competency-gated sessions, approximately 60–90 minutes each; empirical evaluation is a separate research activity.

| Session | Learning objective | Exercise | Completion evidence |
| --- | --- | --- | --- |
| 1. Model | Identify claim sources, epistemic labels and governance stages. | Draw a minimal valid example and one excluded relationship. | Annotated object/relation inventory with explicit assumptions. |
| 2. Contract | Distinguish schema validity from substantive correctness. | Trace validation and propose malformed, missing and boundary inputs. | Input-to-rejection table grounded in current source. |
| 3. Operation | Explain typed claim graphs and stage transitions; defer new physical topology. | Attempt to advance a synthetic claim with missing sources and explain the rejected transition or validation. | Hand trace compared with existing software, or a clearly labeled specification when no runtime exists. |
| 4. Preservation | State what a transformation must preserve. | Rename identifiers, reorder records, then alter one meaningful relation; predict each effect under the actual contract. | Separate invariant, expected change and unsupported transformation. |
| 5. Comparison | Justify mathematical necessity and cost. | Complete the six-criterion card for the existing approach and one proposed alternative; record unknowns honestly. | Evidence-backed recommendation with baseline and explicit veto conditions. |
| 6. Reproduction | Communicate the bounded result. | Reproduce the capstone using existing offline fixtures and record software version, inputs, outputs and limitations. | Reviewable notebook or report distinguishing computation, replay, independent evaluation and authorization. |

## Source-linked reading laboratory

The table is a guided selection of source lines, not an assertion that the whole repository is covered. Line numbers refer to the inspected source blob `8e095f08260145af1036c297471cbfb0d7200a9d` in [quantum_omega/core.py](../../quantum_omega/core.py). Recheck anchors after source changes.

| Line | Statement | Learning check |
| --- | --- | --- |
| [8](../../quantum_omega/core.py#L8) | `class EpistemicStatus(str, Enum):` | State the input/output contract and trace one normal and one failing case. |
| [17](../../quantum_omega/core.py#L17) | `class Stage(IntEnum):` | State the input/output contract and trace one normal and one failing case. |
| [27](../../quantum_omega/core.py#L27) | `class Claim:` | State the input/output contract and trace one normal and one failing case. |
| [34](../../quantum_omega/core.py#L34) | `def __post_init__(self):` | State the input/output contract and trace one normal and one failing case. |
| [36](../../quantum_omega/core.py#L36) | `raise ValueError("Use explicit stage and epistemic enums")` | Construct the triggering input and explain why rejection preserves the contract. |
| [38](../../quantum_omega/core.py#L38) | `raise ValueError("Claim identifier, text, and provenance are required")` | Construct the triggering input and explain why rejection preserves the contract. |
| [40](../../quantum_omega/core.py#L40) | `class RelationType(str, Enum):` | State the input/output contract and trace one normal and one failing case. |
| [47](../../quantum_omega/core.py#L47) | `class Relation:` | State the input/output contract and trace one normal and one failing case. |
| [55](../../quantum_omega/core.py#L55) | `def __post_init__(self):` | State the input/output contract and trace one normal and one failing case. |
| [57](../../quantum_omega/core.py#L57) | `raise ValueError("Use explicit relation type and epistemic status")` | Construct the triggering input and explain why rejection preserves the contract. |
| [59](../../quantum_omega/core.py#L59) | `raise ValueError("Relation ID and endpoint IDs are required")` | Construct the triggering input and explain why rejection preserves the contract. |
| [62](../../quantum_omega/core.py#L62) | `raise ValueError("Immutable evidence references are required")` | Construct the triggering input and explain why rejection preserves the contract. |
| [64](../../quantum_omega/core.py#L64) | `raise ValueError("Self-relations are not supported")` | Construct the triggering input and explain why rejection preserves the contract. |
| [67](../../quantum_omega/core.py#L67) | `class Ledger:` | State the input/output contract and trace one normal and one failing case. |
| [75](../../quantum_omega/core.py#L75) | `def events(self):` | State the input/output contract and trace one normal and one failing case. |
| [76](../../quantum_omega/core.py#L76) | `return tuple(self._events)` | Predict the returned value and distinguish a computed result from authorization. |
| [78](../../quantum_omega/core.py#L78) | `def _append(self, payload):` | State the input/output contract and trace one normal and one failing case. |
| [82](../../quantum_omega/core.py#L82) | `def claims(self):` | State the input/output contract and trace one normal and one failing case. |
| [83](../../quantum_omega/core.py#L83) | `return tuple(self._claims.values())` | Predict the returned value and distinguish a computed result from authorization. |
| [85](../../quantum_omega/core.py#L85) | `def all_relations(self):` | State the input/output contract and trace one normal and one failing case. |
| [86](../../quantum_omega/core.py#L86) | `return tuple(self._relations.values())` | Predict the returned value and distinguish a computed result from authorization. |
| [88](../../quantum_omega/core.py#L88) | `def get(self, claim_id: str):` | State the input/output contract and trace one normal and one failing case. |
| [90](../../quantum_omega/core.py#L90) | `return self._claims[claim_id]` | Predict the returned value and distinguish a computed result from authorization. |
| [92](../../quantum_omega/core.py#L92) | `def register(self, claim: Claim):` | State the input/output contract and trace one normal and one failing case. |
## Assessment and verification

A learner must explain the model, trace the capstone, identify a counterexample and state the scope boundary. Assess these four competencies equally; a numerical score cannot compensate for an unsupported scientific or operational claim.

Relevant existing checks:

- [tests/test_core.py](../../tests/test_core.py)
- [tests/test_gap_adjudication.py](../../tests/test_gap_adjudication.py)
- [tests/test_gap_agreement.py](../../tests/test_gap_agreement.py)

Follow [README](../../README.md) for environment and installed-package instructions. Read scripts before execution; source-reading exercises do not authorize provider calls, model downloads, live orders, hardware actions or messages. Synthetic fixtures establish software behavior only. This documentation change does not report those exercises as already executed.

## Interoperability and adoption gate

Retain explicit domain contracts. Shared assurance records should refer to domain evidence and its assumptions rather than relabeling graph reachability, homology, statistical calibration and epistemic acceptance as interchangeable quantities. The canonical ResearchOs controller remains owned by ResearchOs; this curriculum does not create another controller fork.

Adopt additional mathematics only after a versioned experiment demonstrates a useful operation, the scorecard has evidence, the simpler baseline is inadequate and existing conformance checks remain satisfied. Governance stage names do not establish quantum-gravity results or empirical support.
