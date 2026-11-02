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
from quantum_omega.gap_audit_chain_verify import verify_audit_chain_report
from quantum_omega.gap_audit_chain_verify_cli import main

CATEGORIES = ("registration_authenticity", "reviewer_independence", "label_provenance", "scientific_validity")

class AuditChainVerifyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name) / "study"
        create_provenance_example(root)
        (root / "evaluation.json").unlink()
        bundle = build_audit_bundle(root)
        signoff = create_audit_signoff(
            bundle, auditor="Example", organization="Example",
            reviewed_at="2026-11-01T12:00:00Z", repository_commit="a" * 40,
            evidence_statuses={category: "unverified" for category in CATEGORIES},
            notes="No independently authenticated evidence."
        )
        self.evidence = Path(self.tmp.name) / "evidence"
        self.evidence.mkdir()
        (self.evidence / "record.txt").write_bytes(b"synthetic bytes")
        refs = {category: [] for category in CATEGORIES}
        refs["label_provenance"] = [{
            "locator": "record.txt", "description": "Synthetic evidence",
            "sha256": hashlib.sha256(b"synthetic bytes").hexdigest()
        }]
        manifest = create_evidence_references(bundle, signoff, refs)
        report = build_audit_chain_report(bundle, signoff, manifest, self.evidence)
        self.values = (bundle, signoff, manifest, report)
        self.paths = {}
        for name, value in zip(("bundle", "signoff", "manifest", "report"), self.values):
            path = Path(self.tmp.name) / (name + ".json")
            path.write_text(json.dumps(value))
            self.paths[name] = path

    def tearDown(self):
        self.tmp.cleanup()

    def args(self):
        args = []
        for name in ("bundle", "signoff", "manifest", "report"):
            args.extend(("--" + name, str(self.paths[name])))
        return args + ["--evidence-dir", str(self.evidence)]

    def test_verify_saved_report(self):
        result = verify_audit_chain_report(*self.values[:3], self.evidence, self.values[3])
        self.assertTrue(result["audit_chain_report_matches_inputs"])
        self.assertFalse(result["external_authenticity_verified"])
        with patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertEqual(main(self.args()), 0)
            self.assertTrue(json.loads(output.getvalue())["audit_chain_report_matches_inputs"])

    def test_changed_report_rejected(self):
        report = dict(self.values[3])
        report["checked_reference_count"] = 999
        with self.assertRaises(ValueError):
            verify_audit_chain_report(*self.values[:3], self.evidence, report)
        self.paths["report"].write_text(json.dumps(report))
        with patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(main(self.args()), 1)

    def test_changed_evidence_rejected(self):
        (self.evidence / "record.txt").write_bytes(b"changed")
        with patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(main(self.args()), 1)
