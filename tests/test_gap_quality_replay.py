import json
import unittest
from hashlib import sha256
from unittest.mock import patch
from quantum_omega.gap_quality_replay import replay_with_reviewer_quality

DATA = {"submissions": [
    {"reviewer_id": "a", "pairs": [{"higher_priority": "x", "lower_priority": "y"}]},
    {"reviewer_id": "b", "pairs": [{"higher_priority": "y", "lower_priority": "x"}]}
], "adjudications": [{"claim_a": "x", "claim_b": "y", "higher_priority": "x", "adjudicator_id": "c", "rationale": "Evidence"}]}
BYTES = json.dumps(DATA).encode()
DIGEST = sha256(BYTES).hexdigest()
LABEL_BYTES = json.dumps({"schema_version": 1, "source_id": "study", "pairs": [{"higher_priority": "x", "lower_priority": "y"}]}).encode()

class QualityReplayTests(unittest.TestCase):
    @patch("quantum_omega.gap_quality_replay.replay_evidence")
    def test_combined_replay(self, replay):
        replay.return_value = {"evaluation": {"pairwise_accuracy": 0.5}}
        result = replay_with_reviewer_quality({}, {}, {}, LABEL_BYTES, BYTES, DIGEST)
        self.assertEqual(result["reviewer_quality"]["disagreement_audit"]["disputed_pair_count"], 1)
        self.assertTrue(result["reviewer_label_alignment_verified"])
        self.assertEqual(result["reviewer_data_sha256"], DIGEST)
        replay.assert_called_once()

    def test_rejects_tampered_bytes(self):
        with self.assertRaises(ValueError):
            replay_with_reviewer_quality({}, {}, {}, LABEL_BYTES, BYTES + b" ", DIGEST)

    def test_rejects_invalid_schema(self):
        bad = b"{}"
        with self.assertRaises(ValueError):
            replay_with_reviewer_quality({}, {}, {}, LABEL_BYTES, bad, sha256(bad).hexdigest())
