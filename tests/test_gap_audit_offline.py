import copy
import tempfile
import unittest
from pathlib import Path

from quantum_omega.gap_provenance_example import create_provenance_example
from quantum_omega.gap_audit_bundle import build_audit_bundle
from quantum_omega.gap_audit_offline import verify_bundle_offline

class OfflineAuditTests(unittest.TestCase):
    def make_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "study"
            create_provenance_example(root)
            (root / "evaluation.json").unlink()
            return build_audit_bundle(root)

    def test_checksums_without_original_files(self):
        result = verify_bundle_offline(self.make_bundle())
        self.assertTrue(result["offline_checksums_consistent"])
        self.assertFalse(result["study_inputs_replayed"])
        self.assertFalse(result["external_authenticity_verified"])

    def test_modified_record_rejected(self):
        bundle = self.make_bundle()
        bundle["study_input_inventory"]["files"][0]["size_bytes"] += 1
        with self.assertRaises(ValueError):
            verify_bundle_offline(bundle)

    def test_modified_claim_rejected(self):
        bundle = self.make_bundle()
        bundle["review_summary"]["external_verification"]["scientific_validity"] = True
        with self.assertRaises(ValueError):
            verify_bundle_offline(bundle)

    def test_invalid_file_list_rejected(self):
        bundle = self.make_bundle()
        bundle["study_input_inventory"]["files"].pop()
        with self.assertRaises(ValueError):
            verify_bundle_offline(bundle)
