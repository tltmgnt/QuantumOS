"""Verify the six-file study and all saved TGA audit handoff artifacts."""
import argparse
import json
import sys
from pathlib import Path

from .gap_audit_handoff_check import verify_complete_audit_handoff

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study-dir", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    for name in ("bundle", "signoff", "manifest", "report"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        values = {
            name: json.loads(getattr(args, name).read_text(encoding="utf-8"))
            for name in ("bundle", "signoff", "manifest", "report")
        }
        result = verify_complete_audit_handoff(
            args.study_dir, values["bundle"], values["signoff"], values["manifest"],
            args.evidence_dir, values["report"]
        )
        sys.stdout.write(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"Complete audit handoff verification failed: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
