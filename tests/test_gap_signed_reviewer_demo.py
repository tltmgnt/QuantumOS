import json
import tempfile
import unittest
from pathlib import Path

from quantum_omega.gap_signed_reviewer_demo import create_signed_reviewer_demo
from quantum_omega.gap_portable_handoff_signature import verify_portable_handoff_signature

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
except ImportError:
    Ed25519PrivateKey = None

@unittest.skipUnless(Ed25519PrivateKey is not None, "Optional cryptography dependency unavailable")
class SignedReviewerDemoTests(unittest.TestCase):
    def test_generate_and_verify_with_demo_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "demo"
            result = create_signed_reviewer_demo(root)
            self.assertTrue(result["manifest_signature_valid"])
            self.assertTrue(result["study_inputs_replayed"])
            self.assertFalse(result["signer_real_world_identity_verified"])
            inventory = json.loads((root / "handoff-inventory.json").read_text())
            signature = json.loads((root / "handoff-signature.json").read_text())
            key = (root / "DEMO-public-key.hex").read_text().strip()
            verified = verify_portable_handoff_signature(root / "handoff", inventory, signature, key)
            self.assertTrue(verified["manifest_signature_valid"])
            self.assertFalse(any("private" in p.name.lower() for p in root.rglob("*")))
            with self.assertRaises(FileExistsError):
                create_signed_reviewer_demo(root)

    def test_changed_signature_and_evidence_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "demo"
            create_signed_reviewer_demo(root)
            inventory = json.loads((root / "handoff-inventory.json").read_text())
            signature = json.loads((root / "handoff-signature.json").read_text())
            key = (root / "DEMO-public-key.hex").read_text().strip()
            signature["signature_base64"] = "AA=="
            with self.assertRaises(ValueError):
                verify_portable_handoff_signature(root / "handoff", inventory, signature, key)
            signature = json.loads((root / "handoff-signature.json").read_text())
            (root / "handoff" / "evidence" / "synthetic-record.txt").write_bytes(b"tampered")
            with self.assertRaises(ValueError):
                verify_portable_handoff_signature(root / "handoff", inventory, signature, key)
