"""Preserve reviewer disagreements and append separate, auditable adjudications."""
from collections import defaultdict
from hashlib import sha256
import json

def disagreement_report(submissions, adjudications=()):
    if not isinstance(submissions, list) or len(submissions) < 2:
        raise ValueError("At least two reviewer submissions required")
    votes = defaultdict(list)
    reviewer_ids = set()
    for entry in submissions:
        if not isinstance(entry, dict) or set(entry) != {"reviewer_id", "pairs"}:
            raise ValueError("Invalid reviewer submission")
        rid, pairs = entry["reviewer_id"], entry["pairs"]
        if not isinstance(rid, str) or not rid.strip() or rid in reviewer_ids or not isinstance(pairs, list) or not pairs:
            raise ValueError("Invalid or duplicate reviewer")
        reviewer_ids.add(rid)
        seen = set()
        for pair in pairs:
            if not isinstance(pair, dict) or set(pair) != {"higher_priority", "lower_priority"}:
                raise ValueError("Invalid judgment")
            high, low = pair["higher_priority"], pair["lower_priority"]
            if not isinstance(high, str) or not isinstance(low, str) or not high or not low or high == low:
                raise ValueError("Invalid claim identifiers")
            key = tuple(sorted((high, low)))
            if key in seen:
                raise ValueError("Repeated claim pair within reviewer")
            seen.add(key)
            votes[key].append({"reviewer_id": rid, "higher_priority": high})
    disputed = {}
    for key in sorted(votes):
        rows = sorted(votes[key], key=lambda row: row["reviewer_id"])
        if len({row["higher_priority"] for row in rows}) > 1:
            disputed[key] = rows
    if not isinstance(adjudications, (tuple, list)):
        raise ValueError("Invalid adjudications")
    decisions = {}
    for entry in adjudications:
        if not isinstance(entry, dict) or set(entry) != {"claim_a", "claim_b", "higher_priority", "adjudicator_id", "rationale"}:
            raise ValueError("Invalid adjudication")
        a, b = entry["claim_a"], entry["claim_b"]
        key = tuple(sorted((a, b))) if isinstance(a, str) and isinstance(b, str) else ()
        if key not in disputed or key in decisions or entry["higher_priority"] not in key:
            raise ValueError("Adjudication must address a unique disputed pair")
        if not isinstance(entry["adjudicator_id"], str) or not entry["adjudicator_id"].strip() or not isinstance(entry["rationale"], str) or not entry["rationale"].strip():
            raise ValueError("Adjudicator and rationale required")
        decisions[key] = {"higher_priority": entry["higher_priority"],
                          "adjudicator_id": entry["adjudicator_id"], "rationale": entry["rationale"]}
    rows = [{"claim_pair": list(key), "original_votes": disputed[key],
             "adjudication": decisions.get(key), "resolved": key in decisions} for key in sorted(disputed)]
    result = {"schema_version": 1, "kind": "reviewer_disagreement_audit",
              "disputed_pair_count": len(rows), "adjudicated_pair_count": len(decisions),
              "disagreements": rows, "adjudicator_independence_verified": False,
              "note": "Original votes are preserved; adjudications are separate and do not rewrite reviewer labels."}
    result["sha256"] = sha256(json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    return result
