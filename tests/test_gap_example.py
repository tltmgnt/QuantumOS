import json
from pathlib import Path
import tempfile
import unittest
from quantum_omega.gap_example import create_example
from quantum_omega.gap_cli import main

class EvaluationExampleTests(unittest.TestCase):
    def test_full_example_and_cli_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "example"
            result = create_example(folder)
            self.assertFalse(result["external_independence_verified"])
            args = [x for name in ("protocol", "report", "evidence", "labels")
                    for x in ("--" + name, str(folder / (("priority" if name == "report" else name) + ".json")))]
            output = folder / "cli-result.json"
            self.assertEqual(main(args + ["--output", str(output)]), 0)
            self.assertEqual(json.loads(output.read_text()), result)
            with self.assertRaises(FileExistsError):
                create_example(folder)
