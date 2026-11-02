# Machine-readable independent-audit sign-off

`quantum_omega.gap_audit_signoff.create_audit_signoff(bundle, auditor=..., organization=..., reviewed_at=..., repository_commit=..., evidence_statuses=..., notes=...)` creates a deterministic, SHA-256-bound **self-declaration** linked to a structurally checked audit bundle. `verify_audit_signoff(bundle, record)` checks internal consistency and bundle binding.

All four evidence statuses must be explicitly supplied: `registration_authenticity`, `reviewer_independence`, `label_provenance`, and `scientific_validity`. Each accepts `unverified`, `verified`, or `rejected`. A `verified` value is **only the submitter's assertion**; this software does not independently substantiate it. Do not mark any category verified without documented external evidence.

Required auditor, organization, review timestamp, repository commit, and notes are self-reported strings. Both `identity_authenticated` and `digitally_signed` are always false. The record is **not** a cryptographic signature, trusted timestamp, proof of identity, or scientific endorsement. Preserve independent supporting evidence and authenticated sign-off separately.
