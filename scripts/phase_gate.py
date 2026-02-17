#!/usr/bin/env python3
"""Validate required phase artifacts before progressing or merging."""

from __future__ import annotations

import argparse
import glob
import os
import sys
from typing import List


DESIGN_AGENTS = [
    "CONTRACT_AUDITOR",
    "IMPLEMENTATION_REVIEWER",
    "INVARIANT_GUARDIAN",
    "CONSISTENCY_CHECKER",
    "CHECKLIST_AUDITOR",
]

BUILD_AGENTS = [
    "BUILD_AUDITOR",
    "BUILD_REVIEWER",
    "INVARIANT_GUARDIAN",
    "CONSISTENCY_CHECKER",
    "TEST_AUDITOR",
]


def _existing_non_empty(path: str) -> bool:
    return os.path.isfile(path) and os.path.getsize(path) > 0


def _collect_adr_candidates() -> List[str]:
    return glob.glob("docs/adr/ADR-*.md")


def validate_design(phase: int) -> List[str]:
    errors: List[str] = []
    phase_dir = f"docs/reviews/phase{phase}/design"

    contract = f"docs/contracts/PHASE{phase}_RUNTIME_CONTRACT.md"
    checklist = f"docs/checklists/PHASE{phase}_ACCEPTANCE_CHECKLIST.yaml"
    ext1 = f"{phase_dir}/REVIEW_EXTERNAL_1.md"
    ext2 = f"{phase_dir}/REVIEW_EXTERNAL_2.md"
    verdict = f"{phase_dir}/INTERNAL_VERDICT.md"

    if not _collect_adr_candidates():
        errors.append("Missing ADR file in docs/adr/ (expected ADR-*.md).")
    for path in [contract, checklist, ext1, ext2, verdict]:
        if not _existing_non_empty(path):
            errors.append(f"Missing or empty required file: {path}")

    for agent in DESIGN_AGENTS:
        path = f"{phase_dir}/INTERNAL_REVIEW_{agent}.md"
        if not _existing_non_empty(path):
            errors.append(f"Missing or empty internal design review: {path}")

    if not _existing_non_empty("docs/JOURNAL.md"):
        errors.append("Missing or empty docs/JOURNAL.md")

    return errors


def validate_build(phase: int) -> List[str]:
    errors: List[str] = []
    phase_dir = f"docs/reviews/phase{phase}/build"

    ext1 = f"{phase_dir}/REVIEW_EXTERNAL_1.md"
    ext2 = f"{phase_dir}/REVIEW_EXTERNAL_2.md"
    verdict = f"{phase_dir}/VERDICT.md"
    internal_verdict = f"{phase_dir}/INTERNAL_VERDICT.md"

    for path in [ext1, ext2, verdict, internal_verdict]:
        if not _existing_non_empty(path):
            errors.append(f"Missing or empty required file: {path}")

    for agent in BUILD_AGENTS:
        path = f"{phase_dir}/INTERNAL_REVIEW_{agent}.md"
        if not _existing_non_empty(path):
            errors.append(f"Missing or empty internal build review: {path}")

    for path in ["docs/JOURNAL.md", "docs/ROADMAP_SUMMARY.md", "docs/GIT.md"]:
        if not _existing_non_empty(path):
            errors.append(f"Missing or empty required file: {path}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="PaperTA phase gate checker")
    parser.add_argument("--phase", type=int, required=True, help="Phase number, e.g. 1")
    parser.add_argument(
        "--loop",
        choices=["design", "build"],
        required=True,
        help="Loop type to validate",
    )
    args = parser.parse_args()

    errors = validate_design(args.phase) if args.loop == "design" else validate_build(args.phase)

    if errors:
        print("PHASE GATE FAILED")
        for err in errors:
            print(f"- {err}")
        return 1

    print(f"PHASE GATE PASSED: phase={args.phase} loop={args.loop}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
