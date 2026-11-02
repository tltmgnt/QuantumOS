"""Machine-readable review summary for a validated external study package.

Structural checks are not evidence of external independence or preregistration.
"""
import json
from hashlib import sha256
from .gap_study_package import validate_study_package

def summarize_study_package(directory):
    replay = validate_study_package(directory)
    provenance = replay["provenance"]
    quality_replay = replay["replay"]
    result = {
        "schema_version": 1,
        "kind": "tga_study_review_summary",
        "evaluation_sha256": replay["sha256"],
        "checks": {
            "protocol_digest_consistent": provenance["protocol_digest_consistent"],
            "label_checksum_consistent": provenance["label_checksum_consistent"],
            "label_source_consistent": provenance["label_source_consistent"],
            "reviewer_ids_consistent": provenance["reviewer_ids_consistent"],
            "claimed_registration_timestamp_consistent": provenance["claimed_registration_timestamp_consistent"],
            "reviewer_label_alignment_verified": quality_replay["reviewer_label_alignment_verified"],
        },
        "external_verification": {
            "registration_authenticity": False,
            "reviewer_independence": False,
            "scientific_validity": False,
        },
        "interpretation": "Only internal file consistency and structural reconciliation have been checked.",
    }
    result["sha256"] = sha256(json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    return result
