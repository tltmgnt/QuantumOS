import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from quantum_omega import Claim, EpistemicStatus, Ledger, Relation, RelationType
from quantum_omega.memory import ScientificMemory
from quantum_omega.topology import analyze, shortest_path


class TopologyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)/'graph.sqlite3'

    def test_cycles_isolates_contradictions_and_no_mutation(self):
        with ScientificMemory(self.path) as memory:
            for cid in ('a','b','c','isolated'):
                memory.register(Claim(cid,cid,('local:notes',)))
            for rid,src,dst,kind in [('r1','a','b',RelationType.DEPENDS_ON),
                                      ('r2','b','a',RelationType.DERIVED_FROM),
                                      ('r3','c','a',RelationType.DEPENDS_ON),
                                      ('r4','a','c',RelationType.CONTRADICTS)]:
                memory.link(Relation(rid,src,dst,kind,('local:evidence',)))
            before=memory.snapshot(),memory.history('a')
            report=analyze(memory,'c','b')
            self.assertEqual(report['dependency_cycle_components'],[['a','b']])
            self.assertEqual(report['isolated_claims'],['isolated'])
            self.assertEqual(report['asserted_contradictions'],['r4'])
            self.assertEqual(report['dependency_path']['claim_ids'],('c','a','b'))
            self.assertEqual((memory.snapshot(),memory.history('a')),before)

    def test_paths_respect_direction_types_and_rejected_edges(self):
        ledger=Ledger()
        for cid in ('a','b','c','d'):
            ledger.register(Claim(cid,cid,('local:notes',)))
        for rid,src,dst in [('z','a','c'),('y','a','b'),('x','b','d'),('w','c','d')]:
            ledger.link(Relation(rid,src,dst,RelationType.DEPENDS_ON,('local:x',)))
        ledger.link(Relation('rejected','d','a',RelationType.DEPENDS_ON,('local:x',),EpistemicStatus.REJECTED))
        claims,edges=ledger.claims(),ledger.all_relations()
        self.assertEqual(shortest_path(claims,edges,'a','d'),('a','b','d'))
        self.assertIsNone(shortest_path(claims,edges,'d','a'))
        self.assertEqual(shortest_path(claims,edges,'a','a'),('a',))
        self.assertIsNone(shortest_path(claims,edges,'a','d',(RelationType.SUPPORTS,)))
        with self.assertRaises(KeyError):
            shortest_path(claims,edges,'unknown','a')

    def test_empty_graph_and_invalid_path_pair(self):
        with ScientificMemory(self.path) as memory:
            self.assertEqual(analyze(memory)['claim_count'],0)
            self.assertEqual(analyze(memory)['dependency_cycle_components'],[])
            with self.assertRaises(ValueError):
                analyze(memory,source='a')

    def test_cli_import_restart_analysis_and_missing_database(self):
        root=Path(__file__).resolve().parents[1]
        imported=subprocess.run([sys.executable,'-m','quantum_omega.ingestion',
            str(root/'examples/research_bundle.json'),'--database',str(self.path)],
            cwd=root,capture_output=True,text=True)
        self.assertEqual(imported.returncode,0,imported.stderr)
        before=self.path.read_bytes()
        result=subprocess.run([sys.executable,'-m','quantum_omega.topology','--database',str(self.path),
            '--source','toy-prediction','--target','toy-model'],cwd=root,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(self.path.read_bytes(),before)
        report=json.loads(result.stdout)
        self.assertEqual(report['dependency_path']['hop_count'],1)
        self.assertEqual(report['dependency_path']['claim_ids'],['toy-prediction','toy-model'])
        missing=Path(self.temp.name)/'missing.sqlite3'
        failed=subprocess.run([sys.executable,'-m','quantum_omega.topology','--database',str(missing)],
            cwd=root,capture_output=True,text=True)
        self.assertEqual(failed.returncode,2)
        self.assertFalse(missing.exists())

    def test_read_only_memory_rejects_writes(self):
        with ScientificMemory(self.path) as memory:
            memory.register(Claim('a','Fixture',('local:notes',)))
        import sqlite3
        with ScientificMemory(self.path, read_only=True) as memory:
            with self.assertRaises(sqlite3.OperationalError):
                memory.register(Claim('b','Fixture',('local:notes',)))
            self.assertEqual(analyze(memory)['claim_count'],1)
