"""Check local evidence bytes against declared manifest digests.

This does not authenticate the origin or truth of any evidence.
"""
import hashlib
import os
import stat
from pathlib import Path

from .gap_audit_evidence_refs import verify_evidence_references

def verify_local_evidence_files(bundle, signoff, manifest, evidence_directory):
    verify_evidence_references(bundle, signoff, manifest)
    root = Path(evidence_directory)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Evidence root must be a real directory")
    root = root.resolve(strict=True)
    checks = []
    for category, entries in manifest["references"].items():
        for entry in entries:
            locator = entry["locator"]
            rel = Path(locator)
            if rel.is_absolute() or not rel.parts or any(part in ("..", ".") for part in rel.parts) or "\\" in locator:
                raise ValueError("Evidence locator must be a safe relative path")
            target = root
            for part in rel.parts:
                target = target / part
                if target.is_symlink():
                    raise ValueError("Evidence path must not contain symlinks")
            try:
                if not target.resolve(strict=True).is_relative_to(root):
                    raise ValueError("Evidence path escapes root")
                metadata = target.stat()
            except (OSError, RuntimeError) as exc:
                raise ValueError("Evidence file unavailable") from exc
            if not stat.S_ISREG(metadata.st_mode):
                raise ValueError("Evidence locator must reference a regular file")
            digest = hashlib.sha256()
            flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
            try:
                descriptor = os.open(target, flags)
                with os.fdopen(descriptor, "rb") as stream:
                    if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                        raise ValueError("Evidence file changed type")
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        digest.update(chunk)
            except OSError as exc:
                raise ValueError("Evidence file unreadable") from exc
            if digest.hexdigest() != entry["sha256"]:
                raise ValueError("Evidence checksum mismatch")
            checks.append({"category": category, "locator": locator, "sha256": entry["sha256"], "bytes_match": True})
    return {
        "local_evidence_bytes_match": True,
        "checked_reference_count": len(checks),
        "checks": checks,
        "external_authenticity_verified": False,
    }
