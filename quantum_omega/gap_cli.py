"""CLI for replaying a frozen TGA evaluation from local files.

Usage: python -m quantum_omega.gap_cli --protocol protocol.json
       --report priority.json --evidence evidence.json --labels labels.json
"""
import argparse
import json
import sys
from pathlib import Path
from .gap_replay import replay_evidence

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("protocol", "report", "evidence", "labels"):
        parser.add_argument("--" + key, required=True, type=Path)
    parser.add_argument("--output", type=Path, help="Optional create-only output JSON path")
    args = parser.parse_args(argv)
    try:
        protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
        report = json.loads(args.report.read_text(encoding="utf-8"))
        evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
        labels = args.labels.read_bytes()
        result = replay_evidence(protocol, report, evidence, labels)
        payload = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
        if args.output:
            with args.output.open("x", encoding="utf-8") as handle:
                handle.write(payload)
        else:
            sys.stdout.write(payload)
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"Evaluation failed: {error}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
