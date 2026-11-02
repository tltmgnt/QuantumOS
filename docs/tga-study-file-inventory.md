# Exact-file study inventory

Use `quantum_omega.gap_study_inventory.inventory_study_package(path)` to validate a six-file external-study package and produce a deterministic inventory. Each entry records the filename, byte length and SHA-256 of the original bytes. The inventory also binds to the provenance-gated evaluation digest.

Use `verify_study_inventory(path, inventory)` to detect changed inputs or a modified inventory. Both operations fail closed if package validation fails. Store the inventory outside the six-file input directory, because the package intake intentionally rejects extra files.

Cryptographic hashes detect content changes relative to a trusted inventory. They **do not** prove that the original files came from independent reviewers or that registration occurred at the claimed time.
