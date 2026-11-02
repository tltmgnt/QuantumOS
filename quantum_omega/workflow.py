"""Bounded, reproducible research workflow spanning the architecture's interfaces."""
from hashlib import sha256
import json
import math
from pathlib import Path
import platform
import sys
from .artifacts import RunArtifacts, canonical
from .benchmark import freeze_and_evaluate, freeze_ranking
from .core import Action, Stage
from .experiments import design_experiment
from .memory import ScientificMemory
from .planner import plan
from .theory import generate_theories, rational
from .topology import analyze
from .gap_priority import rank_gaps, propose_review_actions
from .gap_benchmark import evaluate_fixture
from .verification import counterfactuals, validate


def parse_task(task):
    required = {'schema_version','title','coefficient_values','max_degree','training','holdout','probes','action_budget','experiment_budget'}
    if not isinstance(task, dict) or set(task) != required or type(task['schema_version']) is not int or task['schema_version'] != 1:
        raise ValueError('Invalid research task schema')
    if not isinstance(task['title'], str) or not task['title'].strip():
        raise ValueError('A research title is required')
    for key in ('action_budget','experiment_budget'):
        value = task[key]
        if type(value) not in (int,float) or not math.isfinite(value) or value < 0 or value > 1000:
            raise ValueError('Budgets must be finite from 0 to 1000')
    observations = {}
    for split in ('training','holdout'):
        rows = task[split]
        if not isinstance(rows, list) or not 1 <= len(rows) <= 128:
            raise ValueError('Each observation split needs 1 to 128 points')
        parsed = []
        for row in rows:
            if not isinstance(row, dict) or set(row) != {'x','y'}:
                raise ValueError('Observation fields must be x and y')
            parsed.append((rational(row['x']),rational(row['y'])))
        if len({x for x,y in parsed}) != len(parsed):
            raise ValueError('Repeated observation x values are not allowed')
        observations[split] = tuple(parsed)
    if {x for x,y in observations['training']} & {x for x,y in observations['holdout']}:
        raise ValueError('Training and holdout x values must be disjoint')
    if not isinstance(task['probes'], list) or not 1 <= len(task['probes']) <= 128:
        raise ValueError('Provide 1 to 128 counterfactual/experiment probes')
    probes = tuple(rational(x) for x in task['probes'])
    models = generate_theories(task['coefficient_values'], task['max_degree'])
    return models, observations['training'], observations['holdout'], probes


def run_research(task, output):
    models, training, holdout, probes = parse_task(task)
    artifacts = RunArtifacts(output)
    try:
        return _run(task, models, training, holdout, probes, artifacts)
    except Exception as error:
        # Leave a reviewable failure marker, never a completed manifest.
        artifacts.write('FAILED.json', {'error_type': type(error).__name__, 'message': str(error)})
        raise


