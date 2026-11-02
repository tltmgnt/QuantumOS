"""Budgeted deterministic local action selection with explicit proxy scores."""
import math
from .core import Action


def plan(actions, budget, weights=(1.0,1.0,1.0)):
    if type(budget) not in (int,float) or not math.isfinite(budget) or budget < 0:
        raise ValueError('Planner budget must be finite and nonnegative')
    if not actions or len({a.name for a in actions}) != len(actions):
        raise ValueError('Distinct named actions are required')
    scores = {a.name:a.utility(weights) for a in actions}
    eligible = sorted((a for a in actions if a.cost <= budget), key=lambda a:(-scores[a.name],a.name))
    return {'selected_action': eligible[0].name if eligible else None,
            'budget': budget, 'scores': scores,
            'eligible_actions': [a.name for a in eligible],
            'cost': eligible[0].cost if eligible else 0,
            'score_interpretation': 'Configured utility proxies; not calibrated scientific information gain'}
