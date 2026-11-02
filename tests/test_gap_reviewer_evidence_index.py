import copy
import unittest

from quantum_omega.gap_reviewer_evidence_index import (
    _CATEGORIES, _digest, build_reviewer_evidence_index, verify_reviewer_evidence_index
)

class ReviewerEvidenceIndexTests(unittest.TestCase):
    def setUp(self):
        self.ack = {"kind": "tga_reviewer_handoff_acknowledgment", "sha256": "a" * 64}
        self.evidence = {
            category: {"status": "unverified", "references": []}
            for category in _CATEGORIES
        }

    def test_unverified_roundtrip(self):
        index = build_reviewer_evidence_index(self.ack, self.evidence)
        result = verify_reviewer_evidence_index(self.ack, index)
        self.assertTrue(result["reviewer_evidence_index_checksum_consistent"])
        self.assertFalse(result["evidence_authenticity_verified"])

    def test_claimed_verification_requires_reference(self):
        self.evidence["reviewer_identity"]["status"] = "claimed_verified"
        with self.assertRaises(ValueError):
            build_reviewer_evidence_index(self.ack, self.evidence)
        self.evidence["reviewer_identity"]["references"] = [
            {"locator": "private-custody-record-001", "sha256": "a" * 64}
        ]
        index = build_reviewer_evidence_index(self.ack, self.evidence)
        self.assertFalse(index["reviewer_identity_authenticated"])

    def test_extra_category_and_bad_reference_rejected(self):
        self.evidence["unknown"] = {"status": "unverified", "references": []}
        with self.assertRaises(ValueError):
            build_reviewer_evidence_index(self.ack, self.evidence)
        self.evidence.pop("unknown")
        self.evidence["key_custody"]["references"] = [
            {"locator": "../private", "sha256": "wrong"}
        ]
        with self.assertRaises(ValueError):
            build_reviewer_evidence_index(self.ack, self.evidence)

    def test_rehashed_false_authenticity_claim_rejected(self):
        index = build_reviewer_evidence_index(self.ack, self.evidence)
        altered = copy.deepcopy(index)
        altered["reviewer_identity_authenticated"] = True
        altered.pop("sha256")
        altered["sha256"] = _digest(altered)
        with self.assertRaises(ValueError):
            verify_reviewer_evidence_index(self.ack, altered)

    def test_changed_acknowledgment_rejected(self):
        index = build_reviewer_evidence_index(self.ack, self.evidence)
        with self.assertRaises(ValueError):
            verify_reviewer_evidence_index({**self.ack, "sha256": "b" * 64}, index)
