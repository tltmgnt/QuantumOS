import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from quantum_omega.gap_trusted_key_pin import pin_trusted_public_key, read_pinned_public_key
from quantum_omega.gap_trusted_key_pin_cli import main
from quantum_omega.gap_signed_reviewer_demo import create_signed_reviewer_demo

try:
    import cryptography
except ImportError:
    cryptography = None

class TrustedKeyPinTests(unittest.TestCase):
    def test_pin_checks_fingerprint_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "key.json"
            key = bytes(range(32))
            digest = hashlib.sha256(key).hexdigest()
            with self.assertRaises(ValueError):
                pin_trusted_public_key(key.hex(), "0" * 64, path)
            self.assertFalse(path.exists())
            record = pin_trusted_public_key(key.hex(), digest, path)
            self.assertFalse(record["identity_authenticated_by_software"])
            self.assertEqual(read_pinned_public_key(path), key.hex())
            with self.assertRaises(FileExistsError):
                pin_trusted_public_key(key.hex(), digest, path)
            changed = json.loads(path.read_text())
            changed["public_key_sha256"] = "0" * 64
            path.write_text(json.dumps(changed))
            with self.assertRaises(ValueError):
                read_pinned_public_key(path)

    @unittest.skipUnless(cryptography is not None, "Optional cryptography dependency unavailable")
    def test_pin_and_verify_signed_demo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "demo"
            create_signed_reviewer_demo(root)
            key = (root / "DEMO-public-key.hex").read_text().strip()
            pinned = Path(tmp) / "trusted-key.json"
            digest = hashlib.sha256(bytes.fromhex(key)).hexdigest()
            with patch("sys.stdout", new_callable=io.StringIO):
                self.assertEqual(main(["pin", "--public-key-hex", key, "--expected-sha256", digest, "--output", str(pinned)]), 0)
            with patch("sys.stdout", new_callable=io.StringIO) as out:
                self.assertEqual(main(["verify", str(root / "handoff"), "--inventory", str(root / "handoff-inventory.json"), "--signature", str(root / "handoff-signature.json"), "--pinned-key", str(pinned)]), 0)
                self.assertTrue(json.loads(out.getvalue())["manifest_signature_valid"])
            wrong = Path(tmp) / "wrong.json"
            other = bytes(range(1, 33))
            pin_trusted_public_key(other.hex(), hashlib.sha256(other).hexdigest(), wrong)
            with patch("sys.stderr", new_callable=io.StringIO):
                self.assertEqual(main(["verify", str(root / "handoff"), "--inventory", str(root / "handoff-inventory.json"), "--signature", str(root / "handoff-signature.json"), "--pinned-key", str(wrong)]), 1)
