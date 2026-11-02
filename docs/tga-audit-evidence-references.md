# External audit evidence-reference manifest

`create_evidence_references(bundle, signoff, references)` produces a deterministic, checksum-bound manifest of evidence locators linked to an existing audit bundle and sign-off declaration. `verify_evidence_references(bundle, signoff, manifest)` checks consistency.

Supply a dictionary containing exactly four categories: `registration_authenticity`, `reviewer_independence`, `label_provenance`, and `scientific_validity`. Each value is a list of objects with `locator`, `description`, and lowercase 64-character `sha256` fields. Empty lists are allowed for unverified/rejected categories; self-declared `verified` categories must cite at least one reference.

The SHA-256 is a **self-reported digest of the external evidence**. This module does not fetch the locator, verify the bytes, authenticate the evidence source, validate reviewer identity, or independently confirm any status. Save externally authenticated evidence separately and report unsupported assertions as unverified.
