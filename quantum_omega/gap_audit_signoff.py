"""Conservative, checksum-bound declarations for independent audit handoff.

A self-declared sign-off is not identity authentication or a digital signature.
"""
import json
from hashlib import sha256

from .gap_audit_offline import verify_bundle_offline

_EVIDENCE = ("registration_authenticity", "reviewer_independence", "label_provenance", "scientific_validity")
_STATUSES = ("unverified", "verified", "rejected")

def _digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()

def create_audit_signoff(bundle, *, auditor, organization, reviewed_at, repository_commit, evidence_statuses, notes):
    verify_bundle_offline(bundle)
    for name, value in (("auditor", auditor), ("organization", organization), ("reviewed_at", reviewed_at), ("repository_commit", repository_commit), ("notes", notes)):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be nonempty")
    if not isinstance(evidence_statuses, dict) or set(evidence_statuses) != set(_EVIDENCE):
        raise ValueError("All independent evidence statuses are required")
    if any(type(status) is not str or status not in _STATUSES for status in evidence_statuses.values()):
        raise ValueError("Invalid independent evidence status")
    if len(repository_commit) != 40 or any(ch not in "0123456789abcdef" for ch in repository_commit):
        raise ValueError("repository_commit must be a full lowercase Git SHA-1")
    result = {
        "schema_version": 1,
        "kind": "tga_independent_audit_signoff",
        "audit_bundle_sha256": bundle["sha256"],
        "evaluation_sha256": bundle["evaluation_sha256"],
        "auditor": auditor,
        "organization": organization,
        "reviewed_at": reviewed_at,
        "repository_commit": repository_commit,
        "evidence_statuses": dict(sorted(evidence_statuses.items())),
        "notes": notes,
        "identity_authenticated": False,
        "digitally_signed": False,
    }
    result["sha256"] = _digest(result)
    return result

def verify_audit_signoff(bundle, signoff):
    verify_bundle_offline(bundle)
    if not isinstance(signoff, dict) or set(signoff) != {
        "schema_version", "kind", "audit_bundle_sha256", "evaluation_sha256",
        "auditor", "organization", "reviewed_at", "repository_commit",
        "evidence_statuses", "notes", "identity_authenticated", "digitally_signed", "sha256"
    }:
        raise ValueError("Invalid sign-off structure")
    if signoff.get("schema_version") != 1 or signoff.get("kind") != "tga_independent_audit_signoff":
        raise ValueError("Invalid sign-off schema")
    expected = create_audit_signoff(
        bundle, auditor=signoff["auditor"], organization=signoff["organization"],
        reviewed_at=signoff["reviewed_at"], repository_commit=signoff["repository_commit"],
        evidence_statuses=signoff["evidence_statuses"], notes=signoff["notes"],
    )
    if signoff != expected:
        raise ValueError("Sign-off record mismatch")
    return {"signoff_checksum_consistent": True, "identity_authenticated": False, "digitally_signed": False}
