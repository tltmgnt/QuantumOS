"""Checksum-bound self-declared reviewer handoff acknowledgments."""
import hashlib
import json

from .gap_portable_reviewer_receipt_package import verify_portable_reviewer_receipt_package

def _digest(value):
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")).hexdigest()

def create_reviewer_handoff_acknowledgment(
    directory, package, pinned_key_path, expected_sha256, *,
    reviewer_id, reviewed_at, notes=""
):
    if not isinstance(reviewer_id, str) or not reviewer_id.strip():
        raise ValueError("Reviewer ID must be nonempty")
    if not isinstance(reviewed_at, str) or not reviewed_at.strip():
        raise ValueError("Review date must be nonempty")
    if not isinstance(notes, str):
        raise ValueError("Notes must be a string")
    verification = verify_portable_reviewer_receipt_package(
        directory, package, pinned_key_path, expected_sha256
    )
    record = {
        "schema_version": 1,
        "kind": "tga_reviewer_handoff_acknowledgment",
        "reviewer_id": reviewer_id,
        "reviewed_at": reviewed_at,
        "notes": notes,
        "portable_package_sha256": _digest(package),
        "expected_public_key_sha256": expected_sha256,
        "verification_result_sha256": _digest(verification),
        "portable_reviewer_receipt_package_valid": True,
        "reviewer_identity_authenticated": False,
        "fingerprint_source_authenticated_by_software": False,
        "external_authenticity_verified": False,
        "scientific_validity_independently_verified": False,
        "digitally_signed": False,
    }
    record["sha256"] = _digest(record)
    return record

def verify_reviewer_handoff_acknowledgment(
    directory, package, pinned_key_path, expected_sha256, record
):
    if not isinstance(record, dict) or set(record) != {
        "schema_version", "kind", "reviewer_id", "reviewed_at", "notes",
        "portable_package_sha256", "expected_public_key_sha256",
        "verification_result_sha256", "portable_reviewer_receipt_package_valid",
        "reviewer_identity_authenticated", "fingerprint_source_authenticated_by_software",
        "external_authenticity_verified", "scientific_validity_independently_verified",
        "digitally_signed", "sha256",
    }:
        raise ValueError("Invalid reviewer acknowledgment record")
    expected = create_reviewer_handoff_acknowledgment(
        directory, package, pinned_key_path, expected_sha256,
        reviewer_id=record["reviewer_id"], reviewed_at=record["reviewed_at"],
        notes=record["notes"]
    )
    if record != expected:
        raise ValueError("Reviewer acknowledgment differs from replayed inputs")
    return {
        "reviewer_acknowledgment_matches_inputs": True,
        "reviewer_identity_authenticated": False,
        "digitally_signed": False,
        "scientific_validity_independently_verified": False,
    }
