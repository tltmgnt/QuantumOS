# TGA-Ω synthetic evaluation walkthrough

This demonstration uses **synthetic** graph claims, synthetic labels, a placeholder registration URL, and a fictional reviewer ID. It is **not** a preregistered, blinded, expert-reviewed, or scientifically validated study.

From the repository root:

```bash
python -m quantum_omega.gap_example /tmp/tga-example
python -m quantum_omega.gap_cli \
  --protocol /tmp/tga-example/protocol.json \
  --report /tmp/tga-example/priority.json \
  --evidence /tmp/tga-example/evidence.json \
  --labels /tmp/tga-example/labels.json \
  --output /tmp/tga-example/cli-result.json
```

The two evaluation JSON files should match. Both commands refuse to overwrite existing outputs. The label-file SHA-256 is checked before evaluation. The reported scores measure agreement with a single toy pair, not real-world scientific utility.

For a real study, independently collect and review pairwise judgments, register a protocol with trustworthy external timestamps **before** viewing labels, preserve raw label bytes, and have independent reviewers verify chronology and provenance. The software does not automatically certify any of those conditions.
