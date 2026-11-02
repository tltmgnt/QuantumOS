"""Run v1 software acceptance gates and emit a machine-readable candidate report.

This is a local software check, not a scientific or independent security audit.
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_TEST_MODULES = (
    "tests.test_gap_v1_end_to_end_acceptance",
    "tests.test_gap_v1_reproducibility_security",
    "tests.test_gap_v1_release_guide",
)

def run_release_candidate_checks(*, repository=".", python_executable=None):
    root = Path(repository).resolve()
    executable = python_executable or sys.executable
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root,
        capture_output=True, text=True, timeout=30, check=True
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=root,
        capture_output=True, text=True, timeout=30, check=True
    ).stdout
    tests = subprocess.run(
        [executable, "-m", "unittest", *_TEST_MODULES, "-v"],
        cwd=root, capture_output=True, text=True, timeout=180
    )
    # unittest returns success for skipped tests; ensure cryptography is
    # installed and that no acceptance suite was silently skipped.
    output = tests.stdout + tests.stderr
    skipped = "skipped=" in output or " (skipped" in output or "skipped '" in output
    return {
        "schema_version": 1,
        "kind": "tga_v1_release_candidate_software_report",
        "repository_commit": commit,
        "working_tree_clean": not bool(status.strip()),
        "acceptance_tests_passed": tests.returncode == 0 and not skipped,
        "acceptance_tests_skipped": skipped,
        "test_command": [executable, "-m", "unittest", *_TEST_MODULES, "-v"],
        "test_output": output[-16000:],
        "ci_exact_commit_verified_externally": False,
        "independent_security_audit_completed": False,
        "reviewer_identity_authenticated": False,
        "scientific_validity_independently_verified": False,
        "software_release_candidate_ready": (
            not bool(status.strip()) and tests.returncode == 0 and not skipped
        ),
    }

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default=".")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        result = run_release_candidate_checks(repository=args.repository)
        payload = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
        if args.output is not None:
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(payload)
        print(payload, end="")
        return 0 if result["software_release_candidate_ready"] else 1
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"Release candidate validation failed: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
