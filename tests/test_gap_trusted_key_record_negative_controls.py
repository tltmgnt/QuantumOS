"""Negative controls for malformed and self-consistently replaced trust pins."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from quantum_omega.gap_trusted_key_pin import pin_trusted_public_key, read_pinned_public_key

class TrustedKeyRecordNegativeControls(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "trusted.json"
        self.key = bytes(range(32))
        pin_trusted_public_key(self.key.hex(), hashlib.sha256(self.key).hexdigest(), self.path)
        self.original = json.loads(self.path.read_text())

    def tearDown(self):
        self.tmp.cleanup()

    def test_unchanged_record(self):
        self.assertEqual(read_pinned_public_key(self.path), self.key.hex())

    def test_malformed_record_fields_rejected(self):
        cases = [
            ("schema", {"schema_version": 2}),
            ("kind", {"kind": "unknown"}),
            ("flag", {"identity_authenticated_by_software": True}),
            ("fingerprint", {"public_key_sha256": "0" * 64}),
            ("short-key", {"public_key_hex": "00"}),
            ("bad-hex", {"public_key_hex": "z" * 64}),
            ("uppercase-key", {"public_key_hex": self.key.hex().upper()}),
            ("extra-field", {"auditor_identity": "verified"}),
        ]
        for name, changes in cases:
            with self.subTest(name=name):
                modified = copy.deepcopy(self.original)
                modified.update(changes)
                self.path.write_text(json.dumps(modified))
                with self.assertRaises(ValueError):
                    read_pinned_public_key(self.path)

    def test_non_object_json_rejected(self):
        for content in ("[]", "null", '"string"'):
            with self.subTest(content=content):
                self.path.write_text(content)
                with self.assertRaises(ValueError):
                    read_pinned_public_key(self.path)

    def test_self_consistent_replacement_is_not_detected_by_record_alone(self):
        # A file containing a different key and its matching digest is internally
        # consistent. Pin protection must therefore include external file custody.
        attacker = bytes(range(1, 33))
        replacement = copy.deepcopy(self.original)
        replacement["public_key_hex"] = attacker.hex()
        replacement["public_key_sha256"] = hashlib.sha256(attacker).hexdigest()
        self.path.write_text(json.dumps(replacement))
        self.assertEqual(read_pinned_public_key(self.path), attacker.hex())
        self.assertNotEqual(read_pinned_public_key(self.path), self.key.hex())
