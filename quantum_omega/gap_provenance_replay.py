"""Fail-closed replay requiring consistent study metadata and reviewer labels."""
from hashlib import sha256
import json

from .gap_provenance import check_provenance_consistency
from .gap_quality_replay import replay_with_reviewer_quality

def replay_with_provenance(protocol, priority_report, evidence_manifest,
                           label_bytes, reviewer_bytes, study, confidence=0.95):
    """Run provenance consistency checks before frozen scoring or reviewer metrics.

    This checks submitted records only; external attestations remain unverified.
    """
    provenance = check_provenance_consistency(
        study, protocol, evidence_manifest, label_bytes, reviewer_bytes)
    result = replay_with_reviewer_quality(
        protocol, priority_report, evidence_manifest,
        label_bytes, reviewer_bytes, sha256(reviewer_bytes).hexdigest(), confidence)
    output = {
        "schema_version": 1,
        "kind": "provenance_gated_frozen_replay",
        "provenance": provenance,
        "replay": result,
        "external_registration_authenticity_verified": False,
        "reviewer_independence_verified": False,
    }
    output["sha256"] = sha256(json.dumps(output, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    return output
