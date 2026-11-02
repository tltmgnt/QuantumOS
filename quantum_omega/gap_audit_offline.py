"""Offline structural and checksum verification of a saved TGA audit bundle.

This does not re-evaluate study files or establish external provenance.
"""
import json
from hashlib import sha256

_REQUIRED_FILES = {
    "protocol.json", "priority.json", "evidence.json",
    "labels.json", "reviewers.json", "study.json",
}

def _digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()

def _verify_digest(record):
    if not isinstance(record, dict) or not isinstance(record.get("sha256"), str):
        raise ValueError("Missing record checksum")
    content = {key: value for key, value in record.items() if key != "sha256"}
    if _digest(content) != record["sha256"]:
        raise ValueError("Record checksum mismatch")

def verify_bundle_offline(bundle):
    if not isinstance(bundle, dict) or bundle.get("schema_version") != 1 or bundle.get("kind") != "tga_study_audit_bundle":
        raise ValueError("Invalid audit bundle schema")
    if set(bundle) != {"schema_version", "kind", "study_input_inventory", "review_summary", "evaluation_sha256", "external_authenticity_verified", "sha256"}:
        raise ValueError("Unexpected audit bundle fields")
    inventory = bundle["study_input_inventory"]
    summary = bundle["review_summary"]
    if not isinstance(inventory, dict) or inventory.get("kind") != "tga_study_file_inventory":
        raise ValueError("Invalid inventory")
    if not isinstance(summary, dict) or summary.get("kind") != "tga_study_review_summary":
        raise ValueError("Invalid review summary")
    for record in (inventory, summary, bundle):
        _verify_digest(record)
    if bundle["external_authenticity_verified"] is not False or inventory.get("external_authenticity_verified") is not False:
        raise ValueError("Unsupported authenticity claim")
    if not isinstance(summary.get("external_verification"), dict) or set(summary["external_verification"]) != {"registration_authenticity", "reviewer_independence", "scientific_validity"} or any(value is not False for value in summary["external_verification"].values()):
        raise ValueError("Unsupported external verification claim")
    if set(summary.get("checks", {})) != {"protocol_digest_consistent", "label_checksum_consistent", "label_source_consistent", "reviewer_ids_consistent", "claimed_registration_timestamp_consistent", "reviewer_label_alignment_verified"} or any(value is not True for value in summary["checks"].values()):
        raise ValueError("Invalid consistency claims")
    if bundle["evaluation_sha256"] != inventory.get("evaluation_sha256") or bundle["evaluation_sha256"] != summary.get("evaluation_sha256"):
        raise ValueError("Evaluation digests differ")
    files = inventory.get("files")
    if not isinstance(files, list) or len(files) != 6:
        raise ValueError("Invalid inventory file count")
    if {entry.get("name") for entry in files if isinstance(entry, dict)} != _REQUIRED_FILES:
        raise ValueError("Invalid inventory filenames")
    for entry in files:
        if set(entry) != {"name", "size_bytes", "sha256"} or type(entry["size_bytes"]) is not int or entry["size_bytes"] < 0 or not isinstance(entry["sha256"], str) or len(entry["sha256"]) != 64 or any(c not in "0123456789abcdef" for c in entry["sha256"]):
            raise ValueError("Invalid file inventory entry")
    return {"offline_checksums_consistent": True, "study_inputs_replayed": False, "external_authenticity_verified": False}
