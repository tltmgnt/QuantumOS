"""Freeze and verify a declared evaluation protocol before labels are inspected."""
import json
from hashlib import sha256
from .gap_external_eval import evaluate_labels

def _digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()

def freeze_protocol(report, *, study_id, evaluation_set_id):
    if not isinstance(report, dict) or report.get("kind") != "review_priority_heuristic":
        raise ValueError("Expected a frozen TGA priority report")
    if not isinstance(study_id, str) or not study_id.strip() or not isinstance(evaluation_set_id, str) or not evaluation_set_id.strip():
        raise ValueError("Study and evaluation set identifiers are required")
    if not isinstance(report.get("sha256"), str) or len(report["sha256"]) != 64:
        raise ValueError("Priority report must have a SHA-256 digest")
    payload = {
        "schema_version": 1,
        "kind": "preregistered_evaluation_protocol",
        "study_id": study_id,
        "evaluation_set_id": evaluation_set_id,
        "frozen_priority_report_sha256": report["sha256"],
        "metric": "pairwise_order_accuracy",
        "baseline": "alphabetical",
        "label_source": "externally_supplied",
        "independence_verified": False,
        "preregistration_verified": False,
        "note": "A digest proves content consistency, not that this protocol predates label collection.",
    }
    payload["sha256"] = _digest(payload)
    return payload

def evaluate_frozen(protocol, report, judgments):
    if not isinstance(protocol, dict) or protocol.get("kind") != "preregistered_evaluation_protocol":
        raise ValueError("Expected a frozen evaluation protocol")
    checksum = protocol.get("sha256")
    if not isinstance(checksum, str) or checksum != _digest({k: v for k, v in protocol.items() if k != "sha256"}):
        raise ValueError("Protocol digest mismatch")
    if protocol["frozen_priority_report_sha256"] != report.get("sha256"):
        raise ValueError("Priority report differs from frozen protocol")
    if not isinstance(judgments, dict) or judgments.get("source_id") != protocol["evaluation_set_id"]:
        raise ValueError("Evaluation set differs from frozen protocol")
    evaluation = evaluate_labels(report, judgments)
    evaluation["protocol_sha256"] = checksum
    evaluation["preregistration_verified"] = False
    evaluation["sha256"] = _digest({k: v for k, v in evaluation.items() if k != "sha256"})
    return evaluation
