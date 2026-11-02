import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from quantum_omega.gap_provenance_example import create_provenance_example
from quantum_omega.gap_study_package_cli import main

class StudyPackageCLITests(unittest.TestCase):
    def test_valid_synthetic_package_and_create_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "study"
            expected = create_provenance_example(root)
            (root / "evaluation.json").unlink()
            output = Path(tmp) / "result.json"
            self.assertEqual(main([str(root), "--output", str(output)]), 0)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), expected)
            with patch("sys.stderr", new_callable=io.StringIO) as stderr:
                self.assertEqual(main([str(root), "--output", str(output)]), 1)
                self.assertIn("Study package validation failed:", stderr.getvalue())

    def test_invalid_package_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("sys.stderr", new_callable=io.StringIO) as stderr:
                self.assertEqual(main([tmp]), 1)
                self.assertIn("six required", stderr.getvalue())
