"""Run portable byte verification and full audit replay in one command."""
import argparse
import json
import sys
from pathlib import Path

from .gap_portable_handoff_verify import verify_portable_handoff

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--inventory", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
        result = verify_portable_handoff(args.directory, inventory)
        sys.stdout.write(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"Portable audit-handoff verification failed: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
