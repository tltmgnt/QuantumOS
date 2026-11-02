"""Held-out structural ranking evaluation; never claims scientific calibration."""
from .core import Claim, Ledger, Relation, RelationType
from .gap_priority import rank_gaps

def _fixture():
    ledger = Ledger()
    for name in ("supported", "unsupported", "contradicted", "anchor"):
        ledger.register(Claim(name, name, ("local:heldout",)))
    ledger.link(Relation("support", "anchor", "supported", RelationType.SUPPORTS, ("local:heldout",)))
    ledger.link(Relation("support2", "anchor", "contradicted", RelationType.SUPPORTS, ("local:heldout",)))
    ledger.link(Relation("conflict", "anchor", "contradicted", RelationType.CONTRADICTS, ("local:heldout",)))
    return ledger

def evaluate_heldout():
    """Compare a frozen heuristic to two baselines on a declared toy ordering.

    Labels are structural judgments authored with the fixture, not expert labels.
    """
    memory = _fixture()
    expected = ("contradicted", "unsupported", "supported")
    report = rank_gaps(memory)
    ranked = [r["claim_id"] for r in report["ranked_claims"]]
    # Exclude anchor, which is a fixture scaffold rather than an evaluation target.
    ranked = [cid for cid in ranked if cid in expected]
    alphabetical = sorted(expected)
    # A simple baseline prioritizes isolated claims and breaks ties alphabetically.
    rows = {r["claim_id"]: r for r in report["ranked_claims"]}
    isolation = sorted(expected, key=lambda cid: (-rows[cid]["flags"]["isolated"], cid))
    def pairwise_accuracy(order):
        position = {cid: i for i, cid in enumerate(order)}
        pairs = [(a, b) for i, a in enumerate(expected) for b in expected[i + 1:]]
        return sum(position[a] < position[b] for a, b in pairs) / len(pairs)
    results = {
        "tga_heuristic": pairwise_accuracy(ranked),
        "alphabetical_baseline": pairwise_accuracy(alphabetical),
        "isolation_baseline": pairwise_accuracy(isolation),
    }
    return {
        "schema_version": 1,
        "evaluation_type": "synthetic_declared_holdout",
        "independent_expert_labels": False,
        "scientific_calibration": False,
        "target_order": list(expected),
        "predicted_order": ranked,
        "metric": "pairwise_order_accuracy",
        "scores": results,
        "passes_structural_fixture": results["tga_heuristic"] == 1.0,
        "note": "Fixture and expected order are public in code; this is not a blinded scientific benchmark.",
    }
