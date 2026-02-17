# Build Review Verdict — Phase 1

- Date: 2026-02-17
- Phase: 1
- Loop: build

### Feedback: `generate_summary` interface mismatch with contract
Reviewer: Claude External 2
Severity: CRITICAL
Quote: "`generate_summary` signature deviates from the contract interface"
Decision: ACCEPT
Reasoning: Contract and runtime must match for enforcement of invariant checks.
Action Taken: Updated `src/paperta/summary.py` to accept `ingested_paper`; updated `src/paperta/pipeline.py` call path.

### Feedback: Invariant 3 not enforced
Reviewer: Claude External 2
Severity: MAJOR
Quote: "Invariant 3 is not enforced or tested"
Decision: ACCEPT
Reasoning: Grounded citation validity is a core invariant and must be runtime-validated.
Action Taken: Added unknown-chunk validation in `src/paperta/summary.py` and test `test_summary_rejects_unknown_chunk_ids` in `tests/unit/test_summary.py`; checklist updated.

### Feedback: Retrieval trace incomplete for auditability
Reviewer: Claude External 2
Severity: MAJOR
Quote: "no retrieval trace"
Decision: ACCEPT
Reasoning: Auditability requirement includes trace and chunk IDs.
Action Taken: Added `retrieval_trace` to `PipelineResult` in `src/paperta/contracts.py` and returned it in `src/paperta/pipeline.py`.

### Feedback: Retrieval tie-break ordering
Reviewer: Gemini External 1
Severity: MAJOR
Quote: "Retrieval Tie-Break Logic vs. Document Flow"
Decision: ACCEPT
Reasoning: Section-aware retrieval should preserve paper flow for equal-score hits.
Action Taken: Updated `src/paperta/retrieval.py` tie-break to use `section_order`; fixed integration test to validate equal-score ordering.

### Feedback: Integration test did not actually verify section-order tie-break
Reviewer: Gemini External 1
Severity: MAJOR
Quote: "Integration Test `test_pipeline_uses_ingestion_section_order` is Invalid"
Decision: ACCEPT
Reasoning: Test must target the intended behavior directly.
Action Taken: Updated `tests/integration/test_phase1_pipeline.py` to use equal-score sections and assert ingestion-order tie-break.

### Feedback: Citation anchor visibility in rendered bullet text
Reviewer: Gemini External 1
Severity: NIT
Quote: "Citation Anchor Visibility in Summary Text"
Decision: DEFER
Reasoning: Chunk IDs are currently embedded in structured metadata (`SummaryBullet.chunk_ids`), satisfying groundedness contract for Phase 1; UI rendering format is Phase 2/3 concern.
Action Taken: Logged for future UI-level enhancement; no Phase 1 code change.
