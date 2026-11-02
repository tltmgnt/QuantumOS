# Local audit evidence verification CLI

Check local evidence files against their declared SHA-256 digests:

```sh
python -m quantum_omega.gap_audit_local_evidence_cli --bundle audit-bundle.json --signoff signoff.json --manifest evidence-refs.json --evidence-dir evidence/
```

The command validates the bundle, sign-off, and manifest, then reads referenced regular files from `evidence/` and checks each digest. It returns nonzero on a mismatch, missing file, unsafe path, or malformed input. Successful output includes `checked_reference_count`; zero means no evidence files were checked.

**Limit:** This checks local byte agreement only. It does not authenticate who produced the files, establish trusted timestamps, or verify scientific conclusions.
