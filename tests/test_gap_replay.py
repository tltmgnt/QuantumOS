import hashlib
import json
import unittest
from quantum_omega.gap_evidence import build_evidence_manifest
from quantum_omega.gap_protocol import freeze_protocol
from quantum_omega.gap_replay import replay_evidence

REPORT = {"kind": "review_priority_heuristic", "sha256": "a" * 64,
          "ranked_claims": [{"claim_id": "b"}, {"claim_id": "a"}]}
LABELS = {"schema_version": 1, "source_id": "set-1",
          "pairs": [{"higher_priority": "b", "lower_priority": "a"}]}

class ReplayTests(unittest.TestCase):
    def setUp(self):
        self.protocol = freeze_protocol(REPORT, study_id="study-1", evaluation_set_id="set-1")
        self.data = json.dumps(LABELS, sort_keys=True).encode("utf-8")
        self.evidence = build_evidence_manifest(
            self.protocol, registration_url="https://example.org/study-1",
            registration_timestamp="2026-01-01T00:00:00Z",
            labels_sha256=hashlib.sha256(self.data).hexdigest(),
            reviewer_ids=["reviewer-1"])

    def test_reproducible_replay(self):
        result = replay_evidence(self.protocol, REPORT, self.evidence, self.data)
        self.assertEqual(result, replay_evidence(self.protocol, REPORT, self.evidence, self.data))
        self.assertTrue(result["label_integrity_verified"])
        self.assertEqual(result["evaluation"]["scores"]["tga_heuristic"], 1.0)
        self.assertFalse(result["external_independence_verified"])

    def test_changed_bytes_rejected(self):
        with self.assertRaises(ValueError):
            replay_evidence(self.protocol, REPORT, self.evidence, self.data + b" ")

    def test_mismatched_evaluation_set_rejected(self):
        bad = {**LABELS, "source_id": "other"}
        data = json.dumps(bad, sort_keys=True).encode()
        evidence = build_evidence_manifest(
            self.protocol, registration_url="https://example.org/study-1",
            registration_timestamp="2026-01-01T00:00:00Z",
            labels_sha256=hashlib.sha256(data).hexdigest(), reviewer_ids=["reviewer-1"])
        with self.assertRaises(ValueError):
            replay_evidence(self.protocol, REPORT, evidence, data)
