import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from quantum_omega.gap_provenance_cli import main

class ProvenanceCLITests(unittest.TestCase):
    def test_cli_outputs_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            argv = []
            for name in ("protocol", "report", "evidence", "labels", "reviewers", "study"):
                path = root / (name + ".json")
                path.write_text("{}", encoding="utf-8")
                argv.extend(["--" + name, str(path)])
            with patch("quantum_omega.gap_provenance_cli.replay_with_provenance", return_value={"kind": "ok"}):
                with patch("sys.stdout", new_callable=io.StringIO) as stdout:
                    self.assertEqual(main(argv), 0)
                    self.assertEqual(json.loads(stdout.getvalue()), {"kind": "ok"})

    def test_cli_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            argv = []
            for name in ("protocol", "report", "evidence", "labels", "reviewers", "study"):
                path = root / (name + ".json")
                path.write_text("{}", encoding="utf-8")
                argv.extend(["--" + name, str(path)])
            with patch("quantum_omega.gap_provenance_cli.replay_with_provenance", side_effect=ValueError("bad provenance")):
                with patch("sys.stderr", new_callable=io.StringIO):
                    self.assertEqual(main(argv), 1)
