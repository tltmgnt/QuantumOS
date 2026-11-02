"""Two-reviewer transfer controls for portable signed verification receipts."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from quantum_omega.gap_signed_reviewer_demo import create_signed_reviewer_demo
from quantum_omega.gap_trusted_key_pin import pin_trusted_public_key
from quantum_omega.gap_portable_reviewer_receipt_package import (
    build_portable_reviewer_receipt_package, verify_portable_reviewer_receipt_package,
)

try:
    import cryptography
except ImportError:
    cryptography = None

@unittest.skipUnless(cryptography is not None, "Optional cryptography dependency unavailable")
class CrossReviewerPortabilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.demo = self.base / "sender"
        create_signed_reviewer_demo(self.demo)
        self.handoff = self.demo / "handoff"
        self.inventory = json.loads((self.demo / "handoff-inventory.json").read_text())
        self.signature = json.loads((self.demo / "handoff-signature.json").read_text())
        key = (self.demo / "DEMO-public-key.hex").read_text().strip()
        self.fingerprint = hashlib.sha256(bytes.fromhex(key)).hexdigest()
        self.sender_pin = self.base / "sender-trust" / "trusted.json"
        self.sender_pin.parent.mkdir()
        self.receiver_pin = self.base / "receiver-trust" / "trusted.json"
        self.receiver_pin.parent.mkdir()
        pin_trusted_public_key(key, self.fingerprint, self.sender_pin)
        pin_trusted_public_key(key, self.fingerprint, self.receiver_pin)
        self.package = build_portable_reviewer_receipt_package(
            self.handoff, self.inventory, self.signature, self.sender_pin, self.fingerprint
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_two_separately_pinned_reviewers_accept_identical_package(self):
        sender = verify_portable_reviewer_receipt_package(
            self.handoff, self.package, self.sender_pin, self.fingerprint
        )
        receiver = verify_portable_reviewer_receipt_package(
            self.handoff, self.package, self.receiver_pin, self.fingerprint
        )
        self.assertEqual(sender, receiver)
        self.assertTrue(receiver["portable_reviewer_receipt_package_valid"])
        self.assertFalse(receiver["signer_real_world_identity_verified"])

    def test_recipient_rejects_wrong_expected_fingerprint(self):
        with self.assertRaises(ValueError):
            verify_portable_reviewer_receipt_package(
                self.handoff, self.package, self.receiver_pin, "0" * 64
            )

    def test_recipient_rejects_self_consistent_key_substitution(self):
        attacker_key = bytes(range(32))
        pin = json.loads(self.receiver_pin.read_text())
        pin["public_key_hex"] = attacker_key.hex()
        pin["public_key_sha256"] = hashlib.sha256(attacker_key).hexdigest()
        self.receiver_pin.write_text(json.dumps(pin))
        with self.assertRaises(ValueError):
            verify_portable_reviewer_receipt_package(
                self.handoff, self.package, self.receiver_pin, self.fingerprint
            )
        # Sender's separately controlled pin remains usable.
        self.assertTrue(verify_portable_reviewer_receipt_package(
            self.handoff, self.package, self.sender_pin, self.fingerprint
        )["portable_reviewer_receipt_package_valid"])

    def test_recipient_rejects_package_claim_forgery_with_recomputed_checksum(self):
        from quantum_omega.gap_portable_reviewer_receipt_package import _canonical_digest
        changed = copy.deepcopy(self.package)
        changed["external_authenticity_verified"] = True
        changed.pop("sha256")
        changed["sha256"] = _canonical_digest(changed)
        with self.assertRaises(ValueError):
            verify_portable_reviewer_receipt_package(
                self.handoff, changed, self.receiver_pin, self.fingerprint
            )

    def test_recipient_rejects_missing_handoff_evidence(self):
        (self.handoff / "evidence" / "synthetic-record.txt").unlink()
        with self.assertRaises((ValueError, OSError)):
            verify_portable_reviewer_receipt_package(
                self.handoff, self.package, self.receiver_pin, self.fingerprint
            )
