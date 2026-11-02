import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from quantum_omega.gap_portable_handoff_manifest_cli import main

STUDY = ("protocol.json", "priority.json", "evidence.json", "labels.json", "reviewers.json", "study.json")
AUDIT = ("bundle.json", "signoff.json", "manifest.json", "report.json", "receipt.json")

class PortableHandoffManifestCLITests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "handoff"
        (self.root / "study").mkdir(parents=True)
        (self.root / "evidence").mkdir()
        for name in STUDY:
            (self.root / "study" / name).write_bytes(b"{}")
        for name in AUDIT:
            (self.root / name).write_bytes(b"{}")
        (self.root / "evidence" / "record.txt").write_bytes(b"sample")
        self.output = Path(self.tmp.name) / "inventory.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_roundtrip_and_no_overwrite(self):
        self.assertEqual(main(["create", str(self.root), "--output", str(self.output)]), 0)
        self.assertEqual(json.loads(self.output.read_text())["file_count"], 12)
        with patch("sys.stdout", new_callable=io.StringIO) as stdout:
            self.assertEqual(main(["verify", str(self.root), "--manifest", str(self.output)]), 0)
            self.assertTrue(json.loads(stdout.getvalue())["portable_handoff_bytes_match"])
        with patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(main(["create", str(self.root), "--output", str(self.output)]), 1)

    def test_changed_bytes_rejected(self):
        self.assertEqual(main(["create", str(self.root), "--output", str(self.output)]), 0)
        (self.root / "evidence" / "record.txt").write_bytes(b"changed")
        with patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(main(["verify", str(self.root), "--manifest", str(self.output)]), 1)

    def test_output_inside_handoff_rejected(self):
        output = self.root / "inventory.json"
        with patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(main(["create", str(self.root), "--output", str(output)]), 1)
        self.assertFalse(output.exists())
