# ADR-002: Phase 2 Teach Mode Core

- Status: Accepted
- Date: 2026-02-17
- Phase: 2

## Context

Phase 1 delivered deterministic ingestion, retrieval, and grounded summaries.
Phase 2 adds Teach Mode with guided explanations and learner validation while preserving grounding and no-guessing behavior.

## Decision

Implement a deterministic Teach Mode pipeline with these components:

1. `PrerequisiteService`: derives prerequisite concepts from retrieved evidence.
2. `ConceptMapService`: builds evidence-linked concept nodes and edges.
3. `QuizService`: generates MCQ/short-answer quiz items grounded in chunk evidence.
4. `SocraticService`: answers follow-up questions using retrieval-constrained context.

Teach Mode outputs are structured and immutable, with citation anchors per concept and explanation step.

## Alternatives Considered

1. Free-form chat-only teach mode.
- Rejected due weak auditability and unclear evidence linking.

2. LLM-generated concept maps without explicit citation fields.
- Rejected because concept explanations would not be externally verifiable.

## Consequences

Positive:

- Stronger pedagogical UX while retaining traceability.
- Deterministic, testable teach artifacts.

Negative:

- Initial teach content quality is rule-based and limited versus full semantic/graph models.
- Adaptive difficulty beyond static quiz generation deferred.

## Validation Plan

1. Unit tests for prerequisite extraction, concept mapping, quiz construction, and socratic constraints.
2. Integration tests for end-to-end teach mode pipeline with evidence-linked outputs.
3. Negative tests for missing context, invalid mode, and unsupported queries.
