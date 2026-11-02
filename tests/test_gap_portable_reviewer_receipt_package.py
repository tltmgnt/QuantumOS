import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from quantum_omega.gap_signed_reviewer_demo import create_signed_reviewer_demo
from quantum_omega.gap_trusted_key_pin import pin_trusted_public_key
from quantum_omega.gap_portable_reviewer_receipt_package import (
    build_portable_reviewer_receipt_package, verify_portable_reviewer_receipt_package
)

try:
    import cryptography
except ImportError:
    cryptography = None

@unittest.skipUnless(cryptography is not None, "Optional cryptography dependency unavailable")
class PortableReviewerReceiptPackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "demo"
        create_signed_reviewer_demo(self.root)
        inventory = json.loads((self.root / "handoff-inventory.json").read_text())
        signature = json.loads((self.root / "handoff-signature.json").read_text())
        key = (self.root / "DEMO-public-key.hex").read_text().strip()
        self.digest = hashlib.sha256(bytes.fromhex(key)).hexdigest()
        self.pin = Path(self.tmp.name) / "trusted.json"
        pin_trusted_public_key(key, self.digest, self.pin)
        self.handoff = self.root / "handoff"
        self.package = build_portable_reviewer_receipt_package(
            self.handoff, inventory, signature, self.pin, self.digest
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_package_replays_without_embedding_trust_anchor(self):
        self.assertNotIn("public_key_hex", json.dumps(self.package))
        self.assertEqual(self.package["signature"]["public_key_sha256"], self.digest)
        self.assertFalse(self.package["trusted_key_embedded"])
        self.assertFalse(self.package["expected_fingerprint_embedded"])
        result = verify_portable_reviewer_receipt_package(
            self.handoff, self.package, self.pin, self.digest
        )
        self.assertTrue(result["portable_reviewer_receipt_package_valid"])
        self.assertFalse(result["external_authenticity_verified"])

    def test_modified_package_rejected(self):
        for field, value in (
            ("trusted_key_embedded", True),
            ("expected_fingerprint_embedded", True),
            ("scientific_validity_independently_verified", True),
            ("sha256", "0" * 64),
        ):
            with self.subTest(field=field):
                changed = copy.deepcopy(self.package)
                changed[field] = value
                with self.assertRaises(ValueError):
                    verify_portable_reviewer_receipt_package(
                        self.handoff, changed, self.pin, self.digest
                    )

    def test_wrong_external_fingerprint_rejected(self):
        with self.assertRaises(ValueError):
            verify_portable_reviewer_receipt_package(
                self.handoff, self.package, self.pin, "0" * 64
            )

    def test_changed_evidence_rejected(self):
        (self.handoff / "evidence" / "synthetic-record.txt").write_bytes(b"changed")
        with self.assertRaises(ValueError):
            verify_portable_reviewer_receipt_package(
                self.handoff, self.package, self.pin, self.digest
            )
