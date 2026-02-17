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
