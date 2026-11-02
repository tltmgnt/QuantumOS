"""Check local evidence files against an audit evidence-reference manifest.

Usage:
 python -m quantum_omega.gap_audit_local_evidence_cli --bundle bundle.json --signoff signoff.json --manifest refs.json --evidence-dir evidence/
"""
import argparse
import json
import sys
from pathlib import Path

from .gap_audit_local_evidence import verify_local_evidence_files

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--signoff", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        bundle = json.loads(args.bundle.read_text(encoding="utf-8"))
        signoff = json.loads(args.signoff.read_text(encoding="utf-8"))
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        result = verify_local_evidence_files(bundle, signoff, manifest, args.evidence_dir)
        sys.stdout.write(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"Local evidence verification failed: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
