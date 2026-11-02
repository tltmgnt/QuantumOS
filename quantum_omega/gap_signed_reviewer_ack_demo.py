"""Create a synthetic two-signer reviewer acknowledgment demo with disposable keys.

All keys are generated in memory; public keys shipped with the demo are NOT
independently authenticated trust anchors.
"""
import argparse
import base64
import hashlib
import json
import sys
from pathlib import Path

from .gap_signed_reviewer_demo import create_signed_reviewer_demo
from .gap_trusted_key_pin import pin_trusted_public_key
from .gap_portable_reviewer_receipt_package import build_portable_reviewer_receipt_package
from .gap_reviewer_handoff_acknowledgment import create_reviewer_handoff_acknowledgment
from .gap_signed_reviewer_acknowledgment import (
    signed_acknowledgment_payload, verify_signed_reviewer_acknowledgment
)

def create_signed_reviewer_ack_demo(destination):
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    except ImportError as exc:
        raise RuntimeError("Install optional dependency: pip install cryptography") from exc
    root = Path(destination)
    root.mkdir(parents=True, exist_ok=False)
    demo = root / "sender"
    create_signed_reviewer_demo(demo)
    inventory = json.loads((demo / "handoff-inventory.json").read_text(encoding="utf-8"))
    signature = json.loads((demo / "handoff-signature.json").read_text(encoding="utf-8"))
    handoff_key = (demo / "DEMO-public-key.hex").read_text(encoding="utf-8").strip()
    handoff_fingerprint = hashlib.sha256(bytes.fromhex(handoff_key)).hexdigest()
    handoff_pin = root / "DEMO-handoff-pin.json"
    pin_trusted_public_key(handoff_key, handoff_fingerprint, handoff_pin)
    package = build_portable_reviewer_receipt_package(
        demo / "handoff", inventory, signature, handoff_pin, handoff_fingerprint
    )
    (root / "reviewer-package.json").write_text(
        json.dumps(package, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    acknowledgment = create_reviewer_handoff_acknowledgment(
        demo / "handoff", package, handoff_pin, handoff_fingerprint,
        reviewer_id="DEMO-reviewer", reviewed_at="synthetic-demo", notes="No external identity verification"
    )
    (root / "reviewer-acknowledgment.json").write_text(
        json.dumps(acknowledgment, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    private = Ed25519PrivateKey.generate()
    public = private.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    reviewer_fingerprint = hashlib.sha256(public).hexdigest()
    reviewer_pin = root / "DEMO-reviewer-pin.json"
    pin_trusted_public_key(public.hex(), reviewer_fingerprint, reviewer_pin)
    envelope = {
        "schema_version": 1,
        "kind": "tga_reviewer_acknowledgment_signature",
        "algorithm": "Ed25519",
        "acknowledgment_sha256": acknowledgment["sha256"],
        "reviewer_public_key_sha256": reviewer_fingerprint,
        "signature_base64": base64.b64encode(
            private.sign(signed_acknowledgment_payload(acknowledgment))
        ).decode("ascii"),
    }
    (root / "reviewer-acknowledgment-signature.json").write_text(
        json.dumps(envelope, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    (root / "DEMO-handoff-fingerprint.txt").write_text(handoff_fingerprint + "\n", encoding="utf-8")
    (root / "DEMO-reviewer-fingerprint.txt").write_text(reviewer_fingerprint + "\n", encoding="utf-8")
    return verify_signed_reviewer_acknowledgment(
        demo / "handoff", package, handoff_pin, handoff_fingerprint,
        acknowledgment, envelope, reviewer_pin, reviewer_fingerprint
    )

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args(argv)
    try:
        result = create_signed_reviewer_ack_demo(args.destination)
        print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    except (OSError, ValueError, TypeError, KeyError, RuntimeError) as exc:
        print(f"Signed reviewer acknowledgment demo failed: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
