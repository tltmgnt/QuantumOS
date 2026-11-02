import base64
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from quantum_omega.gap_reviewer_quickstart_example import create_reviewer_quickstart_example
from quantum_omega.gap_portable_handoff_signature import (
    signed_manifest_payload, verify_portable_handoff_signature
)

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
except ImportError:
    Ed25519PrivateKey = None

@unittest.skipUnless(Ed25519PrivateKey is not None, "Optional cryptography dependency unavailable")
class PortableHandoffSignatureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "example"
        create_reviewer_quickstart_example(self.root)
        self.inventory = json.loads((self.root / "handoff-inventory.json").read_text())
        self.private = Ed25519PrivateKey.generate()
        self.key = self.private.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        self.envelope = {
            "schema_version": 1, "kind": "tga_portable_manifest_signature",
            "algorithm": "Ed25519", "manifest_sha256": self.inventory["sha256"],
            "public_key_sha256": hashlib.sha256(self.key).hexdigest(),
            "signature_base64": base64.b64encode(
                self.private.sign(signed_manifest_payload(self.inventory))
            ).decode("ascii"),
        }

    def tearDown(self):
        self.tmp.cleanup()

    def verify(self, envelope=None, key=None):
        return verify_portable_handoff_signature(
            self.root / "handoff", self.inventory,
            self.envelope if envelope is None else envelope,
            self.key.hex() if key is None else key,
        )

    def test_valid_signature_and_explicit_identity_limit(self):
        result = self.verify()
        self.assertTrue(result["manifest_signature_valid"])
        self.assertTrue(result["study_inputs_replayed"])
        self.assertFalse(result["signer_real_world_identity_verified"])

    def test_wrong_trusted_key_rejected(self):
        other = Ed25519PrivateKey.generate().public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        with self.assertRaises(ValueError):
            self.verify(key=other.hex())

    def test_changed_signature_rejected(self):
        changed = dict(self.envelope)
        changed["signature_base64"] = base64.b64encode(b"0" * 64).decode("ascii")
        with self.assertRaises(ValueError):
            self.verify(envelope=changed)

    def test_changed_signed_metadata_rejected(self):
        changed = dict(self.envelope)
        changed["manifest_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            self.verify(envelope=changed)

    def test_changed_local_file_rejected_even_with_signature(self):
        (self.root / "handoff" / "evidence" / "synthetic-record.txt").write_bytes(b"tampered")
        with self.assertRaises(ValueError):
            self.verify()
