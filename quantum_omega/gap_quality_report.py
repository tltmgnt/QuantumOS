"""Reproducible reviewer-quality report; no external validation is implied."""
from hashlib import sha256
import json

from .gap_adjudication import disagreement_report
from .gap_uncertainty import agreement_with_uncertainty

def build_reviewer_quality_report(submissions, adjudications=(), confidence=0.95):
    agreement = agreement_with_uncertainty(submissions, confidence)
    disputes = disagreement_report(submissions, adjudications)
    if agreement["reviewer_count"] < 2:
        raise ValueError("At least two reviewers required")
    result = {
        "schema_version": 1,
        "kind": "tga_reviewer_quality_report",
        "agreement": agreement,
        "disagreement_audit": disputes,
        "limitations": [
            "No reviewer identity or independence verification is performed.",
            "Wilson intervals are illustrative because claim pairs and reviewers may be dependent.",
            "Adjudication records do not replace original judgments.",
            "This report does not establish scientific validity or quantum-gravity discovery.",
        ],
    }
    result["sha256"] = sha256(json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()
    return result
