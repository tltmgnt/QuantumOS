# Scientific governance
Epistemic labels and pipeline stages are separate dimensions. Computational reproduction is not empirical support. Formal verification proves a stated proposition under specified axioms and encodings; it does not establish those axioms as physical truth.

A trusted result needs source identifiers, assumptions, derivation, code and dataset versions, predictions, criticisms, verification and replication artifacts, and status history. Failed and retracted results must remain in the historical record.

Promotion requires evidence review. The prototype requires an artifact reference and distinct producer/reviewer strings for D5/D6, but cannot authenticate identities, inspect artifacts, establish independence, or enforce real human approval. It intentionally leaves epistemic status unchanged when advancing a stage. Production promotion must use signed identities, scientific review, protected storage, and human approval for consequential claims and experiments.

SQLite scientific memory now provides transactional persistence and retained-chain verification. It detects changed records and sequence gaps, but cannot detect removal of the trailing history or a coherently rewritten database without an externally trusted checkpoint. Source identifiers and artifact references are preserved without authenticating their content.

Claim rejection with reason and artifact history is implemented; rejected claims cannot be promoted. The integrated workflow retains counterexamples and recovery requirements. General invalidation propagation, hypothesis branching, access control, and experiment execution remain future work. Do not use this prototype as an autonomous discovery authority.

Relations have their own epistemic labels and evidence references. A supports or derived_from edge is an asserted relationship; it does not validate evidence, establish causality, or promote the endpoint claims. Relationship creation is transactional, checked against existing claims, and included in both endpoints’ provenance histories.

Structured ingestion requires registered source metadata for every imported claim source and relation evidence reference. Source fingerprints are supplied by the caller and are not checked against fetched content. Imported claims enter D0 with Speculative or Conjectured status only. Existing lower-level registration APIs continue to accept free-form references for compatibility. No automatic scientific validity or credibility is inferred from a successful import.

The integrated research workflow never automatically advances beyond D4. Restricted algebra certificates, shared-author alternate evaluators, and public synthetic holdouts do not meet independent scientific verification or empirical-support requirements. Every run reports scientific_discovery=false. Experiment proposals remain awaiting_human_review and have no execution adapter. A failure of the pre-holdout champion remains a failed benchmark result even if another candidate survives later selection.
