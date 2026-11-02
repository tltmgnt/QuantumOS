"""Portable, self-contained metadata package for replay-verifiable reviewer receipts.

The received package never supplies its own trusted key or expected fingerprint.
"""
import hashlib
import json

from .gap_reviewer_verification_receipt import (
    build_reviewer_verification_receipt, verify_reviewer_verification_receipt,
)

def _canonical_digest(obj):
    return hashlib.sha256(json.dumps(
        obj, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")).hexdigest()

def build_portable_reviewer_receipt_package(directory, inventory, signature, pinned_key_path, expected_sha256):
    receipt = build_reviewer_verification_receipt(
        directory, inventory, signature, pinned_key_path, expected_sha256
    )
    package = {
        "schema_version": 1,
        "kind": "tga_portable_reviewer_receipt_package",
        "inventory": inventory,
        "signature": signature,
        "receipt": receipt,
        "trusted_key_embedded": False,
        "expected_fingerprint_embedded": False,
        "external_authenticity_verified": False,
        "scientific_validity_independently_verified": False,
    }
    package["sha256"] = _canonical_digest(package)
    return package

def verify_portable_reviewer_receipt_package(directory, package, pinned_key_path, expected_sha256):
    if not isinstance(package, dict) or set(package) != {
        "schema_version", "kind", "inventory", "signature", "receipt",
        "trusted_key_embedded", "expected_fingerprint_embedded",
        "external_authenticity_verified", "scientific_validity_independently_verified",
        "sha256",
    }:
        raise ValueError("Invalid portable reviewer receipt package")
    if (type(package["schema_version"]) is not int or package["schema_version"] != 1
            or package["kind"] != "tga_portable_reviewer_receipt_package"
            or package["trusted_key_embedded"] is not False
            or package["expected_fingerprint_embedded"] is not False
            or package["external_authenticity_verified"] is not False
            or package["scientific_validity_independently_verified"] is not False):
        raise ValueError("Unsupported portable reviewer receipt package")
    unsigned = {k: v for k, v in package.items() if k != "sha256"}
    if package["sha256"] != _canonical_digest(unsigned):
        raise ValueError("Portable reviewer receipt package digest mismatch")
    result = verify_reviewer_verification_receipt(
        directory, package["inventory"], package["signature"],
        pinned_key_path, expected_sha256, package["receipt"]
    )
    return {
        "portable_reviewer_receipt_package_valid": True,
        **result,
        "external_authenticity_verified": False,
    }
