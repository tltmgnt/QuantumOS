# Consolidated local audit-chain report

`build_audit_chain_report(bundle, signoff, manifest, evidence_directory)` validates the saved audit bundle, sign-off declaration, evidence-reference manifest, and actual local evidence bytes. It returns a deterministic SHA-256-bound report with the number of checked references and per-category declared status and evidence count.

A report is only emitted if the complete local checksum chain passes. The result explicitly sets `external_authenticity_verified` and `scientific_validity_independently_verified` to false. The `declared_status` fields remain assertions, not independently adjudicated facts. The report does not authenticate an auditor, verify a registration registry, or validate scientific conclusions.
