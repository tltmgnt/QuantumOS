# One-command independent reviewer verification

After authenticating the signer's expected public-key fingerprint **outside the handoff** and creating a trusted-key pin (see `docs/tga-signed-reviewer-checklist.md`), run:

```sh
python -m quantum_omega.gap_reviewer_verify_cli handoff/ --inventory handoff-inventory.json --signature handoff-signature.json --pinned-key trusted-key.json --expected-sha256 INDEPENDENTLY_CONFIRMED_SHA256
```

The command checks the independently supplied fingerprint against the local pinned public key, fully replays the portable study/audit handoff, and verifies the Ed25519 detached signature. Any mismatch exits nonzero. Its JSON output records successful software checks alongside explicit `false` flags for fingerprint-source authentication, real-world signer identity, external authenticity, and independently validated science.

For a **synthetic rehearsal**, first run `python -m quantum_omega.gap_signed_reviewer_demo /tmp/tga-signed-demo`, then pin its demo key and use the command above with the generated files. The demo key and fingerprint are not independent trust anchors. Real reviewers must authenticate the expected fingerprint through a separate channel, secure the pin file, and conduct independent identity and scientific review.
