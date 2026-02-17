#!/usr/bin/env python3
"""Check Google-style docstrings for public Python APIs."""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any


def _get_non_self_args(node: ast.FunctionDef) -> list[ast.arg]:
    """Return function args excluding self/cls.

    Args:
        node: Function node.

    Returns:
        Non-self argument nodes.
    """
    return [arg for arg in node.args.args if arg.arg not in {"self", "cls"}]


def _has_non_none_return(node: ast.FunctionDef) -> bool:
    """Return True if function has non-None return annotation.

    Args:
        node: Function node.

    Returns:
        Whether function declares non-None return.
    """
    if node.returns is None:
        return False
    if isinstance(node.returns, ast.Constant) and node.returns.value is None:
        return False
    if isinstance(node.returns, ast.Name) and node.returns.id == "None":
        return False
    return True


def _check_google_docstring(node: ast.FunctionDef) -> tuple[bool, str]:
    """Check whether function docstring follows basic Google style.

    Args:
        node: Function node.

    Returns:
        Tuple of (is_valid, reason).
    """
    doc = ast.get_docstring(node)
    if not doc:
        return False, "missing docstring"
    lowered = doc.lower()
    if _get_non_self_args(node) and "args:" not in lowered:
        return False, "missing 'Args:' section"
    if _has_non_none_return(node) and "returns:" not in lowered and "yields:" not in lowered:
        return False, "missing 'Returns:' section"
    return True, ""


def _check_module(path: Path) -> list[dict[str, Any]]:
    """Check one module for docstring violations.

    Args:
        path: Python source file path.

    Returns:
        Violation records.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    violations: list[dict[str, Any]] = []

    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
            ok, reason = _check_google_docstring(node)
            if not ok:
                violations.append(
                    {
                        "path": str(path),
                        "line": node.lineno,
                        "object": node.name,
                        "type": "function",
                        "reason": reason,
                    }
                )
        elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            if not ast.get_docstring(node):
                violations.append(
                    {
                        "path": str(path),
                        "line": node.lineno,
                        "object": node.name,
                        "type": "class",
                        "reason": "missing docstring",
                    }
                )
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
                    ok, reason = _check_google_docstring(item)
                    if not ok:
                        violations.append(
                            {
                                "path": str(path),
                                "line": item.lineno,
                                "object": f"{node.name}.{item.name}",
                                "type": "method",
                                "reason": reason,
                            }
                        )

    return violations


def check_paths(paths: list[Path]) -> dict[str, Any]:
    """Check all Python files under provided roots.

    Args:
        paths: Directories to scan.

    Returns:
        Report payload with violations.
    """
    py_files: list[Path] = []
    for root in paths:
        if root.exists():
            py_files.extend(sorted(p for p in root.rglob("*.py") if p.is_file()))

    violations: list[dict[str, Any]] = []
    for py_file in py_files:
        violations.extend(_check_module(py_file))

    return {
        "files_checked": len(py_files),
        "violations": violations,
        "verdict": "PASS" if not violations else "FAIL",
    }


def main() -> None:
    """Run docstring checker CLI."""
    parser = argparse.ArgumentParser(description="Check Google-style docstrings")
    parser.add_argument(
        "--paths",
        nargs="+",
        default=["src/paperta"],
        help="Paths to scan",
    )
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    report = check_paths([Path(p) for p in args.paths])

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if report["verdict"] == "PASS":
        print(f"Docstring check PASS ({report['files_checked']} files)")
        raise SystemExit(0)

    print(f"Docstring check FAIL ({len(report['violations'])} violations)")
    for violation in report["violations"]:
        print(
            f"- {violation['path']}:{violation['line']} "
            f"{violation['type']} {violation['object']}: {violation['reason']}"
        )
    raise SystemExit(1)


if __name__ == "__main__":
    main()
