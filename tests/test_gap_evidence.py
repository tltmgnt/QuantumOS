import hashlib
import unittest
from quantum_omega.gap_evidence import build_evidence_manifest, verify_evidence_manifest

PROTOCOL = {"kind": "preregistered_evaluation_protocol", "sha256": "a" * 64}
LABELS = b'{"pairs": []}'

class EvidenceManifestTests(unittest.TestCase):
    def setUp(self):
        self.manifest = build_evidence_manifest(PROTOCOL, registration_url="https://example.org/registration/1",
            registration_timestamp="2026-01-01T00:00:00Z", labels_sha256=hashlib.sha256(LABELS).hexdigest(),
            reviewer_ids=["reviewer-1"])

    def test_integrity_and_replay(self):
        self.assertEqual(self.manifest, build_evidence_manifest(PROTOCOL,
            registration_url="https://example.org/registration/1", registration_timestamp="2026-01-01T00:00:00Z",
            labels_sha256=hashlib.sha256(LABELS).hexdigest(), reviewer_ids=["reviewer-1"]))
        result = verify_evidence_manifest(self.manifest, PROTOCOL, LABELS)
        self.assertTrue(result["integrity_verified"])
        self.assertFalse(result["external_independence_verified"])

    def test_tampering(self):
        with self.assertRaises(ValueError):
            verify_evidence_manifest({**self.manifest, "registration_url": "https://example.org/other"}, PROTOCOL, LABELS)

    def test_modified_labels(self):
        with self.assertRaises(ValueError):
            verify_evidence_manifest(self.manifest, PROTOCOL, b"modified")

    def test_duplicate_reviewers(self):
        with self.assertRaises(ValueError):
            build_evidence_manifest(PROTOCOL, registration_url="https://example.org/r",
                registration_timestamp="2026-01-01", labels_sha256=hashlib.sha256(LABELS).hexdigest(),
                reviewer_ids=["a", "a"])
