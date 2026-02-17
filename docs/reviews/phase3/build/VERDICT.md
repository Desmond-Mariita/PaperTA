# Build Review Verdict — Phase 3

- Date: 2026-02-17
- Phase: 3
- Loop: build

### Feedback: unsupported claim counter uses wrong predicate
Reviewer: Claude External 2
Severity: MAJOR
Quote: "`unsupported_claim_count` uses wrong predicate"
Decision: ACCEPT
Reasoning: Observability metric must reflect unsupported support grades rather than fallback claim text.
Action Taken: Updated `unsupported_claim_count` to count `row.support_grade == "unsupported"` in `src/paperta/reviewer.py`.

### Feedback: Missing unit test for `generate_critique`
Reviewer: Claude External 2
Severity: MAJOR
Quote: "No unit test for `generate_critique`"
Decision: ACCEPT
Reasoning: Interface-level unit coverage is required to prevent regressions in fallback and evidence paths.
Action Taken: Added `test_generate_critique_handles_evidence_and_fallback` in `tests/unit/test_reviewer.py` and checklist item `T3-UNIT-003` in `docs/checklists/PHASE3_ACCEPTANCE_CHECKLIST.yaml`.

### Feedback: Incomplete negative test coverage for failure modes
Reviewer: Gemini External 1 / Claude External 2
Severity: MINOR
Quote: "missing negative tests for invalid mode and top_k <= 0"
Decision: ACCEPT
Reasoning: Contract failure modes should be explicitly locked by tests.
Action Taken: Added `test_phase3_pipeline_rejects_non_positive_top_k` and `test_phase3_pipeline_rejects_invalid_mode` in `tests/negative/test_phase3_reviewer_negative.py`; checklist entries `F3-001` and `F3-002` added.

### Feedback: Duplicate fallback constant across modules
Reviewer: Gemini External 1
Severity: MINOR
Quote: "Duplicate Constant Definition"
Decision: DEFER
Reasoning: Consolidating constants is a cleanup task and not required for Phase 3 acceptance.
Action Taken: No code change in Phase 3.

### Feedback: Field naming inconsistency (`evidence_chunk_ids` vs `chunk_ids`)
Reviewer: Gemini External 1
Severity: NIT
Quote: "Field Naming Inconsistency"
Decision: DEFER
Reasoning: Current naming is explicit and backwards-compatible for matrix semantics; rename would be breaking.
Action Taken: No code change in Phase 3.

### Feedback: Reproducibility status value domain not in contract
Reviewer: Claude External 2
Severity: MINOR
Quote: "runtime contract never enumerates the valid set of reproducibility statuses"
Decision: DEFER
Reasoning: Status domain is stable in runtime/tests; formalizing enum can be included in next contract revision.
Action Taken: No code change in Phase 3.
