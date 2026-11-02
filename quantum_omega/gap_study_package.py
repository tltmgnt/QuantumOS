"""Validate a submitted external-study directory without trusting its claims.

This does not authenticate reviewers, registrations or label provenance.
"""
import json
from pathlib import Path
from .gap_provenance_replay import replay_with_provenance

_REQUIRED = {
    "protocol.json", "priority.json", "evidence.json",
    "labels.json", "reviewers.json", "study.json",
}

def validate_study_package(directory):
    root = Path(directory)
    if not root.is_dir() or root.is_symlink():
        raise ValueError("Expected a real study-package directory")
    actual = {item.name for item in root.iterdir()}
    if actual != _REQUIRED:
        raise ValueError("Study package must contain exactly the six required input files")
    for name in _REQUIRED:
        path = root / name
        if not path.is_file() or path.is_symlink():
            raise ValueError("Study package files must be regular files, not symlinks")
    def load(name):
        try:
            return json.loads((root / name).read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("Invalid UTF-8 JSON in " + name) from exc
    return replay_with_provenance(
        load("protocol.json"),
        load("priority.json"),
        load("evidence.json"),
        (root / "labels.json").read_bytes(),
        (root / "reviewers.json").read_bytes(),
        load("study.json"),
    )
