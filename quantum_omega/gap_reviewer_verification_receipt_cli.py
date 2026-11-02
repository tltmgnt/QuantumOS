"""Export or replay-check a reviewer verification receipt."""
import argparse
import json
import sys
from pathlib import Path

from .gap_reviewer_verification_receipt import (
    build_reviewer_verification_receipt, verify_reviewer_verification_receipt
)

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    for command in ("create", "verify"):
        p = subs.add_parser(command)
        p.add_argument("handoff_dir", type=Path)
        p.add_argument("--inventory", type=Path, required=True)
        p.add_argument("--signature", type=Path, required=True)
        p.add_argument("--pinned-key", type=Path, required=True)
        p.add_argument("--expected-sha256", required=True)
        p.add_argument("--receipt" if command == "verify" else "--output",
                       type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
        signature = json.loads(args.signature.read_text(encoding="utf-8"))
        inputs = (args.handoff_dir, inventory, signature, args.pinned_key, args.expected_sha256)
        if args.command == "create":
            result = build_reviewer_verification_receipt(*inputs)
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n")
        else:
            result = verify_reviewer_verification_receipt(
                *inputs, json.loads(args.receipt.read_text(encoding="utf-8"))
            )
        print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    except (OSError, ValueError, TypeError, KeyError, RuntimeError) as exc:
        print(f"Reviewer receipt check failed: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
