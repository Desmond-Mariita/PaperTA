You are an external reviewer. Review the provided phase artifacts.

Treat the context content embedded in this prompt as the full source of truth.
Do not browse files, tools, or external resources.

Rules:
1. Return findings with severity: CRITICAL, MAJOR, MINOR, NIT.
2. Quote exact evidence with file references.
3. If no issues, state "No critical findings."
4. Focus on correctness, consistency, security, and test completeness.

Required output sections:
- Summary
- Findings
- Open Questions
- Final Verdict


## Context File

docs/reviews/phase1/design/EXTERNAL_REVIEW_CONTEXT_INLINE.md

## Context Content

```text
# Phase 1 Design Snapshot

Use only this inline content. Do not access tools or files.

## ADR
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

## CONTRACT
# PHASE1 Runtime Contract

## Scope

Phase 1 delivers deterministic ingestion and grounded summary generation for a single paper.

## Functional Requirements

1. Ingestion accepts paper text and section labels.
2. Text is normalized deterministically.
3. Structural chunks preserve section association and stable chunk IDs.
4. Chunk ID generation uses content-hash scheme:
   - `sha256("{paper_id}|{section}|{normalized_chunk_text}")[:16]`
5. Duplicate section labels are invalid input and raise `ValueError`.
6. Retrieval returns top-k chunk matches for a query.
7. Summary output contains bullets with citation anchors to chunk IDs.
8. Unsupported statements are rendered as `Not stated in the paper.`
9. Phase 1 mode is constrained to `summary`.

## Non-Functional Requirements

1. Determinism: same input/config returns same chunk IDs and summary text.
2. Auditability: pipeline output includes retrieval trace and chunk IDs.
3. Fail-safe: invalid inputs raise explicit errors; no silent defaults.

## Interfaces

1. `ingest_document(paper_id, sections) -> IngestedPaper`
2. `retrieve(query, ingested_paper, top_k) -> RetrievalResult`
3. `generate_summary(ingested_paper, retrieval_result, mode="summary") -> GroundedSummary`
4. `run_phase1_pipeline(paper_id, sections, query, mode="summary", top_k) -> PipelineResult`

## Invariants

1. Every summary bullet has one or more `chunk_ids`, unless text is exactly `Not stated in the paper.`
2. Chunk IDs are stable across identical runs.
3. No bullet may cite a chunk ID absent from the ingested corpus.

## Failure Modes

1. Empty paper content -> `ValueError`.
2. Empty query -> `ValueError`.
3. `top_k <= 0` -> `ValueError`.
4. Retrieval empty set -> summary contains only `Not stated in the paper.`
5. Duplicate section labels -> `ValueError`.
6. Invalid mode (not `summary`) -> `ValueError`.

## Observability

1. Pipeline result includes:
- `paper_id`
- `mode`
- `retrieved_chunk_ids`
- `summary_bullet_count`
- `unsupported_bullet_count`

## Acceptance Gates

1. Unit + integration + negative tests pass.
2. Checklist verifies required files and tests.
3. Internal/external reviews complete with phase gate pass.

## CHECKLIST
version: "1.1"
phase: 1

items:
  - id: D-001
    requirement: "Phase 1 ADR exists"
    evidence:
      type: file_exists
      path: docs/adr/ADR-001-phase1-ingestion-grounded-summary.md

  - id: D-002
    requirement: "Phase 1 runtime contract exists"
    evidence:
      type: file_exists
      path: docs/contracts/PHASE1_RUNTIME_CONTRACT.md

  - id: D-003
    requirement: "Phase 1 acceptance checklist exists"
    evidence:
      type: file_exists
      path: docs/checklists/PHASE1_ACCEPTANCE_CHECKLIST.yaml

  - id: C-001
    requirement: "Contracts module exists"
    evidence:
      type: file_exists
      path: src/paperta/contracts.py

  - id: C-002
    requirement: "Ingestion service module exists"
    evidence:
      type: file_exists
      path: src/paperta/ingestion.py

  - id: C-003
    requirement: "Retrieval service module exists"
    evidence:
      type: file_exists
      path: src/paperta/retrieval.py

  - id: C-004
    requirement: "Summary service module exists"
    evidence:
      type: file_exists
      path: src/paperta/summary.py

  - id: C-005
    requirement: "Pipeline module exists"
    evidence:
      type: file_exists
      path: src/paperta/pipeline.py

  # Three-Test Rule matrix (component-level)
  - id: T-INGEST-UNIT-001
    requirement: "Ingestion unit test exists"
    evidence:
      type: test_exists
      test_pattern: tests/unit/test_ingestion.py
      test_name: test_chunking_assigns_stable_chunk_ids

  - id: T-INGEST-INT-001
    requirement: "Ingestion integration test exists"
    evidence:
      type: test_exists
      test_pattern: tests/integration/test_phase1_pipeline.py
      test_name: test_pipeline_uses_ingestion_section_order

  - id: T-INGEST-NEG-001
    requirement: "Ingestion negative test exists"
    evidence:
      type: test_exists
      test_pattern: tests/negative/test_ingestion_negative.py
      test_name: test_ingestion_rejects_duplicate_sections

  - id: T-RETRIEVE-UNIT-001
    requirement: "Retrieval unit test exists"
    evidence:
      type: test_exists
      test_pattern: tests/unit/test_retrieval.py
      test_name: test_retrieval_orders_by_overlap_score

  - id: T-RETRIEVE-INT-001
    requirement: "Retrieval integration test exists"
    evidence:
      type: test_exists
      test_pattern: tests/integration/test_phase1_pipeline.py
      test_name: test_pipeline_retrieval_trace_contains_chunk_ids

  - id: T-RETRIEVE-NEG-001
    requirement: "Retrieval negative test exists"
    evidence:
      type: test_exists
      test_pattern: tests/negative/test_retrieval_negative.py
      test_name: test_retrieval_rejects_non_positive_top_k

  - id: T-SUMMARY-UNIT-001
    requirement: "Summary unit test exists"
    evidence:
      type: test_exists
      test_pattern: tests/unit/test_summary.py
      test_name: test_summary_bullets_include_citations

  - id: T-SUMMARY-INT-001
    requirement: "Summary integration test exists"
    evidence:
      type: test_exists
      test_pattern: tests/integration/test_phase1_pipeline.py
      test_name: test_phase1_pipeline_generates_grounded_summary

  - id: T-SUMMARY-NEG-001
    requirement: "Summary negative test exists"
    evidence:
      type: test_exists
      test_pattern: tests/negative/test_summary_negative.py
      test_name: test_summary_returns_not_stated_when_no_evidence

  # Contract failure modes coverage
  - id: F-001
    requirement: "Failure mode: empty paper content raises ValueError"
    evidence:
      type: test_exists
      test_pattern: tests/negative/test_pipeline_negative.py
      test_name: test_pipeline_rejects_empty_paper

  - id: F-002
    requirement: "Failure mode: empty query raises ValueError"
    evidence:
      type: test_exists
      test_pattern: tests/negative/test_pipeline_negative.py
      test_name: test_pipeline_rejects_empty_query

  - id: F-003
    requirement: "Failure mode: top_k <= 0 raises ValueError"
    evidence:
      type: test_exists
      test_pattern: tests/negative/test_retrieval_negative.py
      test_name: test_retrieval_rejects_non_positive_top_k

  - id: F-004
    requirement: "Failure mode: empty retrieval yields Not stated in the paper"
    evidence:
      type: test_exists
      test_pattern: tests/negative/test_summary_negative.py
      test_name: test_summary_returns_not_stated_when_no_evidence

  - id: F-005
    requirement: "Failure mode: duplicate section labels raise ValueError"
    evidence:
      type: test_exists
      test_pattern: tests/negative/test_ingestion_negative.py
      test_name: test_ingestion_rejects_duplicate_sections

  - id: F-006
    requirement: "Failure mode: invalid mode raises ValueError"
    evidence:
      type: test_exists
      test_pattern: tests/negative/test_pipeline_negative.py
      test_name: test_pipeline_rejects_invalid_mode

```
