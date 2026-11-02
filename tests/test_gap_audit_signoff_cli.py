import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from quantum_omega.gap_provenance_example import create_provenance_example
from quantum_omega.gap_audit_bundle import build_audit_bundle
from quantum_omega.gap_audit_signoff_cli import main

class SignoffCLITests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name) / "study"
        create_provenance_example(root)
        (root / "evaluation.json").unlink()
        self.bundle = Path(self.tmp.name) / "bundle.json"
        self.bundle.write_text(json.dumps(build_audit_bundle(root)))
        self.declaration = Path(self.tmp.name) / "declaration.json"
        self.declaration.write_text(json.dumps({
            "auditor": "Example Auditor", "organization": "Example Lab",
            "reviewed_at": "2026-11-01T12:00:00Z", "repository_commit": "a" * 40,
            "evidence_statuses": {
                "registration_authenticity": "unverified",
                "reviewer_independence": "unverified",
                "label_provenance": "unverified",
                "scientific_validity": "unverified",
            },
            "notes": "Synthetic example only."
        }))
        self.signoff = Path(self.tmp.name) / "signoff.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_create_verify_and_no_overwrite(self):
        args = ["create", "--bundle", str(self.bundle), "--declaration", str(self.declaration), "--output", str(self.signoff)]
        self.assertEqual(main(args), 0)
        with patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertEqual(main(["verify", "--bundle", str(self.bundle), "--signoff", str(self.signoff)]), 0)
            self.assertTrue(json.loads(output.getvalue())["signoff_checksum_consistent"])
        with patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(main(args), 1)

    def test_rejects_changed_signoff(self):
        self.assertEqual(main(["create", "--bundle", str(self.bundle), "--declaration", str(self.declaration), "--output", str(self.signoff)]), 0)
        signoff = json.loads(self.signoff.read_text())
        signoff["notes"] = "altered"
        self.signoff.write_text(json.dumps(signoff))
        with patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(main(["verify", "--bundle", str(self.bundle), "--signoff", str(self.signoff)]), 1)
