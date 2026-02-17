# External Review Automation (Headless, Verifiable)

## Goal

Guarantee that external reviews are produced by real Gemini/Claude CLI executions, not simulated text.

## Files Produced Per Provider

For each phase loop (`docs/reviews/phase{N}/{loop}`):

- `REVIEW_EXTERNAL_X.raw.txt` (verbatim CLI output)
- `REVIEW_EXTERNAL_X.raw.sha256` (content hash)
- `REVIEW_EXTERNAL_X.meta.json` (command argv, timestamps, exit code, hashes)
- `REVIEW_EXTERNAL_X.md` (human-readable wrapper referencing raw hash)

`X=1` is Gemini, `X=2` is Claude.

## Configure Commands

Edit `configs/reviews/external_review_tools.yaml`:

```yaml
providers:
  gemini:
    output_id: REVIEW_EXTERNAL_1
    command: "gemini --output-format json"
    input_mode: "stdin"
  claude:
    output_id: REVIEW_EXTERNAL_2
    command: "claude -p --output-format json --dangerously-skip-permissions"
    input_mode: "stdin"
```

Supported placeholders:

- `{prompt_file}`
- `{context_file}`
- `{prompt_text}`

Input modes:

- `stdin`: send resolved prompt via standard input (used for Gemini default)
- `arg`: inject prompt via `{prompt_text}` in command string

## Run

```bash
make run-external PHASE=1 LOOP=design
```

Default context file:

- `docs/ROADMAP_SUMMARY.md`

## Verify

```bash
make verify-external PHASE=1 LOOP=design
```

Verification checks:

1. Required files exist and are non-empty.
2. SHA sidecar matches raw file content.
3. Metadata provider and command argv are valid.
4. Metadata raw hash equals computed hash.
5. Markdown wrapper includes the raw SHA marker.

## Merge Gate

`scripts/phase_gate.py` calls external review verification automatically for design/build loops.
