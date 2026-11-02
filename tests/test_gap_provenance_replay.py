import unittest
from unittest.mock import patch
from quantum_omega.gap_provenance_replay import replay_with_provenance

class ProvenanceGatedReplayTests(unittest.TestCase):
    @patch("quantum_omega.gap_provenance_replay.replay_with_reviewer_quality")
    @patch("quantum_omega.gap_provenance_replay.check_provenance_consistency")
    def test_runs_provenance_before_replay(self, check, replay):
        check.return_value = {"reviewer_ids_consistent": True}
        replay.return_value = {"reviewer_label_alignment_verified": True}
        result = replay_with_provenance({}, {}, {}, b"labels", b"reviewers", {})
        self.assertEqual(result["kind"], "provenance_gated_frozen_replay")
        self.assertFalse(result["reviewer_independence_verified"])
        check.assert_called_once()
        replay.assert_called_once()

    @patch("quantum_omega.gap_provenance_replay.replay_with_reviewer_quality")
    @patch("quantum_omega.gap_provenance_replay.check_provenance_consistency")
    def test_rejects_inconsistent_provenance_without_scoring(self, check, replay):
        check.side_effect = ValueError("Reviewer mismatch")
        with self.assertRaises(ValueError):
            replay_with_provenance({}, {}, {}, b"labels", b"reviewers", {})
        replay.assert_not_called()
