"""Exact restricted algebra, counterexamples, and independent code-path checks."""
from fractions import Fraction
from .theory import PolynomialTheory


def direct_evaluate(model, x):
    """Different implementation from Horner; shared runtime is not independence."""
    return sum((c*x**k for k,c in enumerate(model.coefficients)), Fraction(0))


def derivative(model):
    return PolynomialTheory(tuple(k*c for k,c in enumerate(model.coefficients) if k) or (Fraction(0),))


def identity_certificate(left, right):
    """Coefficient normal-form equality is exact within Q[x] only."""
    size = max(len(left.coefficients), len(right.coefficients))
    residual = tuple((left.coefficients[i] if i < len(left.coefficients) else Fraction(0)) -
                     (right.coefficients[i] if i < len(right.coefficients) else Fraction(0))
                     for i in range(size))
    return {'domain': 'Q[x]', 'residual_coefficients': [str(c) for c in residual],
            'passed': all(c == 0 for c in residual)}


def validate(model, observations):
    counterexamples = []
    predictions = []
    consistent = True
    for x, y in observations:
        predicted = model.predict(x)
        consistent = consistent and predicted == direct_evaluate(model, x)
        predictions.append({'x': str(x), 'observed': str(y), 'predicted': str(predicted)})
        if predicted != y:
            counterexamples.append(predictions[-1])
    # Check the product-rule identity for x*p(x) in exact coefficient normal form.
    product_model = PolynomialTheory((Fraction(0),)+model.coefficients) if len(model.coefficients) < 4 else None
    product_rule = None
    if product_model is not None:
        coefficients = tuple((k+1)*c for k,c in enumerate(model.coefficients))
        product_rule = identity_certificate(derivative(product_model), PolynomialTheory(coefficients))
    return {'passed': consistent and not counterexamples,
            'evaluation_code_paths_agree': consistent, 'predictions': predictions,
            'counterexamples': counterexamples, 'product_rule_certificate': product_rule,
            'independently_verified': False,
            'scope': 'Exact algebra and supplied samples; no empirical or independent scientific validation'}


def counterfactuals(model, probes):
    results = []
    for index, coefficient in enumerate(model.coefficients):
        if coefficient == 0:
            continue
        coefficients = list(model.coefficients)
        coefficients[index] = Fraction(0)
        altered = PolynomialTheory(tuple(coefficients))
        results.append({'removed_coefficient': index,
                        'prediction_deltas': [{'x': str(x), 'delta': str(model.predict(x)-altered.predict(x))}
                                              for x in probes]})
    return results
