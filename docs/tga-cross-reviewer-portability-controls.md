# Cross-reviewer signed handoff portability controls

The cross-reviewer tests simulate two reviewers with **separate, independently controlled pinned-key files** and the same separately confirmed expected public-key fingerprint. Both can replay the same portable receipt package and obtain the same verification result.

The suite also demonstrates that the receiving reviewer rejects:
- a different expected fingerprint;
- a self-consistent substitution of the recipient's pinned public key and stored checksum;
- a forged external-authenticity flag, even when the package's self-checksum is regenerated;
- missing local evidence files.

Run with the optional signing dependency:

```sh
python -m pip install cryptography
python -m unittest tests.test_gap_cross_reviewer_portability -v
```

**Boundary:** The synthetic setup supplies the same demo key to both test participants. This checks software behavior across distinct pin files, **not** that two real reviewers independently authenticated the fingerprint, signed an attestation, or confirmed scientific validity. Real reviewers must use separate authenticated channels and maintain their own custody records.
