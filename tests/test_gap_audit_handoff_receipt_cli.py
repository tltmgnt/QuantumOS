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
from quantum_omega.gap_audit_handoff_receipt_cli import main

CATEGORIES = ("registration_authenticity", "reviewer_independence", "label_provenance", "scientific_validity")

class AuditHandoffReceiptCLITests(unittest.TestCase):
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
            "locator": "record.txt", "description": "Synthetic evidence",
            "sha256": hashlib.sha256(b"synthetic bytes").hexdigest()
        }]
        manifest = create_evidence_references(bundle, signoff, refs)
        report = build_audit_chain_report(bundle, signoff, manifest, self.evidence)
        self.paths = {}
        for name, value in zip(("bundle", "signoff", "manifest", "report"), (bundle, signoff, manifest, report)):
            path = base / (name + ".json")
            path.write_text(json.dumps(value))
            self.paths[name] = path
        self.receipt = base / "receipt.json"

    def tearDown(self):
        self.tmp.cleanup()

    def args(self, command):
        result = [command, "--study-dir", str(self.study), "--evidence-dir", str(self.evidence)]
        for name in ("bundle", "signoff", "manifest", "report"):
            result += ["--" + name, str(self.paths[name])]
        return result + (["--output", str(self.receipt)] if command == "create" else ["--receipt", str(self.receipt)])

    def test_create_verify_no_overwrite(self):
        self.assertEqual(main(self.args("create")), 0)
        self.assertFalse(json.loads(self.receipt.read_text())["external_authenticity_verified"])
        with patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertEqual(main(self.args("verify")), 0)
            self.assertTrue(json.loads(output.getvalue())["handoff_receipt_matches_inputs"])
        with patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(main(self.args("create")), 1)

    def test_changed_receipt_rejected(self):
        self.assertEqual(main(self.args("create")), 0)
        receipt = json.loads(self.receipt.read_text())
        receipt["checked_reference_count"] = 999
        self.receipt.write_text(json.dumps(receipt))
        with patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(main(self.args("verify")), 1)

    def test_changed_evidence_rejected(self):
        self.assertEqual(main(self.args("create")), 0)
        (self.evidence / "record.txt").write_bytes(b"changed")
        with patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(main(self.args("verify")), 1)
