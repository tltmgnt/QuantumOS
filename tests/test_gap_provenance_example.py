import json
import tempfile
import unittest
from pathlib import Path
from quantum_omega.gap_provenance_example import create_provenance_example
from quantum_omega.gap_provenance_cli import main

class ProvenanceExampleTests(unittest.TestCase):
    def test_example_replays_via_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "example"
            result = create_provenance_example(root)
            output = root / "cli-evaluation.json"
            args = []
            for key, name in (("protocol", "protocol.json"), ("report", "priority.json"),
                              ("evidence", "evidence.json"), ("labels", "labels.json"),
                              ("reviewers", "reviewers.json"), ("study", "study.json")):
                args.extend(["--" + key, str(root / name)])
            self.assertEqual(main(args + ["--output", str(output)]), 0)
            self.assertEqual(json.loads(output.read_text()), result)
            self.assertTrue(result["replay"]["reviewer_label_alignment_verified"])
            self.assertFalse(result["reviewer_independence_verified"])
            self.assertEqual(main(args + ["--output", str(output)]), 1)
