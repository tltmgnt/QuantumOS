import unittest
from quantum_omega import Claim, EpistemicStatus, Ledger, Relation, RelationType, Stage
from quantum_omega.gap_priority import PriorityWeights, rank_gaps, propose_review_actions

class GapPriorityTests(unittest.TestCase):
    def test_deterministic_priority_and_planner(self):
        ledger = Ledger()
        for cid in ("a", "b", "c"):
            ledger.register(Claim(cid, cid, ("local:fixture",)))
        ledger.link(Relation("support", "b", "a", RelationType.SUPPORTS, ("local:evidence",)))
        ledger.link(Relation("conflict", "a", "b", RelationType.CONTRADICTS, ("local:evidence",)))
        first = rank_gaps(ledger)
        self.assertEqual(first, rank_gaps(ledger))
        self.assertEqual([r["claim_id"] for r in first["ranked_claims"]], ["b", "a", "c"])
        self.assertEqual(propose_review_actions(first, 1)["selected_action"], "review:b")
        self.assertIsNone(propose_review_actions(first, 0)["selected_action"])
        self.assertEqual(len(first["sha256"]), 64)

    def test_rejected_claim_excluded_and_rejected_edges_ignored(self):
        ledger = Ledger()
        ledger.register(Claim("a", "a", ("local:x",)))
        ledger.register(Claim("b", "b", ("local:x",)))
        ledger.link(Relation("r", "a", "b", RelationType.CONTRADICTS,
                             ("local:x",), EpistemicStatus.REJECTED))
        ledger.reject("a", "counterexample", "local:counterexample")
        report = rank_gaps(ledger)
        self.assertEqual([r["claim_id"] for r in report["ranked_claims"]], ["b"])
        self.assertEqual(report["ranked_claims"][0]["flags"]["asserted_contradiction_count"], 0)

    def test_invalid_weights_and_empty_graph(self):
        for invalid in (float("nan"), -1, float("inf"), True):
            with self.assertRaises(ValueError):
                PriorityWeights(contradiction=invalid)
        report = rank_gaps(Ledger())
        self.assertIsNone(propose_review_actions(report, 1)["selected_action"])
        with self.assertRaises(ValueError):
            propose_review_actions({}, 1)
