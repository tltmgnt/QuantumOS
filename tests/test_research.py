import copy
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from quantum_omega import Action, Claim, EpistemicStatus, Stage
from quantum_omega.artifacts import verify_run
from quantum_omega.benchmark import freeze_and_evaluate
from quantum_omega.experiments import design_experiment
from quantum_omega.memory import ScientificMemory
from quantum_omega.planner import plan
from quantum_omega.theory import PolynomialTheory, generate_theories, rational
from quantum_omega.verification import counterfactuals, identity_certificate, validate
from quantum_omega.workflow import parse_task, run_research

ROOT = Path(__file__).resolve().parents[1]


def model(*coefficients):
    return PolynomialTheory(tuple(Fraction(c) for c in coefficients))


class TheoryTests(unittest.TestCase):
    def test_factory_is_bounded_deterministic_and_deduplicates(self):
        first = generate_theories([-1,0,1,1],2)
        self.assertEqual(first,generate_theories([1,0,-1],2))
        self.assertEqual(len(first),27)
        self.assertEqual(model(0,0,1,0),model(0,0,1))
        with self.assertRaises(ValueError):
            generate_theories(list(range(10)),3)
        with self.assertRaises(ValueError):
            generate_theories([0,1],True)

    def test_restricted_identity_and_counterexamples(self):
        square = model(0,0,1)
        self.assertEqual(square.predict(Fraction(3,2)),Fraction(9,4))
        self.assertTrue(identity_certificate(square,model(0,0,1))['passed'])
        self.assertFalse(identity_certificate(square,model(0,1))['passed'])
        check = validate(square,((Fraction(2),Fraction(4)),))
        self.assertTrue(check['passed'])
        self.assertTrue(check['product_rule_certificate']['passed'])
        bad = validate(model(0,1),((Fraction(2),Fraction(4)),))
        self.assertFalse(bad['passed'])
        self.assertEqual(bad['counterexamples'][0]['predicted'],'2')
        self.assertFalse(check['independently_verified'])

    def test_counterfactual_assumption_removal(self):
        result=counterfactuals(model(1,0,2),(Fraction(2),))
        self.assertEqual([r['removed_coefficient'] for r in result],[0,2])
        self.assertEqual(result[1]['prediction_deltas'][0]['delta'],'8')

    def test_literal_validation_without_eval(self):
        self.assertEqual(rational('2/3'),Fraction(2,3))
        for value in (0.5,True,'1/0',"__import__('os')",'9'*100):
            with self.assertRaises(ValueError):
                rational(value)


