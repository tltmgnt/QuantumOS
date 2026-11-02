"""Reconcile frozen pairwise labels against original reviewer votes and adjudications."""
from collections import defaultdict

def reconcile_reviewer_labels(labels, reviewer_data):
    if not isinstance(labels, dict) or set(labels) != {"schema_version", "source_id", "pairs"} or type(labels["schema_version"]) is not int or labels["schema_version"] != 1:
        raise ValueError("Invalid frozen label schema")
    if not isinstance(reviewer_data, dict) or set(reviewer_data) != {"submissions", "adjudications"}:
        raise ValueError("Invalid reviewer data schema")
    votes = defaultdict(list)
    reviewers = set()
    submissions = reviewer_data["submissions"]
    if not isinstance(submissions, list) or len(submissions) < 2:
        raise ValueError("At least two reviewers required")
    for submission in submissions:
        if not isinstance(submission, dict) or set(submission) != {"reviewer_id", "pairs"}:
            raise ValueError("Invalid reviewer record")
        rid = submission["reviewer_id"]
        if not isinstance(rid, str) or not rid.strip() or rid in reviewers or not isinstance(submission["pairs"], list) or not submission["pairs"]:
            raise ValueError("Invalid or duplicate reviewer")
        reviewers.add(rid)
        seen = set()
        for pair in submission["pairs"]:
            key, higher = _parse_pair(pair)
            if key in seen:
                raise ValueError("Duplicate reviewer pair")
            seen.add(key)
            votes[key].append(higher)
    decisions = {}
    adjudications = reviewer_data["adjudications"]
    if not isinstance(adjudications, list):
        raise ValueError("Invalid adjudications")
    for decision in adjudications:
        if not isinstance(decision, dict) or set(decision) != {"claim_a", "claim_b", "higher_priority", "adjudicator_id", "rationale"}:
            raise ValueError("Invalid adjudication")
        a, b = decision["claim_a"], decision["claim_b"]
        if not isinstance(a, str) or not isinstance(b, str) or not a or not b or a == b:
            raise ValueError("Invalid adjudication claims")
        key = tuple(sorted((a, b)))
        if key in decisions or key not in votes or len(set(votes[key])) < 2 or decision["higher_priority"] not in key:
            raise ValueError("Adjudication must be unique and for a disputed reviewed pair")
        if not isinstance(decision["adjudicator_id"], str) or not decision["adjudicator_id"].strip() or not isinstance(decision["rationale"], str) or not decision["rationale"].strip():
            raise ValueError("Adjudication identity and rationale required")
        decisions[key] = decision["higher_priority"]
    label_pairs = {}
    if not isinstance(labels["pairs"], list) or not labels["pairs"]:
        raise ValueError("Frozen labels must be nonempty")
    for pair in labels["pairs"]:
        key, higher = _parse_pair(pair)
        if key in label_pairs:
            raise ValueError("Duplicate frozen label pair")
        label_pairs[key] = higher
    if set(label_pairs) != set(votes):
        raise ValueError("Frozen label pair coverage differs from reviewer submissions")
    resolved_by = {"unanimous": 0, "majority": 0, "adjudication": 0}
    for key, higher in label_pairs.items():
        counts = {candidate: votes[key].count(candidate) for candidate in key}
        if counts[key[0]] == counts[key[1]]:
            if decisions.get(key) != higher:
                raise ValueError("Tied reviewer votes require matching adjudication")
            resolved_by["adjudication"] += 1
        else:
            expected = max(key, key=lambda candidate: counts[candidate])
            if expected != higher:
                raise ValueError("Frozen label contradicts reviewer majority")
            resolved_by["unanimous" if min(counts.values()) == 0 else "majority"] += 1
            if key in decisions and decisions[key] != higher:
                raise ValueError("Adjudication contradicts frozen label")
    return {"schema_version": 1, "kind": "reviewer_label_reconciliation",
            "label_pair_count": len(label_pairs), "reviewer_count": len(reviewers),
            "resolved_by": resolved_by, "reviewer_label_alignment_verified": True,
            "external_reviewer_independence_verified": False,
            "note": "Structural alignment only; reviewer provenance and independence are not verified."}

def _parse_pair(pair):
    if not isinstance(pair, dict) or set(pair) != {"higher_priority", "lower_priority"}:
        raise ValueError("Invalid pair")
    high, low = pair["higher_priority"], pair["lower_priority"]
    if not isinstance(high, str) or not isinstance(low, str) or not high or not low or high == low:
        raise ValueError("Invalid claim IDs")
    return tuple(sorted((high, low))), high
