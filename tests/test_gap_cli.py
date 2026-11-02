import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from quantum_omega.gap_cli import main
from quantum_omega.gap_evidence import build_evidence_manifest
from quantum_omega.gap_protocol import freeze_protocol

class EvaluationCliTests(unittest.TestCase):
    def test_cli_replay_and_no_overwrite(self):
        report = {"kind": "review_priority_heuristic", "sha256": "a" * 64,
                  "ranked_claims": [{"claim_id": "b"}, {"claim_id": "a"}]}
        protocol = freeze_protocol(report, study_id="study-1", evaluation_set_id="set-1")
        labels = json.dumps({"schema_version": 1, "source_id": "set-1",
            "pairs": [{"higher_priority": "b", "lower_priority": "a"}]}).encode()
        evidence = build_evidence_manifest(protocol,
            registration_url="https://example.org/study-1",
            registration_timestamp="2026-01-01T00:00:00Z",
            labels_sha256=hashlib.sha256(labels).hexdigest(), reviewer_ids=["reviewer-1"])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, data in (("protocol", protocol), ("report", report), ("evidence", evidence)):
                (root / (name + ".json")).write_text(json.dumps(data))
            (root / "labels.json").write_bytes(labels)
            args = [flag for name in ("protocol", "report", "evidence", "labels")
                    for flag in ("--" + name, str(root / (name + ".json")))]
            output = root / "result.json"
            self.assertEqual(main(args + ["--output", str(output)]), 0)
            self.assertEqual(json.loads(output.read_text())["evaluation"]["scores"]["tga_heuristic"], 1.0)
            self.assertEqual(main(args + ["--output", str(output)]), 1)
            self.assertEqual(main(args + ["--labels", str(root / "missing.json")]), 1)
