# End-to-end synthetic provenance-gated example

Generate fixture files:

```sh
python -m quantum_omega.gap_provenance_example /tmp/tga-full-demo
```

Replay through the CLI:

```sh
python -m quantum_omega.gap_provenance_cli \\
  --protocol /tmp/tga-full-demo/protocol.json \\
  --report /tmp/tga-full-demo/priority.json \\
  --evidence /tmp/tga-full-demo/evidence.json \\
  --labels /tmp/tga-full-demo/labels.json \\
  --reviewers /tmp/tga-full-demo/reviewers.json \\
  --study /tmp/tga-full-demo/study.json
```

The generated registration URL, timestamps, affiliations, reviewers and labels are **fictional test fixtures**. They do not represent preregistration, independent review, or empirical quantum-gravity evidence. The test asserts that CLI output exactly reproduces the generated report and that the evaluator does not claim reviewer independence.
