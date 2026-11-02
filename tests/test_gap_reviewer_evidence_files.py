import hashlib
import tempfile
import unittest
from pathlib import Path

from quantum_omega.gap_reviewer_evidence_index import _CATEGORIES, build_reviewer_evidence_index
from quantum_omega.gap_reviewer_evidence_files import verify_reviewer_evidence_files

class ReviewerEvidenceFileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.ack = {"kind": "tga_reviewer_handoff_acknowledgment", "sha256": "a" * 64}
        self.evidence = {name: {"status": "unverified", "references": []} for name in _CATEGORIES}
        self.file = self.root / "identity.txt"
        self.file.write_bytes(b"synthetic evidence only")
        self.evidence["reviewer_identity"]["references"] = [
            {"locator": "identity.txt", "sha256": hashlib.sha256(self.file.read_bytes()).hexdigest()}
        ]

    def tearDown(self):
        self.tmp.cleanup()

    def check(self):
        index = build_reviewer_evidence_index(self.ack, self.evidence)
        return verify_reviewer_evidence_files(self.ack, index, self.root)

    def test_matching_file_and_conservative_flags(self):
        result = self.check()
        self.assertTrue(result["reviewer_evidence_bytes_match"])
        self.assertEqual(result["checked_reference_count"], 1)
        self.assertFalse(result["evidence_authenticity_verified"])

    def test_tampered_file_rejected(self):
        self.file.write_bytes(b"tampered")
        with self.assertRaises(ValueError):
            self.check()

    def test_missing_file_rejected(self):
        self.file.unlink()
        with self.assertRaises(OSError):
            self.check()

    def test_traversal_rejected(self):
        self.evidence["reviewer_identity"]["references"][0]["locator"] = "../identity.txt"
        with self.assertRaises(ValueError):
            self.check()

    def test_symlink_rejected(self):
        link = self.root / "link.txt"
        try:
            link.symlink_to(self.file)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unsupported")
        self.evidence["reviewer_identity"]["references"][0]["locator"] = "link.txt"
        with self.assertRaises(ValueError):
            self.check()

    def test_empty_references_are_vacuous_not_authenticity(self):
        self.evidence["reviewer_identity"]["references"] = []
        result = self.check()
        self.assertEqual(result["checked_reference_count"], 0)
        self.assertFalse(result["reviewer_identity_authenticated"])
