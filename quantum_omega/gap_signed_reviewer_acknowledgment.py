"""Verify detached Ed25519 signatures on replay-bound reviewer acknowledgments."""
import base64
import binascii
import hashlib
import json

from .gap_reviewer_handoff_acknowledgment import verify_reviewer_handoff_acknowledgment
from .gap_trusted_key_pin import read_pinned_public_key

_CONTEXT = b"QUANTUM-OMEGA reviewer acknowledgment Ed25519 v1\x00"

def signed_acknowledgment_payload(record):
    if not isinstance(record, dict):
        raise ValueError("Acknowledgment must be a JSON object")
    return _CONTEXT + json.dumps(
        record, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")

def verify_signed_reviewer_acknowledgment(
    directory, package, handoff_pinned_key, handoff_expected_sha256,
    record, signature, reviewer_pinned_key, reviewer_expected_sha256,
):
    """Replay handoff, then verify a separately pinned reviewer's signature."""
    verified = verify_reviewer_handoff_acknowledgment(
        directory, package, handoff_pinned_key, handoff_expected_sha256, record
    )
    if not isinstance(signature, dict) or set(signature) != {
        "schema_version", "kind", "algorithm", "acknowledgment_sha256",
        "reviewer_public_key_sha256", "signature_base64"
    }:
        raise ValueError("Invalid reviewer signature envelope")
    if (type(signature["schema_version"]) is not int or signature["schema_version"] != 1
            or signature["kind"] != "tga_reviewer_acknowledgment_signature"
            or signature["algorithm"] != "Ed25519"):
        raise ValueError("Unsupported reviewer signature envelope")
    if (not isinstance(reviewer_expected_sha256, str)
            or len(reviewer_expected_sha256) != 64
            or any(c not in "0123456789abcdef" for c in reviewer_expected_sha256)):
        raise ValueError("Expected reviewer fingerprint must be 64 lowercase hex characters")
    key = bytes.fromhex(read_pinned_public_key(reviewer_pinned_key))
    actual = hashlib.sha256(key).hexdigest()
    if actual != reviewer_expected_sha256:
        raise ValueError("Reviewer key differs from independently expected fingerprint")
    if (signature["acknowledgment_sha256"] != record["sha256"]
            or signature["reviewer_public_key_sha256"] != actual):
        raise ValueError("Reviewer signature metadata mismatch")
    try:
        raw_signature = base64.b64decode(signature["signature_base64"], validate=True)
    except (ValueError, TypeError, binascii.Error) as exc:
        raise ValueError("Invalid reviewer signature encoding") from exc
    if len(raw_signature) != 64:
        raise ValueError("Invalid reviewer signature length")
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except ImportError as exc:
        raise RuntimeError("Install optional dependency: pip install cryptography") from exc
    try:
        Ed25519PublicKey.from_public_bytes(key).verify(
            raw_signature, signed_acknowledgment_payload(record)
        )
    except (InvalidSignature, ValueError) as exc:
        raise ValueError("Invalid reviewer acknowledgment signature") from exc
    return {
        **verified,
        "reviewer_acknowledgment_signature_valid": True,
        "reviewer_public_key_sha256": actual,
        "reviewer_real_world_identity_verified": False,
        "reviewer_independence_verified": False,
        "scientific_validity_independently_verified": False,
    }
