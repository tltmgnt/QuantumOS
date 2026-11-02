"""Guardrails for the independent-reviewer checklist's command-line examples."""
import unittest
from pathlib import Path

class SignedReviewerChecklistTests(unittest.TestCase):
    def test_checklist_requires_independent_fingerprint_on_verification(self):
        path = Path(__file__).resolve().parents[1] / "docs" / "tga-signed-reviewer-checklist.md"
        text = path.read_text(encoding="utf-8")
        self.assertIn("gap_trusted_key_pin_cli pin", text)
        self.assertIn("gap_trusted_key_pin_cli verify", text)
        self.assertIn("--expected-sha256 INDEPENDENTLY_CONFIRMED_SHA256", text)
        self.assertIn("outside", text)
        self.assertIn("identity", text.lower())
        self.assertIn("scientific validity", text.lower())
        self.assertIn("DEMO-public-key.hex", text)
