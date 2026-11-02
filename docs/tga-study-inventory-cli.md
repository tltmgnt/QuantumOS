# Study-file inventory CLI

Generate a SHA-256 inventory of all six validated study input files:

```sh
python -m quantum_omega.gap_study_inventory_cli create /path/to/study --output /path/to/inventory.json
```

Verify later against the original package:

```sh
python -m quantum_omega.gap_study_inventory_cli verify /path/to/study --inventory /path/to/inventory.json
```

The inventory must be stored **outside** the six-file input directory. Creation never overwrites an existing inventory. Verification returns exit code 1 on missing or changed files, inconsistent evidence, or altered inventory content.

Checksums establish byte-for-byte consistency relative to the saved inventory. They cannot establish who supplied the data or whether preregistration was genuine.