def _run(task, models, training, holdout, probes, artifacts):
    def record(name, payload, memory, kind='derivation'):
        artifact = artifacts.write(name, payload)
        memory.ingest({'schema_version':1, 'sources':[{
            'id': name, 'title': name, 'locator': 'local:'+name, 'kind':kind,
            'domains':['mathematics','computation'], 'content_sha256':artifact['sha256']}],
            'claims':[], 'relations':[]})
        return name

    task_digest = sha256(canonical(task)).hexdigest()
    source_files = {p.name:sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob('*.py'))}
    artifacts.write('runtime.json', {'python':sys.version, 'platform':platform.platform(),
        'source_file_sha256':source_files, 'task_sha256':task_digest,
        'reproducibility': 'Rational arithmetic and deterministic selection; runtime metadata and SQLite timestamps may differ'})
    report = {'schema_version':1, 'title':task['title'], 'task_sha256':task_digest,
              'scientific_discovery':False, 'empirical_support':False,
              'independent_scientific_verification':False, 'novelty_claim':False,
              'software_scope':'Bounded exact-rational polynomial research demonstration',
              'plans':[], 'failures':[], 'surviving_theories':[], 'budget_remaining':task['action_budget']}
    with ScientificMemory(artifacts.directory/'memory.sqlite3') as memory:
        source = record('task.json', task, memory, 'simulation')
        catalog = record('theories.json', [model.record() for model in models], memory)
        memory.ingest({'schema_version':1, 'sources':[], 'claims':[
            {'id':'research-assumptions', 'text':'The task assumes dimensionless exact rational polynomial behavior',
             'sources':[source], 'status':'Conjectured'},
            *[{'id':model.id, 'text':f'Candidate polynomial with ascending coefficients {model.record()["coefficients_ascending"]}',
               'sources':[source,catalog], 'status':'Conjectured'} for model in models]],
            'relations':[{'id':'assumptions-'+model.id, 'source':model.id, 'target':'research-assumptions',
                          'kind':'depends_on', 'evidence':[source,catalog], 'status':'Conjectured'} for model in models]})
        for model in models:
            for stage in (Stage.CONJECTURE,Stage.FORMAL_MODEL):
                memory.advance(model.id,stage,catalog,'workflow-schema-checker','bounded-theory-factory')
        survivors = []
        completed = set()
        agenda = ('verify_training','design_experiment','benchmark_holdout')
        for action_name in agenda:
            if action_name != 'verify_training' and not survivors:
                report['failures'].append({'action':action_name,'reason':'No training-consistent candidates'})
                continue
            decision = plan([Action(action_name,1,0,1,0,1,0)],report['budget_remaining'])
            decision['score_origin'] = 'Fixed demonstration proxies; execution cost is one configured action unit'
            report['plans'].append(decision)
            record(f'plan-{action_name}.json',decision,memory)
            if decision['selected_action'] is None:
                report['failures'].append({'action':action_name,'reason':'Action budget exhausted'})
                break
            report['budget_remaining'] -= decision['cost']
            if action_name == 'verify_training':
                checks = {model.id:validate(model,training) for model in models}
                evidence = record('training-verification.json',checks,memory)
                simulation = record('simulation-counterfactuals.json',{
                    model.id:counterfactuals(model,probes) for model in models},memory,'simulation')
                for model in models:
                    if checks[model.id]['passed']:
                        survivors.append(model)
                        memory.advance(model.id,Stage.DERIVED_PREDICTION,evidence,'exact-sample-checker','bounded-theory-factory')
                        memory.advance(model.id,Stage.COMPUTATIONALLY_REPRODUCED,simulation,'alternate-evaluator','bounded-theory-factory')
                    else:
                        memory.reject(model.id,'Training counterexample',evidence)
                report['training_survivor_count'] = len(survivors)
            elif action_name == 'design_experiment':
                proposal = design_experiment(survivors,probes,task['experiment_budget'])
                record('experiment-proposal.json',{'proposal':proposal,
                    'status':'awaiting_human_review' if proposal else 'no_feasible_distinguishing_probe',
                    'executed':False},memory)
                report['experiment_executed'] = False
            else:
                record('pre-holdout-ranking.json',freeze_ranking(survivors),memory)
                benchmark = freeze_and_evaluate(survivors,holdout)
                evidence = record('benchmark.json',benchmark,memory,'simulation')
                passed = {row['theory_id'] for row in benchmark['results'] if row['passed']}
                for model in survivors:
                    if model.id not in passed:
                        memory.reject(model.id,'Holdout counterexample; benchmark failure preserved',evidence)
                if not benchmark['champion_passed']:
                    report['failures'].append({'action':'benchmark_holdout',
                        'reason':'Pre-holdout champion failed; selecting another model now is adaptive, not blind validation'})
                survivors = [model for model in survivors if model.id in passed]
                recovery = {'abandoned': [r['theory_id'] for r in benchmark['results'] if not r['passed']],
                    'retained_as_hypotheses':[m.id for m in survivors],
                    'next_requirement':'New independent holdout observations and human scientific review',
                    'automatic_promotion_to_D5_or_D6':False}
                record('recovery.json',recovery,memory)
                report['benchmark_champion_passed'] = benchmark['champion_passed']
                report['blind_research_acceptance'] = False
            completed.add(action_name)
        record('topology.json',analyze(memory),memory)
        gap_report = rank_gaps(memory)
        record('gap-priority.json', gap_report, memory)
        review_plan = propose_review_actions(gap_report, report['budget_remaining'])
        record('gap-review-plan.json', review_plan, memory)
        synthetic_benchmark = evaluate_fixture()
        if not synthetic_benchmark['passed']:
            raise ValueError('TGA synthetic benchmark failed')
        record('gap-benchmark.json', synthetic_benchmark, memory)
        report['tga_review_priority'] = {
            'heuristic_only': True,
            'ranked_claim_count': len(gap_report['ranked_claims']),
            'selected_review_action': review_plan['selected_action'],
            'synthetic_benchmark_passed': synthetic_benchmark['passed'],
            'report_sha256': gap_report['sha256'],
        }
        report['surviving_theories'] = [model.id for model in survivors]
        report['candidate_count'] = len(models)
        report['claim_count'] = len(memory.snapshot()[0])
        report['rejected_count'] = sum(c.status.value == 'Rejected' for c in memory.snapshot()[0])
        report['highest_stage'] = max(int(c.stage) for c in memory.snapshot()[0])
        report['outcome'] = 'workflow_completed' if len(completed) == 3 else 'partial_budget_or_no_survivors'
        report['discovery_criterion'] = {'formal_support_scope':'Restricted Q[x] identities only',
            'independent_verification':False, 'independent_replication':False,
            'meaningful_new_physical_prediction':False, 'explanatory_contribution':False, 'D':False}
        report['milestones'] = {
            'I': {'software':'local source/claim ingestion and provenance', 'scientific_acceptance':'Literature retrieval and external source review remain'},
            'II': {'software':'structural graph analysis', 'scientific_acceptance':'No validated explanatory metric or full state-transition topology'},
            'III': {'software':'bounded theory generation with assumptions and falsifiers', 'scientific_acceptance':'Polynomial domain only'},
            'IV': {'software':'exact algebra, alternate evaluator, samples, counterfactuals, rejection', 'scientific_acceptance':'No general theorem prover or independent scientific verification'},
            'V': {'software':'budgeted local action loop with persisted decisions', 'scientific_acceptance':'Proxy utility not scientifically calibrated'},
            'VI': {'software':'frozen-ranking holdout harness with failure retention', 'scientific_acceptance':'Public fixture is not blind research'},
            'VII': {'software':'information-gain experiment proposal under cost budget', 'scientific_acceptance':'Human review pending; no experiment executed'},
            'VIII': {'software':'reproducible workflow artifacts and failure trail', 'scientific_acceptance':'Open-problem discovery and independent publication not achieved'},
        }
        memory.verify()
    artifacts.write('report.json',report)
    artifacts.finalize()
    return report
