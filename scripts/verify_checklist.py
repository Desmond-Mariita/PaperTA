#!/usr/bin/env python3
"""Verify phase acceptance checklist evidence."""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
from pathlib import Path
from typing import Any

import yaml

ALLOWED_PREFIXES = ("src/", "tests/", "docs/", "configs/", "scripts/")
SUPPORTED_EVIDENCE = {
    "test_exists",
    "test_passes",
    "file_exists",
    "file_contains",
    "manual_attestation",
}


def _in_scope(path: str) -> bool:
    return path.startswith(ALLOWED_PREFIXES)


def _has_test(path: Path, test_name: str) -> bool:
    if not path.exists() or not test_name.strip():
        return False
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    if "::" in test_name:
        cls, fn = test_name.split("::", 1)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == cls:
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == fn:
                        return True
        return False
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == test_name:
            return True
    return False


def _run_pytest(nodeid: str) -> tuple[bool, str]:
    proc = subprocess.run(
        ["pytest", "-q", nodeid],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode == 0:
        return True, "pytest pass"
    return False, (proc.stderr or proc.stdout or "pytest fail").strip()


def _check_manual_attestation(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, f"missing file: {path}"
    text = path.read_text(encoding="utf-8")
    patterns = [r"Date:\s*\d{4}-\d{2}-\d{2}", r"Result:\s*(PASS|All.*passed)"]
    for pattern in patterns:
        if not re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE):
            return False, f"missing marker: {pattern}"
    return True, "attestation verified"


def _check_evidence(item: dict[str, Any], root: Path) -> tuple[bool, str]:
    evidence = item.get("evidence", {})
    etype = str(evidence.get("type", "")).strip()
    if etype not in SUPPORTED_EVIDENCE:
        return False, f"unsupported evidence type: {etype}"

    if etype in {"test_exists", "test_passes"}:
        rel = str(evidence.get("test_pattern", "")).strip()
        test_name = str(evidence.get("test_name", "")).strip()
        if not rel or not test_name:
            return False, "missing test_pattern/test_name"
        path = root / rel
        if not path.exists():
            return False, f"missing test file: {rel}"
        if not _has_test(path, test_name):
            return False, f"missing test function: {test_name}"
        if etype == "test_passes":
            return _run_pytest(f"{rel}::{test_name}")
        return True, "test exists"

    if etype in {"file_exists", "file_contains", "manual_attestation"}:
        rel = str(evidence.get("path", "")).strip()
        if not rel:
            return False, "missing path"
        if not _in_scope(rel):
            return False, f"path outside allowed scope: {rel}"
        path = root / rel

        if etype == "file_exists":
            return (path.exists(), "file exists" if path.exists() else f"missing file: {rel}")

        if etype == "file_contains":
            pattern = str(evidence.get("pattern", "")).strip()
            if not pattern:
                return False, "missing pattern"
            if not path.exists():
                return False, f"missing file: {rel}"
            text = path.read_text(encoding="utf-8")
            return (
                re.search(pattern, text, flags=re.MULTILINE) is not None,
                "pattern found",
            )

        return _check_manual_attestation(path)

    return False, "unreachable"


def verify(checklist_path: Path, root: Path) -> dict[str, Any]:
    payload = yaml.safe_load(checklist_path.read_text(encoding="utf-8")) or {}
    items = payload.get("items", [])
    if not isinstance(items, list):
        raise ValueError("checklist missing items list")

    results = []
    passed = 0
    failed = 0

    for item in items:
        ok, message = _check_evidence(item, root)
        row = {
            "id": item.get("id"),
            "requirement": item.get("requirement"),
            "ok": ok,
            "message": message,
        }
        results.append(row)
        if ok:
            passed += 1
        else:
            failed += 1

    return {
        "checklist": str(checklist_path),
        "total_items": len(items),
        "passed": passed,
        "failed": failed,
        "verdict": "PASS" if failed == 0 else "FAIL",
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify phase acceptance checklist")
    parser.add_argument("--checklist", required=True, type=Path)
    parser.add_argument("--report-out", type=Path, default=None)
    args = parser.parse_args()

    report = verify(args.checklist, Path("."))
    print(f"Checklist verdict: {report['verdict']} ({report['passed']}/{report['total_items']})")
    if args.report_out:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Wrote report: {args.report_out}")

    raise SystemExit(0 if report["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
