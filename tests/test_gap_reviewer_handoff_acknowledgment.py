import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from quantum_omega.gap_signed_reviewer_demo import create_signed_reviewer_demo
from quantum_omega.gap_trusted_key_pin import pin_trusted_public_key
from quantum_omega.gap_portable_reviewer_receipt_package import build_portable_reviewer_receipt_package
from quantum_omega.gap_reviewer_handoff_acknowledgment import (
    create_reviewer_handoff_acknowledgment, verify_reviewer_handoff_acknowledgment,
)

try:
    import cryptography
except ImportError:
    cryptography = None

@unittest.skipUnless(cryptography is not None, "Optional cryptography dependency unavailable")
class ReviewerHandoffAcknowledgmentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "demo"
        create_signed_reviewer_demo(self.root)
        self.handoff = self.root / "handoff"
        inventory = json.loads((self.root / "handoff-inventory.json").read_text())
        signature = json.loads((self.root / "handoff-signature.json").read_text())
        key = (self.root / "DEMO-public-key.hex").read_text().strip()
        self.fingerprint = hashlib.sha256(bytes.fromhex(key)).hexdigest()
        self.pin = Path(self.tmp.name) / "trusted.json"
        pin_trusted_public_key(key, self.fingerprint, self.pin)
        self.package = build_portable_reviewer_receipt_package(
            self.handoff, inventory, signature, self.pin, self.fingerprint
        )
        self.common = (self.handoff, self.package, self.pin, self.fingerprint)
        self.record = create_reviewer_handoff_acknowledgment(
            *self.common, reviewer_id="reviewer-B", reviewed_at="2026-11-02",
            notes="Synthetic replay only"
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_acknowledgment_roundtrip_and_explicit_limits(self):
        result = verify_reviewer_handoff_acknowledgment(*self.common, self.record)
        self.assertTrue(result["reviewer_acknowledgment_matches_inputs"])
        self.assertFalse(result["reviewer_identity_authenticated"])
        self.assertFalse(self.record["digitally_signed"])
        self.assertFalse(self.record["scientific_validity_independently_verified"])

    def test_changed_identity_or_timestamp_rejected_even_with_rehashed_record(self):
        from quantum_omega.gap_reviewer_handoff_acknowledgment import _digest
        for field, replacement in (
            ("reviewer_id", "reviewer-C"),
            ("reviewed_at", "2099-01-01"),
            ("expected_public_key_sha256", "0" * 64),
            ("reviewer_identity_authenticated", True),
            ("digitally_signed", True),
        ):
            with self.subTest(field=field):
                altered = copy.deepcopy(self.record)
                altered[field] = replacement
                altered.pop("sha256")
                altered["sha256"] = _digest(altered)
                if field in ("reviewer_id", "reviewed_at"):
                    # Self-declared identity and time are not externally authenticated.
                    self.assertTrue(verify_reviewer_handoff_acknowledgment(
                        *self.common, altered
                    )["reviewer_acknowledgment_matches_inputs"])
                else:
                    with self.assertRaises(ValueError):
                        verify_reviewer_handoff_acknowledgment(*self.common, altered)

    def test_wrong_expected_fingerprint_rejected(self):
        with self.assertRaises(ValueError):
            verify_reviewer_handoff_acknowledgment(
                self.handoff, self.package, self.pin, "0" * 64, self.record
            )

    def test_changed_handoff_evidence_rejected(self):
        (self.handoff / "evidence" / "synthetic-record.txt").write_bytes(b"changed")
        with self.assertRaises(ValueError):
            verify_reviewer_handoff_acknowledgment(*self.common, self.record)
