# Exact declared reference limits

This adapter checks whether a supplied normalized observable recovers a declared scalar reference value in a one-parameter limit. It is a mathematical check of the expression provided by the submitter. It is not a derivation of a Newtonian or relativistic limit from field equations.

## Run

```sh
python -m quantum_omega validate-limits examples/classical_limits.json --output research-runs/limit-demo
python -m quantum_omega verify-run research-runs/limit-demo
```

Use a new output directory. The example ratios are synthetic dimensionless expressions, not physical theories or predictions. No experiment, network request, or arbitrary expression evaluation is performed.

## Supported model

The observable is a finite Laurent expression:

$$f(\epsilon)=b+\sum_{p=-8}^{8}c_p\epsilon^p.$$

Baseline b, declared reference, and coefficients are exact rational literals. The parameter is assumed dimensionless and strictly positive. Approaches are zero_positive or positive_infinity. No logs, exponentials, fractional powers, multiple parameters, symbolic coefficients, or general rational-function denominators are accepted. No dimensional consistency is inferred merely from the parameter label.

The root JSON requires exactly schema_version (integer 1) and records (1–32 records). Each record requires exactly id, parameter, approach, baseline, reference, corrections, and sources. IDs are unique; text fields are nonempty and at most 128 characters. Sources are a nonempty list of supplied references. Corrections contains at most 32 objects, each with integer power (-8 through 8, excluding booleans) and coefficient (integer or fraction string). Empty corrections are valid for a constant observable. Approximate floats, NaNs, and expression strings are rejected.

## Exact classification

Equal powers are combined and zero coefficients removed **before** classifying the limit. Thus cancelling singular terms do not cause a false divergence.

| Approach | Vanishing terms | Potential divergence |
|---|---|---|
| epsilon → 0+ | Positive powers | Negative powers; most negative nonzero power dominates |
| epsilon → +infinity | Negative powers | Positive powers; largest nonzero power dominates |

If there are no divergent terms, the finite limit is baseline plus the combined power-zero coefficient. The check passes only when that exact value equals the declared reference. If the limit diverges, the sign is determined by its dominant coefficient on the positive real axis. A very small exact offset still fails. Three rational samples illustrate behavior but never determine acceptance.

## Reports and governance

checks.json records normalized corrections, exact finite values or divergence, dominant powers, sample residuals, assumptions, and source references. Input and checks fingerprints are registered in the SQLite scientific ledger. Failed reference-limit claims are rejected with retained evidence. Passing submissions remain D0 Conjectured and never acquire empirical or independent verification status. report.json includes source-code/runtime fingerprints and explicit limitations; verify-run checks the manifest, local source fingerprints, and retained event history.

CLI exit codes match quantum validation: 0 for all passing checks; 1 for well-formed mathematical failures with reports saved; 2 for malformed/unsupported input, storage errors, or an existing output directory. Invalid schemas are rejected before creating output. Existing outputs are preserved.

Recovering an assumed normalized scalar limit does not prove the full GR field equations, physical dimensions, stability, causality, conservation, or empirical adequacy. Higher-dimensional and tensorial limits, independent derivations, experimental constraints, and scientific review remain pending.
