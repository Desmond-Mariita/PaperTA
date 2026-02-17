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
- `retrieval_trace`
- `retrieved_chunk_ids`
- `summary_bullet_count`
- `unsupported_bullet_count`

## Acceptance Gates

1. Unit + integration + negative tests pass.
2. Checklist verifies required files and tests.
3. Internal/external reviews complete with phase gate pass.
