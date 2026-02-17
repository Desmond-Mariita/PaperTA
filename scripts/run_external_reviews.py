#!/usr/bin/env python3
"""Run headless external reviews and capture immutable provenance."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import shlex
import subprocess
import sys
from pathlib import Path
from time import perf_counter

import yaml


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _utc_iso() -> str:
    return dt.datetime.now(tz=dt.timezone.utc).isoformat(timespec="seconds")


def _render_cmd(template: str, prompt_file: Path, context_file: Path, prompt_text: str) -> list[str]:
    rendered = template.format(
        prompt_file=str(prompt_file),
        context_file=str(context_file),
        prompt_text=prompt_text,
    )
    return shlex.split(rendered)


def _run_provider(
    provider_name: str,
    output_id: str,
    command_template: str,
    input_mode: str,
    prompt_file: Path,
    context_file: Path,
    prompt_text: str,
    output_dir: Path,
) -> None:
    cmd = _render_cmd(command_template, prompt_file, context_file, prompt_text)
    if not cmd:
        raise ValueError(f"Provider {provider_name} has empty command after rendering")

    started = _utc_iso()
    t0 = perf_counter()
    run_kwargs: dict[str, object] = {"capture_output": True, "text": True, "check": False}
    if input_mode == "stdin":
        run_kwargs["input"] = prompt_text
    elif input_mode != "arg":
        raise ValueError(
            f"Provider {provider_name} has unsupported input_mode '{input_mode}'. Use 'stdin' or 'arg'."
        )
    proc = subprocess.run(cmd, **run_kwargs)
    duration_ms = int((perf_counter() - t0) * 1000)
    ended = _utc_iso()

    raw_out = proc.stdout if proc.stdout else ""
    raw_err = proc.stderr if proc.stderr else ""
    raw_payload = raw_out if raw_out.strip() else raw_err
    raw_bytes = raw_payload.encode("utf-8")

    raw_path = output_dir / f"{output_id}.raw.txt"
    sha_path = output_dir / f"{output_id}.raw.sha256"
    meta_path = output_dir / f"{output_id}.meta.json"
    md_path = output_dir / f"{output_id}.md"

    raw_path.write_bytes(raw_bytes)
    raw_hash = _sha256_file(raw_path)
    sha_path.write_text(f"{raw_hash}  {raw_path.name}\n", encoding="utf-8")

    meta = {
        "provider": provider_name,
        "output_id": output_id,
        "started_at_utc": started,
        "ended_at_utc": ended,
        "duration_ms": duration_ms,
        "command_argv": cmd,
        "input_mode": input_mode,
        "exit_code": proc.returncode,
        "stdout_sha256": _sha256_bytes(raw_out.encode("utf-8")),
        "stderr_sha256": _sha256_bytes(raw_err.encode("utf-8")),
        "raw_file_sha256": raw_hash,
        "prompt_file": str(prompt_file),
        "context_file": str(context_file),
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    md = [
        f"# External Review ({provider_name})",
        "",
        f"- Generated at: {ended}",
        f"- Command: `{' '.join(cmd)}`",
        f"- Input mode: `{input_mode}`",
        f"- Exit code: {proc.returncode}",
        f"- Raw file: `{raw_path.name}`",
        f"- Raw SHA256: `{raw_hash}`",
        "",
        "## Raw Output",
        "",
        "```text",
        raw_payload.strip() if raw_payload.strip() else "<empty>",
        "```",
    ]
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    if proc.returncode != 0:
        raise RuntimeError(
            f"{provider_name} command failed (exit={proc.returncode}). See {meta_path} and {raw_path}."
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run headless Gemini/Claude external reviews")
    parser.add_argument("--phase", type=int, required=True)
    parser.add_argument("--loop", choices=["design", "build"], required=True)
    parser.add_argument(
        "--tools-config",
        type=Path,
        default=Path("configs/reviews/external_review_tools.yaml"),
    )
    parser.add_argument(
        "--prompt-template",
        type=Path,
        default=Path("docs/reviews/templates/EXTERNAL_REVIEW_PROMPT.md"),
    )
    parser.add_argument(
        "--context-file",
        type=Path,
        required=True,
        help="File containing review context (artifact list/summary).",
    )
    args = parser.parse_args()

    if not args.context_file.exists():
        raise SystemExit(f"Missing context file: {args.context_file}")
    if not args.tools_config.exists():
        raise SystemExit(f"Missing tools config: {args.tools_config}")
    if not args.prompt_template.exists():
        raise SystemExit(f"Missing prompt template: {args.prompt_template}")

    cfg = yaml.safe_load(args.tools_config.read_text(encoding="utf-8")) or {}
    providers = cfg.get("providers", {})
    if not isinstance(providers, dict):
        raise SystemExit("Invalid tools config: providers must be a mapping")

    phase_dir = Path(f"docs/reviews/phase{args.phase}/{args.loop}")
    phase_dir.mkdir(parents=True, exist_ok=True)
    prompt_file = phase_dir / "EXTERNAL_REVIEW_PROMPT_RESOLVED.md"

    resolved_prompt = (
        args.prompt_template.read_text(encoding="utf-8")
        + "\n\n## Context File\n\n"
        + str(args.context_file)
        + "\n"
    )
    prompt_file.write_text(resolved_prompt, encoding="utf-8")

    required = [("gemini", "REVIEW_EXTERNAL_1"), ("claude", "REVIEW_EXTERNAL_2")]
    for provider, default_output in required:
        entry = providers.get(provider, {})
        command = str(entry.get("command", "")).strip()
        input_mode = str(entry.get("input_mode", "arg")).strip().lower()
        output_id = str(entry.get("output_id", default_output)).strip() or default_output
        if not command:
            raise SystemExit(
                f"Missing command for provider '{provider}' in {args.tools_config}. "
                "Set providers.<name>.command first."
            )
        _run_provider(
            provider,
            output_id,
            command,
            input_mode,
            prompt_file,
            args.context_file,
            resolved_prompt,
            phase_dir,
        )

    print(f"External reviews completed for phase={args.phase} loop={args.loop}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
