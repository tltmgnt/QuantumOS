# Offline audit-bundle checksum checks

`quantum_omega.gap_audit_offline.verify_bundle_offline(bundle)` checks a saved audit bundle's canonical SHA-256 digests, nested record structure, six-file inventory, matching evaluation references, and conservative external-verification flags. It works without access to the original study directory.

**Important limitation:** offline checks do not replay or validate the original six input files. A party able to rewrite the bundle can recompute unkeyed SHA-256 digests. For meaningful integrity assurance, compare against a digest retained through an independently trusted channel; use the full `verify_audit_bundle(directory, bundle)` when original inputs are available. Neither method establishes reviewer independence or scientific validity.
