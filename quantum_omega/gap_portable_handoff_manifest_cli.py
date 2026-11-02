"""Create or verify a fixed-layout portable TGA audit-handoff byte inventory."""
import argparse
import json
import sys
from pathlib import Path

from .gap_portable_handoff_manifest import build_portable_handoff_manifest, verify_portable_handoff_manifest

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create")
    create.add_argument("directory", type=Path)
    create.add_argument("--output", type=Path, required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("directory", type=Path)
    verify.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "create":
            result = build_portable_handoff_manifest(args.directory)
            output = args.output.resolve(strict=False)
            root = args.directory.resolve(strict=True)
            if output.is_relative_to(root):
                raise ValueError("Inventory output must be outside the handoff directory")
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n")
        else:
            saved = json.loads(args.manifest.read_text(encoding="utf-8"))
            result = verify_portable_handoff_manifest(args.directory, saved)
            sys.stdout.write(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"Portable handoff manifest {args.command} failed: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
