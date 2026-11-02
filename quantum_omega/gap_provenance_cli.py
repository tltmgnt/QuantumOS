"""CLI for provenance-gated frozen TGA evaluation with reviewer quality.

python -m quantum_omega.gap_provenance_cli --protocol protocol.json
  --report priority.json --evidence evidence.json --labels labels.json
  --reviewers reviewers.json --study study.json [--output result.json]
"""
import argparse
import json
import sys
from pathlib import Path
from .gap_provenance_replay import replay_with_provenance

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("protocol", "report", "evidence", "labels", "reviewers", "study"):
        parser.add_argument("--" + key, required=True, type=Path)
    parser.add_argument("--output", type=Path, help="Optional create-only JSON result")
    args = parser.parse_args(argv)
    try:
        protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
        report = json.loads(args.report.read_text(encoding="utf-8"))
        evidence = json.loads(args.evidence.read_text(encoding="utf-8"))
        study = json.loads(args.study.read_text(encoding="utf-8"))
        labels = args.labels.read_bytes()
        reviewers = args.reviewers.read_bytes()
        result = replay_with_provenance(protocol, report, evidence, labels, reviewers, study)
        payload = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
        if args.output:
            with args.output.open("x", encoding="utf-8") as handle:
                handle.write(payload)
        else:
            sys.stdout.write(payload)
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"Provenance-gated evaluation failed: {error}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
