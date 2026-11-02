"""Inventory a portable, fixed-layout audit handoff using exact file bytes."""
import hashlib
import json
from pathlib import Path

_STUDY = ("protocol.json", "priority.json", "evidence.json", "labels.json", "reviewers.json", "study.json")
_AUDIT = ("bundle.json", "signoff.json", "manifest.json", "report.json", "receipt.json")

def _files(directory):
    root = Path(directory)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Handoff root must be a real directory")
    expected = {"study", "evidence", *_AUDIT}
    if {entry.name for entry in root.iterdir()} != expected:
        raise ValueError("Handoff root has missing or unexpected entries")
    study = root / "study"
    evidence = root / "evidence"
    if any(p.is_symlink() or not p.is_dir() for p in (study, evidence)):
        raise ValueError("Study and evidence must be real directories")
    if {entry.name for entry in study.iterdir()} != set(_STUDY):
        raise ValueError("Study must contain exactly six files")
    paths = [root / name for name in _AUDIT]
    paths += [study / name for name in _STUDY]
    for item in evidence.rglob("*"):
        if item.is_symlink() or not item.is_file():
            raise ValueError("Evidence must contain only regular files")
        paths.append(item)
    for item in paths:
        if item.is_symlink() or not item.is_file():
            raise ValueError("Handoff entries must be regular files")
    return root, sorted(paths, key=lambda p: p.relative_to(root).as_posix())

def build_portable_handoff_manifest(directory):
    root, paths = _files(directory)
    files = []
    for path in paths:
        data = path.read_bytes()
        files.append({
            "path": path.relative_to(root).as_posix(),
            "byte_count": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        })
    result = {
        "schema_version": 1,
        "kind": "tga_portable_audit_handoff_manifest",
        "files": files,
        "file_count": len(files),
        "external_authenticity_verified": False,
        "scientific_validity_independently_verified": False,
    }
    result["sha256"] = hashlib.sha256(
        json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()
    return result

def verify_portable_handoff_manifest(directory, manifest):
    if not isinstance(manifest, dict) or manifest != build_portable_handoff_manifest(directory):
        raise ValueError("Portable handoff manifest differs from actual file bytes")
    return {
        "portable_handoff_bytes_match": True,
        "file_count": manifest["file_count"],
        "audit_chain_replayed": False,
        "external_authenticity_verified": False,
        "scientific_validity_independently_verified": False,
    }
