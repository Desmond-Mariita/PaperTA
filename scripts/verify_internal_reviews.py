#!/usr/bin/env python3
"""Verify internal review files and verdicts for a phase loop."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CORE_DESIGN_AGENTS = [
    "CONTRACT_AUDITOR",
    "IMPLEMENTATION_REVIEWER",
    "INVARIANT_GUARDIAN",
    "CONSISTENCY_CHECKER",
    "CHECKLIST_AUDITOR",
]

CORE_BUILD_AGENTS = [
    "BUILD_AUDITOR",
    "BUILD_REVIEWER",
    "INVARIANT_GUARDIAN",
    "CONSISTENCY_CHECKER",
    "TEST_AUDITOR",
]

ROUND_RE = re.compile(r"^## Round (\d+)", re.MULTILINE)
VERDICT_RE = re.compile(r"^## Verdict:\s*(APPROVED|REQUEST_CHANGES)", re.MULTILINE)


def _required_agents(loop: str) -> list[str]:
    if loop == "design":
        return CORE_DESIGN_AGENTS
    if loop == "build":
        return CORE_BUILD_AGENTS
    raise ValueError(f"Unsupported loop: {loop}")


def _check_round_integrity(content: str) -> list[str]:
    rounds = [int(v) for v in ROUND_RE.findall(content)]
    if not rounds:
        return []
    expected = list(range(2, max(rounds) + 1))
    if sorted(rounds) != expected:
        return [f"Round sequence invalid. Found={sorted(rounds)} expected={expected}"]
    return []


def verify(phase: int, loop: str, repo_root: Path) -> tuple[bool, list[str]]:
    errors: list[str] = []
    review_dir = repo_root / "docs" / "reviews" / f"phase{phase}" / loop
    if not review_dir.exists():
        return False, [f"Missing review directory: {review_dir}"]

    for agent in _required_agents(loop):
        file_path = review_dir / f"INTERNAL_REVIEW_{agent}.md"
        if not file_path.exists() or file_path.stat().st_size == 0:
            errors.append(f"Missing or empty: {file_path}")
            continue
        content = file_path.read_text(encoding="utf-8")
        if not VERDICT_RE.findall(content):
            errors.append(f"No valid verdict lines in {file_path.name}")
        for rerr in _check_round_integrity(content):
            errors.append(f"{file_path.name}: {rerr}")

    verdict = review_dir / "INTERNAL_VERDICT.md"
    if not verdict.exists() or verdict.stat().st_size == 0:
        errors.append(f"Missing or empty: {verdict}")
    else:
        vtext = verdict.read_text(encoding="utf-8")
        if "Overall Verdict: APPROVED" not in vtext and "Overall Verdict: BLOCKED" not in vtext:
            errors.append("INTERNAL_VERDICT.md missing Overall Verdict marker")

    return len(errors) == 0, errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify internal review artifacts")
    parser.add_argument("--phase", type=int, required=True)
    parser.add_argument("--loop", choices=["design", "build"], required=True)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()

    ok, errors = verify(args.phase, args.loop, args.repo_root)
    if ok:
        print(f"PASS: internal reviews verified for phase={args.phase} loop={args.loop}")
        raise SystemExit(0)
    print(f"FAIL: internal reviews invalid for phase={args.phase} loop={args.loop}")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
