import unittest
from quantum_omega.gap_reconcile import reconcile_reviewer_labels

A = {"reviewer_id": "a", "pairs": [{"higher_priority": "x", "lower_priority": "y"}]}
B = {"reviewer_id": "b", "pairs": [{"higher_priority": "y", "lower_priority": "x"}]}
LABELS = {"schema_version": 1, "source_id": "external", "pairs": A["pairs"]}
DECISION = {"claim_a": "x", "claim_b": "y", "higher_priority": "x", "adjudicator_id": "c", "rationale": "Evidence"}
DATA = {"submissions": [A, B], "adjudications": [DECISION]}

class ReconciliationTests(unittest.TestCase):
    def test_tie_with_adjudication(self):
        result = reconcile_reviewer_labels(LABELS, DATA)
        self.assertTrue(result["reviewer_label_alignment_verified"])
        self.assertEqual(result["resolved_by"]["adjudication"], 1)

    def test_tie_without_adjudication(self):
        with self.assertRaises(ValueError):
            reconcile_reviewer_labels(LABELS, {**DATA, "adjudications": []})

    def test_unanimous(self):
        result = reconcile_reviewer_labels(LABELS, {"submissions": [A, {**B, "pairs": A["pairs"]}], "adjudications": []})
        self.assertEqual(result["resolved_by"]["unanimous"], 1)

    def test_unmatched_label(self):
        with self.assertRaises(ValueError):
            reconcile_reviewer_labels({**LABELS, "pairs": [{"higher_priority": "a", "lower_priority": "b"}]}, DATA)

    def test_mismatched_decision(self):
        with self.assertRaises(ValueError):
            reconcile_reviewer_labels(LABELS, {**DATA, "adjudications": [{**DECISION, "higher_priority": "y"}]})
