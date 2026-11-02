"""Generate or verify a checksum-bound inventory of a TGA study package.

Usage:
 python -m quantum_omega.gap_study_inventory_cli create PACKAGE --output inventory.json
 python -m quantum_omega.gap_study_inventory_cli verify PACKAGE --inventory inventory.json
"""
import argparse
import json
import sys
from pathlib import Path

from .gap_study_inventory import inventory_study_package, verify_study_inventory

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create", help="Create a checksum-bound inventory")
    create.add_argument("package", type=Path)
    create.add_argument("--output", type=Path, required=True, help="Create-only inventory JSON")
    verify = sub.add_parser("verify", help="Verify an inventory against study files")
    verify.add_argument("package", type=Path)
    verify.add_argument("--inventory", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "create":
            result = inventory_study_package(args.package)
            payload = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(payload)
        else:
            inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
            result = verify_study_inventory(args.package, inventory)
            sys.stdout.write(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"Study inventory operation failed: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
