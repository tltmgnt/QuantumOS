"""Produce a conservative, checksum-bound receipt for an input-backed TGA audit handoff."""
import hashlib
import json

from .gap_audit_handoff_check import verify_complete_audit_handoff

def build_audit_handoff_receipt(study_directory, bundle, signoff, manifest, evidence_directory, saved_report):
    verification = verify_complete_audit_handoff(
        study_directory, bundle, signoff, manifest, evidence_directory, saved_report
    )
    categories = {
        category: {
            "declared_status": signoff["evidence_statuses"][category],
            "checked_local_reference_count": len(manifest["references"][category]),
            "independently_authenticated": False,
        }
        for category in sorted(signoff["evidence_statuses"])
    }
    receipt = {
        "schema_version": 1,
        "kind": "tga_audit_handoff_receipt",
        "handoff_verification_sha256": verification["sha256"],
        "audit_bundle_sha256": bundle["sha256"],
        "signoff_sha256": signoff["sha256"],
        "evidence_references_sha256": manifest["sha256"],
        "audit_chain_report_sha256": saved_report["sha256"],
        "study_inputs_replayed": True,
        "checked_reference_count": verification["checked_reference_count"],
        "categories": categories,
        "external_authenticity_verified": False,
        "scientific_validity_independently_verified": False,
    }
    receipt["sha256"] = hashlib.sha256(
        json.dumps(receipt, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()
    return receipt

def verify_audit_handoff_receipt(study_directory, bundle, signoff, manifest, evidence_directory, saved_report, receipt):
    if not isinstance(receipt, dict):
        raise ValueError("Receipt must be a JSON object")
    expected = build_audit_handoff_receipt(
        study_directory, bundle, signoff, manifest, evidence_directory, saved_report
    )
    if receipt != expected:
        raise ValueError("Handoff receipt does not match recomputed inputs")
    return {
        "handoff_receipt_matches_inputs": True,
        "checked_reference_count": expected["checked_reference_count"],
        "external_authenticity_verified": False,
        "scientific_validity_independently_verified": False,
    }
