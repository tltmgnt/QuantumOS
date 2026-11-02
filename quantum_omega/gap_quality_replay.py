"""Combine frozen evaluation replay with checksum-bound reviewer-quality reporting."""
from hashlib import sha256
import json
import re

from .gap_replay import replay_evidence
from .gap_quality_report import build_reviewer_quality_report

def replay_with_reviewer_quality(protocol, priority_report, evidence_manifest,
                                 label_bytes, reviewer_bytes, reviewer_sha256,
                                 confidence=0.95):
    """Reviewer bytes are separately checksum-bound, not assumed to be label bytes."""
    if not isinstance(reviewer_bytes, bytes):
        raise ValueError("Reviewer data must be original UTF-8 bytes")
    if not isinstance(reviewer_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", reviewer_sha256):
        raise ValueError("Expected lowercase reviewer SHA-256")
    actual = sha256(reviewer_bytes).hexdigest()
    if actual != reviewer_sha256:
        raise ValueError("Reviewer submission checksum mismatch")
    try:
        reviewer_data = json.loads(reviewer_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Reviewer submission must be UTF-8 JSON") from exc
    if not isinstance(reviewer_data, dict) or set(reviewer_data) != {"submissions", "adjudications"}:
        raise ValueError("Expected submissions and adjudications")
    frozen = replay_evidence(protocol, priority_report, evidence_manifest, label_bytes)
    quality = build_reviewer_quality_report(reviewer_data["submissions"],
                                          reviewer_data["adjudications"], confidence)
    result = {
        "schema_version": 1,
        "kind": "frozen_evaluation_with_reviewer_quality",
        "evaluation_replay": frozen,
        "reviewer_data_sha256": actual,
        "reviewer_quality": quality,
        "external_reviewer_independence_verified": False,
        "reviewer_label_alignment_verified": False,
        "note": "Reviewer data has separate byte integrity only; it is not proven to match the frozen evaluation labels.",
    }
    result["sha256"] = sha256(json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    return result
