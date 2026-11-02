import tempfile
import unittest
from pathlib import Path

from quantum_omega.gap_provenance_example import create_provenance_example
from quantum_omega.gap_audit_bundle import build_audit_bundle, verify_audit_bundle

class AuditBundleTests(unittest.TestCase):
    def test_deterministic_and_cross_linked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "study"
            create_provenance_example(root)
            (root / "evaluation.json").unlink()
            bundle = build_audit_bundle(root)
            self.assertEqual(bundle, build_audit_bundle(root))
            self.assertEqual(bundle["evaluation_sha256"], bundle["review_summary"]["evaluation_sha256"])
            self.assertEqual(bundle["evaluation_sha256"], bundle["study_input_inventory"]["evaluation_sha256"])
            self.assertTrue(verify_audit_bundle(root, bundle)["audit_bundle_verified"])
            self.assertFalse(bundle["external_authenticity_verified"])

    def test_rejects_modified_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "study"
            create_provenance_example(root)
            (root / "evaluation.json").unlink()
            bundle = build_audit_bundle(root)
            bundle["review_summary"]["checks"]["reviewer_ids_consistent"] = False
            with self.assertRaises(ValueError):
                verify_audit_bundle(root, bundle)

    def test_rejects_modified_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "study"
            create_provenance_example(root)
            (root / "evaluation.json").unlink()
            bundle = build_audit_bundle(root)
            with (root / "labels.json").open("ab") as stream:
                stream.write(b" ")
            with self.assertRaises(ValueError):
                verify_audit_bundle(root, bundle)
