import json
import tempfile
import unittest
from pathlib import Path

from quantum_omega.gap_signed_reviewer_ack_demo import create_signed_reviewer_ack_demo
from quantum_omega.gap_signed_reviewer_acknowledgment import verify_signed_reviewer_acknowledgment

try:
    import cryptography
except ImportError:
    cryptography = None

@unittest.skipUnless(cryptography is not None, "Optional cryptography dependency unavailable")
class SignedReviewerAckDemoTests(unittest.TestCase):
    def test_demo_roundtrip_and_tamper_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "example"
            result = create_signed_reviewer_ack_demo(root)
            self.assertTrue(result["reviewer_acknowledgment_signature_valid"])
            self.assertFalse(result["reviewer_real_world_identity_verified"])
            self.assertFalse(result["reviewer_independence_verified"])
            package = json.loads((root / "reviewer-package.json").read_text())
            acknowledgment = json.loads((root / "reviewer-acknowledgment.json").read_text())
            signature = json.loads((root / "reviewer-acknowledgment-signature.json").read_text())
            handoff_fingerprint = (root / "DEMO-handoff-fingerprint.txt").read_text().strip()
            reviewer_fingerprint = (root / "DEMO-reviewer-fingerprint.txt").read_text().strip()
            args = (
                root / "sender" / "handoff", package, root / "DEMO-handoff-pin.json",
                handoff_fingerprint, acknowledgment, signature,
                root / "DEMO-reviewer-pin.json", reviewer_fingerprint
            )
            self.assertTrue(verify_signed_reviewer_acknowledgment(
                *args
            )["reviewer_acknowledgment_signature_valid"])
            with self.assertRaises(ValueError):
                verify_signed_reviewer_acknowledgment(
                    *args[:-1], "0" * 64
                )
            signature["signature_base64"] = "AA=="
            with self.assertRaises(ValueError):
                verify_signed_reviewer_acknowledgment(
                    *args[:5], signature, *args[6:]
                )

    def test_existing_destination_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "existing"
            root.mkdir()
            with self.assertRaises(FileExistsError):
                create_signed_reviewer_ack_demo(root)
