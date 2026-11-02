import copy
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from quantum_omega import EpistemicStatus
from quantum_omega.artifacts import verify_run
from quantum_omega.memory import ScientificMemory
from quantum_omega.quantum import (GaussianRational, determinant, parse_matrix,
                                   run_validation, validate_bundle, validate_density, validate_unitary)

ROOT=Path(__file__).resolve().parents[1]


class ExactQuantumTests(unittest.TestCase):
    def test_valid_pure_mixed_complex_and_bell_states(self):
        fixture=json.loads((ROOT/'examples/quantum_constraints.json').read_text())
        self.assertTrue(validate_bundle(fixture)['all_passed'])
        for matrix in ([[1]], [['1/2',0],[0,'1/2']], [[1,0],[0,0]]):
            self.assertTrue(validate_density(parse_matrix(matrix))['passed'])
        report=validate_density(parse_matrix(fixture['records'][1]['matrix']))
        self.assertEqual(len(report['principal_minors']),15)
        self.assertTrue(any(row['determinant']['real']=='0' for row in report['principal_minors']))

    def test_invalid_normalization_hermiticity_and_positivity(self):
        bad_trace=validate_density(parse_matrix([[1,0],[0,1]]))
        self.assertFalse(bad_trace['trace_one'])
        self.assertFalse(bad_trace['passed'])
        nonhermitian=validate_density(parse_matrix([['1/2',1],[0,'1/2']]))
        self.assertFalse(nonhermitian['hermitian'])
        self.assertIsNone(nonhermitian['positive_semidefinite'])
        self.assertFalse(validate_density(parse_matrix([[2,0],[0,-1]]))['passed'])
        # Positive diagonal and positive 2x2 principal minors are insufficient.
        triple=[['1/3','-1/4','-1/4'],['-1/4','1/3','-1/4'],['-1/4','-1/4','1/3']]
        result=validate_density(parse_matrix(triple))
        self.assertTrue(result['hermitian'])
        self.assertTrue(result['trace_one'])
        self.assertTrue(all(row['nonnegative_real'] for row in result['principal_minors'] if len(row['indices'])<3))
        self.assertFalse(result['positive_semidefinite'])
        self.assertFalse(result['passed'])

    def test_all_principal_minors_not_only_leading_minors(self):
        # Leading minors all vanish, but the final diagonal entry is negative.
        result=validate_density(parse_matrix([[0,0,0],[0,2,0],[0,0,-1]]))
        self.assertFalse(result['positive_semidefinite'])
        self.assertFalse(result['passed'])

    def test_unitary_complex_phase_and_rejection(self):
        for matrix in ([[1]],[[0,1],[1,0]],[[[0,1],0],[0,[0,-1]]],
                       [['3/5','-4/5'],['4/5','3/5']]):
            self.assertTrue(validate_unitary(parse_matrix(matrix))['passed'])
        self.assertFalse(validate_unitary(parse_matrix([[1,1],[0,1]]))['passed'])
        self.assertFalse(validate_unitary(parse_matrix([[0,0],[0,0]]))['passed'])

    def test_exact_arithmetic_no_tolerance_acceptance(self):
        epsilon='1/1000000000000'
        self.assertFalse(validate_density(parse_matrix([[1,epsilon],[epsilon,0]]))['passed'])
        self.assertEqual(determinant(parse_matrix([[1,[0,1]],[[0,-1],1]])).real,Fraction(0))
        with self.assertRaises(ValueError):
            GaussianRational(0.5)

    def test_reject_malformed_unsupported_or_approximate_matrices(self):
        for matrix in ([],[[1,0]],[[1],[0]],[[0]*5 for _ in range(5)],[[0.5]],[[True]],
                       [[['1/2']]],[[[0,1,2]]],[['1/0']],[['sqrt(2)']],[[float('nan')]]):
            with self.subTest(matrix=matrix),self.assertRaises(ValueError):
                parse_matrix(matrix)
        for function in (validate_density,validate_unitary,determinant):
            with self.assertRaises(ValueError):
                function(())

    def test_bundle_schema_and_duplicate_identifiers(self):
        fixture=json.loads((ROOT/'examples/quantum_constraints.json').read_text())
        mutations=[lambda b:b.update(schema_version=True),lambda b:b.update(extra=1),
                   lambda b:b['records'].append(copy.deepcopy(b['records'][0])),
                   lambda b:b['records'][0].update(kind='quantum_gravity'),
                   lambda b:b['records'][0].update(sources=[]),
                   lambda b:b['records'][0].update(stage=6)]
        for mutate in mutations:
            bundle=copy.deepcopy(fixture)
            mutate(bundle)
            with self.assertRaises(ValueError):
                validate_bundle(bundle)


class QuantumRunTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.bundle=json.loads((ROOT/'examples/quantum_constraints.json').read_text())

    def test_provenance_run_verify_and_no_scientific_promotion(self):
        output=self.root/'quantum'
        report=run_validation(self.bundle,output)
        self.assertTrue(report['all_passed'])
        self.assertEqual(report['passed_count'],3)
        self.assertEqual(report['highest_discovery_stage'],0)
        self.assertFalse(report['scientific_discovery'])
        self.assertTrue(verify_run(output)['verified'])
        with ScientificMemory(output/'memory.sqlite3',read_only=True) as memory:
            self.assertEqual(len(memory.sources()),2)
            for claim in memory.snapshot()[0]:
                self.assertEqual(claim.stage,0)
                self.assertEqual(claim.status,EpistemicStatus.CONJECTURED)

    def test_invalid_structures_retained_and_rejected(self):
        self.bundle['records'][0]['matrix']=[[2,0],[0,-1]]
        output=self.root/'failed-constraints'
        report=run_validation(self.bundle,output)
        self.assertFalse(report['all_passed'])
        self.assertTrue(verify_run(output)['verified'])
        with ScientificMemory(output/'memory.sqlite3',read_only=True) as memory:
            claim=memory.get('complex-pure-state')
            self.assertEqual(claim.status,EpistemicStatus.REJECTED)
            self.assertEqual(memory.history(claim.id)[-1]['artifact'],'checks.json')

    def test_cli_success_constraint_failure_and_schema_error_codes(self):
        bundle_path=self.root/'input.json'
        bundle_path.write_text(json.dumps(self.bundle))
        def run(output):
            return subprocess.run([sys.executable,'-m','quantum_omega','validate-quantum',str(bundle_path),
                                   '--output',str(output)],cwd=ROOT,capture_output=True,text=True)
        result=run(self.root/'valid')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(json.loads(result.stdout)['all_passed'])
        self.bundle['records'][0]['matrix']=[[2,0],[0,-1]]
        bundle_path.write_text(json.dumps(self.bundle))
        result=run(self.root/'invalid-constraints')
        self.assertEqual(result.returncode,1,result.stderr)
        self.assertFalse(json.loads(result.stdout)['all_passed'])
        self.bundle['records'][0]['matrix']=[[0.5]]
        bundle_path.write_text(json.dumps(self.bundle))
        output=self.root/'malformed'
        result=run(output)
        self.assertEqual(result.returncode,2,result.stderr)
        self.assertFalse(output.exists())

    def test_existing_outputs_preserved(self):
        output=self.root/'quantum'
        run_validation(self.bundle,output)
        before=(output/'report.json').read_bytes()
        with self.assertRaises(FileExistsError):
            run_validation(self.bundle,output)
        self.assertEqual((output/'report.json').read_bytes(),before)
