# TGA audit-bundle CLI

Export a deterministic bundle from a validated six-file study package:

```sh
python -m quantum_omega.gap_audit_bundle_cli export /path/to/study --output /path/to/audit-bundle.json
```

Verify the original files and bundle later:

```sh
python -m quantum_omega.gap_audit_bundle_cli verify /path/to/study --bundle /path/to/audit-bundle.json
```

Store the bundle outside the six-file input directory. Export is create-only; verify returns a nonzero exit code if any study input or bundle field has changed.

The bundle cross-links file hashes, reviewer-quality summary and the evaluation checksum. It is not a digital signature, trusted timestamp, or independent scientific validation.
