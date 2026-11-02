"""Create a deterministic cross-linked audit bundle for validated study inputs."""
import json
from hashlib import sha256
from pathlib import Path

from .gap_study_inventory import inventory_study_package
from .gap_study_review import summarize_study_package

def _digest(data):
    return sha256(json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()

def build_audit_bundle(directory):
    root = Path(directory)
    inventory = inventory_study_package(root)
    summary = summarize_study_package(root)
    if inventory["evaluation_sha256"] != summary["evaluation_sha256"]:
        raise ValueError("Inventory and review summary reference different evaluations")
    result = {
        "schema_version": 1,
        "kind": "tga_study_audit_bundle",
        "study_input_inventory": inventory,
        "review_summary": summary,
        "evaluation_sha256": inventory["evaluation_sha256"],
        "external_authenticity_verified": False,
    }
    result["sha256"] = _digest(result)
    return result

def verify_audit_bundle(directory, bundle):
    if not isinstance(bundle, dict) or bundle.get("kind") != "tga_study_audit_bundle":
        raise ValueError("Invalid audit bundle")
    if bundle != build_audit_bundle(directory):
        raise ValueError("Audit bundle mismatch")
    return {"audit_bundle_verified": True, "external_authenticity_verified": False}
