#!/usr/bin/env python3
"""Verify external review provenance to prevent simulated reviews."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


REQUIRED = [("gemini", "REVIEW_EXTERNAL_1"), ("claude", "REVIEW_EXTERNAL_2")]


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(phase: int, loop: str, strict_exit_zero: bool = True) -> tuple[bool, list[str]]:
    errors: list[str] = []
    base = Path(f"docs/reviews/phase{phase}/{loop}")
    if not base.exists():
        return False, [f"Missing directory: {base}"]

    for provider, output_id in REQUIRED:
        raw_path = base / f"{output_id}.raw.txt"
        sha_path = base / f"{output_id}.raw.sha256"
        meta_path = base / f"{output_id}.meta.json"
        md_path = base / f"{output_id}.md"

        for path in [raw_path, sha_path, meta_path, md_path]:
            if not path.exists() or path.stat().st_size == 0:
                errors.append(f"Missing or empty required file: {path}")
                continue

        if not raw_path.exists() or not sha_path.exists() or not meta_path.exists() or not md_path.exists():
            continue

        actual_hash = _sha256_file(raw_path)
        sha_line = sha_path.read_text(encoding="utf-8").strip()
        if not sha_line:
            errors.append(f"Empty sha file: {sha_path}")
        else:
            declared_hash = sha_line.split()[0]
            if declared_hash != actual_hash:
                errors.append(f"SHA mismatch for {raw_path.name}")

        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if str(meta.get("provider", "")).lower() != provider:
            errors.append(f"Provider mismatch in {meta_path.name}: expected {provider}")
        argv = meta.get("command_argv", [])
        if not isinstance(argv, list) or not argv:
            errors.append(f"Invalid command_argv in {meta_path.name}")
        else:
            exe = str(argv[0]).lower()
            if provider not in exe:
                errors.append(
                    f"Command executable in {meta_path.name} does not look like {provider}: {argv[0]}"
                )
        exit_code = int(meta.get("exit_code", 1))
        if strict_exit_zero and exit_code != 0:
            errors.append(f"Non-zero exit code in {meta_path.name}: {exit_code}")
        if meta.get("raw_file_sha256") != actual_hash:
            errors.append(f"raw_file_sha256 mismatch in {meta_path.name}")

        md_text = md_path.read_text(encoding="utf-8")
        marker = f"Raw SHA256: `{actual_hash}`"
        if marker not in md_text:
            errors.append(f"Markdown hash marker missing in {md_path.name}")

    return len(errors) == 0, errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify external review provenance")
    parser.add_argument("--phase", type=int, required=True)
    parser.add_argument("--loop", choices=["design", "build"], required=True)
    parser.add_argument(
        "--allow-nonzero-exit",
        action="store_true",
        help="Allow provider command non-zero exit codes (not recommended for merge gate)",
    )
    args = parser.parse_args()

    ok, errors = verify(args.phase, args.loop, strict_exit_zero=not args.allow_nonzero_exit)
    if ok:
        print(f"PASS: external review provenance verified for phase={args.phase} loop={args.loop}")
        raise SystemExit(0)
    print(f"FAIL: external review provenance invalid for phase={args.phase} loop={args.loop}")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
