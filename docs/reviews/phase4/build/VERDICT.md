# Build Review Verdict — Phase 4

- Date: 2026-02-17
- Phase: 4
- Loop: build

### Feedback: Missing negative tests for empty query and top_k <= 0
Reviewer: Gemini External 1 / Claude External 2
Severity: MAJOR
Quote: "Missing test for empty query and top_k <= 0 validation paths"
Decision: ACCEPT
Reasoning: Contract-declared failure modes must be directly covered by negative tests.
Action Taken: Added `test_phase4_pipeline_rejects_empty_query` and `test_phase4_pipeline_rejects_non_positive_top_k` in `tests/negative/test_phase4_multi_paper_negative.py`; checklist items `F4-001` and `F4-002` added.

### Feedback: No unit test for cross-paper graph construction
Reviewer: Claude External 2
Severity: MAJOR
Quote: "No test for cross-paper graph construction (`build_cross_paper_graph`)"
Decision: ACCEPT
Reasoning: Interface-level unit coverage is required for relation semantics and evidence anchors.
Action Taken: Added `test_build_cross_paper_graph_emits_expected_edges` in `tests/unit/test_multi_paper.py`; checklist item `T4-UNIT-003` added.

### Feedback: Contradiction heuristic may produce false positives
Reviewer: Claude External 2
Severity: MAJOR
Quote: "Consensus label logic can produce 'contradicting' for benign text"
Decision: ACCEPT
Reasoning: Current phase intentionally uses heuristic contradiction detection; limitation must be explicit.
Action Taken: Added inline limitation comment in `src/paperta/multi_paper.py` and documented the heuristic limitation in `docs/contracts/PHASE4_RUNTIME_CONTRACT.md`.

### Feedback: Adjacent-only paper-pair relationship discovery in graph
Reviewer: Gemini External 1 / Claude External 2
Severity: MINOR
Quote: "only checks shared concepts between adjacent papers"
Decision: DEFER
Reasoning: O(n) adjacency traversal is an intentional deterministic core simplification for Phase 4; all-pairs expansion is a future enhancement.
Action Taken: No code change in Phase 4.

### Feedback: Single concept extraction per paper and evidence truncation limits
Reviewer: Claude External 2
Severity: MINOR
Quote: "only uses first retrieval hit" / "evidence_chunk_ids silently truncated"
Decision: DEFER
Reasoning: Current scope emphasizes deterministic baseline outputs; richer concept/evidence expansion is planned for future iterations.
Action Taken: No code change in Phase 4.

### Feedback: Fallback concept may create semantically weak shares_concept edges
Reviewer: Gemini External 1
Severity: NIT
Quote: "treating missing information as a shared topical concept"
Decision: DEFER
Reasoning: Existing behavior is deterministic and transparent; special-case filtering can be added in refinement phase.
Action Taken: No code change in Phase 4.
