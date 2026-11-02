"""Checksum-bound index of external reviewer custody evidence (not authentication)."""
import hashlib
import json

_CATEGORIES = (
    "reviewer_identity", "reviewer_authorization", "reviewer_independence",
    "handoff_key_authentication", "reviewer_key_authentication",
    "conflict_review", "key_custody",
)
_STATUSES = frozenset(("unverified", "claimed_verified", "rejected"))

def _digest(value):
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")).hexdigest()

def build_reviewer_evidence_index(acknowledgment, evidence):
    if not isinstance(acknowledgment, dict) or acknowledgment.get("kind") != "tga_reviewer_handoff_acknowledgment":
        raise ValueError("Expected a reviewer handoff acknowledgment")
    if not isinstance(evidence, dict) or set(evidence) != set(_CATEGORIES):
        raise ValueError("Evidence must include exactly the required categories")
    normalized = {}
    for category in _CATEGORIES:
        entry = evidence[category]
        if not isinstance(entry, dict) or set(entry) != {"status", "references"}:
            raise ValueError(f"Invalid evidence category: {category}")
        refs = entry["references"]
        if (entry["status"] not in _STATUSES
                or not isinstance(refs, list)
                or any(not isinstance(ref, dict)
                       or set(ref) != {"locator", "sha256"}
                       or not isinstance(ref["locator"], str)
                       or not ref["locator"].strip()
                       or not isinstance(ref["sha256"], str)
                       or len(ref["sha256"]) != 64
                       or any(c not in "0123456789abcdef" for c in ref["sha256"])
                       for ref in refs)):
            raise ValueError(f"Invalid evidence reference or status: {category}")
        if entry["status"] == "claimed_verified" and not refs:
            raise ValueError(f"Claimed verification needs a reference: {category}")
        normalized[category] = {"status": entry["status"], "references": refs}
    result = {
        "schema_version": 1,
        "kind": "tga_reviewer_external_evidence_index",
        "acknowledgment_sha256": _digest(acknowledgment),
        "evidence": normalized,
        "evidence_bytes_checked": False,
        "evidence_authenticity_verified": False,
        "reviewer_identity_authenticated": False,
        "reviewer_independence_verified": False,
    }
    result["sha256"] = _digest(result)
    return result

def verify_reviewer_evidence_index(acknowledgment, index):
    if not isinstance(index, dict) or set(index) != {
        "schema_version", "kind", "acknowledgment_sha256", "evidence",
        "evidence_bytes_checked", "evidence_authenticity_verified",
        "reviewer_identity_authenticated", "reviewer_independence_verified", "sha256",
    }:
        raise ValueError("Invalid reviewer evidence index")
    expected = build_reviewer_evidence_index(acknowledgment, index["evidence"])
    if index != expected:
        raise ValueError("Reviewer evidence index does not match acknowledgment")
    return {
        "reviewer_evidence_index_checksum_consistent": True,
        "evidence_bytes_checked": False,
        "evidence_authenticity_verified": False,
        "reviewer_identity_authenticated": False,
        "reviewer_independence_verified": False,
    }
