"""Release-guide regression checks for scope and repeatability."""
import unittest
from pathlib import Path

GUIDE = Path(__file__).resolve().parents[1] / "docs" / "tga-v1-release-guide.md"

class V1ReleaseGuideTests(unittest.TestCase):
    def test_reproducibility_and_security_boundaries_documented(self):
        text = GUIDE.read_text(encoding="utf-8").lower()
        for phrase in (
            "release candidate",
            "python -m venv",
            "python -m unittest discover",
            "git rev-parse head",
            "exact candidate commit",
            "no private keys",
            "reviewer independence",
            "scientific validation",
            "fingerprints",
            "security audit checklist",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_release_is_not_prematurely_declared(self):
        text = GUIDE.read_text(encoding="utf-8")
        self.assertIn("not a published v1.0 release", text)
        self.assertIn("after the software release gates pass", text)
