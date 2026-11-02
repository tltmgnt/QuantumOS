"""Checksum-bound inventory of exact external-study input files.

Inventories detect byte changes but do not establish external authenticity.
"""
import json
from hashlib import sha256
from pathlib import Path

from .gap_study_package import _REQUIRED, validate_study_package

def inventory_study_package(directory):
    root = Path(directory)
    result = validate_study_package(root)
    files = []
    for name in sorted(_REQUIRED):
        path = root / name
        data = path.read_bytes()
        files.append({"name": name, "size_bytes": len(data), "sha256": sha256(data).hexdigest()})
    inventory = {
        "schema_version": 1,
        "kind": "tga_study_file_inventory",
        "evaluation_sha256": result["sha256"],
        "files": files,
        "external_authenticity_verified": False,
    }
    inventory["sha256"] = sha256(json.dumps(inventory, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    return inventory

def verify_study_inventory(directory, inventory):
    if not isinstance(inventory, dict) or inventory.get("kind") != "tga_study_file_inventory":
        raise ValueError("Invalid study inventory")
    expected = inventory_study_package(directory)
    if inventory != expected:
        raise ValueError("Study file inventory mismatch")
    return {"inventory_verified": True, "external_authenticity_verified": False}
