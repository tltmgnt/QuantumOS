import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from quantum_omega.gap_provenance_example import create_provenance_example
from quantum_omega.gap_study_inventory_cli import main

class InventoryCLITests(unittest.TestCase):
    def test_create_verify_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "study"
            create_provenance_example(root)
            (root / "evaluation.json").unlink()
            inventory = Path(tmp) / "inventory.json"
            self.assertEqual(main(["create", str(root), "--output", str(inventory)]), 0)
            self.assertEqual(len(json.loads(inventory.read_text())["files"]), 6)
            with patch("sys.stdout", new_callable=io.StringIO) as stdout:
                self.assertEqual(main(["verify", str(root), "--inventory", str(inventory)]), 0)
                self.assertTrue(json.loads(stdout.getvalue())["inventory_verified"])
            with patch("sys.stderr", new_callable=io.StringIO):
                self.assertEqual(main(["create", str(root), "--output", str(inventory)]), 1)

    def test_verify_detects_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "study"
            create_provenance_example(root)
            (root / "evaluation.json").unlink()
            inventory = Path(tmp) / "inventory.json"
            self.assertEqual(main(["create", str(root), "--output", str(inventory)]), 0)
            with (root / "labels.json").open("ab") as stream:
                stream.write(b" ")
            with patch("sys.stderr", new_callable=io.StringIO):
                self.assertEqual(main(["verify", str(root), "--inventory", str(inventory)]), 1)
