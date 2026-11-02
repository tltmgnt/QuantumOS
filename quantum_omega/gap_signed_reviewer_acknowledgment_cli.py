"""Verify a reviewer-signed acknowledgment with two independent key fingerprints."""
import argparse
import json
import sys
from pathlib import Path
from .gap_signed_reviewer_acknowledgment import verify_signed_reviewer_acknowledgment

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("handoff_dir", type=Path)
    for flag in ("package", "acknowledgment", "signature", "handoff-pinned-key", "reviewer-pinned-key"):
        p.add_argument("--" + flag, type=Path, required=True)
    p.add_argument("--handoff-expected-sha256", required=True)
    p.add_argument("--reviewer-expected-sha256", required=True)
    args = p.parse_args(argv)
    try:
        result = verify_signed_reviewer_acknowledgment(
            args.handoff_dir,
            json.loads(args.package.read_text(encoding="utf-8")),
            args.handoff_pinned_key, args.handoff_expected_sha256,
            json.loads(args.acknowledgment.read_text(encoding="utf-8")),
            json.loads(args.signature.read_text(encoding="utf-8")),
            args.reviewer_pinned_key, args.reviewer_expected_sha256
        )
        print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
    except (OSError, ValueError, TypeError, KeyError, RuntimeError) as exc:
        print(f"Signed reviewer acknowledgment verification failed: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
