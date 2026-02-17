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

docs/reviews/phase4/design/EXTERNAL_REVIEW_CONTEXT_INLINE.md

## Context Content

```text
# Phase 4 Design Snapshot

## ADR

```text
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
```

## Runtime Contract

```text
# PHASE4 Runtime Contract

## Scope

Phase 4 delivers deterministic multi-paper intelligence artifacts on top of per-paper ingestion/retrieval.

## Functional Requirements

1. Multi-paper pipeline accepts a non-empty set of paper inputs and a cross-paper query.
2. Concept linker emits local concept entries with canonical global concept IDs.
3. Consensus output labels claims as one of: `supporting`, `contradicting`, `mixed`, `insufficient evidence`.
4. Cross-paper graph includes paper-concept and paper-paper relationship edges with evidence anchors.
5. Unsupported outputs use exact text `Not stated in the paper.` when evidence is missing.
6. Mode is constrained to `multi_paper`.

## Non-Functional Requirements

1. Determinism: identical paper set/query produces identical outputs.
2. Groundedness: all non-fallback entries include citation chunk IDs.
3. Auditability: result includes per-paper retrieval traces and aggregate counters.

## Interfaces

1. `run_phase4_multi_paper_pipeline(papers, query, mode="multi_paper", top_k) -> MultiPaperPipelineResult`
2. `link_concepts(paper_results) -> ConceptLinkResult`
3. `build_consensus_matrix(paper_results) -> ConsensusMatrix`
4. `build_cross_paper_graph(paper_results, concept_links) -> CrossPaperGraph`

## Invariants

1. Every non-fallback evidence reference maps to ingested chunk IDs from one of the input papers.
2. Consensus labels are restricted to declared enum values.
3. Fallback text is exact: `Not stated in the paper.`.

## Failure Modes

1. Empty paper set -> `ValueError`.
2. Empty query -> `ValueError`.
3. `top_k <= 0` -> `ValueError`.
4. Invalid mode (not `multi_paper`) -> `ValueError`.
5. Empty retrieval across all papers -> artifacts degrade gracefully with fallback entries.

## Observability

1. Multi-paper result includes:
- `mode`
- `paper_count`
- `per_paper_retrieval`
- `consensus_claim_count`
- `graph_edge_count`
- `unsupported_entry_count`

## Acceptance Gates

1. Unit + integration + negative tests pass.
2. Checklist verifies required files and tests.
3. Internal/external reviews complete with phase gate pass.
```

## Acceptance Checklist

```text
version: "1.0"
phase: 4

items:
  - id: D4-001
    requirement: "Phase 4 ADR exists"
    evidence:
      type: file_exists
      path: docs/adr/ADR-004-phase4-multi-paper-intelligence.md

  - id: D4-002
    requirement: "Phase 4 runtime contract exists"
    evidence:
      type: file_exists
      path: docs/contracts/PHASE4_RUNTIME_CONTRACT.md

  - id: D4-003
    requirement: "Phase 4 acceptance checklist exists"
    evidence:
      type: file_exists
      path: docs/checklists/PHASE4_ACCEPTANCE_CHECKLIST.yaml

  - id: C4-001
    requirement: "Multi-paper module exists"
    evidence:
      type: file_exists
      path: src/paperta/multi_paper.py

  - id: C4-002
    requirement: "Multi-paper contracts module exists"
    evidence:
      type: file_exists
      path: src/paperta/multi_paper_contracts.py

  - id: T4-UNIT-001
    requirement: "Concept linker unit test exists"
    evidence:
      type: test_exists
      test_pattern: tests/unit/test_multi_paper.py
      test_name: test_link_concepts_assigns_canonical_ids

  - id: T4-UNIT-002
    requirement: "Consensus matrix unit test exists"
    evidence:
      type: test_exists
      test_pattern: tests/unit/test_multi_paper.py
      test_name: test_build_consensus_matrix_has_valid_labels

  - id: T4-INT-001
    requirement: "Multi-paper pipeline integration test exists"
    evidence:
      type: test_exists
      test_pattern: tests/integration/test_phase4_multi_paper_pipeline.py
      test_name: test_phase4_pipeline_returns_grounded_multi_paper_artifact

  - id: T4-NEG-001
    requirement: "Multi-paper invalid paper set negative test exists"
    evidence:
      type: test_exists
      test_pattern: tests/negative/test_phase4_multi_paper_negative.py
      test_name: test_phase4_pipeline_rejects_empty_paper_set

  - id: T4-NEG-002
    requirement: "Multi-paper fallback negative test exists"
    evidence:
      type: test_exists
      test_pattern: tests/negative/test_phase4_multi_paper_negative.py
      test_name: test_consensus_returns_insufficient_when_no_evidence
```

```
