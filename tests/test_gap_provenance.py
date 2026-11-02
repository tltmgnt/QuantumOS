import json
import unittest
from hashlib import sha256
from quantum_omega.gap_provenance import check_provenance_consistency

P = {"sha256": "a" * 64}
L = json.dumps({"source_id": "set-01"}).encode()
R = json.dumps({"submissions": [{"reviewer_id": "r1"}, {"reviewer_id": "r2"}]}).encode()
S = {"schema_version": 1, "study_id": "study-01", "protocol_sha256": "a" * 64,
     "registered_at": "2026-01-01T00:00:00Z", "labels_collected_at": "2026-02-01T00:00:00Z",
     "label_source_id": "set-01",
     "reviewers": [{"reviewer_id": "r1", "affiliation": "A", "conflict_declared": False},
                   {"reviewer_id": "r2", "affiliation": "B", "conflict_declared": False}]}
M = {"protocol_sha256": "a" * 64, "labels_sha256": sha256(L).hexdigest(),
     "reviewer_ids_claimed": ["r1", "r2"],
     "registration_timestamp_claimed": "2026-01-01T00:00:00Z"}

class ProvenanceTests(unittest.TestCase):
    def test_consistent(self):
        result = check_provenance_consistency(S, P, M, L, R)
        self.assertTrue(result["reviewer_ids_consistent"])
        self.assertFalse(result["reviewer_independence_verified"])

    def test_wrong_label_source(self):
        with self.assertRaises(ValueError):
            check_provenance_consistency({**S, "label_source_id": "other"}, P, M, L, R)

    def test_reviewer_mismatch(self):
        with self.assertRaises(ValueError):
            check_provenance_consistency(S, P, {**M, "reviewer_ids_claimed": ["r1"]}, L, R)

    def test_timestamp_mismatch(self):
        with self.assertRaises(ValueError):
            check_provenance_consistency(S, P, {**M, "registration_timestamp_claimed": "later"}, L, R)

    def test_tampered_label_bytes(self):
        with self.assertRaises(ValueError):
            check_provenance_consistency(S, P, M, L + b" ", R)
