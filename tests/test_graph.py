import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from quantum_omega import Claim, EpistemicStatus, Relation, RelationType, Stage
from quantum_omega.memory import ScientificMemory


class GraphTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'graph.sqlite3'
        with ScientificMemory(self.path) as memory:
            for identifier in ('a', 'b', 'c'):
                memory.register(Claim(identifier, 'Illustrative claim '+identifier, ('local:notes',)))
        self.edge = Relation('r1', 'a', 'b', RelationType.SUPPORTS, ('local:evidence',))

    def test_persistent_directed_edges_and_provenance(self):
        with ScientificMemory(self.path) as memory:
            memory.link(self.edge)
            memory.advance('a', Stage.CONJECTURE, 'local:artifact', 'reviewer', 'author')
        with ScientificMemory(self.path) as memory:
            self.assertEqual(memory.relations('a', 'outgoing'), (self.edge,))
            self.assertEqual(memory.relations('a', 'incoming'), ())
            self.assertEqual(memory.relations('b', 'incoming'), (self.edge,))
            self.assertEqual(memory.relations('c'), ())
            self.assertEqual(memory.history('b')[-1]['evidence'], ['local:evidence'])
            self.assertTrue(memory.verify())
            self.assertEqual(memory.get('a').status, EpistemicStatus.SPECULATIVE)
            self.assertEqual(memory.get('b').stage, Stage.IDEA)

    def test_rejected_links_do_not_partially_write(self):
        with ScientificMemory(self.path) as memory:
            memory.link(self.edge)
            with self.assertRaises(ValueError):
                memory.link(self.edge)
            with self.assertRaises(KeyError):
                memory.link(Relation('r2', 'a', 'missing', RelationType.DEPENDS_ON, ('local:x',)))
            self.assertEqual(len(memory.history('a')), 2)
            self.assertEqual(memory.relations('a'), (self.edge,))
            self.assertTrue(memory.verify())

    def test_type_filters_and_identifier_namespaces(self):
        # A relation ID may equal a claim ID; history must not mix these namespaces.
        other = Relation('c', 'b', 'a', RelationType.CONTRADICTS, ('local:criticism',))
        with ScientificMemory(self.path) as memory:
            memory.link(self.edge)
            memory.link(other)
            self.assertEqual(memory.relations('a', kind=RelationType.CONTRADICTS), (other,))
            self.assertEqual(len(memory.history('c')), 1)
            with self.assertRaises(ValueError):
                memory.relations('a', direction='sideways')
            with self.assertRaises(ValueError):
                memory.relations('a', kind='supports')
            with self.assertRaises(KeyError):
                memory.history('missing')

    def test_relation_validation(self):
        for evidence in ((), ('',), ['mutable']):
            with self.assertRaises(ValueError):
                Relation('r', 'a', 'b', RelationType.SUPPORTS, evidence)
        with self.assertRaises(ValueError):
            Relation('r', 'a', 'a', RelationType.SUPPORTS, ('local:x',))
        with self.assertRaises(ValueError):
            Relation('r', 'a', 'b', 'supports', ('local:x',))

    def test_corrupt_relation_blocks_queries(self):
        with ScientificMemory(self.path) as memory:
            memory.link(self.edge)
        with sqlite3.connect(self.path) as database:
            payload = json.loads(database.execute('SELECT payload FROM events WHERE sequence=4').fetchone()[0])
            payload['target'] = 'c'
            database.execute('UPDATE events SET payload=? WHERE sequence=4', (json.dumps(payload),))
        with ScientificMemory(self.path) as memory:
            with self.assertRaisesRegex(ValueError, 'integrity'):
                memory.relations('a')

    def test_existing_database_without_edges_remains_readable(self):
        with ScientificMemory(self.path) as memory:
            self.assertEqual(memory.get('a').id, 'a')
            self.assertEqual(memory.relations('a'), ())
            self.assertTrue(memory.verify())
