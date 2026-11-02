import json
from pathlib import Path
import tempfile
import unittest
from quantum_omega.workflow import run_research

class GapWorkflowTests(unittest.TestCase):
    def test_workflow_writes_verifiable_gap_artifacts(self):
        root = Path(__file__).resolve().parents[1]
        task = json.loads((root / "examples/polynomial_research.json").read_text())
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "run"
            report = run_research(task, output)
            self.assertTrue(report["tga_review_priority"]["synthetic_benchmark_passed"])
            gap = json.loads((output / "gap-priority.json").read_text())
            self.assertEqual(report["tga_review_priority"]["report_sha256"], gap["sha256"])
            self.assertTrue(json.loads((output / "gap-benchmark.json").read_text())["passed"])
            self.assertIn("selected_action", json.loads((output / "gap-review-plan.json").read_text()))
            self.assertFalse(report["scientific_discovery"])
