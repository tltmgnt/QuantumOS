"""Reproduce a frozen ranking evaluation from checksum-verified label bytes."""
import json
from .gap_evidence import verify_evidence_manifest
from .gap_protocol import evaluate_frozen

def replay_evidence(protocol, priority_report, evidence_manifest, label_bytes):
    """Reject altered inputs before computing any evaluation score."""
    integrity = verify_evidence_manifest(evidence_manifest, protocol, label_bytes)
    try:
        labels = json.loads(label_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Label file must be valid UTF-8 JSON") from exc
    result = evaluate_frozen(protocol, priority_report, labels)
    return {
        "schema_version": 1,
        "kind": "checksum_verified_evaluation_replay",
        "evidence_manifest_sha256": evidence_manifest["sha256"],
        "protocol_sha256": protocol["sha256"],
        "label_integrity_verified": integrity["integrity_verified"],
        "external_independence_verified": False,
        "chronological_preregistration_verified": False,
        "evaluation": result,
    }
