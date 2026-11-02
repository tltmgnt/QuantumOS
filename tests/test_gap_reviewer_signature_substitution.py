"""Adversarial signer substitution and acknowledgment-signature trust boundaries."""
import base64
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from quantum_omega.gap_signed_reviewer_ack_demo import create_signed_reviewer_ack_demo
from quantum_omega.gap_signed_reviewer_acknowledgment import (
    signed_acknowledgment_payload, verify_signed_reviewer_acknowledgment
)
from quantum_omega.gap_trusted_key_pin import pin_trusted_public_key

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
except ImportError:
    Ed25519PrivateKey = None

@unittest.skipUnless(Ed25519PrivateKey is not None, "Optional cryptography dependency unavailable")
class ReviewerSignatureSubstitutionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "demo"
        create_signed_reviewer_ack_demo(self.root)
        self.package = json.loads((self.root / "reviewer-package.json").read_text())
        self.record = json.loads((self.root / "reviewer-acknowledgment.json").read_text())
        self.signature = json.loads((self.root / "reviewer-acknowledgment-signature.json").read_text())
        self.handoff_fp = (self.root / "DEMO-handoff-fingerprint.txt").read_text().strip()
        self.reviewer_fp = (self.root / "DEMO-reviewer-fingerprint.txt").read_text().strip()
        self.handoff_pin = self.root / "DEMO-handoff-pin.json"
        self.reviewer_pin = self.root / "DEMO-reviewer-pin.json"

    def tearDown(self):
        self.tmp.cleanup()

    def verify(self, *, record=None, signature=None, pin=None, fingerprint=None):
        return verify_signed_reviewer_acknowledgment(
            self.root / "sender" / "handoff", self.package,
            self.handoff_pin, self.handoff_fp,
            self.record if record is None else record,
            self.signature if signature is None else signature,
            self.reviewer_pin if pin is None else pin,
            self.reviewer_fp if fingerprint is None else fingerprint,
        )

    def test_baseline_passes(self):
        self.assertTrue(self.verify()["reviewer_acknowledgment_signature_valid"])

    def test_attacker_resigns_same_record_under_new_key_fails_with_original_fingerprint(self):
        attacker = Ed25519PrivateKey.generate()
        public = attacker.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        fingerprint = hashlib.sha256(public).hexdigest()
        pin = self.root / "attacker-pin.json"
        pin_trusted_public_key(public.hex(), fingerprint, pin)
        forged = copy.deepcopy(self.signature)
        forged["reviewer_public_key_sha256"] = fingerprint
        forged["signature_base64"] = base64.b64encode(
            attacker.sign(signed_acknowledgment_payload(self.record))
        ).decode("ascii")
        with self.assertRaises(ValueError):
            self.verify(signature=forged, pin=pin)
        # Demonstrates the trust boundary: supplying the attacker's own expected
        # fingerprint accepts a valid signature, but does not authenticate identity.
        result = self.verify(signature=forged, pin=pin, fingerprint=fingerprint)
        self.assertTrue(result["reviewer_acknowledgment_signature_valid"])
        self.assertFalse(result["reviewer_real_world_identity_verified"])

    def test_self_consistent_reviewer_pin_replacement_fails(self):
        attacker = Ed25519PrivateKey.generate()
        public = attacker.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        forged_pin = json.loads(self.reviewer_pin.read_text())
        forged_pin["public_key_hex"] = public.hex()
        forged_pin["public_key_sha256"] = hashlib.sha256(public).hexdigest()
        self.reviewer_pin.write_text(json.dumps(forged_pin))
        with self.assertRaises(ValueError):
            self.verify()

    def test_claimed_reviewer_identity_change_requires_original_signing_key(self):
        from quantum_omega.gap_reviewer_handoff_acknowledgment import _digest
        altered = copy.deepcopy(self.record)
        altered["reviewer_id"] = "impostor"
        altered.pop("sha256")
        altered["sha256"] = _digest(altered)
        forged = copy.deepcopy(self.signature)
        forged["acknowledgment_sha256"] = altered["sha256"]
        with self.assertRaises(ValueError):
            self.verify(record=altered, signature=forged)

    def test_signature_envelope_metadata_tampering_fails(self):
        for field, value in (
            ("algorithm", "not-Ed25519"),
            ("reviewer_public_key_sha256", "0" * 64),
            ("acknowledgment_sha256", "0" * 64),
            ("signature_base64", "AA=="),
        ):
            with self.subTest(field=field):
                forged = copy.deepcopy(self.signature)
                forged[field] = value
                with self.assertRaises(ValueError):
                    self.verify(signature=forged)
