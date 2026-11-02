import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from quantum_omega.gap_provenance_example import create_provenance_example
from quantum_omega.gap_audit_bundle import build_audit_bundle
from quantum_omega.gap_audit_signoff import create_audit_signoff
from quantum_omega.gap_audit_evidence_refs_cli import main

CATEGORIES = ("registration_authenticity", "reviewer_independence", "label_provenance", "scientific_validity")

class EvidenceRefsCLITests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name) / "study"
        create_provenance_example(root)
        (root / "evaluation.json").unlink()
        bundle = build_audit_bundle(root)
        signoff = create_audit_signoff(
            bundle, auditor="Example Auditor", organization="Example Lab",
            reviewed_at="2026-11-01T12:00:00Z", repository_commit="a" * 40,
            evidence_statuses={category: "unverified" for category in CATEGORIES},
            notes="No independent external evidence assessed."
        )
        self.bundle = Path(self.tmp.name) / "bundle.json"
        self.signoff = Path(self.tmp.name) / "signoff.json"
        self.references = Path(self.tmp.name) / "references.json"
        self.manifest = Path(self.tmp.name) / "manifest.json"
        self.bundle.write_text(json.dumps(bundle))
        self.signoff.write_text(json.dumps(signoff))
        self.references.write_text(json.dumps({category: [] for category in CATEGORIES}))

    def tearDown(self):
        self.tmp.cleanup()

    def create_args(self):
        return ["create", "--bundle", str(self.bundle), "--signoff", str(self.signoff),
                "--references", str(self.references), "--output", str(self.manifest)]

    def verify_args(self):
        return ["verify", "--bundle", str(self.bundle), "--signoff", str(self.signoff),
                "--manifest", str(self.manifest)]

    def test_roundtrip_and_create_only(self):
        self.assertEqual(main(self.create_args()), 0)
        with patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertEqual(main(self.verify_args()), 0)
            self.assertTrue(json.loads(output.getvalue())["evidence_references_consistent"])
        with patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(main(self.create_args()), 1)

    def test_tampering_rejected(self):
        self.assertEqual(main(self.create_args()), 0)
        manifest = json.loads(self.manifest.read_text())
        manifest["references"]["scientific_validity"].append({
            "locator": "example", "description": "altered", "sha256": "a" * 64
        })
        self.manifest.write_text(json.dumps(manifest))
        with patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(main(self.verify_args()), 1)
