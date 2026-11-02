"""Deterministic TGA-Ω review priorities, not explanatory distance or scientific truth."""
from dataclasses import dataclass
from hashlib import sha256
import json
import math
from .core import EpistemicStatus, RelationType
from .topology import analyze

@dataclass(frozen=True)
class PriorityWeights:
    missing_support: float = 2.0
    missing_verification: float = 1.0
    contradiction: float = 3.0
    isolation: float = 1.0

    def __post_init__(self):
        if any(type(v) not in (float, int) or not math.isfinite(v) or v < 0
               for v in vars(self).values()):
            raise ValueError("Priority weights must be finite and nonnegative")

def _analyze_ledger(ledger):
    from .topology import _graph, _components, DEPENDENCIES
    claims, relations = ledger.claims(), ledger.all_relations()
    graph = _graph(claims, relations, DEPENDENCIES)
    active = [r for r in relations if r.status != EpistemicStatus.REJECTED]
    incident = {node for r in active for node in (r.source, r.target)}
    return {
        'schema_version': 1,
        'interpretation': 'Structural review prompts only; not scientific validation or an explanatory-distance metric.',
        'claim_count': len(claims),
        'relation_count': len(relations),
        'isolated_claims': sorted(c.id for c in claims if c.id not in incident),
        'dependency_cycle_components': [c for c in _components(graph) if len(c) > 1],
        'asserted_contradictions': sorted(r.id for r in active if r.kind == RelationType.CONTRADICTS),
    }

def rank_gaps(memory, weights=PriorityWeights()):
    """Read-only, auditable heuristic on asserted edges and claim stages.

    This is a review-queue ranking, not a graph metric, information gain,
    verification outcome, or measure of scientific importance.
    """
    if not isinstance(weights, PriorityWeights):
        raise TypeError("Expected PriorityWeights")
    if hasattr(memory, 'snapshot'):
        claims, relations = memory.snapshot()
    else:
        claims, relations = memory.claims(), memory.all_relations()
    structural = analyze(memory) if hasattr(memory, 'snapshot') else _analyze_ledger(memory)
    active = [r for r in relations if r.status != EpistemicStatus.REJECTED]
    incident = {node for r in active for node in (r.source, r.target)}
    rows = []
    for claim in claims:
        if claim.status == EpistemicStatus.REJECTED:
            continue
        supports = sum(r.target == claim.id and r.kind == RelationType.SUPPORTS for r in active)
        contradictions = sum(claim.id in (r.source, r.target) and
                             r.kind == RelationType.CONTRADICTS for r in active)
        flags = {
            "missing_asserted_support": int(supports == 0),
            "not_independently_verified": int(int(claim.stage) < 5),
            "asserted_contradiction_count": contradictions,
            "isolated": int(claim.id not in incident),
        }
        score = (weights.missing_support * flags["missing_asserted_support"]
                 + weights.missing_verification * flags["not_independently_verified"]
                 + weights.contradiction * contradictions
                 + weights.isolation * flags["isolated"])
        if not math.isfinite(score):
            raise ValueError("Priority score overflow")
        rows.append({"claim_id": claim.id, "priority_score": score, "flags": flags})
    rows.sort(key=lambda row: (-row["priority_score"], row["claim_id"]))
    payload = {
        "schema_version": 1,
        "kind": "review_priority_heuristic",
        "interpretation": "Uncalibrated review prompts only; not scientific distance, validity, or information gain",
        "weights": vars(weights).copy(),
        "structural_analysis": structural,
        "ranked_claims": rows,
    }
    payload["sha256"] = sha256(json.dumps(payload, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()
    return payload

def propose_review_actions(report, budget):
    """Feed priority ordering into existing bounded planner without fabricating IG."""
    from .core import Action
    from .planner import plan
    if not isinstance(report, dict) or report.get("kind") != "review_priority_heuristic":
        raise ValueError("Expected a TGA review-priority report")
    actions = [Action("review:" + row["claim_id"], 0, 0,
                      row["priority_score"], 0, 1, 0)
               for row in report["ranked_claims"]]
    if not actions:
        return {"selected_action": None, "reason": "No active claims"}
    result = plan(actions, budget)
    result["score_interpretation"] = "Heuristic review priority, not calibrated scientific utility"
    return result
