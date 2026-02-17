# PaperTA

PaperTA is a verifiable academic AI assistant focused on grounded summaries, teach mode, and reviewer mode with evidence-linked outputs.

## Development Model

This repo uses a two-loop workflow:

1. Loop 1: Design (ADRs, contracts, acceptance checklists)
2. Loop 2: Build (implementation against frozen contracts)

See `RULES_OF_ENGAGEMENT.md` for mandatory process gates.

## Local Setup

Use the cross-OS setup in `LOCAL_DEV_SETUP.md`.

## Docs

- `PaperTA_System_Design_v0.3.md`
- `RULES_OF_ENGAGEMENT.md`
- `docs/ROADMAP_SUMMARY.md`
- `docs/JOURNAL.md`
- `docs/GIT.md`
- `docs/INTERNAL_REVIEW_AGENTS.md`

## Quality Gates

Phase gate commands:

```bash
make gate-design PHASE=1
make gate-build PHASE=1
make verify-reviews PHASE=1 LOOP=design
make run-external PHASE=1 LOOP=design
make verify-external PHASE=1 LOOP=design
make check-docstrings PHASE=1
make verify-checklist PHASE=1
make phase-report PHASE=1 LOOP=design
```

External review tooling config:

- `configs/reviews/external_review_tools.yaml`
