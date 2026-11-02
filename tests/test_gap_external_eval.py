import unittest
from quantum_omega.gap_external_eval import evaluate_labels

REPORT = {"kind": "review_priority_heuristic", "sha256": "frozen", "ranked_claims": [{"claim_id": "b"}, {"claim_id": "a"}, {"claim_id": "c"}]}
LABELS = {"schema_version": 1, "source_id": "external:review-set-1", "pairs": [{"higher_priority": "b", "lower_priority": "a"}, {"higher_priority": "a", "lower_priority": "c"}]}

class ExternalLabelEvaluationTests(unittest.TestCase):
    def test_replay_and_baseline(self):
        result = evaluate_labels(REPORT, LABELS)
        self.assertEqual(result, evaluate_labels(REPORT, LABELS))
        self.assertEqual(result["scores"]["tga_heuristic"], 1.0)
        self.assertEqual(result["scores"]["alphabetical_baseline"], 0.5)
        self.assertFalse(result["independence_verified"])

    def test_rejects_duplicate_or_conflicting_labels(self):
        bad = {**LABELS, "pairs": LABELS["pairs"] + [{"higher_priority": "a", "lower_priority": "b"}]}
        with self.assertRaises(ValueError):
            evaluate_labels(REPORT, bad)

    def test_rejects_unknown_claims(self):
        bad = {**LABELS, "pairs": [{"higher_priority": "b", "lower_priority": "unknown"}]}
        with self.assertRaises(ValueError):
            evaluate_labels(REPORT, bad)
