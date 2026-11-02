# Audit metadata adversarial checks and trust boundary

Run:

```sh
python -m unittest tests.test_gap_audit_metadata_adversarial -v
```

The suite starts with the complete synthetic reviewer handoff and tests changes to auditor identity, declared scientific status, evidence locator, and referenced SHA-256. Even when the portable file inventory is rebuilt, **partial metadata tampering must fail** because the audit chain no longer agrees.

## Critical limitation: self-declared chains can be regenerated

The suite also intentionally reconstructs the sign-off, reference manifest, report, receipt, and portable inventory after changing the self-declared auditor. The chain remains internally consistent and can pass software verification, while the output still explicitly states `external_authenticity_verified: false`, `identity_authenticated: false`, and `digitally_signed: false`.

**This is expected, not a bypass of a claimed identity-authentication feature.** SHA-256 proves content consistency, not who created a declaration or whether it is truthful. Reviewers must independently authenticate identity, external registrations, evidence provenance, and scientific claims. For authenticated provenance, a separate cryptographic signature or trusted external attestation workflow would be required.
