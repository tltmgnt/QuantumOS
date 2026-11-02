"""One-command independent-reviewer verification of a signed portable handoff."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

from .gap_trusted_key_pin import read_pinned_public_key
from .gap_portable_handoff_signature import verify_portable_handoff_signature

def verify_reviewer_handoff(directory, inventory, signature, pinned_key_path, expected_sha256):
    """Replay inputs and verify signature against a separately supplied fingerprint."""
    if (not isinstance(expected_sha256, str) or len(expected_sha256) != 64
            or any(ch not in "0123456789abcdef" for ch in expected_sha256)):
        raise ValueError("Expected SHA-256 must be 64 lowercase hex characters")
    key_hex = read_pinned_public_key(pinned_key_path)
    actual = hashlib.sha256(bytes.fromhex(key_hex)).hexdigest()
    if actual != expected_sha256:
        raise ValueError("Pinned key does not match independently confirmed fingerprint")
    result = verify_portable_handoff_signature(directory, inventory, signature, key_hex)
    return {
        "schema_version": 1,
        "kind": "tga_independent_reviewer_verification",
        "signed_handoff_verified": result["manifest_signature_valid"],
        "study_inputs_replayed": result["study_inputs_replayed"],
        "portable_handoff_bytes_match": result["portable_handoff_bytes_match"],
        "trusted_public_key_sha256": actual,
        "fingerprint_matches_supplied_expected": True,
        "fingerprint_source_authenticated_by_software": False,
        "signer_real_world_identity_verified": False,
        "external_authenticity_verified": False,
        "scientific_validity_independently_verified": False,
    }

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("handoff_dir", type=Path)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--signature", type=Path, required=True)
    parser.add_argument("--pinned-key", type=Path, required=True)
    parser.add_argument("--expected-sha256", required=True,
                        help="Fingerprint confirmed out-of-band for this verification")
    args = parser.parse_args(argv)
    try:
        result = verify_reviewer_handoff(
            args.handoff_dir,
            json.loads(args.inventory.read_text(encoding="utf-8")),
            json.loads(args.signature.read_text(encoding="utf-8")),
            args.pinned_key,
            args.expected_sha256,
        )
        print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    except (OSError, ValueError, TypeError, KeyError, RuntimeError) as exc:
        print(f"Independent reviewer verification failed: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
