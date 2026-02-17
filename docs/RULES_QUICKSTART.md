# PaperTA Rules Quickstart

## 1. Start Phase

1. Create branch:
   - `phase-{N}-loop-1-design`
2. Log phase start in `docs/JOURNAL.md`.
3. Create design artifacts:
   - ADR
   - runtime contract
   - acceptance checklist

## 2. Design Gate

1. Run internal design reviews and save all files.
2. Stop for external reviews.
3. Address findings.
4. Run:
   - `make gate-design PHASE={N}`
   - `make verify-reviews PHASE={N} LOOP=design`

## 3. Build Gate

1. Branch:
   - `phase-{N}-loop-2-build`
2. Implement against frozen contract.
3. Add unit + integration + negative tests.
4. Run internal build reviews and external reviews.
5. Run:
   - `make gate-build PHASE={N}`
   - `make verify-reviews PHASE={N} LOOP=build`
   - `make phase-report PHASE={N} LOOP=build`

## 4. Merge

Merge only when all gates are passing and logs are updated:

- `docs/JOURNAL.md`
- `docs/ROADMAP_SUMMARY.md`
- `docs/GIT.md`
