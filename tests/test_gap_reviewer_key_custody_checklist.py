"""Guard the reviewer custody checklist against accidental trust-boundary regressions."""
import unittest
from pathlib import Path

DOC = Path(__file__).resolve().parents[1] / "docs" / "tga-reviewer-key-custody-checklist.md"

class ReviewerKeyCustodyChecklistTests(unittest.TestCase):
    def test_independent_identity_and_fingerprint_controls_documented(self):
        text = DOC.read_text(encoding="utf-8").lower()
        for phrase in (
            "separately authenticated channel",
            "independently confirm",
            "reviewer",
            "handoff signer",
            "key rotation and revocation",
            "separately controlled",
            "conflicts",
            "authorization",
            "scientific validity",
            "unverified",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_does_not_confuse_signature_with_real_world_identity(self):
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("Separate key pairs alone do **not** establish separate people.", text)
        self.assertIn("does not establish", text.lower())
        self.assertIn("Never publish private signing keys", text)
