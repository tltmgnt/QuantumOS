# Offline audit-bundle CLI

After exporting a study audit bundle, verify its internal structure and nested SHA-256 digests **without the original study files**:

```sh
python -m quantum_omega.gap_audit_bundle_cli verify-offline --bundle audit-bundle.json
```

Exit code 0 means the saved bundle is structurally consistent, not that the original study was replayed or independently authenticated. The full `verify PACKAGE --bundle audit-bundle.json` command still validates against the original six study files.

Unkeyed checksums are not signatures: a party able to replace the bundle can recompute its hashes. Compare the bundle checksum with a separately trusted record for stronger assurance.
