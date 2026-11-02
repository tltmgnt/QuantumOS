import tempfile
import unittest
from pathlib import Path
from quantum_omega.gap_provenance_example import create_provenance_example
from quantum_omega.gap_study_inventory import inventory_study_package, verify_study_inventory

class StudyInventoryTests(unittest.TestCase):
    def test_deterministic_inventory_and_verification(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "study"
            create_provenance_example(root)
            (root / "evaluation.json").unlink()
            first = inventory_study_package(root)
            self.assertEqual(first, inventory_study_package(root))
            self.assertEqual(len(first["files"]), 6)
            self.assertTrue(verify_study_inventory(root, first)["inventory_verified"])
            self.assertFalse(first["external_authenticity_verified"])

    def test_detects_changed_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "study"
            create_provenance_example(root)
            (root / "evaluation.json").unlink()
            inventory = inventory_study_package(root)
            with (root / "labels.json").open("ab") as stream:
                stream.write(b" ")
            with self.assertRaises(ValueError):
                verify_study_inventory(root, inventory)

    def test_detects_modified_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "study"
            create_provenance_example(root)
            (root / "evaluation.json").unlink()
            inventory = inventory_study_package(root)
            inventory["files"][0]["size_bytes"] += 1
            with self.assertRaises(ValueError):
                verify_study_inventory(root, inventory)
