"""Adversarial Ed25519 tests for pinned-key and signed-inventory trust boundaries."""
import base64
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from quantum_omega.gap_signed_reviewer_demo import create_signed_reviewer_demo
from quantum_omega.gap_portable_handoff_signature import (
    signed_manifest_payload, verify_portable_handoff_signature
)

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
except ImportError:
    Ed25519PrivateKey = None

@unittest.skipUnless(Ed25519PrivateKey is not None, "Optional cryptography dependency unavailable")
class SignatureTrustBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "demo"
        create_signed_reviewer_demo(self.root)
        self.inventory = json.loads((self.root / "handoff-inventory.json").read_text())
        self.signature = json.loads((self.root / "handoff-signature.json").read_text())
        self.pinned_key = (self.root / "DEMO-public-key.hex").read_text().strip()

    def tearDown(self):
        self.tmp.cleanup()

    def verify(self, signature=None, inventory=None, key=None):
        return verify_portable_handoff_signature(
            self.root / "handoff",
            self.inventory if inventory is None else inventory,
            self.signature if signature is None else signature,
            self.pinned_key if key is None else key,
        )

    def test_baseline(self):
        result = self.verify()
        self.assertTrue(result["manifest_signature_valid"])
        self.assertFalse(result["signer_real_world_identity_verified"])

    def test_attacker_replaces_key_and_resigns_but_pinned_key_rejects(self):
        attacker = Ed25519PrivateKey.generate()
        attacker_public = attacker.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        forged = copy.deepcopy(self.signature)
        forged["public_key_sha256"] = hashlib.sha256(attacker_public).hexdigest()
        forged["signature_base64"] = base64.b64encode(
            attacker.sign(signed_manifest_payload(self.inventory))
        ).decode("ascii")
        with self.assertRaises(ValueError):
            self.verify(signature=forged)
        # This succeeds only if the verifier explicitly trusts the substituted
        # key, demonstrating why a public key shipped with a handoff is not trusted.
        result = self.verify(signature=forged, key=attacker_public.hex())
        self.assertTrue(result["manifest_signature_valid"])
        self.assertFalse(result["signer_real_world_identity_verified"])

    def test_signature_from_wrong_message_rejected(self):
        attacker = Ed25519PrivateKey.generate()
        attacker_public = attacker.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        forged = copy.deepcopy(self.signature)
        forged["public_key_sha256"] = hashlib.sha256(attacker_public).hexdigest()
        forged["signature_base64"] = base64.b64encode(
            attacker.sign(b"unrelated message")
        ).decode("ascii")
        with self.assertRaises(ValueError):
            self.verify(signature=forged, key=attacker_public.hex())

    def test_modified_envelope_rejected(self):
        for field, value in (
            ("algorithm", "RSA"),
            ("kind", "untrusted_signature"),
            ("schema_version", 2),
            ("manifest_sha256", "0" * 64),
            ("signature_base64", "not base64!"),
        ):
            with self.subTest(field=field):
                forged = copy.deepcopy(self.signature)
                forged[field] = value
                with self.assertRaises(ValueError):
                    self.verify(signature=forged)

    def test_altered_study_and_evidence_rejected(self):
        for path in (
            self.root / "handoff" / "study" / "labels.json",
            self.root / "handoff" / "evidence" / "synthetic-record.txt",
        ):
            with self.subTest(path=path.name):
                original = path.read_bytes()
                try:
                    path.write_bytes(original + b"tampered")
                    with self.assertRaises(ValueError):
                        self.verify()
                finally:
                    path.write_bytes(original)

    def test_signed_inventory_mutation_rejected(self):
        changed = copy.deepcopy(self.inventory)
        changed["files"][0]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            self.verify(inventory=changed)
