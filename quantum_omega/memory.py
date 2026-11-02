"""Transactional, event-sourced scientific memory using the standard library."""
from datetime import datetime, timezone
from hashlib import sha256
import json
import sqlite3
from .core import Claim, EpistemicStatus, Ledger, Relation, RelationType, Stage
from .ingestion import Domain, ScientificSource, SourceKind, parse_bundle


class ScientificMemory:
    """Persist governance events; hashes detect edits, not privileged rewrites."""

    def __init__(self, path, *, read_only=False):
        if read_only:
            from pathlib import Path
            self._db = sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro', uri=True, isolation_level=None)
            return
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
            if event['event'] == 'source':
                ledger.add_source(ScientificSource(event['id'], event['title'], event['locator'],
                    SourceKind(event['kind']), tuple(Domain(d) for d in event['domains']), event['content_sha256']))
            elif event['event'] == 'register':
                ledger.register(Claim(event['id'], event['text'], tuple(event['sources']),
                                      status=EpistemicStatus(event['status'])))
            elif event['event'] == 'link':
                ledger.link(Relation(event['id'], event['source'], event['target'],
                                     RelationType(event['kind']), tuple(event['evidence']),
                                     EpistemicStatus(event['status'])))
            elif event['event'] == 'reject':
                ledger.reject(event['id'], event['reason'], event['artifact'])
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
            offset = len(ledger.events)
            result = operation(ledger)
            for sequence, payload in enumerate(ledger.events[offset:], offset + 1):
                timestamp = datetime.now(timezone.utc).isoformat()
                digest = self._hash(sequence, timestamp, payload, parent)
                self._db.execute('INSERT INTO events VALUES (?, ?, ?, ?, ?)',
                                 (sequence, timestamp, payload, parent, digest))
                parent = digest
            self._db.execute('COMMIT')
            return result
        except BaseException:
            self._db.execute('ROLLBACK')
            raise

    def snapshot(self):
        """Return immutable claim/relationship records from one verified replay."""
        ledger, _ = self._replay()
        return ledger.claims(), ledger.all_relations()

    def sources(self):
        ledger, _ = self._replay()
        return ledger.sources()

    def get_source(self, source_id):
        ledger, _ = self._replay()
        return ledger.get_source(source_id)

    def ingest(self, bundle):
        """Atomically ingest a versioned local bundle with registered provenance."""
        sources, claims, relations = parse_bundle(bundle)
        def apply(ledger):
            for source in sources:
                ledger.add_source(source)
            for claim in claims:
                for source_id in claim.sources:
                    ledger.get_source(source_id)
                ledger.register(claim)
            for relation in relations:
                for evidence_id in relation.evidence:
                    ledger.get_source(evidence_id)
                ledger.link(relation)
            return {"sources": len(sources), "claims": len(claims), "relations": len(relations)}
        return self._write(apply)

    def register(self, claim):
        """Atomically validate and persist a new D0 claim."""
        self._write(lambda ledger: ledger.register(claim))
        return claim

    def reject(self, claim_id, reason, artifact):
        return self._write(lambda ledger: ledger.reject(claim_id, reason, artifact))

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
            event['event'] in ('register', 'advance', 'reject') and event['id'] == claim_id) or (
            event['event'] == 'link' and claim_id in (event['source'], event['target'])))
