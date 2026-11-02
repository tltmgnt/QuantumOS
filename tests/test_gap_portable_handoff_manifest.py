import tempfile
import unittest
from pathlib import Path
from quantum_omega.gap_portable_handoff_manifest import (
    build_portable_handoff_manifest, verify_portable_handoff_manifest
)

STUDY = ("protocol.json", "priority.json", "evidence.json", "labels.json", "reviewers.json", "study.json")
AUDIT = ("bundle.json", "signoff.json", "manifest.json", "report.json", "receipt.json")

class PortableHandoffManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "handoff"
        (self.root / "study").mkdir(parents=True)
        (self.root / "evidence").mkdir()
        for name in STUDY:
            (self.root / "study" / name).write_bytes(b"{}")
        for name in AUDIT:
            (self.root / name).write_bytes(b"{}")
        (self.root / "evidence" / "sample.txt").write_bytes(b"sample")

    def tearDown(self):
        self.tmp.cleanup()

    def test_deterministic_inventory_and_verify(self):
        manifest = build_portable_handoff_manifest(self.root)
        self.assertEqual(manifest, build_portable_handoff_manifest(self.root))
        self.assertEqual(manifest["file_count"], 12)
        self.assertFalse(verify_portable_handoff_manifest(self.root, manifest)["audit_chain_replayed"])

    def test_changed_bytes_rejected(self):
        manifest = build_portable_handoff_manifest(self.root)
        (self.root / "evidence" / "sample.txt").write_bytes(b"changed")
        with self.assertRaises(ValueError):
            verify_portable_handoff_manifest(self.root, manifest)

    def test_extra_file_rejected(self):
        (self.root / "extra.json").write_text("{}")
        with self.assertRaises(ValueError):
            build_portable_handoff_manifest(self.root)

    def test_symlink_rejected(self):
        (self.root / "evidence" / "link.txt").symlink_to(self.root / "evidence" / "sample.txt")
        with self.assertRaises(ValueError):
            build_portable_handoff_manifest(self.root)
