"""Export a consolidated, checksum-bound local TGA audit-chain report.

Usage:
 python -m quantum_omega.gap_audit_chain_report_cli --bundle bundle.json --signoff signoff.json --manifest refs.json --evidence-dir evidence/ --output report.json
"""
import argparse
import json
import sys
from pathlib import Path

from .gap_audit_chain_report import build_audit_chain_report

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--signoff", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        bundle = json.loads(args.bundle.read_text(encoding="utf-8"))
        signoff = json.loads(args.signoff.read_text(encoding="utf-8"))
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        result = build_audit_chain_report(bundle, signoff, manifest, args.evidence_dir)
        payload = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(payload)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"Audit-chain report export failed: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
