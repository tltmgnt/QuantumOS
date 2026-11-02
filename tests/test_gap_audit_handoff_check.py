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
from quantum_omega.gap_audit_handoff_check import verify_complete_audit_handoff
from quantum_omega.gap_audit_handoff_check_cli import main

CATEGORIES = ("registration_authenticity", "reviewer_independence", "label_provenance", "scientific_validity")

class CompleteHandoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.study = base / "study"
        create_provenance_example(self.study)
        (self.study / "evaluation.json").unlink()
        bundle = build_audit_bundle(self.study)
        signoff = create_audit_signoff(
            bundle, auditor="Example", organization="Example",
            reviewed_at="2026-11-01T12:00:00Z", repository_commit="a" * 40,
            evidence_statuses={category: "unverified" for category in CATEGORIES},
            notes="Synthetic example only."
        )
        self.evidence = base / "evidence"
        self.evidence.mkdir()
        (self.evidence / "record.txt").write_bytes(b"synthetic bytes")
        refs = {category: [] for category in CATEGORIES}
        refs["label_provenance"] = [{
            "locator": "record.txt", "description": "Synthetic record",
            "sha256": hashlib.sha256(b"synthetic bytes").hexdigest()
        }]
        manifest = create_evidence_references(bundle, signoff, refs)
        report = build_audit_chain_report(bundle, signoff, manifest, self.evidence)
        self.values = (bundle, signoff, manifest, report)
        self.paths = {}
        for name, value in zip(("bundle", "signoff", "manifest", "report"), self.values):
            path = base / (name + ".json")
            path.write_text(json.dumps(value))
            self.paths[name] = path

    def tearDown(self):
        self.tmp.cleanup()

    def args(self):
        result = ["--study-dir", str(self.study), "--evidence-dir", str(self.evidence)]
        for name in ("bundle", "signoff", "manifest", "report"):
            result += ["--" + name, str(self.paths[name])]
        return result

    def test_complete_handoff(self):
        result = verify_complete_audit_handoff(self.study, *self.values[:3], self.evidence, self.values[3])
        self.assertTrue(result["study_inputs_replayed"])
        self.assertFalse(result["external_authenticity_verified"])
        with patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertEqual(main(self.args()), 0)
            self.assertTrue(json.loads(output.getvalue())["audit_bundle_matches_study_inputs"])

    def test_study_input_tampering(self):
        (self.study / "labels.json").write_bytes(b"tampered")
        with patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(main(self.args()), 1)

    def test_saved_report_tampering(self):
        report = dict(self.values[3])
        report["checked_reference_count"] = 99
        self.paths["report"].write_text(json.dumps(report))
        with patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(main(self.args()), 1)
