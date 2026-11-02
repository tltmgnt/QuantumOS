"""Consolidated, conservative report of the complete local TGA audit chain."""
import hashlib
import json

from .gap_audit_local_evidence import verify_local_evidence_files

def build_audit_chain_report(bundle, signoff, manifest, evidence_directory):
    local = verify_local_evidence_files(bundle, signoff, manifest, evidence_directory)
    categories = {}
    for category, status in sorted(signoff["evidence_statuses"].items()):
        references = manifest["references"][category]
        categories[category] = {
            "declared_status": status,
            "reference_count": len(references),
            "local_bytes_checked": len(references),
            "external_authenticity_verified": False,
        }
    report = {
        "schema_version": 1,
        "kind": "tga_audit_chain_report",
        "audit_bundle_sha256": bundle["sha256"],
        "signoff_sha256": signoff["sha256"],
        "evidence_references_sha256": manifest["sha256"],
        "local_evidence_bytes_match": local["local_evidence_bytes_match"],
        "checked_reference_count": local["checked_reference_count"],
        "categories": categories,
        "external_authenticity_verified": False,
        "scientific_validity_independently_verified": False,
    }
    report["sha256"] = hashlib.sha256(
        json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()
    return report
