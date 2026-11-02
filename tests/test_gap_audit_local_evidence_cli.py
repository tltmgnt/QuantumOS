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
from quantum_omega.gap_audit_local_evidence_cli import main

CATEGORIES = ("registration_authenticity", "reviewer_independence", "label_provenance", "scientific_validity")

class LocalEvidenceCLITests(unittest.TestCase):
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
            notes="No independent verification."
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
        self.paths = {}
        for name, value in (("bundle", bundle), ("signoff", signoff), ("manifest", manifest)):
            path = Path(self.tmp.name) / (name + ".json")
            path.write_text(json.dumps(value))
            self.paths[name] = path

    def tearDown(self):
        self.tmp.cleanup()

    def args(self):
        return ["--bundle", str(self.paths["bundle"]), "--signoff", str(self.paths["signoff"]),
                "--manifest", str(self.paths["manifest"]), "--evidence-dir", str(self.evidence)]

    def test_matching_bytes(self):
        with patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertEqual(main(self.args()), 0)
            result = json.loads(output.getvalue())
            self.assertEqual(result["checked_reference_count"], 1)
            self.assertFalse(result["external_authenticity_verified"])

    def test_changed_bytes_fail(self):
        (self.evidence / "record.txt").write_bytes(b"changed")
        with patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(main(self.args()), 1)
