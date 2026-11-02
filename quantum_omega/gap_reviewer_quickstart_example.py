"""Create a fully synthetic portable audit handoff for reviewer onboarding.

Usage: python -m quantum_omega.gap_reviewer_quickstart_example DESTINATION
"""
import argparse
import hashlib
import json
from pathlib import Path

from .gap_provenance_example import create_provenance_example
from .gap_audit_bundle import build_audit_bundle
from .gap_audit_signoff import create_audit_signoff
from .gap_audit_evidence_refs import create_evidence_references
from .gap_audit_chain_report import build_audit_chain_report
from .gap_audit_handoff_receipt import build_audit_handoff_receipt
from .gap_portable_handoff_manifest import build_portable_handoff_manifest
from .gap_portable_handoff_verify import verify_portable_handoff

_CATEGORIES = ("registration_authenticity", "reviewer_independence", "label_provenance", "scientific_validity")

def create_reviewer_quickstart_example(destination):
    root = Path(destination)
    root.mkdir(parents=True, exist_ok=False)
    study = root / "handoff" / "study"
    create_provenance_example(study)
    (study / "evaluation.json").unlink()
    evidence = root / "handoff" / "evidence"
    evidence.mkdir()
    data = b"SYNTHETIC EXAMPLE ONLY - not independently verified.\n"
    (evidence / "synthetic-record.txt").write_bytes(data)
    bundle = build_audit_bundle(study)
    signoff = create_audit_signoff(
        bundle, auditor="Synthetic reviewer", organization="Fictional example",
        reviewed_at="2000-01-03T00:00:00Z", repository_commit="0" * 40,
        evidence_statuses={category: "unverified" for category in _CATEGORIES},
        notes="Synthetic example only; no real registration or independent review.",
    )
    references = {category: [] for category in _CATEGORIES}
    references["label_provenance"] = [{
        "locator": "synthetic-record.txt", "description": "Synthetic example bytes, not provenance proof",
        "sha256": hashlib.sha256(data).hexdigest(),
    }]
    manifest = create_evidence_references(bundle, signoff, references)
    report = build_audit_chain_report(bundle, signoff, manifest, evidence)
    receipt = build_audit_handoff_receipt(study, bundle, signoff, manifest, evidence, report)
    for name, value in (
        ("bundle", bundle), ("signoff", signoff), ("manifest", manifest),
        ("report", report), ("receipt", receipt)
    ):
        (root / "handoff" / (name + ".json")).write_text(
            json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
    inventory = build_portable_handoff_manifest(root / "handoff")
    (root / "handoff-inventory.json").write_text(
        json.dumps(inventory, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return verify_portable_handoff(root / "handoff", inventory)

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args(argv)
    try:
        result = create_reviewer_quickstart_example(args.destination)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(1, f"Reviewer example generation failed: {exc}\n")
    print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
