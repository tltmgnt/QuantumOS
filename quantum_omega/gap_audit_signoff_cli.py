"""Create and verify self-declared TGA audit sign-off records.

Usage:
 python -m quantum_omega.gap_audit_signoff_cli create --bundle bundle.json --declaration declaration.json --output signoff.json
 python -m quantum_omega.gap_audit_signoff_cli verify --bundle bundle.json --signoff signoff.json

The declaration JSON must contain auditor, organization, reviewed_at,
repository_commit, evidence_statuses and notes.
"""
import argparse
import json
import sys
from pathlib import Path

from .gap_audit_signoff import create_audit_signoff, verify_audit_signoff

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create", help="Create a checksum-bound self-declaration")
    create.add_argument("--bundle", type=Path, required=True)
    create.add_argument("--declaration", type=Path, required=True)
    create.add_argument("--output", type=Path, required=True)
    verify = sub.add_parser("verify", help="Check sign-off consistency with a saved bundle")
    verify.add_argument("--bundle", type=Path, required=True)
    verify.add_argument("--signoff", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        bundle = json.loads(args.bundle.read_text(encoding="utf-8"))
        if args.command == "create":
            declaration = json.loads(args.declaration.read_text(encoding="utf-8"))
            if not isinstance(declaration, dict) or set(declaration) != {
                "auditor", "organization", "reviewed_at", "repository_commit",
                "evidence_statuses", "notes"
            }:
                raise ValueError("Declaration must contain exactly six required fields")
            result = create_audit_signoff(bundle, **declaration)
            payload = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(payload)
        else:
            signoff = json.loads(args.signoff.read_text(encoding="utf-8"))
            result = verify_audit_signoff(bundle, signoff)
            sys.stdout.write(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"Audit sign-off operation failed: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
