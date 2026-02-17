#!/usr/bin/env python3
"""Generate phase gate report for PaperTA."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from time import perf_counter


def _run(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    out = (proc.stdout or "") + (("\n" + proc.stderr) if proc.stderr else "")
    return proc.returncode, out.strip()


def _parse_pytest_summary(text: str) -> dict[str, int]:
    def _m(pattern: str) -> int:
        match = re.search(pattern, text)
        return int(match.group(1)) if match else 0

    passed = _m(r"(\d+)\s+passed")
    failed = _m(r"(\d+)\s+failed")
    skipped = _m(r"(\d+)\s+skipped")
    return {"passed": passed, "failed": failed, "skipped": skipped, "total": passed + failed + skipped}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate phase report")
    parser.add_argument("--phase", type=int, required=True)
    parser.add_argument("--loop", choices=["design", "build"], required=True)
    args = parser.parse_args()

    start = perf_counter()
    report_dir = Path(f"reports/phase{args.phase}")
    report_dir.mkdir(parents=True, exist_ok=True)

    status = {"phase_gate": "FAIL", "internal_reviews": "FAIL", "checklist": "SKIP", "pytest": "SKIP"}
    details: dict[str, str | dict[str, int]] = {}

    rc, out = _run(["python3", "scripts/phase_gate.py", "--phase", str(args.phase), "--loop", args.loop])
    status["phase_gate"] = "PASS" if rc == 0 else "FAIL"
    details["phase_gate_output"] = out

    rc, out = _run(
        ["python3", "scripts/verify_internal_reviews.py", "--phase", str(args.phase), "--loop", args.loop]
    )
    status["internal_reviews"] = "PASS" if rc == 0 else "FAIL"
    details["internal_review_output"] = out

    checklist = Path(f"docs/checklists/PHASE{args.phase}_ACCEPTANCE_CHECKLIST.yaml")
    if checklist.exists():
        rc, out = _run(
            [
                "python3",
                "scripts/verify_checklist.py",
                "--checklist",
                str(checklist),
                "--report-out",
                str(report_dir / "checklist_report.json"),
            ]
        )
        status["checklist"] = "PASS" if rc == 0 else "FAIL"
        details["checklist_output"] = out

    if Path("tests").exists():
        rc, out = _run([sys.executable, "-m", "pytest", "tests/", "-q"])
        parsed = _parse_pytest_summary(out)
        details["pytest_summary"] = parsed
        status["pytest"] = "PASS" if rc == 0 else "FAIL"

    overall = "PASS"
    required = ["phase_gate", "internal_reviews"]
    for key in required:
        if status[key] != "PASS":
            overall = "FAIL"
    for opt in ["checklist", "pytest"]:
        if status[opt] == "FAIL":
            overall = "FAIL"

    payload = {
        "phase": args.phase,
        "loop": args.loop,
        "status": status,
        "overall_verdict": overall,
        "duration_seconds": round(perf_counter() - start, 2),
        "details": details,
    }
    (report_dir / "phase_report.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps(payload, indent=2))
    raise SystemExit(0 if overall == "PASS" else 1)


if __name__ == "__main__":
    main()
