"""Small, explicit governance primitives; evidence content requires external review."""
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from hashlib import sha256
import json
import math

class EpistemicStatus(str, Enum):
    OBSERVED = "Observed"
    ESTABLISHED = "Established"
    DERIVED = "Derived"
    SUPPORTED = "Supported"
    CONJECTURED = "Conjectured"
    SPECULATIVE = "Speculative"
    REJECTED = "Rejected"

class Stage(IntEnum):
    IDEA = 0
    CONJECTURE = 1
    FORMAL_MODEL = 2
    DERIVED_PREDICTION = 3
    COMPUTATIONALLY_REPRODUCED = 4
    INDEPENDENTLY_VERIFIED = 5
    EMPIRICALLY_SUPPORTED = 6

@dataclass(frozen=True)
class Claim:
    id: str
    text: str
    sources: tuple[str, ...]
    stage: Stage = Stage.IDEA
    status: EpistemicStatus = EpistemicStatus.SPECULATIVE

    def __post_init__(self):
        if not isinstance(self.stage, Stage) or not isinstance(self.status, EpistemicStatus):
            raise ValueError("Use explicit stage and epistemic enums")
        if not self.id.strip() or not self.text.strip() or not self.sources or any(not s.strip() for s in self.sources):
            raise ValueError("Claim identifier, text, and provenance are required")

class RelationType(str, Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    DEPENDS_ON = "depends_on"
    DERIVED_FROM = "derived_from"

@dataclass(frozen=True)
class Relation:
    id: str
    source: str
    target: str
    kind: RelationType
    evidence: tuple[str, ...]
    status: EpistemicStatus = EpistemicStatus.CONJECTURED

    def __post_init__(self):
        if not isinstance(self.kind, RelationType) or not isinstance(self.status, EpistemicStatus):
            raise ValueError("Use explicit relation type and epistemic status")
        if any(not isinstance(value, str) or not value.strip() for value in (self.id, self.source, self.target)):
            raise ValueError("Relation ID and endpoint IDs are required")
        if not isinstance(self.evidence, tuple) or not self.evidence or any(
                not isinstance(value, str) or not value.strip() for value in self.evidence):
            raise ValueError("Immutable evidence references are required")
        if self.source == self.target:
            raise ValueError("Self-relations are not supported")

@dataclass
class Ledger:
    """In-memory hash-linked audit trail. Not an immutable production store."""
    _claims: dict[str, Claim] = field(default_factory=dict, init=False, repr=False)
    _events: list[str] = field(default_factory=list, init=False, repr=False)
    _relations: dict[str, Relation] = field(default_factory=dict, init=False, repr=False)
    _sources: dict = field(default_factory=dict, init=False, repr=False)

    @property
    def events(self):
        return tuple(self._events)

    def _append(self, payload):
        previous = sha256(self._events[-1].encode()).hexdigest() if self._events else None
        self._events.append(json.dumps({"previous": previous, **payload}, sort_keys=True))

    def claims(self):
        return tuple(self._claims.values())

    def all_relations(self):
        return tuple(self._relations.values())

    def get(self, claim_id: str):
        """Return the immutable current claim record."""
        return self._claims[claim_id]

    def register(self, claim: Claim):
        if claim.id in self._claims:
            raise ValueError("Duplicate claim identifier")
        if claim.stage != Stage.IDEA or claim.status not in (EpistemicStatus.SPECULATIVE, EpistemicStatus.CONJECTURED):
            raise ValueError("New research claims must enter at D0 without established status")
        self._claims[claim.id] = claim
        self._append({"event": "register", "id": claim.id, "text": claim.text, "sources": claim.sources, "status": claim.status.value})

    def add_source(self, source):
        from .ingestion import ScientificSource
        if not isinstance(source, ScientificSource):
            raise ValueError("Expected a validated scientific source")
        if source.id in self._sources:
            raise ValueError("Duplicate source identifier")
        self._sources[source.id] = source
        self._append({"event": "source", "id": source.id, "title": source.title,
                      "locator": source.locator, "kind": source.kind.value,
                      "domains": [d.value for d in source.domains],
                      "content_sha256": source.content_sha256})
        return source

    def get_source(self, source_id):
        return self._sources[source_id]

    def link(self, relation: Relation):
        """Record an asserted directed relation without promoting either claim."""
        if relation.id in self._relations:
            raise ValueError("Duplicate relation identifier")
        self.get(relation.source)
        self.get(relation.target)
        self._relations[relation.id] = relation
        self._append({"event": "link", "id": relation.id, "source": relation.source,
                      "target": relation.target, "kind": relation.kind.value,
                      "evidence": relation.evidence, "status": relation.status.value})
        return relation

    def relations(self, claim_id: str, direction="both", kind=None):
        """Return direct edges in insertion order; no scientific inference occurs."""
        self.get(claim_id)
        if direction not in ("incoming", "outgoing", "both"):
            raise ValueError("Direction must be incoming, outgoing, or both")
        if kind is not None and not isinstance(kind, RelationType):
            raise ValueError("Use an explicit relation type")
        return tuple(r for r in self._relations.values()
                     if (kind is None or r.kind == kind) and (
                         (direction in ("outgoing", "both") and r.source == claim_id) or
                         (direction in ("incoming", "both") and r.target == claim_id)))

    def advance(self, claim_id: str, target: Stage, artifact: str, reviewer: str, producer: str):
        from dataclasses import replace
        current = self._claims[claim_id]
        if not isinstance(target, Stage) or int(target) != int(current.stage) + 1:
            raise ValueError("Discovery stages must advance sequentially")
        if not artifact.strip() or not reviewer.strip() or not producer.strip():
            raise ValueError("Evidence artifact, producer, and reviewer are required")
        if target >= Stage.INDEPENDENTLY_VERIFIED and reviewer.casefold().strip() == producer.casefold().strip():
            raise ValueError("Independent verification requires a distinct reviewer")
        self._claims[claim_id] = replace(current, stage=target)
        self._append({"event": "advance", "id": claim_id, "stage": int(target), "artifact": artifact, "reviewer": reviewer, "producer": producer})
        return self._claims[claim_id]

@dataclass(frozen=True)
class Action:
    name: str
    information_gain: float
    scientific_impact: float
    evidentiary_value: float
    uncertainty_reduction: float
    cost: float
    risk: float

    def utility(self, weights=(1.0, 1.0, 1.0)):
        values = (self.information_gain, self.scientific_impact, self.evidentiary_value, self.uncertainty_reduction, self.cost, self.risk)
        if len(weights) != 3 or any(not math.isfinite(v) or v < 0 for v in (*values, *weights)):
            raise ValueError("Estimates and weights must be finite and nonnegative")
        denominator = self.cost + self.risk
        if denominator <= 0:
            raise ValueError("Cost plus risk must be positive")
        result = (self.information_gain + sum(w*v for w,v in zip(weights, values[1:4]))) / denominator
        if not math.isfinite(result):
            raise ValueError("Utility must be finite")
        return result

def select_action(actions, weights=(1.0, 1.0, 1.0)):
    candidates = list(actions)
    if not candidates:
        raise ValueError("At least one action is required")
    return max(candidates, key=lambda a: a.utility(weights))
