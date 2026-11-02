"""Generate a complete SYNTHETIC example for the provenance-gated TGA CLI.

Usage: python -m quantum_omega.gap_provenance_example /tmp/tga-full-demo
"""
import argparse
import json
from hashlib import sha256
from pathlib import Path

from .gap_evidence import build_evidence_manifest
from .gap_heldout import _fixture
from .gap_priority import rank_gaps
from .gap_protocol import freeze_protocol
from .gap_provenance_replay import replay_with_provenance

def _json_bytes(data):
    return (json.dumps(data, sort_keys=True, indent=2) + "\n").encode("utf-8")

def create_provenance_example(destination):
    root = Path(destination)
    root.mkdir(parents=True, exist_ok=False)
    report = rank_gaps(_fixture())
    ids = [row["claim_id"] for row in report["ranked_claims"]]
    protocol = freeze_protocol(report, study_id="synthetic-study", evaluation_set_id="synthetic-labels")
    higher, lower = ids[0], ids[-1]
    pair = {"higher_priority": higher, "lower_priority": lower}
    labels = {"schema_version": 1, "source_id": "synthetic-labels", "pairs": [pair]}
    label_bytes = _json_bytes(labels)
    reviewers = {
        "submissions": [
            {"reviewer_id": "synthetic-r1", "pairs": [pair]},
            {"reviewer_id": "synthetic-r2", "pairs": [pair]},
        ],
        "adjudications": [],
    }
    reviewer_bytes = _json_bytes(reviewers)
    registered_at = "2000-01-01T00:00:00Z"
    evidence = build_evidence_manifest(
        protocol, registration_url="https://example.org/synthetic-only",
        registration_timestamp=registered_at,
        labels_sha256=sha256(label_bytes).hexdigest(),
        reviewer_ids=["synthetic-r1", "synthetic-r2"],
    )
    study = {
        "schema_version": 1,
        "study_id": "synthetic-study",
        "protocol_sha256": protocol["sha256"],
        "registered_at": registered_at,
        "labels_collected_at": "2000-01-02T00:00:00Z",
        "label_source_id": "synthetic-labels",
        "reviewers": [
            {"reviewer_id": "synthetic-r1", "affiliation": "fictional-A", "conflict_declared": False},
            {"reviewer_id": "synthetic-r2", "affiliation": "fictional-B", "conflict_declared": False},
        ],
    }
    for name, data in (("priority.json", report), ("protocol.json", protocol),
                       ("evidence.json", evidence), ("study.json", study)):
        (root / name).write_bytes(_json_bytes(data))
    (root / "labels.json").write_bytes(label_bytes)
    (root / "reviewers.json").write_bytes(reviewer_bytes)
    result = replay_with_provenance(protocol, report, evidence, label_bytes, reviewer_bytes, study)
    (root / "evaluation.json").write_bytes(_json_bytes(result))
    return result

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args(argv)
    create_provenance_example(args.destination)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
