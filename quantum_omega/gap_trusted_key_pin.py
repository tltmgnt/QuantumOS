"""Pin an independently authenticated Ed25519 public key by expected SHA-256."""
import hashlib
import json
import os
import stat
from pathlib import Path

def _check_parent(path):
    if path.parent.is_symlink() or not path.parent.is_dir():
        raise ValueError("Pinned-key parent must be a real directory, not a symlink")


def pin_trusted_public_key(public_key_hex, expected_sha256, destination):
    if not isinstance(public_key_hex, str) or len(public_key_hex) != 64:
        raise ValueError("Ed25519 public key must be 64 hex characters")
    try:
        key = bytes.fromhex(public_key_hex)
    except ValueError as exc:
        raise ValueError("Invalid public key hex") from exc
    if (not isinstance(expected_sha256, str) or len(expected_sha256) != 64
            or any(c not in "0123456789abcdef" for c in expected_sha256)):
        raise ValueError("Expected fingerprint must be a lowercase SHA-256 hex digest")
    actual = hashlib.sha256(key).hexdigest()
    if actual != expected_sha256:
        raise ValueError("Public key differs from independently supplied fingerprint")
    record = {
        "schema_version": 1,
        "kind": "tga_pinned_ed25519_public_key",
        "public_key_hex": key.hex(),
        "public_key_sha256": actual,
        "identity_authenticated_by_software": False,
    }
    destination = Path(destination)
    _check_parent(destination)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(destination, flags, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True, indent=2) + "\n")
    return record

def read_pinned_public_key(path):
    path = Path(path)
    _check_parent(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("Pinned key must be a regular non-symlink file")
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags)
    with os.fdopen(fd, "r", encoding="utf-8") as stream:
        metadata = os.fstat(stream.fileno())
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise ValueError("Pinned key must be an unlinked regular file (no hardlinks)")
        record = json.load(stream)
    if not isinstance(record, dict) or set(record) != {
        "schema_version", "kind", "public_key_hex", "public_key_sha256",
        "identity_authenticated_by_software"
    } or record["schema_version"] != 1 or record["kind"] != "tga_pinned_ed25519_public_key" or record["identity_authenticated_by_software"] is not False:
        raise ValueError("Invalid pinned-key record")
    key = record["public_key_hex"]
    if not isinstance(key, str) or len(key) != 64:
        raise ValueError("Invalid pinned public key")
    try:
        raw = bytes.fromhex(key)
    except ValueError as exc:
        raise ValueError("Invalid pinned public key hex") from exc
    if key != raw.hex() or hashlib.sha256(raw).hexdigest() != record["public_key_sha256"]:
        raise ValueError("Pinned-key fingerprint mismatch")
    return key
