import tempfile
import unittest
from pathlib import Path
from quantum_omega.gap_provenance_example import create_provenance_example
from quantum_omega.gap_audit_bundle import build_audit_bundle
from quantum_omega.gap_audit_signoff import create_audit_signoff, verify_audit_signoff

class AuditSignoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name) / "study"
        create_provenance_example(root)
        (root / "evaluation.json").unlink()
        self.bundle = build_audit_bundle(root)
        self.fields = dict(
            auditor="Example Auditor", organization="Example Lab",
            reviewed_at="2026-11-01T12:00:00Z", repository_commit="a" * 40,
            evidence_statuses={
                "registration_authenticity": "unverified",
                "reviewer_independence": "unverified",
                "label_provenance": "unverified",
                "scientific_validity": "unverified",
            }, notes="Synthetic demonstration; no independent verification performed."
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_deterministic_declaration(self):
        record = create_audit_signoff(self.bundle, **self.fields)
        self.assertEqual(record, create_audit_signoff(self.bundle, **self.fields))
        self.assertTrue(verify_audit_signoff(self.bundle, record)["signoff_checksum_consistent"])
        self.assertFalse(record["identity_authenticated"])
        self.assertFalse(record["digitally_signed"])

    def test_tampering_rejected(self):
        record = create_audit_signoff(self.bundle, **self.fields)
        record["notes"] = "changed"
        with self.assertRaises(ValueError):
            verify_audit_signoff(self.bundle, record)

    def test_missing_status_rejected(self):
        fields = dict(self.fields)
        fields["evidence_statuses"] = {"scientific_validity": "verified"}
        with self.assertRaises(ValueError):
            create_audit_signoff(self.bundle, **fields)

    def test_bundle_mismatch_rejected(self):
        record = create_audit_signoff(self.bundle, **self.fields)
        bundle = dict(self.bundle)
        bundle["evaluation_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            verify_audit_signoff(bundle, record)
