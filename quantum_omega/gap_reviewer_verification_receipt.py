"""Create and verify checksum-bound receipts for signed reviewer handoff checks."""
import hashlib
import json

from .gap_reviewer_verify_cli import verify_reviewer_handoff

def _digest(value):
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")).hexdigest()

def build_reviewer_verification_receipt(directory, inventory, signature, pinned_key_path, expected_sha256):
    result = verify_reviewer_handoff(
        directory, inventory, signature, pinned_key_path, expected_sha256
    )
    receipt = {
        "schema_version": 1,
        "kind": "tga_reviewer_verification_receipt",
        "portable_inventory_sha256": _digest(inventory),
        "signature_envelope_sha256": _digest(signature),
        "trusted_public_key_sha256": result["trusted_public_key_sha256"],
        "verification_result_sha256": _digest(result),
        "signed_handoff_verified": True,
        "study_inputs_replayed": True,
        "fingerprint_source_authenticated_by_software": False,
        "signer_real_world_identity_verified": False,
        "external_authenticity_verified": False,
        "scientific_validity_independently_verified": False,
    }
    receipt["sha256"] = _digest(receipt)
    return receipt

def verify_reviewer_verification_receipt(directory, inventory, signature, pinned_key_path, expected_sha256, receipt):
    if not isinstance(receipt, dict):
        raise ValueError("Receipt must be a JSON object")
    expected = build_reviewer_verification_receipt(
        directory, inventory, signature, pinned_key_path, expected_sha256
    )
    if receipt != expected:
        raise ValueError("Saved reviewer receipt does not match replayed inputs")
    return {
        "reviewer_receipt_matches_inputs": True,
        "signed_handoff_verified": True,
        "signer_real_world_identity_verified": False,
        "scientific_validity_independently_verified": False,
    }
