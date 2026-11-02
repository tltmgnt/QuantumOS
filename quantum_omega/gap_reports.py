"""Persist and verify immutable TGA review reports without promoting claims."""
from hashlib import sha256
import json
from pathlib import Path
from .gap_priority import rank_gaps

def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")

def verify_gap_report(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("Report must be a regular file, not a symlink")
    report = json.loads(path.read_bytes())
    if not isinstance(report, dict) or report.get("kind") != "review_priority_heuristic":
        raise ValueError("Invalid gap report")
    digest = report.get("sha256")
    if not isinstance(digest, str) or len(digest) != 64:
        raise ValueError("Missing report digest")
    unsigned = {k: v for k, v in report.items() if k != "sha256"}
    if sha256(_canonical(unsigned)).hexdigest() != digest:
        raise ValueError("Gap report integrity failure")
    return report

def save_gap_report(memory, destination):
    """Create once; never overwrite or follow a destination symlink."""
    destination = Path(destination)
    report = rank_gaps(memory)
    if destination.is_symlink():
        raise ValueError("Refusing symlink report destination")
    payload = _canonical(report) + b"\n"
    with destination.open("xb") as stream:
        stream.write(payload)
    verify_gap_report(destination)
    return report
