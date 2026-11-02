from .core import Action, Claim, Ledger, Stage, select_action

def legacy_demo():
    ledger = Ledger()
    ledger.register(Claim("demo-001", "Illustrative hypothesis, not a verified physical claim", ("local:demo",)))
    ledger.advance("demo-001", Stage.CONJECTURE, "local:assumptions.md", "reviewer-a", "author-a")
    selected = select_action([
        Action("derive a falsifiable prediction", 3, 2, 2, 3, 2, 1),
        Action("repeat an uninformative simulation", 0.1, 0, 0.1, 0.1, 2, 1),
    ])
    print("Illustrative next action:", selected.name)
    print("Audit events:", len(ledger.events))
    print("No scientific discovery or empirical validation is asserted.")

def main():
    import argparse
    import json
    import sqlite3
    import sys
    from pathlib import Path
    if len(sys.argv) == 1:
        legacy_demo()
        return
    parser = argparse.ArgumentParser(description="QUANTUM-Ω local research workflow")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="Run a bounded exact-polynomial research task")
    run.add_argument("task", type=Path)
    run.add_argument("--output", type=Path, required=True)
    verify = sub.add_parser("verify-run", help="Verify run artifact checksums and database integrity")
    verify.add_argument("directory", type=Path)
    quantum = sub.add_parser("validate-quantum", help="Check exact finite density/unitary matrices")
    quantum.add_argument("bundle", type=Path)
    quantum.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "run":
            from .workflow import run_research
            result = run_research(json.loads(args.task.read_text()), args.output)
        elif args.command == "validate-quantum":
            from .quantum import run_validation
            result = run_validation(json.loads(args.bundle.read_text()), args.output)
        else:
            from .artifacts import verify_run
            result = verify_run(args.directory)
        print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
        if args.command == "validate-quantum" and not result['all_passed']:
            raise SystemExit(1)
    except (ValueError, KeyError, TypeError, OSError, sqlite3.Error) as error:
        parser.exit(2, f"Research workflow failed: {error}\n")


if __name__ == "__main__":
    main()
