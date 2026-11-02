import unittest
from quantum_omega.gap_protocol import freeze_protocol, evaluate_frozen

REPORT = {"kind": "review_priority_heuristic", "sha256": "a" * 64, "ranked_claims": [{"claim_id": "b"}, {"claim_id": "a"}]}
LABELS = {"schema_version": 1, "source_id": "set-01", "pairs": [{"higher_priority": "b", "lower_priority": "a"}]}

class ProtocolTests(unittest.TestCase):
    def test_replay(self):
        protocol = freeze_protocol(REPORT, study_id="study-01", evaluation_set_id="set-01")
        self.assertEqual(evaluate_frozen(protocol, REPORT, LABELS), evaluate_frozen(protocol, REPORT, LABELS))
        self.assertFalse(evaluate_frozen(protocol, REPORT, LABELS)["preregistration_verified"])

    def test_protocol_tampering(self):
        protocol = freeze_protocol(REPORT, study_id="study-01", evaluation_set_id="set-01")
        with self.assertRaises(ValueError):
            evaluate_frozen({**protocol, "metric": "accuracy"}, REPORT, LABELS)

    def test_report_mismatch(self):
        protocol = freeze_protocol(REPORT, study_id="study-01", evaluation_set_id="set-01")
        with self.assertRaises(ValueError):
            evaluate_frozen(protocol, {**REPORT, "sha256": "b" * 64}, LABELS)

    def test_label_source_mismatch(self):
        protocol = freeze_protocol(REPORT, study_id="study-01", evaluation_set_id="set-01")
        with self.assertRaises(ValueError):
            evaluate_frozen(protocol, REPORT, {**LABELS, "source_id": "other"})
