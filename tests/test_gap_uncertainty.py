import unittest
from quantum_omega.gap_uncertainty import agreement_with_uncertainty, wilson_interval

A = {"reviewer_id": "a", "pairs": [{"higher_priority": "x", "lower_priority": "y"}]}
B = {"reviewer_id": "b", "pairs": [{"higher_priority": "x", "lower_priority": "y"}]}

class UncertaintyTests(unittest.TestCase):
    def test_wilson_bounds(self):
        low, high = wilson_interval(1, 1)
        self.assertGreaterEqual(low, 0)
        self.assertLessEqual(high, 1)
        self.assertLess(low, high)

    def test_no_overlap(self):
        other = {"reviewer_id": "b", "pairs": [{"higher_priority": "p", "lower_priority": "q"}]}
        result = agreement_with_uncertainty([A, other])
        self.assertIsNone(result["illustrative_pooled_wilson_interval"])

    def test_replay(self):
        result = agreement_with_uncertainty([A, B])
        self.assertEqual(result, agreement_with_uncertainty([B, A]))
        self.assertFalse(result["independent_sample_assumption_verified"])
        self.assertIsNotNone(result["illustrative_pooled_wilson_interval"])

    def test_invalid_counts(self):
        with self.assertRaises(ValueError):
            wilson_interval(2, 1)
        with self.assertRaises(ValueError):
            wilson_interval(0, 0)
        with self.assertRaises(ValueError):
            wilson_interval(1, 2, 1)
