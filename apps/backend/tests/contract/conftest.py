"""Write ``.quality-reports/schemathesis.{md,json}`` after the contract suite runs.

``make test-schemathesis`` pytest args stay unchanged; this hook only observes
the run and emits a summary for the sticky PR comment
(``scripts/ci/format_contracts_pr_comment.py``).

[Corpus: api] [Corpus: tests]
"""

from __future__ import annotations

import json
import os
import re
from importlib import metadata
from pathlib import Path
from typing import Any

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[4]
_OPERATION_RE = re.compile(r"\[(?P<op>[^\]]+)\]$")
_HTTP_OPERATION_RE = re.compile(r"^[A-Z]+ /")
_MAX_FAILURE_ROWS = 25

_results: list[dict[str, Any]] = []


def _report_dir() -> Path:
    raw = os.environ.get("QUALITY_REPORTS_DIR", ".quality-reports")
    path = Path(raw)
    return path if path.is_absolute() else _REPO_ROOT / path


def _operation(nodeid: str) -> str:
    match = _OPERATION_RE.search(nodeid)
    return match.group("op") if match else nodeid.rsplit("::", 1)[-1]


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    """Record one row per Schemathesis operation (call phase, or setup skip/error)."""
    if "test_schemathesis_openapi" not in report.nodeid:
        return
    if report.when == "call" or (report.when == "setup" and report.outcome != "passed"):
        detail = ""
        if report.outcome == "failed":
            detail = str(report.longreprtext).strip().splitlines()[-1][:300] if report.longreprtext else ""
        _results.append(
            {
                "operation": _operation(report.nodeid),
                "outcome": report.outcome,
                "duration_s": round(report.duration, 3),
                "detail": detail,
            }
        )


def _render_markdown(summary: dict[str, Any]) -> str:
    counts = summary["counts"]
    lines = [
        "### Schemathesis",
        "",
        f"- Overall: **{summary['status'].upper()}**",
        f"- Operations: {counts['total']} "
        f"({counts['passed']} passed, {counts['failed']} failed, {counts['skipped']} skipped)",
        f"- Budget: `max_examples={summary['max_examples']}` (locked ceiling 25), "
        f"schemathesis `{summary['schemathesis_version']}`",
    ]
    failed = [r for r in summary["results"] if r["outcome"] == "failed"]
    if failed:
        lines += ["", "| Operation | Failure |", "|---|---|"]
        for row in failed[:_MAX_FAILURE_ROWS]:
            detail = row["detail"].replace("|", "\\|") or "see CI log"
            lines.append(f"| `{row['operation']}` | {detail} |")
        if len(failed) > _MAX_FAILURE_ROWS:
            lines.append(f"| ... | {len(failed) - _MAX_FAILURE_ROWS} more in `schemathesis.json` |")
    return "\n".join(lines) + "\n"


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Emit the report only when Schemathesis operations actually ran."""
    del session
    if not _results:
        return
    # Schemathesis reports one subtest per "METHOD /path"; drop the parent row when present.
    rows = [r for r in _results if _HTTP_OPERATION_RE.match(r["operation"])] or _results
    counts = {
        "total": len(rows),
        "passed": sum(r["outcome"] == "passed" for r in rows),
        "failed": sum(r["outcome"] == "failed" for r in rows),
        "skipped": sum(r["outcome"] == "skipped" for r in rows),
    }
    try:
        version = metadata.version("schemathesis")
    except metadata.PackageNotFoundError:  # pragma: no cover - dependency is required
        version = "unknown"
    summary: dict[str, Any] = {
        "tool": "schemathesis",
        "schemathesis_version": version,
        "max_examples": int(os.environ.get("SCHEMATHESIS_MAX_EXAMPLES", "25")),
        "status": "pass" if counts["failed"] == 0 and exitstatus == 0 else "fail",
        "counts": counts,
        "results": sorted(rows, key=lambda r: r["operation"]),
    }
    out = _report_dir()
    out.mkdir(parents=True, exist_ok=True)
    (out / "schemathesis.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (out / "schemathesis.md").write_text(_render_markdown(summary), encoding="utf-8")
