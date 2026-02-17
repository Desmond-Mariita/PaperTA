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
