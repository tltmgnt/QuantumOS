import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from quantum_omega.gap_signed_reviewer_demo import create_signed_reviewer_demo
from quantum_omega.gap_trusted_key_pin import pin_trusted_public_key
from quantum_omega.gap_reviewer_verify_cli import main

try:
    import cryptography
except ImportError:
    cryptography = None

@unittest.skipUnless(cryptography is not None, "Optional cryptography dependency unavailable")
class ReviewerVerifyCommandTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "demo"
        create_signed_reviewer_demo(self.root)
        key = (self.root / "DEMO-public-key.hex").read_text().strip()
        self.digest = hashlib.sha256(bytes.fromhex(key)).hexdigest()
        self.pin = Path(self.tmp.name) / "trusted-key.json"
        pin_trusted_public_key(key, self.digest, self.pin)
        self.args = [
            str(self.root / "handoff"),
            "--inventory", str(self.root / "handoff-inventory.json"),
            "--signature", str(self.root / "handoff-signature.json"),
            "--pinned-key", str(self.pin),
            "--expected-sha256", self.digest,
        ]

    def tearDown(self):
        self.tmp.cleanup()

    def test_success_preserves_external_trust_limitations(self):
        with patch("sys.stdout", new_callable=io.StringIO) as out:
            self.assertEqual(main(self.args), 0)
        result = json.loads(out.getvalue())
        self.assertTrue(result["signed_handoff_verified"])
        self.assertTrue(result["study_inputs_replayed"])
        self.assertFalse(result["fingerprint_source_authenticated_by_software"])
        self.assertFalse(result["signer_real_world_identity_verified"])
        self.assertFalse(result["scientific_validity_independently_verified"])

    def test_wrong_expected_fingerprint_fails(self):
        with patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(main(self.args[:-1] + ["0" * 64]), 1)

    def test_changed_evidence_fails(self):
        (self.root / "handoff" / "evidence" / "synthetic-record.txt").write_bytes(b"changed")
        with patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(main(self.args), 1)

    def test_changed_signature_fails(self):
        path = self.root / "handoff-signature.json"
        signature = json.loads(path.read_text())
        signature["signature_base64"] = "AA=="
        path.write_text(json.dumps(signature))
        with patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(main(self.args), 1)
