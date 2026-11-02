"""Generate a synthetic portable handoff signed with a disposable Ed25519 key.

The private key is used only in memory and never saved. The exported public key
is a demonstration artifact, NOT an independently authenticated trust anchor.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path

from .gap_reviewer_quickstart_example import create_reviewer_quickstart_example
from .gap_portable_handoff_signature import signed_manifest_payload, verify_portable_handoff_signature

def create_signed_reviewer_demo(destination):
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    except ImportError as exc:
        raise RuntimeError("Install optional dependency: pip install cryptography") from exc
    root = Path(destination)
    create_reviewer_quickstart_example(root)
    inventory = json.loads((root / "handoff-inventory.json").read_text(encoding="utf-8"))
    private = Ed25519PrivateKey.generate()
    key = private.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    signature = {
        "schema_version": 1,
        "kind": "tga_portable_manifest_signature",
        "algorithm": "Ed25519",
        "manifest_sha256": inventory["sha256"],
        "public_key_sha256": hashlib.sha256(key).hexdigest(),
        "signature_base64": base64.b64encode(
            private.sign(signed_manifest_payload(inventory))
        ).decode("ascii"),
    }
    (root / "handoff-signature.json").write_text(
        json.dumps(signature, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    (root / "DEMO-public-key.hex").write_text(key.hex() + "\n", encoding="utf-8")
    return verify_portable_handoff_signature(root / "handoff", inventory, signature, key.hex())

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args(argv)
    try:
        result = create_signed_reviewer_demo(args.destination)
    except (OSError, ValueError, TypeError, KeyError, RuntimeError) as exc:
        parser.exit(1, f"Signed reviewer demo failed: {exc}\n")
    print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
