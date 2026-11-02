"""Recompute a saved TGA audit-chain report from its original local inputs."""
from .gap_audit_chain_report import build_audit_chain_report

def verify_audit_chain_report(bundle, signoff, manifest, evidence_directory, saved_report):
    if not isinstance(saved_report, dict):
        raise ValueError("Saved audit-chain report must be a JSON object")
    expected = build_audit_chain_report(bundle, signoff, manifest, evidence_directory)
    if saved_report != expected:
        raise ValueError("Saved audit-chain report differs from recomputed inputs")
    return {
        "audit_chain_report_matches_inputs": True,
        "checked_reference_count": expected["checked_reference_count"],
        "external_authenticity_verified": False,
        "scientific_validity_independently_verified": False,
    }
