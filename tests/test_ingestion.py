import copy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from quantum_omega.memory import ScientificMemory
from quantum_omega import Stage

FIXTURE = Path(__file__).resolve().parents[1] / 'examples' / 'research_bundle.json'


class IngestionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'ingestion.sqlite3'
        self.bundle = json.loads(FIXTURE.read_text())

    def event_count(self):
        with sqlite3.connect(self.path) as db:
            return db.execute('SELECT count(*) FROM events').fetchone()[0]

    def test_end_to_end_reopen_and_provenance(self):
        with ScientificMemory(self.path) as memory:
            self.assertEqual(memory.ingest(self.bundle), {'sources':1,'claims':2,'relations':1})
        with ScientificMemory(self.path) as memory:
            self.assertEqual(memory.get_source('source:toy').title, self.bundle['sources'][0]['title'])
            self.assertEqual(memory.get('toy-model').stage, Stage.IDEA)
            self.assertEqual(len(memory.relations('toy-model','incoming')),1)
            self.assertTrue(memory.verify())
            source_id = memory.history('toy-model')[0]['sources'][0]
            self.assertEqual(memory.get_source(source_id).content_sha256, self.bundle['sources'][0]['content_sha256'])

    def test_missing_source_rolls_back_whole_batch(self):
        self.bundle['claims'][1]['sources']=['missing']
        with ScientificMemory(self.path) as memory:
            with self.assertRaises(KeyError):
                memory.ingest(self.bundle)
            self.assertEqual(self.event_count(),0)
            with self.assertRaises(KeyError):
                memory.get_source('source:toy')

    def test_invalid_relation_rolls_back_claims_and_sources(self):
        self.bundle['relations'][0]['target']='missing'
        with ScientificMemory(self.path) as memory:
            with self.assertRaises(KeyError):
                memory.ingest(self.bundle)
            self.assertEqual(self.event_count(),0)

    def test_duplicate_reimport_does_not_change_history(self):
        with ScientificMemory(self.path) as memory:
            memory.ingest(self.bundle)
            with self.assertRaises(ValueError):
                memory.ingest(self.bundle)
            self.assertEqual(self.event_count(),4)
            self.assertTrue(memory.verify())

    def test_strict_schema_and_ontology(self):
        mutations=[lambda b:b.update(schema_version=True),
                   lambda b:b.update(extra='unknown'),
                   lambda b:b['sources'][0].update(kind='unknown'),
                   lambda b:b['sources'][0].update(domains=['unlisted']),
                   lambda b:b['sources'][0].update(content_sha256='invalid'),
                   lambda b:b['claims'][0].update(stage=6),
                   lambda b:b['claims'][0].update(sources='source:toy'),
                   lambda b:b['claims'][0].update(status='Established'),
                   lambda b:b['relations'][0].update(evidence=['missing'])]
        with ScientificMemory(self.path) as memory:
            for mutate in mutations:
                with self.subTest(mutate=mutate):
                    bundle=copy.deepcopy(self.bundle)
                    mutate(bundle)
                    with self.assertRaises((ValueError,KeyError)):
                        memory.ingest(bundle)
                    self.assertEqual(self.event_count(),0)

    def test_source_and_claim_identifier_collision_keeps_history_separate(self):
        self.bundle['sources'][0]['id']='toy-model'
        for claim in self.bundle['claims']:
            claim['sources']=['toy-model']
        self.bundle['relations'][0]['evidence']=['toy-model']
        with ScientificMemory(self.path) as memory:
            memory.ingest(self.bundle)
            self.assertEqual(len(memory.history('toy-model')),2)

    def test_registered_source_can_be_reused_in_later_bundle(self):
        with ScientificMemory(self.path) as memory:
            memory.ingest(self.bundle)
            memory.ingest({'schema_version':1,'sources':[], 'claims':[
                {'id':'later','text':'Later conjecture','sources':['source:toy'],'status':'Speculative'}], 'relations':[]})
            self.assertEqual(memory.get('later').sources,('source:toy',))
            self.assertTrue(memory.verify())
