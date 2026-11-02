# Local evidence-byte verification

`verify_local_evidence_files(bundle, signoff, manifest, evidence_directory)` validates the audit bundle, sign-off, and evidence-reference manifest, then reads each referenced local file and compares its SHA-256 against the declared digest.

Locators must be relative paths under the evidence directory; absolute paths, parent traversal, and symlinks are rejected. Missing files, nonregular files, and digest mismatches fail closed. The result reports the number of checked references and always sets `external_authenticity_verified` to false.

This verifies **local byte agreement only**. If both the file and the self-reported digest are replaced, the check can still pass. Use a separately authenticated source or trusted digest channel to establish origin. An empty manifest produces zero checked references and does not establish evidence completeness.
