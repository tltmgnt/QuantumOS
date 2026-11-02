"""Train/holdout protocol. Public fixtures are not genuinely blind research."""
from hashlib import sha256
import json
from .theory import complexity
from .verification import direct_evaluate


def evaluate_holdout(models, holdout):
    if not holdout:
        raise ValueError('Holdout observations are required')
    results = []
    for model in models:
        predicted = [direct_evaluate(model, x) for x,y in holdout]
        results.append({'theory_id': model.id,
                        'passed': all(p == y for p,(x,y) in zip(predicted,holdout)),
                        'correct': sum(p == y for p,(x,y) in zip(predicted,holdout)),
                        'count': len(holdout), 'predictions': [str(p) for p in predicted]})
    return results


def freeze_ranking(models):
    ranked = tuple(sorted(models, key=complexity))
    frozen = [model.id for model in ranked]
    return {'frozen_ranking': frozen,
            'ranking_commitment_sha256': sha256(json.dumps(frozen, separators=(',', ':')).encode()).hexdigest()}


def freeze_and_evaluate(models, holdout):
    """Freeze ranking before exposing results; do not refit on the holdout."""
    ranked = tuple(sorted(models, key=complexity))
    frozen = [model.id for model in ranked]
    commitment = freeze_ranking(ranked)['ranking_commitment_sha256']
    evaluations = evaluate_holdout(ranked, holdout)
    return {'frozen_ranking': frozen, 'ranking_commitment_sha256': commitment,
            'pre_holdout_champion': frozen[0] if frozen else None,
            'champion_passed': evaluations[0]['passed'] if evaluations else False,
            'results': evaluations,
            'protocol': 'Ranking frozen before holdout evaluation; no model refit',
            'scientific_blindness': False,
            'limitations': ['Public synthetic fixture; not an externally withheld research problem',
                            'Independent code path shares runtime and author with discovery',
                            'Any later choice using these results is adaptive and needs fresh holdout data']}
