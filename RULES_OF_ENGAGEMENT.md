# PaperTA — Rules of Engagement

**Version:** 2.0  
**Status:** AUTHORITATIVE  
**For:** Architect + Coder + Review Workflow

## Purpose

Build PaperTA correctly the first time with explicit gates. No skipped steps. No silent deferrals.

---

## 1. Two-Loop Workflow (Mandatory)

Each phase has two loops, in order:

1. **Loop 1 (Design):** ADR + runtime contract + acceptance checklist + reviews + freeze
2. **Loop 2 (Build):** implement against frozen contract + tests + reviews + merge gate

You cannot start Loop 2 until Loop 1 is complete and frozen.

---

## 2. Phase Start Protocol

When phase work begins, execute in this order:

1. Create branch:
   - `phase-{N}-loop-1-design` for design loop
   - `phase-{N}-loop-2-build` for build loop
2. Append phase start entry to `docs/JOURNAL.md`.
3. Create phase artifact directories:
   - `docs/reviews/phase{N}/design/`
   - `docs/reviews/phase{N}/build/`

---

## 3. Loop 1 (Design) Protocol

### 3.1 Required Design Artifacts

Must create all:

- `docs/adr/ADR-{NNN}-{topic}.md`
- `docs/contracts/PHASE{N}_RUNTIME_CONTRACT.md`
- `docs/checklists/PHASE{N}_ACCEPTANCE_CHECKLIST.yaml`

### 3.2 Internal Design Review (Required)

Run internal review with these agents:

- `CONTRACT_AUDITOR`
- `IMPLEMENTATION_REVIEWER`
- `INVARIANT_GUARDIAN`
- `CONSISTENCY_CHECKER`
- `CHECKLIST_AUDITOR`

Rules:

- Max 5 rounds per agent.
- Resolve all `CRITICAL` and `MAJOR` findings.
- Save outputs:
  - `docs/reviews/phase{N}/design/INTERNAL_REVIEW_{AGENT}.md`
  - `docs/reviews/phase{N}/design/INTERNAL_VERDICT.md`

### 3.3 External Design Review Stop Point

After internal design review completion, stop and run headless external review commands. Required artifacts:

- `docs/reviews/phase{N}/design/REVIEW_EXTERNAL_1.md`
- `docs/reviews/phase{N}/design/REVIEW_EXTERNAL_2.md`
- `docs/reviews/phase{N}/design/REVIEW_EXTERNAL_1.raw.txt`
- `docs/reviews/phase{N}/design/REVIEW_EXTERNAL_2.raw.txt`
- `docs/reviews/phase{N}/design/REVIEW_EXTERNAL_1.raw.sha256`
- `docs/reviews/phase{N}/design/REVIEW_EXTERNAL_2.raw.sha256`
- `docs/reviews/phase{N}/design/REVIEW_EXTERNAL_1.meta.json`
- `docs/reviews/phase{N}/design/REVIEW_EXTERNAL_2.meta.json`

External reviews must come from real CLI execution (Gemini/Claude), never simulated text.

### 3.4 Design Freeze

After external feedback is addressed:

1. Freeze contract/checklist.
2. Add freeze entry to `docs/JOURNAL.md`.
3. Run gate checker:
   - `python3 scripts/phase_gate.py --phase N --loop design`

Loop 1 is complete only if gate passes.

---

## 4. Loop 2 (Build) Protocol

### 4.1 Pre-Flight Reads (Required)

Before coding:

1. `RULES_OF_ENGAGEMENT.md`
2. `docs/ROADMAP_SUMMARY.md`
3. `docs/contracts/PHASE{N}_RUNTIME_CONTRACT.md`
4. `docs/checklists/PHASE{N}_ACCEPTANCE_CHECKLIST.yaml`

### 4.2 Implementation Requirements

Implement only within frozen contract scope.

### 4.3 Three-Test Rule (Mandatory)

Each component must include all:

1. Unit test
2. Integration test
3. Negative test

Missing any one category means phase fails.

### 4.4 Internal Build Review (Required)

Run internal review with these agents:

- `BUILD_AUDITOR`
- `BUILD_REVIEWER`
- `INVARIANT_GUARDIAN`
- `CONSISTENCY_CHECKER`
- `TEST_AUDITOR`

Rules:

- Max 5 rounds per agent.
- Resolve all `CRITICAL`; resolve `MAJOR` or explicitly defer in verdict.
- Save outputs:
  - `docs/reviews/phase{N}/build/INTERNAL_REVIEW_{AGENT}.md`
  - `docs/reviews/phase{N}/build/INTERNAL_VERDICT.md`

### 4.5 External Build Review Stop Point

Stop and run headless external review commands. Required artifacts:

- `docs/reviews/phase{N}/build/REVIEW_EXTERNAL_1.md`
- `docs/reviews/phase{N}/build/REVIEW_EXTERNAL_2.md`
- `docs/reviews/phase{N}/build/REVIEW_EXTERNAL_1.raw.txt`
- `docs/reviews/phase{N}/build/REVIEW_EXTERNAL_2.raw.txt`
- `docs/reviews/phase{N}/build/REVIEW_EXTERNAL_1.raw.sha256`
- `docs/reviews/phase{N}/build/REVIEW_EXTERNAL_2.raw.sha256`
- `docs/reviews/phase{N}/build/REVIEW_EXTERNAL_1.meta.json`
- `docs/reviews/phase{N}/build/REVIEW_EXTERNAL_2.meta.json`

Then produce:

- `docs/reviews/phase{N}/build/VERDICT.md`

### 4.6 Merge Gate (Non-Skippable)

Before merge, all must pass:

1. Local tests pass.
2. Review findings resolved/deferred with rationale.
3. Docs updated:
   - `docs/JOURNAL.md`
   - `docs/ROADMAP_SUMMARY.md`
   - `docs/GIT.md`
4. Gate checker passes:
   - `python3 scripts/phase_gate.py --phase N --loop build`
5. External provenance check passes:
   - `python3 scripts/verify_external_reviews.py --phase N --loop build`

If gate fails, merge is blocked.

---

## 5. Required Files Per Loop

### Loop 1 (Design) must exist

- ADR
- runtime contract
- acceptance checklist
- all internal design review files
- internal design verdict
- both external design reviews

### Loop 2 (Build) must exist

- all internal build review files
- internal build verdict
- both external build reviews
- final build verdict

---

## 6. Severity Policy

- `CRITICAL`: must fix before loop completion.
- `MAJOR`: should fix; deferral allowed only with explicit risk note in verdict.
- `MINOR`: optional.
- `NIT`: optional.

---

## 7. Verdict Format (Mandatory)

Every external/internal finding addressed in `VERDICT.md` uses:

```markdown
### Feedback: <short title>
Reviewer: <source>
Severity: CRITICAL | MAJOR | MINOR | NIT
Quote: "<exact quote>"
Decision: ACCEPT | DEFER | REJECT
Reasoning: <brief rationale>
Action Taken: <commit/file/test change or none>
```

---

## 8. No-Skip Enforcement

Enforcement mechanisms:

1. Human process gate in this document.
2. Mechanical gate: `scripts/phase_gate.py`.
3. Optional CI gate: run `phase_gate.py` in pull-request checks.

If any required artifact is missing/empty, hash mismatched, or provider metadata is invalid, gate fails.

---

## 9. Definition of Phase Completion

A phase is complete only when:

1. Loop 1 and Loop 2 gates pass.
2. Required review artifacts exist.
3. Required tests exist and pass.
4. Journal/roadmap/git logs are updated.
5. Branch merged and pushed to `main`.
