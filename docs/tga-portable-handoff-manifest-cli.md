# Portable audit-handoff manifest CLI

Create an inventory of a fixed-layout handoff, storing the manifest **outside** the handoff directory:

```sh
python -m quantum_omega.gap_portable_handoff_manifest_cli create handoff/ --output handoff-inventory.json
```

Verify all saved relative paths, byte counts and SHA-256 digests against the current directory:

```sh
python -m quantum_omega.gap_portable_handoff_manifest_cli verify handoff/ --manifest handoff-inventory.json
```

Create mode rejects an existing output path and output paths inside the handoff tree. Verification exits nonzero for changed bytes, missing/extra files, symlinks or a changed inventory. This is a **byte-level check only**; the response sets `audit_chain_replayed: false` and never claims external authentication or scientific validation. Use the receipt verification CLI for input-backed audit replay.
