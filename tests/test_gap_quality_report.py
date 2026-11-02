import unittest
from quantum_omega.gap_quality_report import build_reviewer_quality_report

A = {"reviewer_id": "a", "pairs": [{"higher_priority": "x", "lower_priority": "y"}]}
B = {"reviewer_id": "b", "pairs": [{"higher_priority": "y", "lower_priority": "x"}]}
D = {"claim_a": "x", "claim_b": "y", "higher_priority": "x", "adjudicator_id": "c", "rationale": "Evidence"}

class QualityReportTests(unittest.TestCase):
    def test_combined_report(self):
        result = build_reviewer_quality_report([A, B], [D])
        self.assertEqual(result["agreement"]["pooled_agreement_rate"], 0)
        self.assertEqual(result["disagreement_audit"]["adjudicated_pair_count"], 1)
        self.assertEqual(len(result["sha256"]), 64)
        self.assertEqual(result, build_reviewer_quality_report([B, A], [D]))

    def test_unresolved(self):
        result = build_reviewer_quality_report([A, B])
        self.assertEqual(result["disagreement_audit"]["adjudicated_pair_count"], 0)

    def test_invalid_adjudication(self):
        with self.assertRaises(ValueError):
            build_reviewer_quality_report([A, B], [{**D, "claim_b": "z"}])
