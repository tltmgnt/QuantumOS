# Independent reviewer identity and signing-key custody checklist

This checklist supplements [signed reviewer acknowledgment verification](tga-signed-reviewer-acknowledgment.md) and [signature substitution controls](tga-reviewer-signature-substitution-controls.md). It is a **human process**: no software-generated checksum or signature automatically authenticates real-world identity, authorization, independence, chronology, or scientific conclusions.

## Before accepting a reviewer signature

- [ ] Establish the reviewer's legal or institutional identity using a separately authenticated channel (not an ID or name inside the acknowledgment).
- [ ] Verify the reviewer's authority to review or sign for the claimed institution; record the confirming contact and method outside the handoff.
- [ ] Check declared financial, professional, supervisory, authorship, and other conflicts against independently obtained records.
- [ ] Independently confirm that the reviewer is not the handoff signer or an undisclosed collaborator. Separate key pairs alone do **not** establish separate people.
- [ ] Obtain the reviewer's Ed25519 public-key fingerprint through a previously trusted, independently authenticated channel; record who confirmed it, when, and how.
- [ ] Confirm the handoff signer's key fingerprint **separately** from the reviewer's fingerprint; do not trust fingerprints delivered only in the same package as signatures.
- [ ] Pin each key in separately controlled local storage; protect the original out-of-band fingerprints against later package or pin substitution.
- [ ] Establish signing-key custody, authorized users, key rotation and revocation procedures; record any suspected compromise and reverify against trusted history.

## During verification

- [ ] Replay the original signed handoff and portable reviewer receipt against the handoff signer's pinned key and independently expected fingerprint.
- [ ] Replay the acknowledgment and verify its detached Ed25519 signature against the **reviewer's** separately pinned key and independently expected fingerprint.
- [ ] Confirm the signature's covered payload, acknowledgment checksum, and expected reviewer fingerprint; reject rewritten metadata and substituted keys.
- [ ] Record the exact input package SHA-256, reviewer acknowledgment SHA-256, relevant repository commit, tool version, and verification command.
- [ ] Preserve the independently authenticated custody record and verification log in access-controlled storage separate from the transfer package.
- [ ] Investigate provenance and scientific claims using primary records; successful cryptographic verification is not evidence of scientific validity.

## After verification

- [ ] Preserve any external reviewer identity, authorization, independence, and fingerprint-authentication evidence under a documented retention policy.
- [ ] Record disputes, key revocation, reviewer withdrawal, and updated conflict disclosures; rerun verification after any changes.
- [ ] Distinguish **software verified**, **externally authenticated**, **self-declared**, **unverified**, and **rejected** in any publication or audit report.

## Required reporting language

A successful CLI result means that a signed acknowledgment was verified against the *supplied* independently expected fingerprints and that the underlying handoff was replayed. The CLI **does not establish** whether those fingerprints were actually authenticated out of band, whether a named reviewer controls the key, whether the reviewer is independent, whether the claimed review date is genuine, or whether the underlying science is valid.

If identity or independence cannot be confirmed externally, report it as **unverified**, not as passed or verified. Never publish private signing keys, personal identity records, or confidential conflicts in public demonstration artifacts.
