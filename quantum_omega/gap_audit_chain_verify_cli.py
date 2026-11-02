"""Verify a saved TGA audit-chain report against original local inputs."""
import argparse
import json
import sys
from pathlib import Path
from .gap_audit_chain_verify import verify_audit_chain_report

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ("bundle", "signoff", "manifest", "report"):
        parser.add_argument("--" + flag, type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        inputs = {
            name: json.loads(getattr(args, name).read_text(encoding="utf-8"))
            for name in ("bundle", "signoff", "manifest", "report")
        }
        result = verify_audit_chain_report(
            inputs["bundle"], inputs["signoff"], inputs["manifest"],
            args.evidence_dir, inputs["report"]
        )
        sys.stdout.write(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"Audit-chain report verification failed: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
