"""Recheck the original six-file study and its complete saved local audit chain."""
import hashlib
import json

from .gap_audit_bundle import verify_audit_bundle
from .gap_audit_chain_verify import verify_audit_chain_report

def verify_complete_audit_handoff(study_directory, bundle, signoff, manifest, evidence_directory, saved_report):
    verify_audit_bundle(study_directory, bundle)
    result = verify_audit_chain_report(bundle, signoff, manifest, evidence_directory, saved_report)
    handoff = {
        "schema_version": 1,
        "kind": "tga_complete_audit_handoff_check",
        "study_inputs_replayed": True,
        "audit_bundle_matches_study_inputs": True,
        "audit_chain_report_matches_inputs": result["audit_chain_report_matches_inputs"],
        "checked_reference_count": result["checked_reference_count"],
        "audit_bundle_sha256": bundle["sha256"],
        "signoff_sha256": signoff["sha256"],
        "evidence_references_sha256": manifest["sha256"],
        "audit_chain_report_sha256": saved_report["sha256"],
        "external_authenticity_verified": False,
        "scientific_validity_independently_verified": False,
    }
    handoff["sha256"] = hashlib.sha256(
        json.dumps(handoff, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()
    return handoff
