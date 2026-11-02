"""Generate a local synthetic demonstration of frozen evaluation replay.

Usage: python -m quantum_omega.gap_example /tmp/tga-evaluation-demo
"""
import argparse
import json
from pathlib import Path
from hashlib import sha256
from .gap_priority import rank_gaps
from .gap_protocol import freeze_protocol
from .gap_evidence import build_evidence_manifest
from .gap_replay import replay_evidence
from .gap_heldout import _fixture

def create_example(destination):
    root = Path(destination)
    root.mkdir(parents=True, exist_ok=False)
    report = rank_gaps(_fixture())
    ids = [row["claim_id"] for row in report["ranked_claims"]]
    protocol = freeze_protocol(report, study_id="synthetic-example", evaluation_set_id="synthetic-labels")
    labels = {"schema_version": 1, "source_id": "synthetic-labels",
              "pairs": [{"higher_priority": ids[0], "lower_priority": ids[-1]}]}
    label_bytes = (json.dumps(labels, sort_keys=True, indent=2) + "\n").encode()
    evidence = build_evidence_manifest(protocol,
        registration_url="https://example.org/synthetic-only",
        registration_timestamp="2000-01-01T00:00:00Z",
        labels_sha256=sha256(label_bytes).hexdigest(),
        reviewer_ids=["synthetic-reviewer-not-a-person"])
    files = {"priority.json": report, "protocol.json": protocol, "evidence.json": evidence}
    for name, payload in files.items():
        (root / name).write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    (root / "labels.json").write_bytes(label_bytes)
    result = replay_evidence(protocol, report, evidence, label_bytes)
    (root / "evaluation.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return result

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args(argv)
    create_example(args.destination)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
