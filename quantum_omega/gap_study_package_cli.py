"""Validate a six-file external TGA study package from the command line.

Usage: python -m quantum_omega.gap_study_package_cli PACKAGE_DIR [--output RESULT.json]
"""
import argparse
import json
import sys
from pathlib import Path

from .gap_study_package import validate_study_package

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path, help="Directory with six required JSON input files")
    parser.add_argument("--output", type=Path, help="Create-only result JSON path")
    args = parser.parse_args(argv)
    try:
        result = validate_study_package(args.package)
        payload = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
        if args.output is not None:
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(payload)
        else:
            sys.stdout.write(payload)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"Study package validation failed: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
