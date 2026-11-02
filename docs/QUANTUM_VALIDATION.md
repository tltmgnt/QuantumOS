# Exact finite quantum matrix constraints

This adapter checks small density matrices and unitary operators over Gaussian rationals Q(i). It validates mathematical input constraints only. It does not test quantum field theory, a proposed quantum-gravity bridge, physical realizability of an experiment, or empirical agreement.

## Run and inspect

```sh
python -m quantum_omega validate-quantum examples/quantum_constraints.json --output research-runs/quantum-demo
python -m quantum_omega verify-run research-runs/quantum-demo
```

Use a new output directory. Inspect checks.json for exact results and report.json for counts and limits. The example contains a complex pure state, Bell-state density matrix, and rational rotation. Existing outputs are never overwritten.

## Input schema

The JSON root requires exactly schema_version (integer 1) and records (1–32 entries). Each entry requires exactly id, kind, matrix, and sources. IDs must be nonempty, unique, and at most 128 characters. Sources must be a nonempty list of reference strings; those references are recorded in input.json without retrieval or authentication.

Kinds are density_matrix and unitary_operator. Matrices must be square with dimension 1–4. Entries are integers, fraction strings such as "1/2", or complex pairs such as ["1/2", "-1/3"]. A pair represents real and imaginary components. Approximate JSON floats, booleans, non-finite values, symbolic expressions, and unsupported dimensions are rejected. Input literal magnitudes and denominators are bounded by the shared rational parser. Irrational entries such as 1/sqrt(2) are not representable; do not substitute approximate floats.

## Exact methods

Density matrices require Hermiticity and trace exactly one. For a Hermitian matrix, positive semidefiniteness is checked using **all** principal minors, not merely diagonal entries or leading minors. Each minor determinant must be real and nonnegative. The method handles rank-deficient pure states without a positive-pivot assumption. If Hermiticity fails, the PSD field is null and the overall result fails.

Unitary operators are checked by computing U-dagger U minus identity exactly. Every complex residual must be zero. No floating-point tolerance is applied. A tiny exact violation is still a failure. Reports expose all checked minors or all unitary residuals. The bounded Leibniz determinant algorithm is appropriate only for these small matrices.

## Provenance and exit status

| Exit code | Meaning |
|---|---|
| 0 | Valid schema; every submitted constraint passed |
| 1 | Valid schema; at least one mathematical constraint failed; reports are saved |
| 2 | Malformed/unsupported input, existing output, or run/storage error |

The input and checks are fingerprinted sources in the same SQLite scientific ledger used elsewhere. Submitted validity claims enter D0 as Conjectured. Failed submissions are marked Rejected with checks.json as evidence. Passing submissions do not advance stages or become empirical facts. report.json includes runtime and code fingerprints; manifest.json tracks local artifacts. verify-run checks artifacts, source fingerprints, and the retained event chain. These are unsigned local integrity controls, not a substitute for independent review.

The quantum adapter is a separate command. The polynomial workflow does not claim its candidates satisfy quantum constraints merely because this adapter exists. Connecting physical theories to matrix representations, larger/symbolic backends, gravity limits, and independent scientific validation remains future work.
