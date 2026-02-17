# PaperTA — Rules of Engagement

**Version:** 1.0  
**Status:** Authoritative  
**Scope:** Architecture, implementation, internal/external review

## 1. Two-Loop Workflow

PaperTA development runs in two loops per phase.

1. Loop 1 (Design)
- Create ADR, runtime contract, acceptance checklist.
- Run internal review.
- Pause for external review.
- Address feedback, freeze design artifacts.

2. Loop 2 (Build)
- Implement only against frozen contract.
- Add tests (unit + integration + negative).
- Run internal review.
- Pause for external review.
- Address feedback, re-test, then merge.

## 2. Mandatory Artifacts Per Phase

- `docs/adr/ADR-{NNN}-{topic}.md`
- `docs/contracts/PHASE{N}_RUNTIME_CONTRACT.md`
- `docs/checklists/PHASE{N}_ACCEPTANCE_CHECKLIST.yaml`
- `docs/reviews/phase{N}/design/INTERNAL_REVIEW_{AGENT}.md`
- `docs/reviews/phase{N}/design/INTERNAL_VERDICT.md`
- `docs/reviews/phase{N}/design/REVIEW_EXTERNAL_1.md` (human-provided)
- `docs/reviews/phase{N}/design/REVIEW_EXTERNAL_2.md` (human-provided)
- `docs/reviews/phase{N}/build/INTERNAL_REVIEW_{AGENT}.md`
- `docs/reviews/phase{N}/build/INTERNAL_VERDICT.md`
- `docs/reviews/phase{N}/build/REVIEW_EXTERNAL_1.md` (human-provided)
- `docs/reviews/phase{N}/build/REVIEW_EXTERNAL_2.md` (human-provided)
- `docs/reviews/phase{N}/build/VERDICT.md`

## 3. Test Rule

Every implemented component must include all three:

1. Unit tests (isolated logic)
2. Integration tests (real wiring path)
3. Negative tests (failure behavior)

Missing any test category means phase is not complete.

## 4. Review Severity Policy

- CRITICAL: must fix before merge.
- MAJOR: should fix before merge, document if deferred.
- MINOR: optional fix.
- NIT: optional.

All review decisions must be logged in `VERDICT.md` with quote, decision, and action.

## 5. Required Documents to Maintain

- `docs/JOURNAL.md`: phase starts/ends, blockers, waivers, major decisions.
- `docs/ROADMAP_SUMMARY.md`: phase outcomes, shipped components, next phase.
- `docs/GIT.md`: branch, commits, merges, release tags.

## 6. Freeze Rule

After Loop 1 external review completion, contract and checklist are frozen.
Any contract change during Loop 2 requires:

1. ADR addendum
2. checklist update
3. review note in `docs/JOURNAL.md`

## 7. Branching Convention

- `phase-{N}-loop-1-design`
- `phase-{N}-loop-2-build`

## 8. Definition of Phase Completion

A phase is complete only if all are true:

1. Design and build loops completed.
2. Required docs exist and are updated.
3. Tests pass locally.
4. External review findings resolved or formally deferred.
5. Merged to `main` and recorded in `docs/GIT.md`.
