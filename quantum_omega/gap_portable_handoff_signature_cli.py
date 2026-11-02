"""Verify a portable handoff and its detached Ed25519 manifest signature."""
import argparse
import json
import sys
from pathlib import Path

from .gap_portable_handoff_signature import verify_portable_handoff_signature

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--signature", type=Path, required=True)
    parser.add_argument("--trusted-public-key-hex", required=True,
                        help="32-byte Ed25519 public key obtained independently")
    args = parser.parse_args(argv)
    try:
        inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
        signature = json.loads(args.signature.read_text(encoding="utf-8"))
        result = verify_portable_handoff_signature(
            args.directory, inventory, signature, args.trusted_public_key_hex
        )
        print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    except (OSError, ValueError, TypeError, KeyError, RuntimeError) as exc:
        print(f"Signed portable handoff verification failed: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
