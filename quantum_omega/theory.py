"""Bounded exact-rational polynomial theory factory; no arbitrary code execution."""
from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
from itertools import product

MAX_DEGREE = 3
MAX_CANDIDATES = 512


def rational(value):
    if type(value) not in (str, int):
        raise ValueError('Rationals must be integer values or fraction strings')
    if len(str(value)) > 64:
        raise ValueError('Rational literal too long')
    try:
        result = Fraction(value)
    except (ValueError, ZeroDivisionError) as error:
        raise ValueError('Invalid rational literal') from error
    if abs(result.numerator) > 10**12 or result.denominator > 10**12:
        raise ValueError('Rational exceeds research-task bounds')
    return result


@dataclass(frozen=True)
class PolynomialTheory:
    coefficients: tuple[Fraction, ...]

    def __post_init__(self):
        if not isinstance(self.coefficients, tuple) or not self.coefficients or len(self.coefficients) > MAX_DEGREE+1:
            raise ValueError('Polynomial degree outside supported bounds')
        if any(not isinstance(c, Fraction) for c in self.coefficients):
            raise ValueError('Coefficients must be exact Fractions')
        coefficients = self.coefficients
        while len(coefficients) > 1 and coefficients[-1] == 0:
            coefficients = coefficients[:-1]
        object.__setattr__(self, 'coefficients', coefficients)

    @property
    def id(self):
        encoded = ','.join(str(c) for c in self.coefficients)
        return 'theory-'+sha256(encoded.encode()).hexdigest()[:16]

    def predict(self, x):
        result = Fraction(0)
        for coefficient in reversed(self.coefficients):
            result = result*x + coefficient
        return result

    def record(self):
        return {
            'id': self.id, 'family': 'rational_polynomial',
            'coefficients_ascending': [str(c) for c in self.coefficients],
            'assumptions': ['Exact rational, dimensionless inputs and outputs',
                            'A deterministic polynomial in the configured finite search space'],
            'mathematical_model': 'y = sum(c[k] * x**k)',
            'falsification_condition': 'Any exact observed y differs from the model at the same x',
            'computational_representation': 'Horner evaluation with fractions.Fraction',
            'verification_scope': 'Restricted rational polynomial algebra, not a theorem about physical reality',
        }


def generate_theories(coefficient_values, max_degree):
    if type(max_degree) is not int or not 0 <= max_degree <= MAX_DEGREE:
        raise ValueError('max_degree must be an integer from 0 to 3')
    if not isinstance(coefficient_values, list) or not 1 <= len(coefficient_values) <= 32:
        raise ValueError('A nonempty coefficient grid is required')
    values = tuple(sorted(set(rational(c) for c in coefficient_values)))
    if len(values)**(max_degree+1) > MAX_CANDIDATES:
        raise ValueError('Candidate count exceeds bounded factory capacity')
    models = {m.id: m for cs in product(values, repeat=max_degree+1)
              for m in (PolynomialTheory(cs),)}
    return tuple(sorted(models.values(), key=complexity))


def complexity(model):
    return len(model.coefficients), sum(abs(c) for c in model.coefficients), model.id
