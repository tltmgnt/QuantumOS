import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from quantum_omega.gap_provenance_example import create_provenance_example
from quantum_omega.gap_study_package import validate_study_package

class StudyPackageTests(unittest.TestCase):
    def test_example_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "package"
            expected = create_provenance_example(root)
            (root / "evaluation.json").unlink()
            self.assertEqual(validate_study_package(root), expected)

    def test_rejects_extra_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "package"
            create_provenance_example(root)
            with self.assertRaises(ValueError):
                validate_study_package(root)

    def test_rejects_tampered_label(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "package"
            create_provenance_example(root)
            (root / "evaluation.json").unlink()
            with (root / "labels.json").open("ab") as stream:
                stream.write(b" ")
            with self.assertRaises(ValueError):
                validate_study_package(root)

    def test_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "package"
            create_provenance_example(root)
            (root / "evaluation.json").unlink()
            (root / "labels.json").unlink()
            (root / "labels.json").symlink_to(root / "study.json")
            with self.assertRaises(ValueError):
                validate_study_package(root)
