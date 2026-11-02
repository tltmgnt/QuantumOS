"""Create or replay-verify a self-declared reviewer handoff acknowledgment."""
import argparse
import json
import sys
from pathlib import Path
from .gap_reviewer_handoff_acknowledgment import (
    create_reviewer_handoff_acknowledgment, verify_reviewer_handoff_acknowledgment
)

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    for command in ("create", "verify"):
        p = subs.add_parser(command)
        p.add_argument("handoff_dir", type=Path)
        p.add_argument("--package", type=Path, required=True)
        p.add_argument("--pinned-key", type=Path, required=True)
        p.add_argument("--expected-sha256", required=True)
        if command == "create":
            p.add_argument("--reviewer-id", required=True)
            p.add_argument("--reviewed-at", required=True)
            p.add_argument("--notes", default="")
            p.add_argument("--output", type=Path, required=True)
        else:
            p.add_argument("--acknowledgment", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        package = json.loads(args.package.read_text(encoding="utf-8"))
        common = (args.handoff_dir, package, args.pinned_key, args.expected_sha256)
        if args.command == "create":
            result = create_reviewer_handoff_acknowledgment(
                *common, reviewer_id=args.reviewer_id,
                reviewed_at=args.reviewed_at, notes=args.notes
            )
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n")
        else:
            result = verify_reviewer_handoff_acknowledgment(
                *common, json.loads(args.acknowledgment.read_text(encoding="utf-8"))
            )
        print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    except (OSError, ValueError, TypeError, KeyError, RuntimeError) as exc:
        print(f"Reviewer acknowledgment failed: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
