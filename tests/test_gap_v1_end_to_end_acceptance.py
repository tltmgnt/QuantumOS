"""v1 software acceptance: signed replay, reviewer signature, local evidence bytes."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from quantum_omega.gap_signed_reviewer_ack_demo import create_signed_reviewer_ack_demo
from quantum_omega.gap_signed_reviewer_acknowledgment import verify_signed_reviewer_acknowledgment
from quantum_omega.gap_reviewer_evidence_index import _CATEGORIES, build_reviewer_evidence_index
from quantum_omega.gap_reviewer_evidence_files import verify_reviewer_evidence_files

try:
    import cryptography
except ImportError:
    cryptography = None

@unittest.skipUnless(cryptography is not None, "Optional cryptography dependency unavailable")
class V1EndToEndAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "review"
        create_signed_reviewer_ack_demo(self.root)
        self.package = json.loads((self.root / "reviewer-package.json").read_text())
        self.ack = json.loads((self.root / "reviewer-acknowledgment.json").read_text())
        self.signature = json.loads((self.root / "reviewer-acknowledgment-signature.json").read_text())
        self.handoff_fp = (self.root / "DEMO-handoff-fingerprint.txt").read_text().strip()
        self.reviewer_fp = (self.root / "DEMO-reviewer-fingerprint.txt").read_text().strip()
        self.evidence_root = self.root / "private-review-evidence"
        self.evidence_root.mkdir()
        self.evidence_file = self.evidence_root / "synthetic-identity.txt"
        self.evidence_file.write_bytes(b"Synthetic record; not externally authenticated.\n")
        self.references = {
            category: {"status": "unverified", "references": []}
            for category in _CATEGORIES
        }
        self.references["reviewer_identity"]["references"] = [{
            "locator": "synthetic-identity.txt",
            "sha256": hashlib.sha256(self.evidence_file.read_bytes()).hexdigest(),
        }]

    def tearDown(self):
        self.tmp.cleanup()

    def verify_signatures(self):
        return verify_signed_reviewer_acknowledgment(
            self.root / "sender" / "handoff", self.package,
            self.root / "DEMO-handoff-pin.json", self.handoff_fp,
            self.ack, self.signature,
            self.root / "DEMO-reviewer-pin.json", self.reviewer_fp,
        )

    def verify_evidence(self):
        index = build_reviewer_evidence_index(self.ack, self.references)
        return verify_reviewer_evidence_files(self.ack, index, self.evidence_root)

    def test_complete_synthetic_acceptance_path(self):
        signature_result = self.verify_signatures()
        evidence_result = self.verify_evidence()
        self.assertTrue(signature_result["reviewer_acknowledgment_signature_valid"])
        self.assertTrue(evidence_result["reviewer_evidence_bytes_match"])
        self.assertEqual(evidence_result["checked_reference_count"], 1)
        self.assertFalse(signature_result["reviewer_real_world_identity_verified"])
        self.assertFalse(signature_result["reviewer_independence_verified"])
        self.assertFalse(evidence_result["evidence_authenticity_verified"])

    def test_modified_handoff_breaks_acceptance(self):
        (self.root / "sender" / "handoff" / "evidence" / "synthetic-record.txt").write_bytes(b"altered")
        with self.assertRaises(ValueError):
            self.verify_signatures()

    def test_modified_local_custody_evidence_breaks_acceptance(self):
        self.evidence_file.write_bytes(b"altered")
        with self.assertRaises(ValueError):
            self.verify_evidence()

    def test_wrong_reviewer_fingerprint_breaks_acceptance(self):
        self.reviewer_fp = "0" * 64
        with self.assertRaises(ValueError):
            self.verify_signatures()

    def test_missing_evidence_breaks_acceptance(self):
        self.evidence_file.unlink()
        with self.assertRaises(OSError):
            self.verify_evidence()
