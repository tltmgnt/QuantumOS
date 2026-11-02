import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from quantum_omega.gap_provenance_example import create_provenance_example
from quantum_omega.gap_audit_bundle_cli import main

class AuditBundleCLITests(unittest.TestCase):
    def test_export_verify_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "study"
            create_provenance_example(root)
            (root / "evaluation.json").unlink()
            bundle = Path(tmp) / "bundle.json"
            self.assertEqual(main(["export", str(root), "--output", str(bundle)]), 0)
            self.assertEqual(json.loads(bundle.read_text())["kind"], "tga_study_audit_bundle")
            with patch("sys.stdout", new_callable=io.StringIO) as stdout:
                self.assertEqual(main(["verify", str(root), "--bundle", str(bundle)]), 0)
                self.assertTrue(json.loads(stdout.getvalue())["audit_bundle_verified"])
            with patch("sys.stderr", new_callable=io.StringIO):
                self.assertEqual(main(["export", str(root), "--output", str(bundle)]), 1)

    def test_verify_rejects_changed_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "study"
            create_provenance_example(root)
            (root / "evaluation.json").unlink()
            bundle = Path(tmp) / "bundle.json"
            self.assertEqual(main(["export", str(root), "--output", str(bundle)]), 0)
            with (root / "labels.json").open("ab") as stream:
                stream.write(b" ")
            with patch("sys.stderr", new_callable=io.StringIO):
                self.assertEqual(main(["verify", str(root), "--bundle", str(bundle)]), 1)
