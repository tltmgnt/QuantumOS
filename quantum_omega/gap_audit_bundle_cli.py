"""Export and verify deterministic audit bundles for six-file TGA studies.

Usage:
 python -m quantum_omega.gap_audit_bundle_cli export PACKAGE --output bundle.json
 python -m quantum_omega.gap_audit_bundle_cli verify PACKAGE --bundle bundle.json
 python -m quantum_omega.gap_audit_bundle_cli verify-offline --bundle bundle.json
"""
import argparse
import json
import sys
from pathlib import Path

from .gap_audit_bundle import build_audit_bundle, verify_audit_bundle
from .gap_audit_offline import verify_bundle_offline

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    export = sub.add_parser("export", help="Export a create-only audit bundle")
    export.add_argument("package", type=Path)
    export.add_argument("--output", type=Path, required=True)
    verify = sub.add_parser("verify", help="Verify an audit bundle against original inputs")
    verify.add_argument("package", type=Path)
    verify.add_argument("--bundle", type=Path, required=True)
    offline = sub.add_parser("verify-offline", help="Check saved bundle checksums without study inputs")
    offline.add_argument("--bundle", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "export":
            result = build_audit_bundle(args.package)
            payload = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(payload)
        else:
            bundle = json.loads(args.bundle.read_text(encoding="utf-8"))
            result = verify_bundle_offline(bundle) if args.command == "verify-offline" else verify_audit_bundle(args.package, bundle)
            sys.stdout.write(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"Audit bundle operation failed: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
