# Complete TGA audit-handoff verification

Recheck the original six-file study, saved audit bundle, sign-off declaration, evidence-reference manifest, local evidence bytes and saved consolidated report in one command:

```sh
python -m quantum_omega.gap_audit_handoff_check_cli --study-dir STUDY_DIR --bundle audit-bundle.json --signoff signoff.json --manifest evidence-refs.json --evidence-dir evidence/ --report audit-chain-report.json
```

All artifacts must remain outside the six-file study directory. The command returns a deterministic JSON summary on success and exits nonzero for changed study inputs, mismatched evidence bytes, malformed records or changed report fields.

`study_inputs_replayed: true` means the six submitted inputs were recomputed through the software pipeline, **not** that independent reviewers or registrations were authenticated. External authenticity and independent scientific validity remain explicitly false.
