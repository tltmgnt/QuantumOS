"""Pin a public key against an out-of-band fingerprint, or verify with a pinned key."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

from .gap_trusted_key_pin import pin_trusted_public_key, read_pinned_public_key
from .gap_portable_handoff_signature import verify_portable_handoff_signature

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    pin = subs.add_parser("pin")
    pin.add_argument("--public-key-hex", required=True)
    pin.add_argument("--expected-sha256", required=True)
    pin.add_argument("--output", type=Path, required=True)
    verify = subs.add_parser("verify")
    verify.add_argument("directory", type=Path)
    verify.add_argument("--inventory", type=Path, required=True)
    verify.add_argument("--signature", type=Path, required=True)
    verify.add_argument("--pinned-key", type=Path, required=True)
    verify.add_argument("--expected-sha256", required=True,
                        help="Public-key fingerprint independently confirmed for THIS verification")
    args = parser.parse_args(argv)
    try:
        if args.command == "pin":
            result = pin_trusted_public_key(args.public_key_hex, args.expected_sha256, args.output)
        else:
            key = read_pinned_public_key(args.pinned_key)
            if (len(args.expected_sha256) != 64
                    or any(c not in "0123456789abcdef" for c in args.expected_sha256)
                    or hashlib.sha256(bytes.fromhex(key)).hexdigest() != args.expected_sha256):
                raise ValueError("Pinned key differs from independently expected fingerprint")
            result = verify_portable_handoff_signature(
                args.directory,
                json.loads(args.inventory.read_text(encoding="utf-8")),
                json.loads(args.signature.read_text(encoding="utf-8")),
                key,
            )
        print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    except (OSError, ValueError, TypeError, KeyError, RuntimeError) as exc:
        print(f"Pinned-key workflow failed: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
