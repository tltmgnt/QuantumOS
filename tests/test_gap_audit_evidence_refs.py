import tempfile
import unittest
from pathlib import Path
from quantum_omega.gap_provenance_example import create_provenance_example
from quantum_omega.gap_audit_bundle import build_audit_bundle
from quantum_omega.gap_audit_signoff import create_audit_signoff
from quantum_omega.gap_audit_evidence_refs import create_evidence_references, verify_evidence_references

CATEGORIES = ("registration_authenticity", "reviewer_independence", "label_provenance", "scientific_validity")

class EvidenceReferenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name) / "study"
        create_provenance_example(root)
        (root / "evaluation.json").unlink()
        self.bundle = build_audit_bundle(root)
        self.signoff = create_audit_signoff(
            self.bundle, auditor="Example Auditor", organization="Example Lab",
            reviewed_at="2026-11-01T12:00:00Z", repository_commit="a" * 40,
            evidence_statuses={category: "unverified" for category in CATEGORIES},
            notes="No external evidence independently checked."
        )
    def tearDown(self):
        self.tmp.cleanup()

    def test_empty_unverified_references_allowed(self):
        refs = {category: [] for category in CATEGORIES}
        manifest = create_evidence_references(self.bundle, self.signoff, refs)
        self.assertEqual(manifest, create_evidence_references(self.bundle, self.signoff, refs))
        self.assertTrue(verify_evidence_references(self.bundle, self.signoff, manifest)["evidence_references_consistent"])
        self.assertFalse(manifest["evidence_authenticity_verified"])

    def test_tampering_rejected(self):
        manifest = create_evidence_references(self.bundle, self.signoff, {category: [] for category in CATEGORIES})
        manifest["references"]["scientific_validity"].append({"locator": "example", "description": "test", "sha256": "a" * 64})
        with self.assertRaises(ValueError):
            verify_evidence_references(self.bundle, self.signoff, manifest)

    def test_verified_requires_reference(self):
        signoff = create_audit_signoff(
            self.bundle, auditor="Example Auditor", organization="Example Lab",
            reviewed_at="2026-11-01T12:00:00Z", repository_commit="a" * 40,
            evidence_statuses={category: "verified" if category == "scientific_validity" else "unverified" for category in CATEGORIES},
            notes="Self-reported verified status."
        )
        with self.assertRaises(ValueError):
            create_evidence_references(self.bundle, signoff, {category: [] for category in CATEGORIES})
