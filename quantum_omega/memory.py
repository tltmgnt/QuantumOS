"""Transactional, event-sourced scientific memory using the standard library."""
from datetime import datetime, timezone
from hashlib import sha256
import json
import sqlite3
from .core import Claim, EpistemicStatus, Ledger, Relation, RelationType, Stage


class ScientificMemory:
    """Persist governance events; hashes detect edits, not privileged rewrites."""

    def __init__(self, path):
        self._db = sqlite3.connect(path, isolation_level=None)
        self._db.execute('''CREATE TABLE IF NOT EXISTS events (
            sequence INTEGER PRIMARY KEY,
            recorded_at TEXT NOT NULL,
            payload TEXT NOT NULL,
            previous_hash TEXT NOT NULL,
            event_hash TEXT NOT NULL
        )''')

    def close(self):
        self._db.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    @staticmethod
    def _hash(sequence, recorded_at, payload, previous):
        encoded = json.dumps([sequence, recorded_at, payload, previous], separators=(',', ':'))
        return sha256(encoded.encode()).hexdigest()

    def _replay(self):
        ledger = Ledger()
        previous = ''
        for expected, row in enumerate(self._db.execute(
                'SELECT sequence, recorded_at, payload, previous_hash, event_hash FROM events ORDER BY sequence'), 1):
            sequence, timestamp, payload, parent, digest = row
            if sequence != expected or parent != previous or digest != self._hash(sequence, timestamp, payload, parent):
                raise ValueError('Scientific memory integrity check failed')
            event = json.loads(payload)
            if event['event'] == 'register':
                ledger.register(Claim(event['id'], event['text'], tuple(event['sources']),
                                      status=EpistemicStatus(event['status'])))
            elif event['event'] == 'link':
                ledger.link(Relation(event['id'], event['source'], event['target'],
                                     RelationType(event['kind']), tuple(event['evidence']),
                                     EpistemicStatus(event['status'])))
            elif event['event'] == 'advance':
                ledger.advance(event['id'], Stage(event['stage']), event['artifact'],
                               event['reviewer'], event['producer'])
            else:
                raise ValueError('Unknown scientific memory event')
            previous = digest
        return ledger, previous

    def _write(self, operation):
        self._db.execute('BEGIN IMMEDIATE')
        try:
            ledger, parent = self._replay()
            result = operation(ledger)
            payload = ledger.events[-1]
            sequence = len(ledger.events)
            timestamp = datetime.now(timezone.utc).isoformat()
            digest = self._hash(sequence, timestamp, payload, parent)
            self._db.execute('INSERT INTO events VALUES (?, ?, ?, ?, ?)',
                             (sequence, timestamp, payload, parent, digest))
            self._db.execute('COMMIT')
            return result
        except BaseException:
            self._db.execute('ROLLBACK')
            raise

    def register(self, claim):
        """Atomically validate and persist a new D0 claim."""
        self._write(lambda ledger: ledger.register(claim))
        return claim

    def advance(self, claim_id, target, artifact, reviewer, producer):
        return self._write(lambda ledger: ledger.advance(claim_id, target, artifact, reviewer, producer))

    def link(self, relation):
        return self._write(lambda ledger: ledger.link(relation))

    def relations(self, claim_id, direction="both", kind=None):
        ledger, _ = self._replay()
        return ledger.relations(claim_id, direction, kind)

    def get(self, claim_id):
        ledger, _ = self._replay()
        return ledger.get(claim_id)

    def verify(self):
        """Validate the retained chain and replay all governance constraints."""
        self._replay()
        return True

    def history(self, claim_id):
        """Return provenance events for a claim after validating the whole log."""
        ledger, _ = self._replay()
        events = [json.loads(payload) for payload in ledger.events]
        ledger.get(claim_id)
        return tuple(event for event in events if (
            event['event'] != 'link' and event['id'] == claim_id) or (
            event['event'] == 'link' and claim_id in (event['source'], event['target'])))
