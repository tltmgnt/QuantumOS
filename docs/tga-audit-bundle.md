# Cross-linked TGA study audit bundle

Call `quantum_omega.gap_audit_bundle.build_audit_bundle(study_directory)` to produce a deterministic JSON-compatible object containing the exact-byte SHA-256 inventory, the conservative independent-study review summary, and their shared evaluation SHA-256. The bundle itself has a canonical JSON SHA-256 digest.

Call `verify_audit_bundle(study_directory, bundle)` to validate the original six-file study package and compare it with the saved bundle. Keep the bundle outside the strict six-file input directory.

The audit bundle is useful for exchanging and checking research software outputs. Its checksum is **not** a digital signature or trusted timestamp, and does not authenticate reviewer identities, independent preregistration, or scientific validity.
