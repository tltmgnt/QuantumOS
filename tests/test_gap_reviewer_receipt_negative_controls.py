"""Adversarial checks for replay-verifiable signed reviewer receipts."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from quantum_omega.gap_signed_reviewer_demo import create_signed_reviewer_demo
from quantum_omega.gap_trusted_key_pin import pin_trusted_public_key
from quantum_omega.gap_reviewer_verification_receipt import (
    build_reviewer_verification_receipt, verify_reviewer_verification_receipt,
)

try:
    import cryptography
except ImportError:
    cryptography = None

@unittest.skipUnless(cryptography is not None, "Optional cryptography dependency unavailable")
class ReviewerReceiptNegativeControls(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "demo"
        create_signed_reviewer_demo(self.root)
        self.inventory = json.loads((self.root / "handoff-inventory.json").read_text())
        self.signature = json.loads((self.root / "handoff-signature.json").read_text())
        key = (self.root / "DEMO-public-key.hex").read_text().strip()
        self.expected = hashlib.sha256(bytes.fromhex(key)).hexdigest()
        self.pin = Path(self.tmp.name) / "trusted.json"
        pin_trusted_public_key(key, self.expected, self.pin)
        self.args = (self.root / "handoff", self.inventory, self.signature, self.pin, self.expected)
        self.receipt = build_reviewer_verification_receipt(*self.args)

    def tearDown(self):
        self.tmp.cleanup()

    def test_baseline_receipt_replays(self):
        self.assertTrue(
            verify_reviewer_verification_receipt(*self.args, self.receipt)["reviewer_receipt_matches_inputs"]
        )

    def test_receipt_field_tampering_rejected_even_if_checksum_regenerated(self):
        from quantum_omega.gap_reviewer_verification_receipt import _digest
        for field, replacement in (
            ("portable_inventory_sha256", "0" * 64),
            ("signature_envelope_sha256", "0" * 64),
            ("trusted_public_key_sha256", "0" * 64),
            ("verification_result_sha256", "0" * 64),
            ("signed_handoff_verified", False),
            ("signer_real_world_identity_verified", True),
            ("scientific_validity_independently_verified", True),
        ):
            with self.subTest(field=field):
                changed = copy.deepcopy(self.receipt)
                changed[field] = replacement
                changed.pop("sha256")
                changed["sha256"] = _digest(changed)
                with self.assertRaises(ValueError):
                    verify_reviewer_verification_receipt(*self.args, changed)

    def test_substituted_signature_envelope_rejected(self):
        forged = copy.deepcopy(self.signature)
        forged["signature_base64"] = "AA=="
        with self.assertRaises(ValueError):
            verify_reviewer_verification_receipt(
                self.args[0], self.inventory, forged, self.pin, self.expected, self.receipt
            )

    def test_replaced_pin_rejected_by_independent_expected_fingerprint(self):
        attacker = bytes(range(32))
        pin = json.loads(self.pin.read_text())
        pin["public_key_hex"] = attacker.hex()
        pin["public_key_sha256"] = hashlib.sha256(attacker).hexdigest()
        self.pin.write_text(json.dumps(pin))
        with self.assertRaises(ValueError):
            verify_reviewer_verification_receipt(*self.args, self.receipt)

    def test_inventory_replacement_rejected(self):
        changed = copy.deepcopy(self.inventory)
        changed["files"][0]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            verify_reviewer_verification_receipt(
                self.args[0], changed, self.signature, self.pin, self.expected, self.receipt
            )
