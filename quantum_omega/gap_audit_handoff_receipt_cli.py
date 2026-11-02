"""Create or verify an input-backed TGA audit-handoff receipt."""
import argparse
import json
import sys
from pathlib import Path

from .gap_audit_handoff_receipt import build_audit_handoff_receipt, verify_audit_handoff_receipt

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("create", "verify"):
        sub = commands.add_parser(command)
        sub.add_argument("--study-dir", type=Path, required=True)
        sub.add_argument("--evidence-dir", type=Path, required=True)
        for name in ("bundle", "signoff", "manifest", "report"):
            sub.add_argument("--" + name, type=Path, required=True)
        if command == "create":
            sub.add_argument("--output", type=Path, required=True)
        else:
            sub.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        values = {
            name: json.loads(getattr(args, name).read_text(encoding="utf-8"))
            for name in ("bundle", "signoff", "manifest", "report")
        }
        params = (
            args.study_dir, values["bundle"], values["signoff"], values["manifest"],
            args.evidence_dir, values["report"]
        )
        if args.command == "create":
            result = build_audit_handoff_receipt(*params)
            payload = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(payload)
        else:
            receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
            result = verify_audit_handoff_receipt(*params, receipt)
            sys.stdout.write(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"Audit-handoff receipt {args.command} failed: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
