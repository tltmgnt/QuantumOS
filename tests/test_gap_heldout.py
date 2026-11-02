import unittest
from quantum_omega.gap_heldout import evaluate_heldout

class HeldoutTests(unittest.TestCase):
    def test_declared_structural_ranking_and_baselines(self):
        result = evaluate_heldout()
        self.assertTrue(result["passes_structural_fixture"], result)
        self.assertEqual(result, evaluate_heldout())
        self.assertFalse(result["independent_expert_labels"])
        self.assertFalse(result["scientific_calibration"])
        self.assertGreaterEqual(result["scores"]["tga_heuristic"], result["scores"]["alphabetical_baseline"])
