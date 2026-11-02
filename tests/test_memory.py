import sqlite3
import tempfile
import unittest
from pathlib import Path
from quantum_omega import Claim, Stage
from quantum_omega.memory import ScientificMemory


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'memory.sqlite3'
        self.claim = Claim('c1', 'Illustrative conjecture', ('doi:example-only',))

    def test_survives_reopening_with_provenance(self):
        with ScientificMemory(self.path) as memory:
            memory.register(self.claim)
            memory.advance('c1', Stage.CONJECTURE, 'local:derivation', 'reviewer', 'author')
        with ScientificMemory(self.path) as memory:
            result = memory.get('c1')
            self.assertEqual(result.stage, Stage.CONJECTURE)
            self.assertEqual(result.sources, self.claim.sources)
            self.assertEqual(result.status, self.claim.status)
            self.assertEqual(memory.history('c1')[1]['artifact'], 'local:derivation')
            self.assertTrue(memory.verify())

    def test_failed_transition_and_duplicate_leave_no_events(self):
        with ScientificMemory(self.path) as memory:
            memory.register(self.claim)
            with self.assertRaises(ValueError):
                memory.advance('c1', Stage.EMPIRICALLY_SUPPORTED, 'x', 'b', 'a')
            with self.assertRaises(ValueError):
                memory.register(self.claim)
            self.assertEqual(len(memory.history('c1')), 1)
            memory.advance('c1', Stage.CONJECTURE, 'x', 'b', 'a')
            self.assertTrue(memory.verify())

    def test_multiple_connections_replay_latest_committed_state(self):
        with ScientificMemory(self.path) as first, ScientificMemory(self.path) as second:
            first.register(self.claim)
            second.advance('c1', Stage.CONJECTURE, 'x', 'b', 'a')
            self.assertEqual(first.get('c1').stage, Stage.CONJECTURE)
            with self.assertRaises(ValueError):
                first.advance('c1', Stage.CONJECTURE, 'x', 'b', 'a')

    def test_payload_tampering_blocks_reads_and_writes(self):
        with ScientificMemory(self.path) as memory:
            memory.register(self.claim)
        with sqlite3.connect(self.path) as database:
            database.execute("UPDATE events SET payload = '{}' WHERE sequence = 1")
        with ScientificMemory(self.path) as memory:
            with self.assertRaisesRegex(ValueError, 'integrity'):
                memory.get('c1')
            with self.assertRaisesRegex(ValueError, 'integrity'):
                memory.register(Claim('c2', 'Another conjecture', ('local:source',)))
        with sqlite3.connect(self.path) as database:
            self.assertEqual(database.execute('SELECT count(*) FROM events').fetchone()[0], 1)

    def test_deleted_middle_event_detected(self):
        with ScientificMemory(self.path) as memory:
            memory.register(self.claim)
            memory.advance('c1', Stage.CONJECTURE, 'x', 'b', 'a')
        with sqlite3.connect(self.path) as database:
            database.execute('DELETE FROM events WHERE sequence = 1')
        with ScientificMemory(self.path) as memory:
            with self.assertRaisesRegex(ValueError, 'integrity'):
                memory.verify()
