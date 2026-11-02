import subprocess
import unittest
from unittest.mock import patch

from quantum_omega.gap_v1_release_candidate import run_release_candidate_checks

class V1ReleaseCandidateTests(unittest.TestCase):
    def test_clean_successful_run_is_only_software_ready(self):
        def fake_run(command, **kwargs):
            if command[:2] == ["git", "rev-parse"]:
                return subprocess.CompletedProcess(command, 0, "a" * 40 + "\n", "")
            if command[:2] == ["git", "status"]:
                return subprocess.CompletedProcess(command, 0, "", "")
            return subprocess.CompletedProcess(command, 0, "", "Ran 10 tests in 0.1s\n\nOK\n")
        with patch("quantum_omega.gap_v1_release_candidate.subprocess.run", side_effect=fake_run):
            result = run_release_candidate_checks()
        self.assertTrue(result["software_release_candidate_ready"])
        self.assertFalse(result["ci_exact_commit_verified_externally"])
        self.assertFalse(result["scientific_validity_independently_verified"])

    def test_dirty_tree_is_not_ready(self):
        def fake_run(command, **kwargs):
            if command[:2] == ["git", "rev-parse"]:
                return subprocess.CompletedProcess(command, 0, "a" * 40, "")
            if command[:2] == ["git", "status"]:
                return subprocess.CompletedProcess(command, 0, " M README.md\n", "")
            return subprocess.CompletedProcess(command, 0, "", "OK")
        with patch("quantum_omega.gap_v1_release_candidate.subprocess.run", side_effect=fake_run):
            result = run_release_candidate_checks()
        self.assertFalse(result["software_release_candidate_ready"])

    def test_skipped_acceptance_suite_is_not_ready(self):
        def fake_run(command, **kwargs):
            if command[:2] == ["git", "rev-parse"]:
                return subprocess.CompletedProcess(command, 0, "a" * 40, "")
            if command[:2] == ["git", "status"]:
                return subprocess.CompletedProcess(command, 0, "", "")
            return subprocess.CompletedProcess(command, 0, "", "OK (skipped=2)")
        with patch("quantum_omega.gap_v1_release_candidate.subprocess.run", side_effect=fake_run):
            result = run_release_candidate_checks()
        self.assertFalse(result["software_release_candidate_ready"])
        self.assertTrue(result["acceptance_tests_skipped"])

    def test_failing_acceptance_suite_is_not_ready(self):
        def fake_run(command, **kwargs):
            if command[:2] == ["git", "rev-parse"]:
                return subprocess.CompletedProcess(command, 0, "a" * 40, "")
            if command[:2] == ["git", "status"]:
                return subprocess.CompletedProcess(command, 0, "", "")
            return subprocess.CompletedProcess(command, 1, "", "FAILED")
        with patch("quantum_omega.gap_v1_release_candidate.subprocess.run", side_effect=fake_run):
            result = run_release_candidate_checks()
        self.assertFalse(result["software_release_candidate_ready"])
