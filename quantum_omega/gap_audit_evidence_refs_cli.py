"""Create and verify external evidence-reference manifests for TGA audits.

Usage:
 python -m quantum_omega.gap_audit_evidence_refs_cli create --bundle bundle.json --signoff signoff.json --references references.json --output evidence-refs.json
 python -m quantum_omega.gap_audit_evidence_refs_cli verify --bundle bundle.json --signoff signoff.json --manifest evidence-refs.json
"""
import argparse
import json
import sys
from pathlib import Path

from .gap_audit_evidence_refs import create_evidence_references, verify_evidence_references

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create", help="Create a checksum-bound evidence-reference manifest")
    verify = sub.add_parser("verify", help="Check evidence-reference manifest consistency")
    for command in (create, verify):
        command.add_argument("--bundle", type=Path, required=True)
        command.add_argument("--signoff", type=Path, required=True)
    create.add_argument("--references", type=Path, required=True)
    create.add_argument("--output", type=Path, required=True)
    verify.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        bundle = json.loads(args.bundle.read_text(encoding="utf-8"))
        signoff = json.loads(args.signoff.read_text(encoding="utf-8"))
        if args.command == "create":
            references = json.loads(args.references.read_text(encoding="utf-8"))
            result = create_evidence_references(bundle, signoff, references)
            payload = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(payload)
        else:
            manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
            result = verify_evidence_references(bundle, signoff, manifest)
            sys.stdout.write(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"Audit evidence-reference operation failed: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
