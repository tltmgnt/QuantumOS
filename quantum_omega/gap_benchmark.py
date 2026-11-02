"""Deterministic benchmark for review-priority ordering, not scientific calibration."""
from .core import Claim, Ledger, Relation, RelationType
from .gap_priority import PriorityWeights, rank_gaps

def evaluate_fixture():
    ledger = Ledger()
    for cid in ("supported", "unsupported", "contradicted", "reference"):
        ledger.register(Claim(cid, cid, ("local:benchmark",)))
    ledger.link(Relation("s1", "reference", "supported", RelationType.SUPPORTS, ("local:benchmark",)))
    ledger.link(Relation("s2", "reference", "contradicted", RelationType.SUPPORTS, ("local:benchmark",)))
    ledger.link(Relation("c1", "reference", "contradicted", RelationType.CONTRADICTS, ("local:benchmark",)))
    weights = PriorityWeights(contradiction=4.0)
    result = rank_gaps(ledger, weights)
    scores = {row["claim_id"]: row["priority_score"] for row in result["ranked_claims"]}
    checks = {
        "contradiction_outweighs_unsupported": scores["contradicted"] > scores["unsupported"],
        "unsupported_outweighs_supported": scores["unsupported"] > scores["supported"],
        "deterministic_replay": rank_gaps(ledger, weights) == result,
        "all_claims_ranked": set(scores) == {"supported", "unsupported", "contradicted", "reference"},
    }
    return {
        "schema_version": 1,
        "benchmark_kind": "synthetic_structural_fixture",
        "scientific_calibration": False,
        "passed": all(checks.values()),
        "checks": checks,
        "scores": scores,
        "report_sha256": result["sha256"],
    }
