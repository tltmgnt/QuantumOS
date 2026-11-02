"""Exact small-matrix quantum constraints over Q(i), not physical validation."""
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, permutations
from .theory import rational

MAX_DIMENSION = 4


@dataclass(frozen=True)
class GaussianRational:
    real: Fraction = Fraction(0)
    imag: Fraction = Fraction(0)

    def __post_init__(self):
        if not isinstance(self.real,Fraction) or not isinstance(self.imag,Fraction):
            raise ValueError('Gaussian rational components must be Fractions')

    def __add__(self, other):
        return GaussianRational(self.real+other.real, self.imag+other.imag)

    def __neg__(self):
        return GaussianRational(-self.real, -self.imag)

    def __mul__(self, other):
        return GaussianRational(self.real*other.real-self.imag*other.imag,
                                self.real*other.imag+self.imag*other.real)

    def conjugate(self):
        return GaussianRational(self.real, -self.imag)

    def json(self):
        return {'real':str(self.real), 'imag':str(self.imag)}


ZERO = GaussianRational()
ONE = GaussianRational(Fraction(1))


def parse_matrix(value):
    if not isinstance(value, list) or not 1 <= len(value) <= MAX_DIMENSION:
        raise ValueError('Matrix dimension must be from 1 through 4')
    size = len(value)
    result = []
    for row in value:
        if not isinstance(row, list) or len(row) != size:
            raise ValueError('Matrix must be square')
        parsed = []
        for entry in row:
            if isinstance(entry, list):
                if len(entry) != 2:
                    raise ValueError('Complex entries require [real, imag]')
                parsed.append(GaussianRational(rational(entry[0]), rational(entry[1])))
            else:
                parsed.append(GaussianRational(rational(entry)))
        result.append(tuple(parsed))
    return tuple(result)


def _check_parsed_matrix(matrix):
    if not isinstance(matrix,(tuple,list)) or not 1 <= len(matrix) <= MAX_DIMENSION:
        raise ValueError('Parsed matrix dimension must be from 1 through 4')
    if any(not isinstance(row,(tuple,list)) or len(row) != len(matrix) or
           any(not isinstance(entry,GaussianRational) for entry in row) for row in matrix):
        raise ValueError('Expected a square parsed Gaussian-rational matrix')


def determinant(matrix):
    """Exact Leibniz determinant; dimension is explicitly bounded at four."""
    _check_parsed_matrix(matrix)
    size = len(matrix)
    total = ZERO
    for permutation in permutations(range(size)):
        product = ONE
        for index, column in enumerate(permutation):
            product = product*matrix[index][column]
        inversions = sum(permutation[i] > permutation[j] for i in range(size) for j in range(i+1,size))
        total = total + (-product if inversions % 2 else product)
    return total


def validate_density(matrix):
    _check_parsed_matrix(matrix)
    size = len(matrix)
    hermitian = all(matrix[i][j] == matrix[j][i].conjugate()
                    for i in range(size) for j in range(size))
    trace = sum((matrix[i][i] for i in range(size)),ZERO)
    minors = []
    if hermitian:
        for count in range(1,size+1):
            for indices in combinations(range(size),count):
                minor = determinant(tuple(tuple(matrix[i][j] for j in indices) for i in indices))
                minors.append({'indices':list(indices), 'determinant':minor.json(),
                               'nonnegative_real':minor.imag == 0 and minor.real >= 0})
    positive = all(row['nonnegative_real'] for row in minors) if hermitian else None
    return {'kind':'density_matrix', 'dimension':size, 'hermitian':hermitian,
            'trace':trace.json(), 'trace_one':trace == ONE,
            'positive_semidefinite':positive, 'principal_minors':minors,
            'passed':hermitian and trace == ONE and positive is True,
            'method':'Hermitian check, exact trace, and all principal minors nonnegative',
            'scope':'Finite matrix constraints over exact Gaussian rationals Q(i)'}