class DecisionTests(unittest.TestCase):
    def test_budget_ranking_ties_and_invalid_inputs(self):
        actions=[Action('z',2,0,0,0,1,0),Action('a',2,0,0,0,1,0),Action('too-costly',100,0,0,0,4,0)]
        self.assertEqual(plan(actions,1)['selected_action'],'a')
        self.assertIsNone(plan(actions,0)['selected_action'])
        for budget in (-1,float('nan'),True):
            with self.assertRaises(ValueError):
                plan(actions,budget)
        with self.assertRaises(ValueError):
            plan([actions[0],actions[0]],2)

    def test_information_gain_and_experiment_gate(self):
        proposals=[model(0,1),model(0,0,1)]
        request=design_experiment(proposals,(Fraction(0),Fraction(1),Fraction(2)),1)
        self.assertEqual(request['x'],'2')
        self.assertAlmostEqual(request['expected_information_gain_bits'],1)
        self.assertEqual(request['status'],'awaiting_human_review')
        self.assertFalse(request['executed'])
        self.assertIsNone(design_experiment(proposals,(Fraction(2),),0))
        self.assertIsNone(design_experiment(proposals,(Fraction(0),Fraction(1)),1))
        with self.assertRaises(ValueError):
            design_experiment(proposals,(Fraction(2),),float('inf'))

    def test_benchmark_freezes_simple_baseline_and_preserves_failure(self):
        linear,square=model(0,1),model(0,0,1)
        report=freeze_and_evaluate([square,linear],((Fraction(2),Fraction(4)),))
        self.assertEqual(report['pre_holdout_champion'],linear.id)
        self.assertFalse(report['champion_passed'])
        self.assertEqual(report['results'][1]['theory_id'],square.id)
        self.assertTrue(report['results'][1]['passed'])
        self.assertFalse(report['scientific_blindness'])


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.task=json.loads((ROOT/'examples/polynomial_research.json').read_text())

    def test_all_software_interfaces_and_rejection_history(self):
        output=self.root/'run'
        report=run_research(self.task,output)
        self.assertEqual(report['outcome'],'workflow_completed')
        self.assertEqual(report['candidate_count'],27)
        self.assertEqual(report['training_survivor_count'],2)
        self.assertEqual(report['rejected_count'],26)
        self.assertEqual(report['highest_stage'],4)
        self.assertEqual(set(report['milestones']),set(('I','II','III','IV','V','VI','VII','VIII')))
        self.assertFalse(report['scientific_discovery'])
        self.assertFalse(report['benchmark_champion_passed'])
        self.assertEqual(len(report['surviving_theories']),1)
        self.assertTrue(verify_run(output)['verified'])
        with ScientificMemory(output/'memory.sqlite3',read_only=True) as memory:
            rejected=memory.get(model(0,1).id)
            self.assertEqual(rejected.status,EpistemicStatus.REJECTED)
            self.assertEqual(memory.history(rejected.id)[-1]['event'],'reject')
            self.assertTrue(memory.relations(report['surviving_theories'][0]))
            source_ids=[s.id for s in memory.sources()]
            self.assertLess(source_ids.index('pre-holdout-ranking.json'),source_ids.index('benchmark.json'))
            for claim in memory.snapshot()[0]:
                self.assertLessEqual(claim.stage,Stage.COMPUTATIONALLY_REPRODUCED)
        request=json.loads((output/'experiment-proposal.json').read_text())
        self.assertFalse(request['executed'])
        self.assertEqual(request['proposal']['status'],'awaiting_human_review')

    def test_deterministic_replay_of_semantic_report(self):
        first=run_research(self.task,self.root/'first')
        second=run_research(self.task,self.root/'second')
        self.assertEqual(first,second)
        for name in ('theories.json','benchmark.json','recovery.json'):
            self.assertEqual((self.root/'first'/name).read_bytes(),(self.root/'second'/name).read_bytes())

    def test_exhausted_budget_and_no_training_survivors(self):
        task=copy.deepcopy(self.task)
        task['action_budget']=0
        report=run_research(task,self.root/'no-budget')
        self.assertEqual(report['outcome'],'partial_budget_or_no_survivors')
        self.assertNotIn('benchmark_champion_passed',report)
        self.assertFalse((self.root/'no-budget'/'benchmark.json').exists())
        self.assertTrue(verify_run(self.root/'no-budget')['verified'])
        task=copy.deepcopy(self.task)
        task['training'][0]['y']=99
        report=run_research(task,self.root/'no-survivors')
        self.assertEqual(report['training_survivor_count'],0)
        self.assertEqual(report['rejected_count'],27)
        self.assertEqual(report['outcome'],'partial_budget_or_no_survivors')

    def test_invalid_task_does_not_create_run(self):
        mutations=[lambda t:t['holdout'][0].update(x=0),lambda t:t.update(max_degree=9),
                   lambda t:t.update(action_budget=-1),lambda t:t.update(extra='field'),
                   lambda t:t.update(probes=[]),lambda t:t['training'].append({'x':0,'y':1})]
        for index,mutate in enumerate(mutations):
            task=copy.deepcopy(self.task)
            mutate(task)
            output=self.root/str(index)
            with self.assertRaises(ValueError):
                run_research(task,output)
            self.assertFalse(output.exists())

    def test_integrity_detects_edited_artifact_even_with_manifest_rehash(self):
        output=self.root/'run'
        run_research(self.task,output)
        artifact=output/'theories.json'
        artifact.write_text('[]\n')
        with self.assertRaisesRegex(ValueError,'integrity'):
            verify_run(output)
        manifest_path=output/'manifest.json'
        manifest=json.loads(manifest_path.read_text())
        for row in manifest['artifacts']:
            if row['path']=='theories.json':
                row['sha256']=sha256(artifact.read_bytes()).hexdigest()
                row['size_bytes']=artifact.stat().st_size
        manifest_path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError,'provenance'):
            verify_run(output)

    def test_reject_paths_symlinks_and_existing_output(self):
        output=self.root/'run'
        run_research(self.task,output)
        with self.assertRaises(FileExistsError):
            run_research(self.task,output)
        manifest_path=output/'manifest.json'
        manifest=json.loads(manifest_path.read_text())
        manifest['artifacts'][0]['path']='../outside'
        manifest_path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError,'path'):
            verify_run(output)

    def test_cli_and_failure_marker(self):
        output=self.root/'cli'
        result=subprocess.run([sys.executable,'-m','quantum_omega','run',
            str(ROOT/'examples/polynomial_research.json'),'--output',str(output)],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        verified=subprocess.run([sys.executable,'-m','quantum_omega','verify-run',str(output)],
            cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(verified.returncode,0,verified.stderr)
        self.assertTrue(json.loads(verified.stdout)['verified'])
        failure=self.root/'failure'
        with patch('quantum_omega.workflow.validate',side_effect=ValueError('injected failure')):
            with self.assertRaisesRegex(ValueError,'injected failure'):
                run_research(self.task,failure)
        self.assertTrue((failure/'FAILED.json').exists())
        self.assertFalse((failure/'manifest.json').exists())

    def test_rejection_persists_and_prevents_promotion(self):
        path=self.root/'reject.sqlite3'
        with ScientificMemory(path) as memory:
            memory.register(Claim('bad','Failed conjecture',('local:source',)))
            memory.reject('bad','Counterexample','local:check')
            with self.assertRaises(ValueError):
                memory.advance('bad',Stage.CONJECTURE,'local:proof','reviewer','author')
        with ScientificMemory(path) as memory:
            self.assertEqual(memory.get('bad').status,EpistemicStatus.REJECTED)
            self.assertTrue(memory.verify())

    def test_run_verification_rejects_symlink_artifacts(self):
        output=self.root/'run'
        run_research(self.task,output)
        outside=self.root/'outside.json'
        original=output/'theories.json'
        outside.write_bytes(original.read_bytes())
        original.unlink()
        original.symlink_to(outside)
        with self.assertRaisesRegex(ValueError,'symlink'):
            verify_run(output)
