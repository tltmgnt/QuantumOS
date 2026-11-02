"""Strict local JSON ingestion. Metadata validation does not validate science."""
from dataclasses import dataclass
from enum import Enum
import re
from .core import Claim, EpistemicStatus, Relation, RelationType


class SourceKind(str, Enum):
    LITERATURE = 'literature'
    OBSERVATION = 'observation'
    EXPERIMENT = 'experiment'
    SIMULATION = 'simulation'
    DERIVATION = 'derivation'


class Domain(str, Enum):
    MATHEMATICS = 'mathematics'
    QUANTUM = 'quantum'
    GRAVITY = 'gravity'
    INFORMATION = 'information'
    COMPUTATION = 'computation'


@dataclass(frozen=True)
class ScientificSource:
    id: str
    title: str
    locator: str
    kind: SourceKind
    domains: tuple[Domain, ...]
    content_sha256: str

    def __post_init__(self):
        if any(not isinstance(v, str) or not v.strip() for v in (self.id, self.title, self.locator)):
            raise ValueError('Source ID, title, and locator are required')
        if not isinstance(self.kind, SourceKind):
            raise ValueError('Unknown source kind')
        if not isinstance(self.domains, tuple) or not self.domains or any(not isinstance(d, Domain) for d in self.domains):
            raise ValueError('At least one controlled domain is required')
        if len(set(self.domains)) != len(self.domains):
            raise ValueError('Duplicate source domains')
        if not isinstance(self.content_sha256, str) or not re.fullmatch('[0-9a-f]{64}', self.content_sha256):
            raise ValueError('Source content SHA-256 must be 64 lowercase hex characters')


def _record(value, fields):
    if not isinstance(value, dict) or set(value) != set(fields):
        raise ValueError('Record fields must be exactly: '+', '.join(fields))
    return value


def _texts(value):
    if not isinstance(value, list) or not value or any(not isinstance(v, str) or not v.strip() for v in value):
        raise ValueError('Expected a nonempty array of nonempty strings')
    return tuple(value)


def parse_bundle(bundle):
    """Validate all records before any database writes; reject unknown fields."""
    _record(bundle, ('schema_version', 'sources', 'claims', 'relations'))
    if type(bundle['schema_version']) is not int or bundle['schema_version'] != 1:
        raise ValueError('Unsupported ingestion schema version')
    if any(not isinstance(bundle[k], list) for k in ('sources', 'claims', 'relations')):
        raise ValueError('Bundle collections must be arrays')
    sources, claims, relations = [], [], []
    for row in bundle['sources']:
        _record(row, ('id', 'title', 'locator', 'kind', 'domains', 'content_sha256'))
        sources.append(ScientificSource(row['id'], row['title'], row['locator'], SourceKind(row['kind']),
                                        tuple(Domain(d) for d in _texts(row['domains'])), row['content_sha256']))
    for row in bundle['claims']:
        _record(row, ('id', 'text', 'sources', 'status'))
        if any(not isinstance(row[k], str) or not row[k].strip() for k in ('id', 'text')):
            raise ValueError('Claim ID and text must be nonempty strings')
        claims.append(Claim(row['id'], row['text'], _texts(row['sources']), status=EpistemicStatus(row['status'])))
    for row in bundle['relations']:
        _record(row, ('id', 'source', 'target', 'kind', 'evidence', 'status'))
        relations.append(Relation(row['id'], row['source'], row['target'], RelationType(row['kind']),
                                  _texts(row['evidence']), EpistemicStatus(row['status'])))
    if not (sources or claims or relations):
        raise ValueError('Empty ingestion bundle')
    return sources, claims, relations


def main():
    import argparse
    import json
    from pathlib import Path
    from .memory import ScientificMemory
    parser = argparse.ArgumentParser(description='Ingest a local QUANTUM-Ω JSON bundle')
    parser.add_argument('bundle', type=Path)
    parser.add_argument('--database', required=True, type=Path)
    args = parser.parse_args()
    try:
        bundle = json.loads(args.bundle.read_text(encoding='utf-8'))
        # Validate before opening or creating a database.
        parse_bundle(bundle)
        with ScientificMemory(args.database) as memory:
            result = memory.ingest(bundle)
        print(json.dumps(result, sort_keys=True))
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(2, f'Ingestion failed: {error}\n')


if __name__ == '__main__':
    main()
