# Synthetic two-signer reviewer acknowledgment walkthrough

Generate a complete synthetic signed handoff, portable reviewer receipt package, self-declared reviewer acknowledgment, and detached reviewer signature:

```sh
python -m pip install cryptography
python -m quantum_omega.gap_signed_reviewer_ack_demo /tmp/tga-reviewer-ack-demo
```

The demo creates two **distinct, disposable** Ed25519 signing keys (handoff signer and acknowledgment signer), two local pinned-key records, a portable receipt package, and a reviewer acknowledgment signature. Neither private key is written to disk.

Verify using the CLI and the demo fingerprints:

```sh
python -m quantum_omega.gap_signed_reviewer_acknowledgment_cli /tmp/tga-reviewer-ack-demo/sender/handoff --package /tmp/tga-reviewer-ack-demo/reviewer-package.json --acknowledgment /tmp/tga-reviewer-ack-demo/reviewer-acknowledgment.json --signature /tmp/tga-reviewer-ack-demo/reviewer-acknowledgment-signature.json --handoff-pinned-key /tmp/tga-reviewer-ack-demo/DEMO-handoff-pin.json --handoff-expected-sha256 "$(cat /tmp/tga-reviewer-ack-demo/DEMO-handoff-fingerprint.txt)" --reviewer-pinned-key /tmp/tga-reviewer-ack-demo/DEMO-reviewer-pin.json --reviewer-expected-sha256 "$(cat /tmp/tga-reviewer-ack-demo/DEMO-reviewer-fingerprint.txt)"
```

**This is a software rehearsal only.** Both fingerprints and both pins are generated locally by the same demo, not independently authenticated. A real recipient must authenticate each signer's fingerprint out of band and investigate identity, reviewer independence, evidence provenance, and scientific validity separately.
