# PaperTA Internal Review Agents

**Version:** 1.0  
**Status:** AUTHORITATIVE  
**Referenced by:** `RULES_OF_ENGAGEMENT.md`

## Purpose

Internal review agents provide structured pre-screening for:

1. Loop 1 (Design): contracts/checklists/invariants consistency
2. Loop 2 (Build): implementation quality, wiring, and test discipline

External reviews are still human-provided.

## Protocol

1. Run required agents for the phase loop.
2. Save per-agent files:
   - `docs/reviews/phase{N}/{loop}/INTERNAL_REVIEW_{AGENT}.md`
3. Create summary file:
   - `docs/reviews/phase{N}/{loop}/INTERNAL_VERDICT.md`
4. Resolve all CRITICAL findings before loop completion.
5. Re-run only failed agents, max 5 rounds.

## Required Agents

### Design Loop

- `CONTRACT_AUDITOR`
- `IMPLEMENTATION_REVIEWER`
- `INVARIANT_GUARDIAN`
- `CONSISTENCY_CHECKER`
- `CHECKLIST_AUDITOR`

### Build Loop

- `BUILD_AUDITOR`
- `BUILD_REVIEWER`
- `INVARIANT_GUARDIAN`
- `CONSISTENCY_CHECKER`
- `TEST_AUDITOR`

## Round Rules

- Round 1 creates file.
- Round 2+ append new section headers (`## Round N`).
- No overwriting previous rounds.
- Max 5 rounds per agent.

## Required Verdict Values

Per-agent:

- `APPROVED`
- `REQUEST_CHANGES`

Overall verdict (`INTERNAL_VERDICT.md`):

- `Overall Verdict: APPROVED`
- `Overall Verdict: BLOCKED`
