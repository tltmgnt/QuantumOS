import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from quantum_omega.gap_provenance_example import create_provenance_example
from quantum_omega.gap_audit_bundle_cli import main

class OfflineAuditCLITests(unittest.TestCase):
    def test_offline_after_study_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "study"
            create_provenance_example(root)
            (root / "evaluation.json").unlink()
            bundle = Path(tmp) / "bundle.json"
            self.assertEqual(main(["export", str(root), "--output", str(bundle)]), 0)
            for path in root.iterdir():
                path.unlink()
            root.rmdir()
            with patch("sys.stdout", new_callable=io.StringIO) as output:
                self.assertEqual(main(["verify-offline", "--bundle", str(bundle)]), 0)
            result = json.loads(output.getvalue())
            self.assertTrue(result["offline_checksums_consistent"])
            self.assertFalse(result["study_inputs_replayed"])

    def test_offline_rejects_modified_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "study"
            create_provenance_example(root)
            (root / "evaluation.json").unlink()
            bundle = Path(tmp) / "bundle.json"
            self.assertEqual(main(["export", str(root), "--output", str(bundle)]), 0)
            record = json.loads(bundle.read_text())
            record["study_input_inventory"]["files"][0]["size_bytes"] += 1
            bundle.write_text(json.dumps(record))
            with patch("sys.stderr", new_callable=io.StringIO):
                self.assertEqual(main(["verify-offline", "--bundle", str(bundle)]), 1)
