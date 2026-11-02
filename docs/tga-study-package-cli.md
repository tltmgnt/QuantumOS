# External study-package CLI

Validate a directory containing exactly `protocol.json`, `priority.json`, `evidence.json`, `labels.json`, `reviewers.json`, and `study.json`:

```sh
python -m quantum_omega.gap_study_package_cli /path/to/study-package --output /path/to/result.json
```

Omit `--output` to print JSON to stdout. An existing output file is never overwritten. Validation errors print to stderr and return exit code 1.

For a local **synthetic** demonstration:

```sh
python -m quantum_omega.gap_provenance_example /tmp/tga-package-demo
rm /tmp/tga-package-demo/evaluation.json
python -m quantum_omega.gap_study_package_cli /tmp/tga-package-demo
```

The demonstration's fictional registration and reviewers are not independent evidence. A successful exit establishes internal consistency only, not externally verified reviewer independence or registration chronology.
