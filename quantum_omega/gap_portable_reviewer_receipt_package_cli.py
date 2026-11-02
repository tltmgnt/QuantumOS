"""Create or verify a portable signed reviewer receipt package."""
import argparse
import json
import sys
from pathlib import Path
from .gap_portable_reviewer_receipt_package import (
    build_portable_reviewer_receipt_package, verify_portable_reviewer_receipt_package
)

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("create", "verify"):
        p = sub.add_parser(command)
        p.add_argument("handoff_dir", type=Path)
        p.add_argument("--pinned-key", type=Path, required=True)
        p.add_argument("--expected-sha256", required=True)
        if command == "create":
            p.add_argument("--inventory", type=Path, required=True)
            p.add_argument("--signature", type=Path, required=True)
            p.add_argument("--output", type=Path, required=True)
        else:
            p.add_argument("--package", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "create":
            result = build_portable_reviewer_receipt_package(
                args.handoff_dir,
                json.loads(args.inventory.read_text(encoding="utf-8")),
                json.loads(args.signature.read_text(encoding="utf-8")),
                args.pinned_key, args.expected_sha256
            )
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n")
        else:
            result = verify_portable_reviewer_receipt_package(
                args.handoff_dir,
                json.loads(args.package.read_text(encoding="utf-8")),
                args.pinned_key, args.expected_sha256
            )
        print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    except (OSError, ValueError, TypeError, KeyError, RuntimeError) as exc:
        print(f"Portable reviewer receipt package failed: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
