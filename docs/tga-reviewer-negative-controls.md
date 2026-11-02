# Independent-reviewer negative controls

Run the adversarial portable-handoff checks with:

```sh
python -m unittest tests.test_gap_reviewer_negative_controls -v
```

The tests generate a **synthetic** complete handoff, confirm the unchanged baseline, then separately mutate every one of the six study inputs, every one of the five audit records, and local evidence. They also reject missing or extra evidence and an altered inventory.

Two stronger controls **rebuild the portable manifest after tampering** with a receipt or study label file. This distinguishes superficial byte consistency from the full audit-chain replay: a newly generated inventory cannot make an inconsistent study or receipt pass.

The negative controls demonstrate software detection of selected tampering scenarios, not the authenticity of a real registration, independence of reviewers, correctness of externally supplied labels, or scientific validity. Successful CI does not imply those claims have been independently established.
