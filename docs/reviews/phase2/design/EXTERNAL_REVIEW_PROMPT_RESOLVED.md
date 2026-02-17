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

docs/reviews/phase2/design/EXTERNAL_REVIEW_CONTEXT_INLINE.md

## Context Content

```text
# Phase 2 Design Snapshot

Use only this inline content. Do not access tools or files.

## ADR
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

## CONTRACT
# PHASE2 Runtime Contract

## Scope

Phase 2 delivers deterministic Teach Mode artifacts built on Phase 1 ingestion and retrieval outputs.

## Functional Requirements

1. Teach pipeline accepts paper sections and a learning objective query.
2. Prerequisite checklist includes concept label, reason, and citation chunk IDs.
3. Concept map includes nodes and edges with evidence anchors.
4. Step-by-step explanation contains ordered steps with citation chunk IDs.
5. Quiz includes MCQ and short-answer items with answer key and evidence anchors.
6. Socratic response is constrained to retrieved context and returns `Not stated in the paper.` if unsupported.
7. Mode is constrained to `teach`.

## Non-Functional Requirements

1. Determinism: same inputs/config produce identical Teach Mode artifacts.
2. Groundedness: all factual teaching claims include citation chunk IDs.
3. Auditability: result includes retrieval trace and concept/quiz evidence mappings.

## Interfaces

1. `run_phase2_teach_pipeline(paper_id, sections, objective, mode="teach", top_k) -> TeachPipelineResult`
2. `generate_prerequisites(retrieval_result) -> PrerequisiteChecklist`
3. `generate_concept_map(retrieval_result) -> ConceptMap`
4. `generate_explanation(retrieval_result) -> Explanation`
5. `generate_quiz(retrieval_result) -> Quiz`
6. `answer_socratic_question(ingested_paper, question, retrieval_result) -> SocraticAnswer`

## Invariants

1. Every concept/explanation/quiz evidence reference must map to an ingested chunk ID.
2. Unsupported socratic responses use exact text `Not stated in the paper.`
3. Quiz answer keys must correspond to generated options/prompts.

## Failure Modes

1. Empty objective -> `ValueError`.
2. `top_k <= 0` -> `ValueError`.
3. Empty paper content -> `ValueError`.
4. Invalid mode (not `teach`) -> `ValueError`.
5. Retrieval empty set -> teach artifacts degrade gracefully with `Not stated in the paper.` for unsupported fields.

## Observability

1. Teach pipeline result includes:
- `paper_id`
- `mode`
- `retrieval_trace`
- `retrieved_chunk_ids`
- `concept_count`
- `quiz_item_count`
- `unsupported_response_count`

## Acceptance Gates

1. Unit + integration + negative tests pass.
2. Checklist verifies required files and tests.
3. Internal/external reviews complete with phase gate pass.

## CHECKLIST
version: "1.0"
phase: 2

items:
  - id: D2-001
    requirement: "Phase 2 ADR exists"
    evidence:
      type: file_exists
      path: docs/adr/ADR-002-phase2-teach-mode-core.md

  - id: D2-002
    requirement: "Phase 2 runtime contract exists"
    evidence:
      type: file_exists
      path: docs/contracts/PHASE2_RUNTIME_CONTRACT.md

  - id: D2-003
    requirement: "Phase 2 acceptance checklist exists"
    evidence:
      type: file_exists
      path: docs/checklists/PHASE2_ACCEPTANCE_CHECKLIST.yaml

  - id: C2-001
    requirement: "Teach mode module exists"
    evidence:
      type: file_exists
      path: src/paperta/teach.py

  - id: C2-002
    requirement: "Teach contracts module exists"
    evidence:
      type: file_exists
      path: src/paperta/teach_contracts.py

  - id: T2-UNIT-001
    requirement: "Prerequisite generation unit test exists"
    evidence:
      type: test_exists
      test_pattern: tests/unit/test_teach.py
      test_name: test_generate_prerequisites_with_citations

  - id: T2-UNIT-002
    requirement: "Concept map unit test exists"
    evidence:
      type: test_exists
      test_pattern: tests/unit/test_teach.py
      test_name: test_generate_concept_map_links_nodes

  - id: T2-INT-001
    requirement: "Teach pipeline integration test exists"
    evidence:
      type: test_exists
      test_pattern: tests/integration/test_phase2_teach_pipeline.py
      test_name: test_phase2_pipeline_returns_grounded_teach_artifact

  - id: T2-NEG-001
    requirement: "Teach pipeline invalid objective negative test exists"
    evidence:
      type: test_exists
      test_pattern: tests/negative/test_phase2_teach_negative.py
      test_name: test_phase2_pipeline_rejects_empty_objective

  - id: T2-NEG-002
    requirement: "Socratic fallback negative test exists"
    evidence:
      type: test_exists
      test_pattern: tests/negative/test_phase2_teach_negative.py
      test_name: test_socratic_returns_not_stated_when_unsupported

```
