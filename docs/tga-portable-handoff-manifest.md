# Portable audit-handoff inventory

Use `build_portable_handoff_manifest(directory)` to create a deterministic checksum inventory for a fixed-layout handoff directory:

```text
handoff/
  study/
    protocol.json
    priority.json
    evidence.json
    labels.json
    reviewers.json
    study.json
  evidence/
    ... referenced local evidence files ...
  bundle.json
  signoff.json
  manifest.json
  report.json
  receipt.json
```

The function rejects unexpected top-level files, missing study inputs, symlinks, nonregular files and special entries. It records each file's relative path, exact byte count and SHA-256 digest. Store the resulting inventory **outside** `handoff/` so it does not recursively inventory itself.

`verify_portable_handoff_manifest(directory, manifest)` recomputes every digest and checks the saved inventory. This is a **byte-level portability check only**. It does not replay the audit chain or independently authenticate the records. For substantive local replay, run `gap_audit_handoff_receipt_cli verify` on the handoff inputs.
