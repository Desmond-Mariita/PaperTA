# ADR-004: Phase 4 Multi-Paper Intelligence

- Status: Accepted
- Date: 2026-02-17
- Phase: 4

## Context

Phase 3 delivered deterministic reviewer artifacts for a single paper. Phase 4 adds multi-paper intelligence for cross-paper concept and claim analysis.

## Decision

Implement a deterministic Multi-Paper pipeline with these components:

1. `ConceptLinkerService`: extracts local concepts from each paper and maps them to canonical global concept IDs.
2. `ConsensusService`: computes cross-paper claim consensus labels (`supporting`, `contradicting`, `mixed`, `insufficient evidence`).
3. `CrossPaperGraphService`: emits deterministic edges between papers and canonical concepts.
4. `MultiPaperPipeline`: orchestrates per-paper ingestion/retrieval and aggregate multi-paper artifacts.

## Alternatives Considered

1. Fully embedding-based concept linker only.
- Rejected for initial phase due deterministic-auditability requirements.

2. Unstructured cross-paper summary text.
- Rejected because comparative workflows need machine-checkable structures.

## Consequences

Positive:

- Enables comparative reviewer workflows.
- Introduces canonical concept anchors for cross-paper analysis.

Negative:

- Initial linker is lexical and conservative.
- Contradiction detection remains heuristic in core phase.

## Validation Plan

1. Unit tests for concept linking and consensus classification.
2. Integration test for end-to-end multi-paper pipeline outputs.
3. Negative tests for invalid mode and empty-paper-set handling.
