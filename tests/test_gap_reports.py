import json
from pathlib import Path
import tempfile
import unittest
from quantum_omega import Claim, Ledger
from quantum_omega.gap_reports import save_gap_report, verify_gap_report

class GapReportTests(unittest.TestCase):
    def test_persistence_and_tamper_detection(self):
        ledger = Ledger()
        ledger.register(Claim("x", "example", ("local:fixture",)))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "gap.json"
            report = save_gap_report(ledger, path)
            self.assertEqual(report, verify_gap_report(path))
            with self.assertRaises(FileExistsError):
                save_gap_report(ledger, path)
            edited = json.loads(path.read_text())
            edited["ranked_claims"][0]["priority_score"] = 999
            path.write_text(json.dumps(edited))
            with self.assertRaisesRegex(ValueError, "integrity"):
                verify_gap_report(path)

    def test_reject_symlink(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "gap.json"
            target = Path(folder) / "target.json"
            target.write_text("{}")
            path.symlink_to(target)
            with self.assertRaisesRegex(ValueError, "symlink"):
                save_gap_report(Ledger(), path)
            with self.assertRaises(ValueError):
                verify_gap_report(path)
