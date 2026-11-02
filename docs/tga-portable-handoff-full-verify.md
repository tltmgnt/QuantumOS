# Verify a complete portable TGA audit handoff

Given a fixed-layout `handoff/` directory and an inventory file stored outside it, run:

```sh
python -m quantum_omega.gap_portable_handoff_verify_cli handoff/ --inventory handoff-inventory.json
```

The command first compares exact file paths, byte counts and SHA-256 digests against the portable manifest. It then reads the five audit artifacts and replays the original six-file study and the local evidence-backed receipt verification.

Any changed study input, missing or extra file, altered evidence, invalid report or receipt produces a nonzero exit code. The result is checksum-bound and reports both byte consistency and successful input-backed replay.

This verifies **internal software consistency**, not external registration authenticity, reviewer independence, digitally authenticated identity, or scientific validity.
