"""Filesystem attack controls for trusted Ed25519 key pin records."""
import hashlib
import os
import tempfile
import unittest
from pathlib import Path

from quantum_omega.gap_trusted_key_pin import pin_trusted_public_key, read_pinned_public_key

class TrustedKeyFilesystemSafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.key = bytes(range(32))
        self.digest = hashlib.sha256(self.key).hexdigest()

    def tearDown(self):
        self.tmp.cleanup()

    def test_create_only_and_private_permissions(self):
        target = self.root / "trusted.json"
        pin_trusted_public_key(self.key.hex(), self.digest, target)
        self.assertEqual(read_pinned_public_key(target), self.key.hex())
        self.assertEqual(target.stat().st_mode & 0o777, 0o600)
        with self.assertRaises(FileExistsError):
            pin_trusted_public_key(self.key.hex(), self.digest, target)

    def test_existing_symlink_target_never_overwritten(self):
        original = self.root / "original.txt"
        original.write_text("untouched")
        link = self.root / "trusted.json"
        link.symlink_to(original)
        with self.assertRaises(FileExistsError):
            pin_trusted_public_key(self.key.hex(), self.digest, link)
        with self.assertRaises(ValueError):
            read_pinned_public_key(link)
        self.assertEqual(original.read_text(), "untouched")

    def test_symlink_parent_rejected(self):
        real = self.root / "real"
        real.mkdir()
        alias = self.root / "alias"
        alias.symlink_to(real, target_is_directory=True)
        with self.assertRaises(ValueError):
            pin_trusted_public_key(self.key.hex(), self.digest, alias / "key.json")
        self.assertFalse((real / "key.json").exists())
        pin_trusted_public_key(self.key.hex(), self.digest, real / "key.json")
        with self.assertRaises(ValueError):
            read_pinned_public_key(alias / "key.json")

    def test_hardlinked_record_rejected(self):
        original = self.root / "key.json"
        pin_trusted_public_key(self.key.hex(), self.digest, original)
        alias = self.root / "alias.json"
        os.link(original, alias)
        with self.assertRaises(ValueError):
            read_pinned_public_key(original)
        with self.assertRaises(ValueError):
            read_pinned_public_key(alias)

    def test_directory_not_accepted_as_pin(self):
        with self.assertRaises(ValueError):
            read_pinned_public_key(self.root)
