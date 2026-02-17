# ADR-001: Phase 1 Ingestion and Grounded Summary Core

- Status: Accepted
- Date: 2026-02-17
- Phase: 1

## Context

PaperTA currently has governance, gates, and deployment scaffolding but no executable Phase 1 pipeline.
Phase 1 target is ingestion plus grounded summary generation with deterministic, evidence-linked output.

## Decision

Implement a Python backend core with the following components:

1. `DocumentIngestionService` for deterministic text normalization and structural chunking.
2. `RetrievalEngine` for section-aware lexical retrieval over chunk corpus.
3. `GroundedSummaryService` that outputs structured summary bullets with chunk citations.
4. Fail-closed behavior when no supporting evidence exists for a generated claim.

Data contracts will use frozen dataclasses to preserve deterministic behavior and immutability.

Chunking specification for Phase 1:

1. Input sections are processed in deterministic insertion order.
2. Chunk granularity is paragraph-level within each section.
3. Chunk IDs are content-addressed:
   - `chunk_id = sha256("{paper_id}|{section}|{normalized_chunk_text}")[:16]`
4. Duplicate section labels are rejected with `ValueError` to avoid ambiguous ordering.

## Alternatives Considered

1. Immediate full RAG + embeddings stack.
- Rejected for Phase 1 due complexity and infrastructure dependency.

2. LLM-only summarization with no retrieval contract.
- Rejected due weak groundedness and auditability.

## Consequences

Positive:

- Rapid delivery of a verifiable Phase 1 vertical slice.
- Deterministic replay and testable core behavior.

Negative:

- Retrieval quality is lexical baseline only in Phase 1.
- Advanced modes (Teach/Reviewer) deferred to later phases.

## Validation Plan

1. Unit tests for chunking, retrieval ranking, and summary formatting.
2. Integration test for end-to-end ingestion -> retrieval -> grounded summary pipeline.
3. Negative tests for missing evidence and malformed input.
