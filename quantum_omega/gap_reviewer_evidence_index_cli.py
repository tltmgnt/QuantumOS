"""Create or check a self-declared reviewer custody evidence index."""
import argparse
import json
import sys
from pathlib import Path
from .gap_reviewer_evidence_index import (
    build_reviewer_evidence_index, verify_reviewer_evidence_index
)

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    subs = p.add_subparsers(dest="command", required=True)
    for cmd in ("create", "verify"):
        s = subs.add_parser(cmd)
        s.add_argument("--acknowledgment", type=Path, required=True)
        if cmd == "create":
            s.add_argument("--evidence", type=Path, required=True)
            s.add_argument("--output", type=Path, required=True)
        else:
            s.add_argument("--index", type=Path, required=True)
    args = p.parse_args(argv)
    try:
        ack = json.loads(args.acknowledgment.read_text(encoding="utf-8"))
        if args.command == "create":
            result = build_reviewer_evidence_index(
                ack, json.loads(args.evidence.read_text(encoding="utf-8"))
            )
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n")
        else:
            result = verify_reviewer_evidence_index(
                ack, json.loads(args.index.read_text(encoding="utf-8"))
            )
        print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    except (OSError, ValueError, TypeError, KeyError, RuntimeError) as exc:
        print(f"Reviewer evidence index failed: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
