"""Adversarial audit metadata tests, including the limits of self-declared claims."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from quantum_omega.gap_reviewer_quickstart_example import create_reviewer_quickstart_example
from quantum_omega.gap_portable_handoff_manifest import build_portable_handoff_manifest
from quantum_omega.gap_portable_handoff_verify import verify_portable_handoff
from quantum_omega.gap_audit_signoff import create_audit_signoff
from quantum_omega.gap_audit_evidence_refs import create_evidence_references
from quantum_omega.gap_audit_chain_report import build_audit_chain_report
from quantum_omega.gap_audit_handoff_receipt import build_audit_handoff_receipt

class AuditMetadataAdversarialTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "example"
        create_reviewer_quickstart_example(self.root)
        self.handoff = self.root / "handoff"

    def tearDown(self):
        self.tmp.cleanup()

    def load(self, name):
        return json.loads((self.handoff / (name + ".json")).read_text())

    def save(self, name, value):
        (self.handoff / (name + ".json")).write_text(json.dumps(value))

    def test_signoff_claim_changed_with_rebuilt_inventory_rejected(self):
        signoff = self.load("signoff")
        signoff["auditor"] = "Impersonated reviewer"
        self.save("signoff", signoff)
        with self.assertRaises(ValueError):
            verify_portable_handoff(self.handoff, build_portable_handoff_manifest(self.handoff))

    def test_signoff_status_changed_with_rebuilt_inventory_rejected(self):
        signoff = self.load("signoff")
        signoff["evidence_statuses"]["scientific_validity"] = "verified"
        self.save("signoff", signoff)
        with self.assertRaises(ValueError):
            verify_portable_handoff(self.handoff, build_portable_handoff_manifest(self.handoff))

    def test_reference_locator_changed_with_rebuilt_inventory_rejected(self):
        manifest = self.load("manifest")
        manifest["references"]["label_provenance"][0]["locator"] = "not-present.txt"
        self.save("manifest", manifest)
        with self.assertRaises(ValueError):
            verify_portable_handoff(self.handoff, build_portable_handoff_manifest(self.handoff))

    def test_reference_digest_changed_with_rebuilt_inventory_rejected(self):
        manifest = self.load("manifest")
        manifest["references"]["label_provenance"][0]["sha256"] = "0" * 64
        self.save("manifest", manifest)
        with self.assertRaises(ValueError):
            verify_portable_handoff(self.handoff, build_portable_handoff_manifest(self.handoff))

    def test_regenerated_self_declarations_remain_unauthenticated(self):
        # Deliberately demonstrates the trust boundary: anyone holding these
        # inputs can create a new internally consistent self-declared chain.
        bundle = self.load("bundle")
        previous = self.load("signoff")
        signoff = create_audit_signoff(
            bundle, auditor="Unverified alternate reviewer",
            organization=previous["organization"], reviewed_at=previous["reviewed_at"],
            repository_commit=previous["repository_commit"],
            evidence_statuses=previous["evidence_statuses"],
            notes="A newly self-declared record; identity is not authenticated.",
        )
        manifest = create_evidence_references(bundle, signoff, self.load("manifest")["references"])
        report = build_audit_chain_report(bundle, signoff, manifest, self.handoff / "evidence")
        receipt = build_audit_handoff_receipt(
            self.handoff / "study", bundle, signoff, manifest,
            self.handoff / "evidence", report,
        )
        for name, value in (("signoff", signoff), ("manifest", manifest), ("report", report), ("receipt", receipt)):
            self.save(name, value)
        inventory = build_portable_handoff_manifest(self.handoff)
        result = verify_portable_handoff(self.handoff, inventory)
        self.assertTrue(result["handoff_receipt_matches_inputs"])
        self.assertFalse(result["external_authenticity_verified"])
        self.assertFalse(result["scientific_validity_independently_verified"])
        self.assertFalse(signoff["identity_authenticated"])
        self.assertFalse(signoff["digitally_signed"])