def validate_unitary(matrix):
    _check_parsed_matrix(matrix)
    size = len(matrix)
    product = tuple(tuple(sum((matrix[k][i].conjugate()*matrix[k][j]
                              for k in range(size)),ZERO) for j in range(size)) for i in range(size))
    residual = tuple(tuple(product[i][j] + (-ONE if i == j else ZERO)
                           for j in range(size)) for i in range(size))
    return {'kind':'unitary_operator', 'dimension':size,
            'u_dagger_u_minus_identity':[[entry.json() for entry in row] for row in residual],
            'passed':all(entry == ZERO for row in residual for entry in row),
            'method':'Exact U-dagger U minus identity',
            'scope':'Finite square matrix constraints over exact Gaussian rationals Q(i)'}


def validate_bundle(bundle):
    if not isinstance(bundle, dict) or set(bundle) != {'schema_version','records'}:
        raise ValueError('Quantum bundle requires schema_version and records')
    if type(bundle['schema_version']) is not int or bundle['schema_version'] != 1:
        raise ValueError('Unsupported quantum bundle schema version')
    records = bundle['records']
    if not isinstance(records,list) or not 1 <= len(records) <= 32:
        raise ValueError('A bundle requires 1–32 records')
    seen, results = set(), []
    for record in records:
        if not isinstance(record,dict) or set(record) != {'id','kind','matrix','sources'}:
            raise ValueError('Record fields must be id, kind, matrix, sources')
        identifier = record['id']
        if not isinstance(identifier,str) or not identifier.strip() or len(identifier) > 128 or identifier in seen:
            raise ValueError('Record IDs must be nonempty, unique, and at most 128 characters')
        seen.add(identifier)
        if not isinstance(record['sources'],list) or not record['sources'] or any(
                not isinstance(s,str) or not s.strip() for s in record['sources']):
            raise ValueError('Record source references are required')
        if record['kind'] not in ('density_matrix','unitary_operator'):
            raise ValueError('Unknown quantum constraint kind')
        matrix = parse_matrix(record['matrix'])
        checker = validate_density if record['kind'] == 'density_matrix' else validate_unitary
        results.append({'id':identifier, 'source_references':record['sources'], **checker(matrix)})
    return {'schema_version':1, 'records':results, 'all_passed':all(row['passed'] for row in results),
            'independent_scientific_verification':False, 'empirical_support':False,
            'scope':'Small finite matrix consistency only; no claim of quantum-gravity validity'}


def run_validation(bundle, output):
    from .artifacts import RunArtifacts
    from hashlib import sha256
    from pathlib import Path
    import sys
    from .memory import ScientificMemory
    checks = validate_bundle(bundle)
    artifacts = RunArtifacts(output)
    try:
        input_artifact = artifacts.write('input.json',bundle)
        checks_artifact = artifacts.write('checks.json',checks)
        with ScientificMemory(artifacts.directory/'memory.sqlite3') as memory:
            memory.ingest({'schema_version':1,'sources':[
                {'id':artifact['path'], 'title':artifact['path'], 'locator':'local:'+artifact['path'],
                 'kind':'derivation','domains':['mathematics','quantum'], 'content_sha256':artifact['sha256']}
                for artifact in (input_artifact,checks_artifact)],
                'claims':[{'id':row['id'],'text':'Submitted matrix satisfies '+row['kind']+' constraints',
                           'sources':['input.json','checks.json'],'status':'Conjectured'} for row in checks['records']],
                'relations':[]})
            for row in checks['records']:
                if not row['passed']:
                    memory.reject(row['id'],'Exact finite quantum matrix constraint failed','checks.json')
            memory.verify()
        report = {'schema_version':1,'validation_type':'finite_quantum_matrices',
                  'all_passed':checks['all_passed'], 'record_count':len(checks['records']),
                  'python':sys.version,
                  'source_file_sha256':{p.name:sha256(p.read_bytes()).hexdigest()
                                        for p in sorted(Path(__file__).parent.glob('*.py'))},
                  'passed_count':sum(row['passed'] for row in checks['records']),
                  'highest_discovery_stage':0, 'scientific_discovery':False,
                  'independent_scientific_verification':False, 'empirical_support':False,
                  'limitations':['Only dimensions 1–4 with exact rational real/imaginary entries',
                                 'Source references are supplied, not retrieved or authenticated',
                                 'Passing a finite matrix check does not validate a physical theory']}
        artifacts.write('report.json',report)
        artifacts.finalize()
        return report
    except Exception as error:
        artifacts.write('FAILED.json',{'error_type':type(error).__name__,'message':str(error)})
        raise
