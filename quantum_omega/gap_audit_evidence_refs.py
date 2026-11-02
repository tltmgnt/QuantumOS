"""Checksum-bound references to externally supplied audit evidence.

References are assertions, not proof that the evidence exists or is authentic.
"""
import json
from hashlib import sha256

from .gap_audit_signoff import verify_audit_signoff

_CATEGORIES = ("registration_authenticity", "reviewer_independence", "label_provenance", "scientific_validity")

def _digest(record):
    return sha256(json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()

def create_evidence_references(bundle, signoff, references):
    verify_audit_signoff(bundle, signoff)
    if not isinstance(references, dict) or set(references) != set(_CATEGORIES):
        raise ValueError("All evidence categories must be present")
    normalized = {}
    for category in _CATEGORIES:
        entries = references[category]
        if not isinstance(entries, list):
            raise ValueError("Evidence references must be lists")
        validated = []
        for entry in entries:
            if not isinstance(entry, dict) or set(entry) != {"locator", "description", "sha256"}:
                raise ValueError("Evidence reference must have locator, description and sha256")
            if any(not isinstance(entry[key], str) or not entry[key].strip() for key in ("locator", "description")):
                raise ValueError("Evidence reference locator and description must be nonempty")
            digest = entry["sha256"]
            if not isinstance(digest, str) or len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
                raise ValueError("Evidence reference requires a lowercase SHA-256")
            validated.append(dict(entry))
        normalized[category] = sorted(validated, key=lambda e: (e["locator"], e["sha256"], e["description"]))
        if signoff["evidence_statuses"][category] == "verified" and not validated:
            raise ValueError("Verified category requires at least one evidence reference")
    result = {
        "schema_version": 1,
        "kind": "tga_audit_evidence_references",
        "audit_bundle_sha256": bundle["sha256"],
        "signoff_sha256": signoff["sha256"],
        "references": normalized,
        "evidence_authenticity_verified": False,
    }
    result["sha256"] = _digest(result)
    return result

def verify_evidence_references(bundle, signoff, manifest):
    if not isinstance(manifest, dict) or set(manifest) != {
        "schema_version", "kind", "audit_bundle_sha256", "signoff_sha256",
        "references", "evidence_authenticity_verified", "sha256"
    }:
        raise ValueError("Invalid evidence-reference manifest")
    if manifest.get("schema_version") != 1 or manifest.get("kind") != "tga_audit_evidence_references" or manifest.get("evidence_authenticity_verified") is not False:
        raise ValueError("Unsupported evidence-reference claim")
    expected = create_evidence_references(bundle, signoff, manifest["references"])
    if manifest != expected:
        raise ValueError("Evidence-reference manifest mismatch")
    return {"evidence_references_consistent": True, "evidence_authenticity_verified": False}
