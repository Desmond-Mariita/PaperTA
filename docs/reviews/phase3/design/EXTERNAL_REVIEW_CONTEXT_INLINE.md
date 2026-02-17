# Phase 3 Design Snapshot

## ADR

```text
# ADR-003: Phase 3 Reviewer Mode + Verification Loop

- Status: Accepted
- Date: 2026-02-17
- Phase: 3

## Context

Phase 2 delivered deterministic Teach Mode artifacts. Phase 3 adds Reviewer Mode with evidence-linked critique and explicit claim verification outputs.

## Decision

Implement a deterministic Reviewer Mode pipeline with these components:

1. `CritiqueService`: generates strengths/weaknesses and threats to validity with chunk citations.
2. `ReproducibilityService`: emits a checklist with status and evidence anchors.
3. `ClaimMatrixService`: produces claim-evidence rows with support grade.
4. `ReviewerPipeline`: orchestrates ingestion, retrieval, reviewer artifact generation, and observability metadata.

Reviewer Mode outputs are immutable and grounded, with explicit fallback behavior when unsupported.

## Alternatives Considered

1. Free-form reviewer chat with no structured schema.
- Rejected due weak auditability and difficult downstream verification.

2. Binary support/no-support matrix only.
- Rejected because reviewer workflows need uncertainty classes (`supported`, `mixed`, `unsupported`).

## Consequences

Positive:

- Enables evidence-linked peer-review style outputs.
- Improves traceability for critique and reproducibility checks.

Negative:

- Initial support grading is lexical and conservative.
- Deeper statistical-method checks are deferred to later phases.

## Validation Plan

1. Unit tests for claim matrix and reproducibility checklist generation.
2. Integration test for end-to-end reviewer pipeline outputs.
3. Negative tests for invalid mode and unsupported claims behavior.
```

## Runtime Contract

```text
# PHASE3 Runtime Contract

## Scope

Phase 3 delivers deterministic Reviewer Mode artifacts built on ingestion and retrieval outputs.

## Functional Requirements

1. Reviewer pipeline accepts paper sections and a review query.
2. Critique output includes strengths, weaknesses, and threats to validity with citation chunk IDs.
3. Reproducibility checklist includes item label, status, notes, and citation chunk IDs.
4. Claim-evidence matrix includes claim text, evidence chunk IDs, support grade, and notes.
5. Unsupported reviewer responses must use exact text `Not stated in the paper.` when evidence is missing.
6. Mode is constrained to `reviewer`.

## Non-Functional Requirements

1. Determinism: identical inputs produce identical reviewer artifacts.
2. Groundedness: reviewer claims include citation chunk IDs or explicit unsupported fallback.
3. Auditability: result includes retrieval trace and aggregate reviewer counters.

## Interfaces

1. `run_phase3_reviewer_pipeline(paper_id, sections, review_query, mode="reviewer", top_k) -> ReviewerPipelineResult`
2. `generate_critique(retrieval_result) -> CritiqueArtifact`
3. `generate_reproducibility_checklist(retrieval_result) -> ReproducibilityChecklist`
4. `generate_claim_evidence_matrix(retrieval_result) -> ClaimEvidenceMatrix`

## Invariants

1. Every non-fallback evidence reference maps to an ingested chunk ID.
2. Support grade is one of: `supported`, `mixed`, `unsupported`.
3. Unsupported fallback uses exact text `Not stated in the paper.`.

## Failure Modes

1. Empty review query -> `ValueError`.
2. `top_k <= 0` -> `ValueError`.
3. Empty paper content -> `ValueError`.
4. Invalid mode (not `reviewer`) -> `ValueError`.
5. Retrieval empty set -> reviewer artifacts degrade gracefully with fallback entries.

## Observability

1. Reviewer pipeline result includes:
- `paper_id`
- `mode`
- `retrieval_trace`
- `retrieved_chunk_ids`
- `claim_count`
- `unsupported_claim_count`
- `reproducibility_item_count`

## Acceptance Gates

1. Unit + integration + negative tests pass.
2. Checklist verifies required files and tests.
3. Internal/external reviews complete with phase gate pass.
```

## Acceptance Checklist

```text
version: "1.0"
phase: 3

items:
  - id: D3-001
    requirement: "Phase 3 ADR exists"
    evidence:
      type: file_exists
      path: docs/adr/ADR-003-phase3-reviewer-mode-verification.md

  - id: D3-002
    requirement: "Phase 3 runtime contract exists"
    evidence:
      type: file_exists
      path: docs/contracts/PHASE3_RUNTIME_CONTRACT.md

  - id: D3-003
    requirement: "Phase 3 acceptance checklist exists"
    evidence:
      type: file_exists
      path: docs/checklists/PHASE3_ACCEPTANCE_CHECKLIST.yaml

  - id: C3-001
    requirement: "Reviewer mode module exists"
    evidence:
      type: file_exists
      path: src/paperta/reviewer.py

  - id: C3-002
    requirement: "Reviewer contracts module exists"
    evidence:
      type: file_exists
      path: src/paperta/reviewer_contracts.py

  - id: T3-UNIT-001
    requirement: "Claim matrix unit test exists"
    evidence:
      type: test_exists
      test_pattern: tests/unit/test_reviewer.py
      test_name: test_generate_claim_matrix_has_valid_support_grades

  - id: T3-UNIT-002
    requirement: "Reproducibility checklist unit test exists"
    evidence:
      type: test_exists
      test_pattern: tests/unit/test_reviewer.py
      test_name: test_generate_reproducibility_checklist_with_citations

  - id: T3-INT-001
    requirement: "Reviewer pipeline integration test exists"
    evidence:
      type: test_exists
      test_pattern: tests/integration/test_phase3_reviewer_pipeline.py
      test_name: test_phase3_pipeline_returns_grounded_reviewer_artifact

  - id: T3-NEG-001
    requirement: "Reviewer pipeline invalid query negative test exists"
    evidence:
      type: test_exists
      test_pattern: tests/negative/test_phase3_reviewer_negative.py
      test_name: test_phase3_pipeline_rejects_empty_review_query

  - id: T3-NEG-002
    requirement: "Reviewer fallback negative test exists"
    evidence:
      type: test_exists
      test_pattern: tests/negative/test_phase3_reviewer_negative.py
      test_name: test_claim_matrix_returns_not_stated_when_no_evidence
```
