import hashlib
import tempfile
import unittest
from pathlib import Path

from quantum_omega.gap_provenance_example import create_provenance_example
from quantum_omega.gap_audit_bundle import build_audit_bundle
from quantum_omega.gap_audit_signoff import create_audit_signoff
from quantum_omega.gap_audit_evidence_refs import create_evidence_references
from quantum_omega.gap_audit_local_evidence import verify_local_evidence_files

CATEGORIES = ("registration_authenticity", "reviewer_independence", "label_provenance", "scientific_validity")

class LocalEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name) / "study"
        create_provenance_example(root)
        (root / "evaluation.json").unlink()
        self.bundle = build_audit_bundle(root)
        self.signoff = create_audit_signoff(
            self.bundle, auditor="Example", organization="Example",
            reviewed_at="2026-11-01T12:00:00Z", repository_commit="a" * 40,
            evidence_statuses={category: "unverified" for category in CATEGORIES},
            notes="No external authenticity claims."
        )
        self.evidence = Path(self.tmp.name) / "external"
        self.evidence.mkdir()
        (self.evidence / "record.txt").write_bytes(b"synthetic evidence")
    def tearDown(self):
        self.tmp.cleanup()

    def manifest(self, locator="record.txt"):
        refs = {category: [] for category in CATEGORIES}
        refs["label_provenance"] = [{
            "locator": locator, "description": "Synthetic local file",
            "sha256": hashlib.sha256(b"synthetic evidence").hexdigest()
        }]
        return create_evidence_references(self.bundle, self.signoff, refs)

    def test_matching_bytes(self):
        result = verify_local_evidence_files(self.bundle, self.signoff, self.manifest(), self.evidence)
        self.assertEqual(result["checked_reference_count"], 1)
        self.assertFalse(result["external_authenticity_verified"])

    def test_tampering(self):
        (self.evidence / "record.txt").write_bytes(b"changed")
        with self.assertRaises(ValueError):
            verify_local_evidence_files(self.bundle, self.signoff, self.manifest(), self.evidence)

    def test_traversal(self):
        with self.assertRaises(ValueError):
            verify_local_evidence_files(self.bundle, self.signoff, self.manifest("../record.txt"), self.evidence)

    def test_symlink(self):
        (self.evidence / "alias.txt").symlink_to(self.evidence / "record.txt")
        with self.assertRaises(ValueError):
            verify_local_evidence_files(self.bundle, self.signoff, self.manifest("alias.txt"), self.evidence)
