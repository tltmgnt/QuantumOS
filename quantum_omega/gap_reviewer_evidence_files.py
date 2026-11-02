"""Verify local reviewer evidence bytes against a self-declared evidence index.

This verifies local file integrity, not the authenticity of referenced records.
"""
import hashlib
import os
import stat
from pathlib import Path

from .gap_reviewer_evidence_index import verify_reviewer_evidence_index

def verify_reviewer_evidence_files(acknowledgment, index, evidence_directory):
    verify_reviewer_evidence_index(acknowledgment, index)
    root = Path(evidence_directory)
    root_info = root.lstat()
    if not stat.S_ISDIR(root_info.st_mode) or stat.S_ISLNK(root_info.st_mode):
        raise ValueError("Evidence root must be a real directory")
    checks = []
    for category, entry in sorted(index["evidence"].items()):
        for reference in entry["references"]:
            locator = reference["locator"]
            if (not isinstance(locator, str) or not locator
                    or "\\" in locator or "\x00" in locator
                    or locator.startswith("/") or ":" in locator):
                raise ValueError("Invalid evidence file locator")
            parts = locator.split("/")
            if any(part in ("", ".", "..") for part in parts):
                raise ValueError("Evidence locator cannot traverse directories")
            candidate = root
            for part in parts:
                candidate = candidate / part
                info = candidate.lstat()
                if stat.S_ISLNK(info.st_mode):
                    raise ValueError("Evidence path contains a symlink")
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise ValueError("Evidence must be a regular, single-link file")
            # O_NOFOLLOW protects the final component from a simple symlink swap.
            flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
            fd = os.open(candidate, flags)
            try:
                opened = os.fstat(fd)
                if (not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1
                        or opened.st_dev != info.st_dev or opened.st_ino != info.st_ino):
                    raise ValueError("Evidence file changed while opening")
                digest = hashlib.sha256()
                with os.fdopen(fd, "rb", closefd=False) as stream:
                    while True:
                        chunk = stream.read(1024 * 1024)
                        if not chunk:
                            break
                        digest.update(chunk)
                if digest.hexdigest() != reference["sha256"]:
                    raise ValueError(f"Evidence SHA-256 mismatch: {locator}")
            finally:
                os.close(fd)
            checks.append({"category": category, "locator": locator, "sha256": digest.hexdigest()})
    return {
        "reviewer_evidence_bytes_match": True,
        "checked_reference_count": len(checks),
        "checks": checks,
        "evidence_authenticity_verified": False,
        "reviewer_identity_authenticated": False,
        "reviewer_independence_verified": False,
    }
