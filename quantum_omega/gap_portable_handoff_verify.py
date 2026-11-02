"""Verify both portable file bytes and the full input-backed audit receipt."""
import hashlib
import json
from pathlib import Path

from .gap_portable_handoff_manifest import verify_portable_handoff_manifest
from .gap_audit_handoff_receipt import verify_audit_handoff_receipt

def verify_portable_handoff(directory, inventory):
    root = Path(directory)
    byte_check = verify_portable_handoff_manifest(root, inventory)
    def load(name):
        path = root / name
        if path.is_symlink() or not path.is_file():
            raise ValueError("Expected a regular audit artifact: " + name)
        return json.loads(path.read_text(encoding="utf-8"))
    bundle, signoff, manifest, report, receipt = (
        load(name) for name in ("bundle.json", "signoff.json", "manifest.json", "report.json", "receipt.json")
    )
    receipt_check = verify_audit_handoff_receipt(
        root / "study", bundle, signoff, manifest, root / "evidence", report, receipt
    )
    result = {
        "schema_version": 1,
        "kind": "tga_portable_handoff_full_verification",
        "portable_manifest_sha256": inventory["sha256"],
        "audit_handoff_receipt_sha256": receipt["sha256"],
        "portable_handoff_bytes_match": byte_check["portable_handoff_bytes_match"],
        "handoff_receipt_matches_inputs": receipt_check["handoff_receipt_matches_inputs"],
        "study_inputs_replayed": True,
        "file_count": byte_check["file_count"],
        "checked_reference_count": receipt_check["checked_reference_count"],
        "external_authenticity_verified": False,
        "scientific_validity_independently_verified": False,
    }
    result["sha256"] = hashlib.sha256(
        json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()
    return result
