"""v1 reproducibility and fail-closed verification regression controls."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from quantum_omega.gap_signed_reviewer_ack_demo import create_signed_reviewer_ack_demo
from quantum_omega.gap_signed_reviewer_acknowledgment import verify_signed_reviewer_acknowledgment
from quantum_omega.gap_reviewer_evidence_index import _CATEGORIES, build_reviewer_evidence_index
from quantum_omega.gap_reviewer_evidence_files import verify_reviewer_evidence_files

try:
    import cryptography
except ImportError:
    cryptography = None

@unittest.skipUnless(cryptography is not None, "Optional cryptography dependency unavailable")
class V1ReproducibilitySecurityTests(unittest.TestCase):
    def test_independent_runs_verify_and_use_distinct_disposable_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            results = []
            for name in ("first", "second"):
                root = Path(tmp) / name
                result = create_signed_reviewer_ack_demo(root)
                self.assertTrue(result["reviewer_acknowledgment_signature_valid"])
                self.assertFalse(result["reviewer_real_world_identity_verified"])
                reviewer_fp = (root / "DEMO-reviewer-fingerprint.txt").read_text().strip()
                handoff_fp = (root / "DEMO-handoff-fingerprint.txt").read_text().strip()
                self.assertNotEqual(reviewer_fp, handoff_fp)
                self.assertEqual(len(reviewer_fp), 64)
                self.assertFalse(any("private-key" in str(path).lower() for path in root.rglob("*")))
                results.append((reviewer_fp, handoff_fp))
            self.assertNotEqual(results[0], results[1])

    def test_cli_rejects_wrong_reviewer_fingerprint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "demo"
            create_signed_reviewer_ack_demo(root)
            cmd = [
                sys.executable, "-m", "quantum_omega.gap_signed_reviewer_acknowledgment_cli",
                str(root / "sender" / "handoff"),
                "--package", str(root / "reviewer-package.json"),
                "--acknowledgment", str(root / "reviewer-acknowledgment.json"),
                "--signature", str(root / "reviewer-acknowledgment-signature.json"),
                "--handoff-pinned-key", str(root / "DEMO-handoff-pin.json"),
                "--handoff-expected-sha256", (root / "DEMO-handoff-fingerprint.txt").read_text().strip(),
                "--reviewer-pinned-key", str(root / "DEMO-reviewer-pin.json"),
                "--reviewer-expected-sha256", "0" * 64,
            ]
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            self.assertNotEqual(process.returncode, 0)

    def test_rehashed_forged_evidence_authenticity_claim_rejected(self):
        from quantum_omega.gap_reviewer_evidence_index import _digest
        ack = {"kind": "tga_reviewer_handoff_acknowledgment", "sha256": "a" * 64}
        evidence = {
            category: {"status": "unverified", "references": []}
            for category in _CATEGORIES
        }
        index = build_reviewer_evidence_index(ack, evidence)
        index["evidence_authenticity_verified"] = True
        index["sha256"] = _digest({k: v for k, v in index.items() if k != "sha256"})
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                verify_reviewer_evidence_files(ack, index, tmp)

    def test_empty_evidence_index_never_implies_external_authenticity(self):
        ack = {"kind": "tga_reviewer_handoff_acknowledgment", "sha256": "a" * 64}
        evidence = {
            category: {"status": "unverified", "references": []}
            for category in _CATEGORIES
        }
        index = build_reviewer_evidence_index(ack, evidence)
        with tempfile.TemporaryDirectory() as tmp:
            result = verify_reviewer_evidence_files(ack, index, tmp)
            self.assertEqual(result["checked_reference_count"], 0)
            self.assertFalse(result["evidence_authenticity_verified"])
            self.assertFalse(result["reviewer_identity_authenticated"])
