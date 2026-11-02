"""Exact one-parameter Laurent limits; no inference of gravitational validity."""
from fractions import Fraction
from .theory import rational


def _text(value, label):
    if not isinstance(value,str) or not value.strip() or len(value) > 128:
        raise ValueError(label+' must be nonempty text of at most 128 characters')
    return value


def validate_record(record):
    fields={'id','parameter','approach','baseline','reference','corrections','sources'}
    if not isinstance(record,dict) or set(record) != fields:
        raise ValueError('Limit record fields must be exactly: '+', '.join(sorted(fields)))
    identifier=_text(record['id'],'ID')
    parameter=_text(record['parameter'],'Parameter')
    if record['approach'] not in ('zero_positive','positive_infinity'):
        raise ValueError('Approach must be zero_positive or positive_infinity')
    if not isinstance(record['sources'],list) or not record['sources']:
        raise ValueError('Source references are required')
    for source in record['sources']:
        _text(source,'Source reference')
    baseline,reference=rational(record['baseline']),rational(record['reference'])
    terms=record['corrections']
    if not isinstance(terms,list) or len(terms) > 32:
        raise ValueError('Corrections must be an array with at most 32 terms')
    coefficients={}
    for term in terms:
        if not isinstance(term,dict) or set(term) != {'power','coefficient'}:
            raise ValueError('Each correction requires power and coefficient')
        power=term['power']
        if type(power) is not int or not -8 <= power <= 8:
            raise ValueError('Laurent powers must be integers from -8 through 8')
        coefficients[power]=coefficients.get(power,Fraction(0))+rational(term['coefficient'])
    coefficients={p:c for p,c in coefficients.items() if c != 0}
    toward_zero=record['approach']=='zero_positive'
    divergent=[p for p in coefficients if (p < 0 if toward_zero else p > 0)]
    leading=min(divergent) if toward_zero and divergent else max(divergent) if divergent else None
    finite=not divergent
    value=baseline+coefficients.get(0,Fraction(0)) if finite else None
    residual_constant=baseline-reference+coefficients.get(0,Fraction(0))
    samples=[]
    for index in (1,2,3):
        x=Fraction(1,10**index) if toward_zero else Fraction(10**index)
        observable=baseline+sum((coefficient*x**power for power,coefficient in coefficients.items()),Fraction(0))
        samples.append({'parameter':str(x),'observable':str(observable),'residual':str(observable-reference)})
    return {'id':identifier, 'parameter':parameter, 'approach':record['approach'],
            'source_references':record['sources'], 'baseline':str(baseline),'reference':str(reference),
            'normalized_corrections':[{'power':p,'coefficient':str(c)} for p,c in sorted(coefficients.items())],
            'finite_limit':finite,'limit_value':str(value) if finite else None,
            'divergence':None if finite else ('positive_infinity' if coefficients[leading] > 0 else 'negative_infinity'),
            'leading_divergent_power':leading,
            'residual_limit':str(residual_constant) if finite else None,
            'passed':finite and value == reference,
            'samples':samples,
            'method':'Combine equal powers exactly, remove zero terms, classify powers on the positive real axis',
            'assumptions':['Finite Laurent polynomial with exact rational coefficients',
                           'Parameter and normalized observable are dimensionless as declared by submitter',
                           'Positive real parameter approaches the declared endpoint'],
            'scope':'Symbolic limit of supplied expression only; no derivation from a physical theory'}


def validate_bundle(bundle):
    if not isinstance(bundle,dict) or set(bundle) != {'schema_version','records'}:
        raise ValueError('Limit bundle requires schema_version and records')
    if type(bundle['schema_version']) is not int or bundle['schema_version'] != 1:
        raise ValueError('Unsupported limit bundle schema version')
    records=bundle['records']
    if not isinstance(records,list) or not 1 <= len(records) <= 32:
        raise ValueError('A limit bundle requires 1–32 records')
    results=[validate_record(record) for record in records]
    if len({row['id'] for row in results}) != len(results):
        raise ValueError('Limit record IDs must be unique')
    return {'schema_version':1,'records':results,'all_passed':all(row['passed'] for row in results),
            'independent_scientific_verification':False,'empirical_support':False,
            'scope':'Exact dimensionless one-parameter Laurent limits; not validation of Einstein equations or quantum gravity'}


def run_validation(bundle,output):
    from hashlib import sha256
    from pathlib import Path
    import sys
    from .artifacts import RunArtifacts
    from .memory import ScientificMemory
    checks=validate_bundle(bundle)
    artifacts=RunArtifacts(output)
    try:
        inputs=artifacts.write('input.json',bundle)
        results=artifacts.write('checks.json',checks)
        with ScientificMemory(artifacts.directory/'memory.sqlite3') as memory:
            memory.ingest({'schema_version':1,'sources':[
                {'id':artifact['path'],'title':artifact['path'],'locator':'local:'+artifact['path'],
                 'kind':'derivation','domains':['mathematics','gravity'],'content_sha256':artifact['sha256']}
                for artifact in (inputs,results)],
                'claims':[{'id':row['id'],'text':'Submitted normalized expression recovers its declared reference limit',
                           'sources':['input.json','checks.json'],'status':'Conjectured'} for row in checks['records']],
                'relations':[]})
            for row in checks['records']:
                if not row['passed']:
                    memory.reject(row['id'],'Symbolic reference limit failed','checks.json')
            memory.verify()
        report={'schema_version':1,'validation_type':'classical_limit_laurent',
                'record_count':len(checks['records']),'passed_count':sum(row['passed'] for row in checks['records']),
                'all_passed':checks['all_passed'],'highest_discovery_stage':0,
                'scientific_discovery':False,'independent_scientific_verification':False,'empirical_support':False,
                'python':sys.version,'source_file_sha256':{p.name:sha256(p.read_bytes()).hexdigest()
                    for p in sorted(Path(__file__).parent.glob('*.py'))},
                'limitations':['Finite one-parameter rational Laurent expressions only',
                    'Dimensionless normalization and physical provenance are supplied assumptions',
                    'Passing this check does not establish a GR limit, conservation law, or physical theory']}
        artifacts.write('report.json',report)
        artifacts.finalize()
        return report
    except Exception as error:
        artifacts.write('FAILED.json',{'error_type':type(error).__name__,'message':str(error)})
        raise
