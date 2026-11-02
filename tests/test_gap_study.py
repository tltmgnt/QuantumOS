import unittest
from quantum_omega.gap_study import validate_study_submission

S = {"schema_version": 1, "study_id": "study-01", "protocol_sha256": "a" * 64,
     "registered_at": "2026-01-01T00:00:00Z", "labels_collected_at": "2026-02-01T00:00:00Z",
     "label_source_id": "set-01",
     "reviewers": [{"reviewer_id": "r1", "affiliation": "institution-A", "conflict_declared": False},
                   {"reviewer_id": "r2", "affiliation": "institution-B", "conflict_declared": True}]}

class StudyKitTests(unittest.TestCase):
    def test_valid_submission_not_certified(self):
        result = validate_study_submission(S)
        self.assertTrue(result["claimed_chronological_order_valid"])
        self.assertFalse(result["external_timestamp_verified"])
        self.assertFalse(result["reviewer_independence_verified"])
        self.assertEqual(result["declared_conflict_count"], 1)

    def test_bad_chronology(self):
        with self.assertRaises(ValueError):
            validate_study_submission({**S, "registered_at": "2026-03-01T00:00:00Z"})

    def test_duplicate_reviewers(self):
        with self.assertRaises(ValueError):
            validate_study_submission({**S, "reviewers": [S["reviewers"][0]] * 2})

    def test_naive_timestamp(self):
        with self.assertRaises(ValueError):
            validate_study_submission({**S, "registered_at": "2026-01-01T00:00:00"})

    def test_bad_protocol_digest(self):
        with self.assertRaises(ValueError):
            validate_study_submission({**S, "protocol_sha256": "not-a-digest"})
