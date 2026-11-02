"""Cross-check self-reported study provenance against checksum-bound inputs.

This validates consistency, not the authenticity of external attestations.
"""
import json
from hashlib import sha256
from .gap_study import validate_study_submission

def check_provenance_consistency(study, protocol, manifest, label_bytes, reviewer_bytes):
    validated = validate_study_submission(study)
    if not isinstance(protocol, dict) or not isinstance(manifest, dict):
        raise ValueError("Protocol and manifest must be objects")
    digest = protocol.get("sha256")
    if validated["protocol_sha256"] != digest or manifest.get("protocol_sha256") != digest:
        raise ValueError("Study, manifest and protocol digests differ")
    if not isinstance(label_bytes, bytes) or not isinstance(reviewer_bytes, bytes):
        raise ValueError("Original label and reviewer bytes required")
    if sha256(label_bytes).hexdigest() != manifest.get("labels_sha256"):
        raise ValueError("Manifest does not match label bytes")
    try:
        labels = json.loads(label_bytes.decode("utf-8"))
        reviewer_data = json.loads(reviewer_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Inputs must be UTF-8 JSON") from exc
    if not isinstance(labels, dict) or labels.get("source_id") != validated["label_source_id"]:
        raise ValueError("Study label source differs from frozen labels")
    if not isinstance(reviewer_data, dict) or not isinstance(reviewer_data.get("submissions"), list):
        raise ValueError("Invalid reviewer submissions")
    ids = []
    for entry in reviewer_data["submissions"]:
        if not isinstance(entry, dict) or not isinstance(entry.get("reviewer_id"), str):
            raise ValueError("Invalid reviewer ID")
        ids.append(entry["reviewer_id"])
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate reviewer IDs")
    study_ids = {r["reviewer_id"] for r in study["reviewers"]}
    if set(ids) != study_ids or set(ids) != set(manifest.get("reviewer_ids_claimed", [])):
        raise ValueError("Reviewer identities differ across study, evidence and submissions")
    if manifest.get("registration_timestamp_claimed") != study["registered_at"]:
        raise ValueError("Registration timestamps differ")
    return {
        "schema_version": 1,
        "kind": "provenance_consistency_check",
        "protocol_digest_consistent": True,
        "label_checksum_consistent": True,
        "label_source_consistent": True,
        "reviewer_ids_consistent": True,
        "claimed_registration_timestamp_consistent": True,
        "external_registration_authenticity_verified": False,
        "reviewer_independence_verified": False,
    }
