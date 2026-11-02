"""Verification-time fingerprint checks reject internally consistent pin substitution."""
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from quantum_omega.gap_trusted_key_pin import pin_trusted_public_key
from quantum_omega.gap_trusted_key_pin_cli import main
from quantum_omega.gap_signed_reviewer_demo import create_signed_reviewer_demo

try:
    import cryptography
except ImportError:
    cryptography = None

@unittest.skipUnless(cryptography is not None, "Optional cryptography dependency unavailable")
class VerificationFingerprintTests(unittest.TestCase):
    def test_external_fingerprint_rejects_replaced_pin(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "demo"
            create_signed_reviewer_demo(root)
            key = (root / "DEMO-public-key.hex").read_text().strip()
            expected = hashlib.sha256(bytes.fromhex(key)).hexdigest()
            pin = Path(tmp) / "trusted.json"
            pin_trusted_public_key(key, expected, pin)
            args = [
                "verify", str(root / "handoff"),
                "--inventory", str(root / "handoff-inventory.json"),
                "--signature", str(root / "handoff-signature.json"),
                "--pinned-key", str(pin),
            ]
            with patch("sys.stdout", new_callable=io.StringIO) as out:
                self.assertEqual(main(args + ["--expected-sha256", expected]), 0)
                self.assertTrue(json.loads(out.getvalue())["manifest_signature_valid"])
            attacker = bytes(range(32))
            forged = json.loads(pin.read_text())
            forged["public_key_hex"] = attacker.hex()
            forged["public_key_sha256"] = hashlib.sha256(attacker).hexdigest()
            pin.write_text(json.dumps(forged))
            with patch("sys.stderr", new_callable=io.StringIO):
                self.assertEqual(main(args + ["--expected-sha256", expected]), 1)
                self.assertEqual(main(args + ["--expected-sha256", "0" * 64]), 1)
                self.assertEqual(main(args + ["--expected-sha256", "not-a-digest"]), 1)
