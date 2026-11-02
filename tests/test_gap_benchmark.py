import unittest
from quantum_omega.gap_benchmark import evaluate_fixture

class GapBenchmarkTests(unittest.TestCase):
    def test_synthetic_baseline(self):
        report = evaluate_fixture()
        self.assertTrue(report["passed"], report)
        self.assertFalse(report["scientific_calibration"])
        self.assertEqual(report, evaluate_fixture())
        self.assertEqual(len(report["report_sha256"]), 64)
