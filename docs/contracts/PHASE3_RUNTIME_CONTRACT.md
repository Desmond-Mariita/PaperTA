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
