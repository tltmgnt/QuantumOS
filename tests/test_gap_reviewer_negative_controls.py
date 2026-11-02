"""Adversarial reviewer checks against a complete synthetic portable handoff."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from quantum_omega.gap_reviewer_quickstart_example import create_reviewer_quickstart_example
from quantum_omega.gap_portable_handoff_verify import verify_portable_handoff
from quantum_omega.gap_portable_handoff_manifest import build_portable_handoff_manifest

class ReviewerNegativeControlsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "example"
        create_reviewer_quickstart_example(self.root)
        self.handoff = self.root / "handoff"
        self.inventory = json.loads((self.root / "handoff-inventory.json").read_text())

    def tearDown(self):
        self.tmp.cleanup()

    def test_unchanged_baseline(self):
        result = verify_portable_handoff(self.handoff, self.inventory)
        self.assertTrue(result["study_inputs_replayed"])
        self.assertFalse(result["external_authenticity_verified"])

    def test_each_study_file_byte_mutation_rejected(self):
        for name in ("protocol", "priority", "evidence", "labels", "reviewers", "study"):
            with self.subTest(name=name):
                path = self.handoff / "study" / (name + ".json")
                original = path.read_bytes()
                try:
                    path.write_bytes(original + b" ")
                    with self.assertRaises(ValueError):
                        verify_portable_handoff(self.handoff, self.inventory)
                finally:
                    path.write_bytes(original)

    def test_each_audit_artifact_byte_mutation_rejected(self):
        for name in ("bundle", "signoff", "manifest", "report", "receipt"):
            with self.subTest(name=name):
                path = self.handoff / (name + ".json")
                original = path.read_bytes()
                try:
                    path.write_bytes(original + b" ")
                    with self.assertRaises(ValueError):
                        verify_portable_handoff(self.handoff, self.inventory)
                finally:
                    path.write_bytes(original)

    def test_local_evidence_mutation_rejected(self):
        path = self.handoff / "evidence" / "synthetic-record.txt"
        path.write_bytes(b"wrong evidence")
        with self.assertRaises(ValueError):
            verify_portable_handoff(self.handoff, self.inventory)

    def test_missing_or_extra_evidence_rejected(self):
        extra = self.handoff / "evidence" / "unlisted.txt"
        extra.write_bytes(b"unexpected")
        with self.assertRaises(ValueError):
            verify_portable_handoff(self.handoff, self.inventory)
        extra.unlink()
        (self.handoff / "evidence" / "synthetic-record.txt").unlink()
        with self.assertRaises(ValueError):
            verify_portable_handoff(self.handoff, self.inventory)

    def test_saved_inventory_tampering_rejected(self):
        changed = copy.deepcopy(self.inventory)
        changed["files"][0]["byte_count"] += 1
        with self.assertRaises(ValueError):
            verify_portable_handoff(self.handoff, changed)

    def test_self_consistent_inventory_cannot_hide_bad_audit_record(self):
        path = self.handoff / "receipt.json"
        receipt = json.loads(path.read_text())
        receipt["checked_reference_count"] += 1
        path.write_text(json.dumps(receipt))
        rebuilt_inventory = build_portable_handoff_manifest(self.handoff)
        with self.assertRaises(ValueError):
            verify_portable_handoff(self.handoff, rebuilt_inventory)

    def test_self_consistent_inventory_cannot_hide_changed_study(self):
        path = self.handoff / "study" / "labels.json"
        path.write_bytes(path.read_bytes() + b" ")
        rebuilt_inventory = build_portable_handoff_manifest(self.handoff)
        with self.assertRaises(ValueError):
            verify_portable_handoff(self.handoff, rebuilt_inventory)
