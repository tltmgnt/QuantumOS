import unittest
from quantum_omega.gap_agreement import evaluate_reviewer_agreement

A = {"reviewer_id": "a", "pairs": [
    {"higher_priority": "x", "lower_priority": "y"},
    {"higher_priority": "x", "lower_priority": "z"}]}
B = {"reviewer_id": "b", "pairs": [
    {"higher_priority": "x", "lower_priority": "y"},
    {"higher_priority": "z", "lower_priority": "x"}]}

class ReviewerAgreementTests(unittest.TestCase):
    def test_partial_agreement(self):
        result = evaluate_reviewer_agreement([A, B])
        self.assertEqual(result["total_pairwise_overlaps"], 2)
        self.assertEqual(result["pooled_agreement_rate"], 0.5)
        self.assertFalse(result["independence_verified"])
        self.assertEqual(result, evaluate_reviewer_agreement([B, A]))

    def test_no_overlap(self):
        result = evaluate_reviewer_agreement([A, {"reviewer_id": "b", "pairs": [
            {"higher_priority": "q", "lower_priority": "r"}]}])
        self.assertIsNone(result["pooled_agreement_rate"])

    def test_conflicting_duplicate(self):
        bad = {"reviewer_id": "b", "pairs": [
            {"higher_priority": "x", "lower_priority": "y"},
            {"higher_priority": "y", "lower_priority": "x"}]}
        with self.assertRaises(ValueError):
            evaluate_reviewer_agreement([A, bad])

    def test_duplicate_reviewer(self):
        with self.assertRaises(ValueError):
            evaluate_reviewer_agreement([A, A])
