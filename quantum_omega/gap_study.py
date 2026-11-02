"""Strict template validation for independent TGA-Ω reviewer study submissions.

This checks structure and basic data quality, not reviewer independence.
"""
from datetime import datetime, timezone
import re

_SHA = re.compile(r"^[0-9a-f]{64}$")

def _utc(value):
    if not isinstance(value, str):
        raise ValueError("Timestamp must be ISO-8601 text")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Invalid ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("Timestamp must contain a timezone")
    return parsed.astimezone(timezone.utc)

def validate_study_submission(submission):
    required = {"schema_version", "study_id", "protocol_sha256", "registered_at",
                "labels_collected_at", "reviewers", "label_source_id"}
    if not isinstance(submission, dict) or set(submission) != required or type(submission["schema_version"]) is not int or submission["schema_version"] != 1:
        raise ValueError("Invalid study submission schema")
    for key in ("study_id", "label_source_id"):
        if not isinstance(submission[key], str) or not submission[key].strip():
            raise ValueError("Missing study identifier")
    if not isinstance(submission["protocol_sha256"], str) or not _SHA.fullmatch(submission["protocol_sha256"]):
        raise ValueError("Invalid protocol SHA-256")
    registered = _utc(submission["registered_at"])
    collected = _utc(submission["labels_collected_at"])
    if registered >= collected:
        raise ValueError("Claimed registration must precede label collection")
    reviewers = submission["reviewers"]
    if not isinstance(reviewers, list) or len(reviewers) < 2:
        raise ValueError("At least two reviewer records required")
    ids = set()
    for reviewer in reviewers:
        if not isinstance(reviewer, dict) or set(reviewer) != {"reviewer_id", "affiliation", "conflict_declared"}:
            raise ValueError("Invalid reviewer record")
        rid = reviewer["reviewer_id"]
        if not isinstance(rid, str) or not rid.strip() or rid in ids:
            raise ValueError("Reviewer IDs must be unique and nonempty")
        ids.add(rid)
        if not isinstance(reviewer["affiliation"], str) or not reviewer["affiliation"].strip() or type(reviewer["conflict_declared"]) is not bool:
            raise ValueError("Invalid reviewer affiliation or conflict declaration")
    return {
        "schema_version": 1,
        "study_id": submission["study_id"],
        "protocol_sha256": submission["protocol_sha256"],
        "label_source_id": submission["label_source_id"],
        "claimed_chronological_order_valid": True,
        "reviewer_count": len(reviewers),
        "declared_conflict_count": sum(r["conflict_declared"] for r in reviewers),
        "external_timestamp_verified": False,
        "reviewer_independence_verified": False,
        "label_quality_verified": False,
    }
