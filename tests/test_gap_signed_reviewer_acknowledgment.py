import base64
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from quantum_omega.gap_signed_reviewer_demo import create_signed_reviewer_demo
from quantum_omega.gap_trusted_key_pin import pin_trusted_public_key
from quantum_omega.gap_portable_reviewer_receipt_package import build_portable_reviewer_receipt_package
from quantum_omega.gap_reviewer_handoff_acknowledgment import create_reviewer_handoff_acknowledgment
from quantum_omega.gap_signed_reviewer_acknowledgment import (
    signed_acknowledgment_payload, verify_signed_reviewer_acknowledgment,
)

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
except ImportError:
    Ed25519PrivateKey = None

@unittest.skipUnless(Ed25519PrivateKey is not None, "Optional cryptography dependency unavailable")
class SignedReviewerAcknowledgmentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        demo = root / "demo"
        create_signed_reviewer_demo(demo)
        self.handoff = demo / "handoff"
        inventory = json.loads((demo / "handoff-inventory.json").read_text())
        signature = json.loads((demo / "handoff-signature.json").read_text())
        handoff_key = (demo / "DEMO-public-key.hex").read_text().strip()
        self.handoff_digest = hashlib.sha256(bytes.fromhex(handoff_key)).hexdigest()
        self.handoff_pin = root / "handoff-pin.json"
        pin_trusted_public_key(handoff_key, self.handoff_digest, self.handoff_pin)
        self.package = build_portable_reviewer_receipt_package(
            self.handoff, inventory, signature, self.handoff_pin, self.handoff_digest
        )
        self.record = create_reviewer_handoff_acknowledgment(
            self.handoff, self.package, self.handoff_pin, self.handoff_digest,
            reviewer_id="reviewer-B", reviewed_at="2026-11-02"
        )
        private = Ed25519PrivateKey.generate()
        key = private.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        self.reviewer_digest = hashlib.sha256(key).hexdigest()
        self.reviewer_pin = root / "reviewer-pin.json"
        pin_trusted_public_key(key.hex(), self.reviewer_digest, self.reviewer_pin)
        self.signature = {
            "schema_version": 1, "kind": "tga_reviewer_acknowledgment_signature",
            "algorithm": "Ed25519",
            "acknowledgment_sha256": self.record["sha256"],
            "reviewer_public_key_sha256": self.reviewer_digest,
            "signature_base64": base64.b64encode(
                private.sign(signed_acknowledgment_payload(self.record))
            ).decode("ascii"),
        }

    def tearDown(self):
        self.tmp.cleanup()

    def verify(self, record=None, signature=None, reviewer_digest=None):
        return verify_signed_reviewer_acknowledgment(
            self.handoff, self.package, self.handoff_pin, self.handoff_digest,
            self.record if record is None else record,
            self.signature if signature is None else signature,
            self.reviewer_pin,
            self.reviewer_digest if reviewer_digest is None else reviewer_digest,
        )

    def test_valid_signature_and_conservative_flags(self):
        result = self.verify()
        self.assertTrue(result["reviewer_acknowledgment_signature_valid"])
        self.assertFalse(result["reviewer_real_world_identity_verified"])
        self.assertFalse(result["reviewer_independence_verified"])

    def test_wrong_independent_reviewer_fingerprint_fails(self):
        with self.assertRaises(ValueError):
            self.verify(reviewer_digest="0" * 64)

    def test_changed_self_declared_identity_fails_signature_even_if_rehashed(self):
        from quantum_omega.gap_reviewer_handoff_acknowledgment import _digest
        altered = copy.deepcopy(self.record)
        altered["reviewer_id"] = "reviewer-C"
        altered.pop("sha256")
        altered["sha256"] = _digest(altered)
        envelope = copy.deepcopy(self.signature)
        envelope["acknowledgment_sha256"] = altered["sha256"]
        with self.assertRaises(ValueError):
            self.verify(record=altered, signature=envelope)

    def test_corrupt_signature_fails(self):
        altered = copy.deepcopy(self.signature)
        altered["signature_base64"] = base64.b64encode(b"0" * 64).decode("ascii")
        with self.assertRaises(ValueError):
            self.verify(signature=altered)
