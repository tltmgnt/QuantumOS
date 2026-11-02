"""Optional Ed25519 verification of a portable manifest using a pinned public key.

This authenticates possession of a private key, not the real-world identity
of its owner. No private key material is accepted or generated here.
"""
import base64
import binascii
import hashlib
import json

from .gap_portable_handoff_verify import verify_portable_handoff

_CONTEXT = b"QUANTUM-OMEGA portable handoff manifest Ed25519 v1\x00"

def signed_manifest_payload(inventory):
    """Canonical, domain-separated bytes covered by an Ed25519 signature."""
    if not isinstance(inventory, dict):
        raise ValueError("Inventory must be a JSON object")
    return _CONTEXT + json.dumps(
        inventory, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")

def verify_portable_handoff_signature(directory, inventory, signature, trusted_public_key_hex):
    """Verify complete handoff and detached signature against an out-of-band key."""
    full = verify_portable_handoff(directory, inventory)
    if not isinstance(signature, dict) or set(signature) != {
        "schema_version", "kind", "algorithm", "manifest_sha256",
        "public_key_sha256", "signature_base64"
    }:
        raise ValueError("Invalid signature envelope")
    if (signature["schema_version"] != 1
            or signature["kind"] != "tga_portable_manifest_signature"
            or signature["algorithm"] != "Ed25519"):
        raise ValueError("Unsupported signature format")
    if not isinstance(trusted_public_key_hex, str) or len(trusted_public_key_hex) != 64:
        raise ValueError("Expected a 32-byte pinned Ed25519 public key in hex")
    try:
        key_bytes = bytes.fromhex(trusted_public_key_hex)
        signature_bytes = base64.b64decode(signature["signature_base64"], validate=True)
    except (ValueError, TypeError, binascii.Error) as exc:
        raise ValueError("Invalid public key or signature encoding") from exc
    if len(signature_bytes) != 64:
        raise ValueError("Invalid Ed25519 signature length")
    if (signature["manifest_sha256"] != inventory["sha256"]
            or signature["public_key_sha256"] != hashlib.sha256(key_bytes).hexdigest()):
        raise ValueError("Signature metadata does not match trusted key or inventory")
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except ImportError as exc:
        raise RuntimeError("Install optional dependency: pip install cryptography") from exc
    try:
        Ed25519PublicKey.from_public_bytes(key_bytes).verify(
            signature_bytes, signed_manifest_payload(inventory)
        )
    except (InvalidSignature, ValueError) as exc:
        raise ValueError("Invalid detached Ed25519 signature") from exc
    return {
        **full,
        "manifest_signature_valid": True,
        "trusted_public_key_sha256": hashlib.sha256(key_bytes).hexdigest(),
        "signer_real_world_identity_verified": False,
        "external_authenticity_verified": False,
        "scientific_validity_independently_verified": False,
    }
