import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from quantum_omega.gap_signed_reviewer_demo import create_signed_reviewer_demo
from quantum_omega.gap_trusted_key_pin import pin_trusted_public_key
from quantum_omega.gap_reviewer_verification_receipt import (
    build_reviewer_verification_receipt, verify_reviewer_verification_receipt
)

try:
    import cryptography
except ImportError:
    cryptography = None

@unittest.skipUnless(cryptography is not None, "Optional cryptography dependency unavailable")
class ReviewerVerificationReceiptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "demo"
        create_signed_reviewer_demo(self.root)
        self.inventory = json.loads((self.root / "handoff-inventory.json").read_text())
        self.signature = json.loads((self.root / "handoff-signature.json").read_text())
        key = (self.root / "DEMO-public-key.hex").read_text().strip()
        self.digest = hashlib.sha256(bytes.fromhex(key)).hexdigest()
        self.pin = Path(self.tmp.name) / "trusted.json"
        pin_trusted_public_key(key, self.digest, self.pin)
        self.inputs = (self.root / "handoff", self.inventory, self.signature, self.pin, self.digest)

    def tearDown(self):
        self.tmp.cleanup()

    def test_receipt_roundtrip_and_conservative_flags(self):
        receipt = build_reviewer_verification_receipt(*self.inputs)
        self.assertEqual(receipt, build_reviewer_verification_receipt(*self.inputs))
        self.assertFalse(receipt["signer_real_world_identity_verified"])
        self.assertFalse(receipt["scientific_validity_independently_verified"])
        self.assertTrue(verify_reviewer_verification_receipt(*self.inputs, receipt)["reviewer_receipt_matches_inputs"])

    def test_modified_receipt_rejected(self):
        receipt = build_reviewer_verification_receipt(*self.inputs)
        changed = copy.deepcopy(receipt)
        changed["signer_real_world_identity_verified"] = True
        with self.assertRaises(ValueError):
            verify_reviewer_verification_receipt(*self.inputs, changed)
        changed = copy.deepcopy(receipt)
        changed["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            verify_reviewer_verification_receipt(*self.inputs, changed)

    def test_modified_local_evidence_rejected(self):
        receipt = build_reviewer_verification_receipt(*self.inputs)
        (self.root / "handoff" / "evidence" / "synthetic-record.txt").write_bytes(b"changed")
        with self.assertRaises(ValueError):
            verify_reviewer_verification_receipt(*self.inputs, receipt)
