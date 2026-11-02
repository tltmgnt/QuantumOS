# Local ingestion schema v1

The JSON root requires exactly `schema_version`, `sources`, `claims`, and `relations`. Version must be integer 1; collections must be arrays. At least one record is required. See `examples/research_bundle.json` for a complete fixture.

| Record | Exact fields |
|---|---|
| Source | id, title, locator, kind, domains, content_sha256 |
| Claim | id, text, sources, status |
| Relation | id, source, target, kind, evidence, status |

Source kinds and domains are controlled enums defined in `quantum_omega.ingestion`. Domains must be a nonempty, duplicate-free list. Source fingerprints require 64 lowercase hexadecimal characters. Locators are retained as supplied and are never opened. Text fields and reference lists cannot be empty.

Claims must reference registered sources and enter D0 as Speculative or Conjectured. Relations must reference existing claims, use an existing RelationType, and cite registered sources in their evidence lists. Relations carry their own explicit EpistemicStatus; this supplied label does not establish its scientific truth. Self-links and duplicate IDs within each record namespace are rejected. Source, claim, and relation namespaces are separate.

The importer parses before writing, then applies all source, claim, and relation events in one SQLite transaction. Any validation, duplicate, or reference error rolls back all new events. Duplicate bundles are rejected rather than silently overwritten. Existing registered sources and claims can be referenced by later bundles.

`ScientificMemory.ingest(bundle)` returns counts of sources, claims, and relations. `get_source(id)` returns immutable source metadata. Claim history retains source IDs; resolve them with get_source to retrieve locators and fingerprints. Legacy direct register/link APIs still permit unregistered references and are not equivalent to strict ingestion.

Existing logs need no schema migration. New source events, like graph link events, cannot be replayed by older versions of the code. Full event replay targets small logs; the existing hash-chain threat model remains unchanged. Literature retrieval, PDF extraction, credibility evaluation, content-hash verification, and automatic classification are not implemented.
