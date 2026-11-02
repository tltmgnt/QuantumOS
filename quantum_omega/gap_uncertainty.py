"""Descriptive Wilson intervals for observed reviewer agreement.

Intervals treat pairwise overlaps as Bernoulli trials; shared reviewers and
repeated items violate independence, so intervals are illustrative only.
"""
from math import sqrt
from statistics import NormalDist
from .gap_agreement import evaluate_reviewer_agreement

def wilson_interval(successes, trials, confidence=0.95):
    if type(successes) is not int or type(trials) is not int or trials < 1 or successes < 0 or successes > trials:
        raise ValueError("Expected 0 <= successes <= positive trials")
    if type(confidence) not in (int, float) or not 0 < confidence < 1:
        raise ValueError("Confidence must be strictly between zero and one")
    z = NormalDist().inv_cdf((1 + confidence) / 2)
    p = successes / trials
    denom = 1 + z * z / trials
    center = (p + z * z / (2 * trials)) / denom
    radius = z * sqrt((p * (1 - p) + z * z / (4 * trials)) / trials) / denom
    return [max(0.0, center - radius), min(1.0, center + radius)]

def agreement_with_uncertainty(submissions, confidence=0.95):
    result = evaluate_reviewer_agreement(submissions)
    comparisons = []
    for row in result["reviewer_comparisons"]:
        comparisons.append({**row, "illustrative_wilson_interval":
            wilson_interval(row["agreeing_pairs"], row["overlapping_pairs"], confidence)
            if row["overlapping_pairs"] else None})
    total = result["total_pairwise_overlaps"]
    agreed = sum(row["agreeing_pairs"] for row in comparisons)
    return {
        **result,
        "reviewer_comparisons": comparisons,
        "confidence_level": confidence,
        "illustrative_pooled_wilson_interval": wilson_interval(agreed, total, confidence) if total else None,
        "uncertainty_interpretation": "Descriptive binomial intervals only. Overlaps may share reviewers and claim pairs; do not interpret as valid independent-sample confidence intervals.",
        "independent_sample_assumption_verified": False,
    }
