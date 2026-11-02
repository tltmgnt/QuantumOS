import tempfile
import unittest
from pathlib import Path
from quantum_omega.gap_provenance_example import create_provenance_example
from quantum_omega.gap_study_review import summarize_study_package

class StudyReviewSummaryTests(unittest.TestCase):
    def test_summary_is_deterministic_and_conservative(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "package"
            create_provenance_example(root)
            (root / "evaluation.json").unlink()
            first = summarize_study_package(root)
            second = summarize_study_package(root)
            self.assertEqual(first, second)
            self.assertTrue(all(first["checks"].values()))
            self.assertFalse(any(first["external_verification"].values()))

    def test_tampering_blocks_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "package"
            create_provenance_example(root)
            (root / "evaluation.json").unlink()
            with (root / "labels.json").open("ab") as stream:
                stream.write(b" ")
            with self.assertRaises(ValueError):
                summarize_study_package(root)
