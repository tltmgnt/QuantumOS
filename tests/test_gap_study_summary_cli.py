import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from quantum_omega.gap_provenance_example import create_provenance_example
from quantum_omega.gap_study_package_cli import main

class SummaryCLITests(unittest.TestCase):
    def test_summary_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "study"
            create_provenance_example(root)
            (root / "evaluation.json").unlink()
            with patch("sys.stdout", new_callable=io.StringIO) as output:
                self.assertEqual(main([str(root), "--summary"]), 0)
            summary = json.loads(output.getvalue())
            self.assertEqual(summary["kind"], "tga_study_review_summary")
            self.assertTrue(all(summary["checks"].values()))
            self.assertFalse(any(summary["external_verification"].values()))

    def test_summary_rejects_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "study"
            create_provenance_example(root)
            (root / "evaluation.json").unlink()
            with (root / "labels.json").open("ab") as stream:
                stream.write(b" ")
            with patch("sys.stderr", new_callable=io.StringIO):
                self.assertEqual(main([str(root), "--summary"]), 1)
