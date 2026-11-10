"""Offline curriculum answer key. Synthetic checks, never operational approval."""
import ast
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
for base in (ROOT, ROOT / "src", ROOT / "layer-b"):
    sys.path.insert(0, str(base))
CASES = []

def check(name, actual, expected):
    passed = actual == expected
    CASES.append({"case": name, "actual": actual, "expected": expected, "passed": passed})
    if not passed:
        raise AssertionError(f"{name}: expected {expected!r}, got {actual!r}")

def rejects(name, call, error=ValueError):
    try:
        call()
    except error:
        check(name, error.__name__, error.__name__)
    else:
        raise AssertionError(f"{name}: expected {error.__name__}")




def run():
    from quantum_omega import Claim, Ledger, Stage
    ledger = Ledger()
    claim = Claim("c","Synthetic conjecture",("fictional:source",))
    ledger.register(claim)
    rejects("no stage skipping", lambda: ledger.advance("c",Stage.EMPIRICALLY_SUPPORTED,"synthetic-artifact","reviewer","author"))
    check("failed transition appends no stage event", len(ledger.events), 1)
    rejects("no source-free claim", lambda: Claim("bad","No source",()))
    for stage in list(Stage)[1:5]:
        ledger.advance("c",stage,"synthetic-artifact","author","author")
    rejects("same normalized reviewer is not separate", lambda: ledger.advance("c",Stage.INDEPENDENTLY_VERIFIED,"synthetic-artifact"," AUTHOR ","author"))
    r = ledger.advance("c",Stage.INDEPENDENTLY_VERIFIED,"synthetic-artifact","reviewer","author")
    check("declared separate reviewer permits recorded stage", int(r.stage), int(Stage.INDEPENDENTLY_VERIFIED))
    check("stage advancement does not change epistemic label", r.status.value, claim.status.value)

if __name__ == "__main__":
    if sys.argv[1:] not in ([], ["--verify"]):
        raise SystemExit("Usage: python curriculum/lab.py [--verify]")
    run()
    report = {"schema_version": 1, "status": "PASS", "case_count": len(CASES),
              "cases": CASES, "scope": "Synthetic curriculum checks only"}
    if sys.argv[1:] == ["--verify"]:
        expected = json.loads((Path(__file__).parent / "expected.json").read_text())
        if report != expected:
            raise AssertionError("Observed answers differ from curriculum/expected.json")
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))
