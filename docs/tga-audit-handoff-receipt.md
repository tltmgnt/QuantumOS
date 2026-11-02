# Input-backed audit-handoff receipt

`build_audit_handoff_receipt(study_directory, bundle, signoff, manifest, evidence_directory, saved_report)` produces a deterministic, checksum-bound reviewer receipt after rechecking the complete six-file study and all local audit artifacts.

The receipt links the study verification, bundle, sign-off, evidence references and consolidated report; summarizes the number of checked local evidence files; and displays each category's **declared** evidence status.

`verify_audit_handoff_receipt(..., receipt)` recomputes the complete chain and rejects changed receipts or underlying inputs. Every category's `independently_authenticated` field is false; external authenticity and independent scientific validity are also false. This receipt is not a signature, trusted timestamp or scientific endorsement.
