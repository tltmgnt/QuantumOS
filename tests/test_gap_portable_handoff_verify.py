import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from quantum_omega.gap_provenance_example import create_provenance_example
from quantum_omega.gap_audit_bundle import build_audit_bundle
from quantum_omega.gap_audit_signoff import create_audit_signoff
from quantum_omega.gap_audit_evidence_refs import create_evidence_references
from quantum_omega.gap_audit_chain_report import build_audit_chain_report
from quantum_omega.gap_audit_handoff_receipt import build_audit_handoff_receipt
from quantum_omega.gap_portable_handoff_manifest import build_portable_handoff_manifest
from quantum_omega.gap_portable_handoff_verify import verify_portable_handoff
from quantum_omega.gap_portable_handoff_verify_cli import main

CATEGORIES = ("registration_authenticity", "reviewer_independence", "label_provenance", "scientific_validity")

class PortableFullVerifyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "handoff"
        study = self.root / "study"
        create_provenance_example(study)
        (study / "evaluation.json").unlink()
        evidence = self.root / "evidence"
        evidence.mkdir()
        (evidence / "record.txt").write_bytes(b"synthetic bytes")
        bundle = build_audit_bundle(study)
        signoff = create_audit_signoff(
            bundle, auditor="Example", organization="Example",
            reviewed_at="2026-11-01T12:00:00Z", repository_commit="a" * 40,
            evidence_statuses={category: "unverified" for category in CATEGORIES},
            notes="Synthetic example."
        )
        refs = {category: [] for category in CATEGORIES}
        refs["label_provenance"] = [{
            "locator": "record.txt", "description": "Synthetic record",
            "sha256": hashlib.sha256(b"synthetic bytes").hexdigest()
        }]
        manifest = create_evidence_references(bundle, signoff, refs)
        report = build_audit_chain_report(bundle, signoff, manifest, evidence)
        receipt = build_audit_handoff_receipt(study, bundle, signoff, manifest, evidence, report)
        for name, value in zip(("bundle", "signoff", "manifest", "report", "receipt"), (bundle, signoff, manifest, report, receipt)):
            (self.root / (name + ".json")).write_text(json.dumps(value))
        self.inventory = build_portable_handoff_manifest(self.root)
        self.inventory_path = Path(self.tmp.name) / "inventory.json"
        self.inventory_path.write_text(json.dumps(self.inventory))

    def tearDown(self):
        self.tmp.cleanup()

    def test_full_verify_and_cli(self):
        result = verify_portable_handoff(self.root, self.inventory)
        self.assertTrue(result["portable_handoff_bytes_match"])
        self.assertTrue(result["handoff_receipt_matches_inputs"])
        self.assertTrue(result["study_inputs_replayed"])
        self.assertFalse(result["external_authenticity_verified"])
        with patch("sys.stdout", new_callable=io.StringIO) as stdout:
            self.assertEqual(main([str(self.root), "--inventory", str(self.inventory_path)]), 0)
            self.assertTrue(json.loads(stdout.getvalue())["handoff_receipt_matches_inputs"])

    def test_changed_evidence_rejected(self):
        (self.root / "evidence" / "record.txt").write_bytes(b"changed")
        with patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(main([str(self.root), "--inventory", str(self.inventory_path)]), 1)

    def test_changed_study_rejected(self):
        (self.root / "study" / "labels.json").write_bytes(b"changed")
        with self.assertRaises(ValueError):
            verify_portable_handoff(self.root, self.inventory)
