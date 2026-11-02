import unittest
from quantum_omega import Action, Claim, Ledger, Stage, select_action

class GovernanceTests(unittest.TestCase):
    def setUp(self):
        self.ledger = Ledger()
        self.claim = Claim("c1", "Toy conjecture", ("local:source",))
        self.ledger.register(self.claim)

    def test_no_stage_skipping(self):
        with self.assertRaises(ValueError):
            self.ledger.advance("c1", Stage.EMPIRICALLY_SUPPORTED, "artifact", "b", "a")
        self.assertEqual(len(self.ledger.events), 1)

    def test_provenance_required(self):
        with self.assertRaises(ValueError):
            Claim("bad", "No provenance", ())

    def test_independent_reviewer(self):
        for stage in list(Stage)[1:5]:
            self.ledger.advance("c1", stage, "artifact", "a", "a")
        with self.assertRaises(ValueError):
            self.ledger.advance("c1", Stage.INDEPENDENTLY_VERIFIED, "artifact", " A ", "a")
        result = self.ledger.advance("c1", Stage.INDEPENDENTLY_VERIFIED, "artifact", "b", "a")
        self.assertEqual(result.stage, Stage.INDEPENDENTLY_VERIFIED)
        self.assertEqual(result.status, self.claim.status)

    def test_duplicate_claim(self):
        with self.assertRaises(ValueError):
            self.ledger.register(self.claim)

    def test_invalid_action_estimates(self):
        for invalid in (-1, float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                Action("bad", invalid, 0, 0, 0, 1, 0).utility()
        with self.assertRaises(ValueError):
            Action("free", 1, 1, 1, 1, 0, 0).utility()

    def test_action_ranking_and_empty_input(self):
        low = Action("low", 1, 0, 0, 0, 2, 0)
        high = Action("high", 4, 0, 0, 0, 2, 0)
        self.assertEqual(select_action([low, high]), high)
        with self.assertRaises(ValueError):
            select_action([])

if __name__ == '__main__':
    unittest.main()
