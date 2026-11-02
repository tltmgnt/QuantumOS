"""Check local reviewer evidence bytes against an evidence index."""
import argparse
import json
import sys
from pathlib import Path
from .gap_reviewer_evidence_files import verify_reviewer_evidence_files

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--acknowledgment", type=Path, required=True)
    p.add_argument("--index", type=Path, required=True)
    p.add_argument("--evidence-dir", type=Path, required=True)
    args = p.parse_args(argv)
    try:
        result = verify_reviewer_evidence_files(
            json.loads(args.acknowledgment.read_text(encoding="utf-8")),
            json.loads(args.index.read_text(encoding="utf-8")),
            args.evidence_dir
        )
        print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    except (OSError, ValueError, TypeError, KeyError, RuntimeError) as exc:
        print(f"Reviewer evidence file check failed: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
