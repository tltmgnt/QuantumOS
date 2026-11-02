import hashlib
import tempfile
import unittest
from pathlib import Path
from quantum_omega.gap_provenance_example import create_provenance_example
from quantum_omega.gap_audit_bundle import build_audit_bundle
from quantum_omega.gap_audit_signoff import create_audit_signoff
from quantum_omega.gap_audit_evidence_refs import create_evidence_references
from quantum_omega.gap_audit_chain_report import build_audit_chain_report

CATEGORIES = ("registration_authenticity", "reviewer_independence", "label_provenance", "scientific_validity")

class AuditChainReportTests(unittest.TestCase):
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
            notes="No independently verified evidence."
        )
        self.evidence = Path(self.tmp.name) / "evidence"
        self.evidence.mkdir()
        (self.evidence / "record.txt").write_bytes(b"synthetic bytes")
        refs = {category: [] for category in CATEGORIES}
        refs["label_provenance"] = [{
            "locator": "record.txt", "description": "Synthetic record",
            "sha256": hashlib.sha256(b"synthetic bytes").hexdigest()
        }]
        self.manifest = create_evidence_references(self.bundle, self.signoff, refs)
    def tearDown(self):
        self.tmp.cleanup()

    def test_deterministic_conservative_report(self):
        report = build_audit_chain_report(self.bundle, self.signoff, self.manifest, self.evidence)
        self.assertEqual(report, build_audit_chain_report(self.bundle, self.signoff, self.manifest, self.evidence))
        self.assertEqual(report["checked_reference_count"], 1)
        self.assertFalse(report["external_authenticity_verified"])
        self.assertFalse(report["scientific_validity_independently_verified"])
        self.assertEqual(report["categories"]["label_provenance"]["local_bytes_checked"], 1)

    def test_modified_evidence_rejected(self):
        (self.evidence / "record.txt").write_bytes(b"modified")
        with self.assertRaises(ValueError):
            build_audit_chain_report(self.bundle, self.signoff, self.manifest, self.evidence)
