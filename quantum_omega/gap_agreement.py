"""Pairwise reviewer agreement on externally collected review-priority judgments.

No reviewer data is supplied or invented by this module.
"""
from collections import defaultdict
from itertools import combinations

def evaluate_reviewer_agreement(submissions):
    """Each submission has reviewer_id and a nonempty list of directed claim pairs.

    Agreement is computed only on overlapping unordered claim pairs.
    Missing overlaps are reported, not treated as agreement.
    """
    if not isinstance(submissions, list) or len(submissions) < 2:
        raise ValueError("At least two reviewer submissions required")
    reviewers = {}
    for entry in submissions:
        if not isinstance(entry, dict) or set(entry) != {"reviewer_id", "pairs"}:
            raise ValueError("Invalid reviewer submission")
        rid, pairs = entry["reviewer_id"], entry["pairs"]
        if not isinstance(rid, str) or not rid.strip() or rid in reviewers:
            raise ValueError("Reviewer IDs must be unique")
        if not isinstance(pairs, list) or not pairs:
            raise ValueError("Reviewer judgments must be nonempty")
        decisions = {}
        for pair in pairs:
            if not isinstance(pair, dict) or set(pair) != {"higher_priority", "lower_priority"}:
                raise ValueError("Invalid pairwise judgment")
            high, low = pair["higher_priority"], pair["lower_priority"]
            if not isinstance(high, str) or not isinstance(low, str) or not high or not low or high == low:
                raise ValueError("Invalid claim identifiers")
            key = tuple(sorted((high, low)))
            if key in decisions:
                raise ValueError("Duplicate or contradictory pair within reviewer")
            decisions[key] = high
        reviewers[rid] = decisions
    comparisons = []
    for left, right in combinations(sorted(reviewers), 2):
        common = sorted(set(reviewers[left]) & set(reviewers[right]))
        matches = sum(reviewers[left][pair] == reviewers[right][pair] for pair in common)
        comparisons.append({
            "reviewers": [left, right],
            "overlapping_pairs": len(common),
            "agreeing_pairs": matches,
            "agreement_rate": matches / len(common) if common else None,
        })
    total = sum(row["overlapping_pairs"] for row in comparisons)
    matched = sum(row["agreeing_pairs"] for row in comparisons)
    return {
        "schema_version": 1,
        "kind": "pairwise_reviewer_agreement",
        "reviewer_count": len(reviewers),
        "reviewer_comparisons": comparisons,
        "total_pairwise_overlaps": total,
        "pooled_agreement_rate": matched / total if total else None,
        "independence_verified": False,
        "note": "Descriptive overlap agreement only; repeated pairs across reviewer comparisons are not independent observations.",
    }
