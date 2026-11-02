import hashlib
import tempfile
import unittest
from pathlib import Path
from quantum_omega.gap_provenance_example import create_provenance_example
from quantum_omega.gap_audit_bundle import build_audit_bundle
from quantum_omega.gap_audit_signoff import create_audit_signoff
from quantum_omega.gap_audit_evidence_refs import create_evidence_references
from quantum_omega.gap_audit_chain_report import build_audit_chain_report
from quantum_omega.gap_audit_handoff_receipt import build_audit_handoff_receipt, verify_audit_handoff_receipt

CATEGORIES = ("registration_authenticity", "reviewer_independence", "label_provenance", "scientific_validity")

class AuditHandoffReceiptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.study = Path(self.tmp.name) / "study"
        create_provenance_example(self.study)
        (self.study / "evaluation.json").unlink()
        bundle = build_audit_bundle(self.study)
        signoff = create_audit_signoff(
            bundle, auditor="Example", organization="Example",
            reviewed_at="2026-11-01T12:00:00Z", repository_commit="a" * 40,
            evidence_statuses={category: "unverified" for category in CATEGORIES},
            notes="Synthetic example; no independently authenticated evidence."
        )
        self.evidence = Path(self.tmp.name) / "evidence"
        self.evidence.mkdir()
        (self.evidence / "record.txt").write_bytes(b"synthetic bytes")
        refs = {category: [] for category in CATEGORIES}
        refs["label_provenance"] = [{
            "locator": "record.txt", "description": "Synthetic record",
            "sha256": hashlib.sha256(b"synthetic bytes").hexdigest()
        }]
        manifest = create_evidence_references(bundle, signoff, refs)
        report = build_audit_chain_report(bundle, signoff, manifest, self.evidence)
        self.values = (bundle, signoff, manifest, report)

    def tearDown(self):
        self.tmp.cleanup()

    def build(self):
        return build_audit_handoff_receipt(self.study, *self.values[:3], self.evidence, self.values[3])

    def test_receipt_deterministic_and_conservative(self):
        receipt = self.build()
        self.assertEqual(receipt, self.build())
        self.assertEqual(receipt["checked_reference_count"], 1)
        self.assertFalse(receipt["external_authenticity_verified"])
        self.assertTrue(verify_audit_handoff_receipt(
            self.study, *self.values[:3], self.evidence, self.values[3], receipt
        )["handoff_receipt_matches_inputs"])

    def test_receipt_tampering_rejected(self):
        receipt = self.build()
        receipt["checked_reference_count"] = 999
        with self.assertRaises(ValueError):
            verify_audit_handoff_receipt(
                self.study, *self.values[:3], self.evidence, self.values[3], receipt
            )

    def test_study_tampering_rejected(self):
        (self.study / "labels.json").write_bytes(b"changed")
        with self.assertRaises(ValueError):
            self.build()
