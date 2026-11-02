import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import io

from quantum_omega.gap_reviewer_quickstart_example import create_reviewer_quickstart_example, main
from quantum_omega.gap_portable_handoff_verify_cli import main as verify_main

class ReviewerQuickstartExampleTests(unittest.TestCase):
    def test_generate_and_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "example"
            result = create_reviewer_quickstart_example(root)
            self.assertTrue(result["portable_handoff_bytes_match"])
            self.assertTrue(result["handoff_receipt_matches_inputs"])
            self.assertFalse(result["external_authenticity_verified"])
            signoff = json.loads((root / "handoff" / "signoff.json").read_text())
            self.assertEqual(set(signoff["evidence_statuses"].values()), {"unverified"})
            with patch("sys.stdout", new_callable=io.StringIO):
                self.assertEqual(verify_main([
                    str(root / "handoff"), "--inventory", str(root / "handoff-inventory.json")
                ]), 0)
            with self.assertRaises(FileExistsError):
                create_reviewer_quickstart_example(root)

    def test_tampered_evidence_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "example"
            with patch("sys.stdout", new_callable=io.StringIO):
                self.assertEqual(main([str(root)]), 0)
            (root / "handoff" / "evidence" / "synthetic-record.txt").write_bytes(b"changed")
            with patch("sys.stderr", new_callable=io.StringIO):
                self.assertEqual(verify_main([
                    str(root / "handoff"), "--inventory", str(root / "handoff-inventory.json")
                ]), 1)
