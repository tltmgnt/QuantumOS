import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from quantum_omega import EpistemicStatus
from quantum_omega.artifacts import verify_run
from quantum_omega.limits import run_validation, validate_bundle, validate_record
from quantum_omega.memory import ScientificMemory

ROOT=Path(__file__).resolve().parents[1]


def record(terms=None,approach='zero_positive',baseline=1,reference=1):
    return {'id':'limit','parameter':'epsilon','approach':approach,'baseline':baseline,'reference':reference,
            'corrections':terms or [],'sources':['local:fixture']}


class LimitTests(unittest.TestCase):
    def test_positive_powers_vanish_near_zero(self):
        result=validate_record(record([{'power':2,'coefficient':'1/3'}]))
        self.assertTrue(result['passed'])
        self.assertEqual(result['limit_value'],'1')
        self.assertEqual(result['residual_limit'],'0')
        self.assertEqual(result['samples'][0]['residual'],'1/300')

    def test_negative_powers_vanish_at_infinity(self):
        result=validate_record(record([{'power':-2,'coefficient':'-3/5'}],approach='positive_infinity'))
        self.assertTrue(result['passed'])
        self.assertEqual(result['samples'][0]['residual'],'-3/500')

    def test_divergence_sign_is_determined_by_dominant_power(self):
        near_zero=validate_record(record([{'power':-1,'coefficient':100},{'power':-2,'coefficient':-1}]))
        self.assertFalse(near_zero['passed'])
        self.assertFalse(near_zero['finite_limit'])
        self.assertEqual(near_zero['divergence'],'negative_infinity')
        self.assertEqual(near_zero['leading_divergent_power'],-2)
        at_infinity=validate_record(record([{'power':1,'coefficient':-100},{'power':2,'coefficient':1}],
                                          approach='positive_infinity'))
        self.assertEqual(at_infinity['divergence'],'positive_infinity')
        self.assertEqual(at_infinity['leading_divergent_power'],2)

    def test_exact_cancellation_and_zero_coefficients(self):
        result=validate_record(record([{'power':-8,'coefficient':'1/3'},
            {'power':-8,'coefficient':'-1/3'},{'power':-1,'coefficient':0}]))
        self.assertTrue(result['passed'])
        self.assertEqual(result['normalized_corrections'],[])

    def test_finite_but_wrong_constant_and_nonunit_reference(self):
        self.assertFalse(validate_record(record([{'power':0,'coefficient':'1/1000000000000'}]))['passed'])
        result=validate_record(record([{'power':0,'coefficient':2}],baseline=1,reference=3))
        self.assertTrue(result['passed'])
        self.assertEqual(result['limit_value'],'3')
        self.assertFalse(validate_record(record(baseline=2,reference=1))['passed'])

    def test_samples_do_not_replace_symbolic_analysis(self):
        # Small sampled residuals do not establish a limit; this term diverges.
        result=validate_record(record([{'power':-1,'coefficient':'1/1000000000000'}]))
        self.assertFalse(result['passed'])
        self.assertEqual(result['divergence'],'positive_infinity')

    def test_schema_bounds_and_unsupported_expressions(self):
        changes=[{'approach':'zero_negative'},{'baseline':0.5},{'reference':True},
                 {'corrections':[{'power':True,'coefficient':1}]},
                 {'corrections':[{'power':9,'coefficient':1}]},
                 {'corrections':[{'power':1,'coefficient':'sin(epsilon)'}]},
                 {'corrections':[{'power':1,'coefficient':1,'extra':1}]},
                 {'sources':[]},{'extra':'unknown'}]
        for change in changes:
            data=record()
            data.update(change)
            with self.subTest(change=change),self.assertRaises(ValueError):
                validate_record(data)
        with self.assertRaises(ValueError):
            validate_bundle({'schema_version':True,'records':[record()]})
        with self.assertRaises(ValueError):
            validate_bundle({'schema_version':1,'records':[record(),record()]})


class LimitRunTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.bundle=json.loads((ROOT/'examples/classical_limits.json').read_text())

    def test_cli_to_verified_provenance_report(self):
        output=self.root/'run'
        result=subprocess.run([sys.executable,'-m','quantum_omega','validate-limits',
            str(ROOT/'examples/classical_limits.json'),'--output',str(output)],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        report=json.loads(result.stdout)
        self.assertEqual(report['passed_count'],2)
        self.assertEqual(report['highest_discovery_stage'],0)
        self.assertFalse(report['empirical_support'])
        self.assertTrue(verify_run(output)['verified'])
        with ScientificMemory(output/'memory.sqlite3',read_only=True) as memory:
            self.assertEqual(len(memory.sources()),2)
            for claim in memory.snapshot()[0]:
                self.assertEqual(claim.stage,0)

    def test_failed_limit_has_evidence_and_rejection(self):
        bundle={'schema_version':1,'records':[record([{'power':-1,'coefficient':1}])]}
        output=self.root/'rejected'
        report=run_validation(bundle,output)
        self.assertFalse(report['all_passed'])
        self.assertTrue(verify_run(output)['verified'])
        with ScientificMemory(output/'memory.sqlite3',read_only=True) as memory:
            self.assertEqual(memory.get('limit').status,EpistemicStatus.REJECTED)
            self.assertEqual(memory.history('limit')[-1]['artifact'],'checks.json')

    def test_cli_failure_codes_and_existing_output(self):
        bundle_path=self.root/'input.json'
        self.bundle['records'][0]['corrections']=[{'power':0,'coefficient':1}]
        bundle_path.write_text(json.dumps(self.bundle))
        output=self.root/'finite-failure'
        args=[sys.executable,'-m','quantum_omega','validate-limits',str(bundle_path),'--output',str(output)]
        failed=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(failed.returncode,1,failed.stderr)
        self.assertFalse(json.loads(failed.stdout)['all_passed'])
        before=(output/'report.json').read_bytes()
        existing=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(existing.returncode,2)
        self.assertEqual((output/'report.json').read_bytes(),before)
        invalid=self.root/'invalid'
        self.bundle['records'][0]['baseline']='unsupported_symbol'
        bundle_path.write_text(json.dumps(self.bundle))
        args[-1]=str(invalid)
        malformed=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(malformed.returncode,2)
        self.assertFalse(invalid.exists())
