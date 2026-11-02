"""Auditable external evidence metadata, without claiming third-party verification."""
import json
from hashlib import sha256

def _digest(data):
    return sha256(json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()

def build_evidence_manifest(protocol, *, registration_url, registration_timestamp, labels_sha256, reviewer_ids):
    if not isinstance(protocol, dict) or protocol.get("kind") != "preregistered_evaluation_protocol":
        raise ValueError("Expected evaluation protocol")
    if not isinstance(protocol.get("sha256"), str) or len(protocol["sha256"]) != 64:
        raise ValueError("Protocol digest required")
    if not isinstance(registration_url, str) or not registration_url.startswith("https://"):
        raise ValueError("HTTPS registration URL required")
    if not isinstance(registration_timestamp, str) or not registration_timestamp.strip():
        raise ValueError("Registration timestamp required")
    if not isinstance(labels_sha256, str) or len(labels_sha256) != 64 or any(c not in "0123456789abcdef" for c in labels_sha256):
        raise ValueError("Lowercase SHA-256 label digest required")
    if not isinstance(reviewer_ids, list) or not reviewer_ids or any(not isinstance(x, str) or not x.strip() for x in reviewer_ids) or len(set(reviewer_ids)) != len(reviewer_ids):
        raise ValueError("Unique nonempty reviewer identifiers required")
    payload = {
        "schema_version": 1,
        "kind": "external_evaluation_evidence_manifest",
        "protocol_sha256": protocol["sha256"],
        "registration_url": registration_url,
        "registration_timestamp_claimed": registration_timestamp,
        "labels_sha256": labels_sha256,
        "reviewer_ids_claimed": reviewer_ids,
        "registration_independently_verified": False,
        "reviewer_independence_verified": False,
        "labels_independently_verified": False,
        "note": "Metadata is self-reported. Fetching the registration, verifying chronology and reviewing signed attestations remain external obligations.",
    }
    payload["sha256"] = _digest(payload)
    return payload

def verify_evidence_manifest(manifest, protocol, label_bytes):
    if not isinstance(manifest, dict) or manifest.get("kind") != "external_evaluation_evidence_manifest":
        raise ValueError("Expected evidence manifest")
    digest = manifest.get("sha256")
    if not isinstance(digest, str) or digest != _digest({k: v for k, v in manifest.items() if k != "sha256"}):
        raise ValueError("Evidence manifest tampered")
    if manifest["protocol_sha256"] != protocol.get("sha256"):
        raise ValueError("Protocol mismatch")
    if not isinstance(label_bytes, bytes) or sha256(label_bytes).hexdigest() != manifest["labels_sha256"]:
        raise ValueError("Label file checksum mismatch")
    return {"integrity_verified": True, "external_independence_verified": False,
            "chronological_preregistration_verified": False}
