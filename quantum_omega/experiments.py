"""Finite deterministic experiment design; proposals only, no execution adapter."""
from collections import Counter
from hashlib import sha256
import json
import math


def design_experiment(models, probes, budget, cost=1):
    if not models or len({m.id for m in models}) != len(models):
        raise ValueError('Distinct candidate models are required')
    if any(type(v) not in (int, float) or not math.isfinite(v) for v in (budget, cost)) or budget < 0 or cost <= 0:
        raise ValueError('Budget must be finite/nonnegative and cost finite/positive')
    if cost > budget:
        return None
    proposals = []
    for x in sorted(set(probes)):
        outcomes = Counter(str(model.predict(x)) for model in models)
        n = len(models)
        information_gain = -sum((count/n)*math.log2(count/n) for count in outcomes.values())
        if information_gain <= 0:
            continue
        proposals.append((information_gain, x, outcomes))
    if not proposals:
        return None
    information_gain, x, outcomes = max(proposals, key=lambda row: (row[0], -row[1]))
    identity = {'model_ids': sorted(m.id for m in models), 'x': str(x), 'cost': cost}
    return {'id': 'experiment-'+sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:16],
            **identity, 'expected_information_gain_bits': information_gain,
            'predicted_outcome_counts': dict(sorted(outcomes.items())),
            'assumptions': ['Uniform prior over supplied models', 'Deterministic noiseless predictions',
                            'Configured cost units; estimates are not laboratory costs'],
            'status': 'awaiting_human_review', 'executed': False,
            'scope': 'Synthetic dimensionless proposal; no hardware, network, or laboratory execution'}
