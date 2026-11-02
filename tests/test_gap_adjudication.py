import unittest
from quantum_omega.gap_adjudication import disagreement_report

A = {"reviewer_id": "a", "pairs": [{"higher_priority": "x", "lower_priority": "y"}]}
B = {"reviewer_id": "b", "pairs": [{"higher_priority": "y", "lower_priority": "x"}]}
D = {"claim_a": "x", "claim_b": "y", "higher_priority": "x", "adjudicator_id": "c", "rationale": "Reviewed evidence"}

class AdjudicationTests(unittest.TestCase):
    def test_preserves_original_votes(self):
        result = disagreement_report([A, B], [D])
        self.assertEqual(result["disputed_pair_count"], 1)
        self.assertEqual(result["adjudicated_pair_count"], 1)
        self.assertEqual(len(result["disagreements"][0]["original_votes"]), 2)
        self.assertFalse(result["adjudicator_independence_verified"])
        self.assertEqual(result, disagreement_report([B, A], [D]))

    def test_unresolved_disagreement(self):
        result = disagreement_report([A, B])
        self.assertFalse(result["disagreements"][0]["resolved"])

    def test_rejects_unrelated_adjudication(self):
        with self.assertRaises(ValueError):
            disagreement_report([A, B], [{**D, "claim_b": "z"}])

    def test_rejects_duplicate_adjudication(self):
        with self.assertRaises(ValueError):
            disagreement_report([A, B], [D, D])
