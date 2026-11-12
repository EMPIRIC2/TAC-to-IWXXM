#!/usr/bin/env python3
"""Format the sticky PR contracts comment from oasdiff + Schemathesis reports.

Reads ``oasdiff.json`` (written by ``scripts/ci/run_oasdiff.sh``) and
``schemathesis.json`` (written by the contract-suite pytest hook) from a reports
directory (default ``.quality-reports``). Prints markdown that starts with the
sticky marker used by ``.github/workflows/quality-contracts.yml``.

[Corpus: api] [Corpus: tests]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

MARKER = "<!-- tooling-contracts-pr-comment -->"
DEFAULT_DIR = ".quality-reports"
MAX_ROWS = 25

_BADGE = {"pass": "PASS", "fail": "FAIL", "skipped": "SKIPPED"}


def load_report(path: Path) -> dict[str, Any] | None:
    """Return the parsed JSON object, or ``None`` when missing or unreadable."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _badge(status: object) -> str:
    return _BADGE.get(str(status), str(status).upper() or "UNKNOWN")


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_oasdiff(report: dict[str, Any] | None) -> list[str]:
    """Markdown block for the oasdiff report."""
    lines = ["### oasdiff (OpenAPI breaking changes)", ""]
    if report is None:
        return [*lines, "_Not run (no `oasdiff.json`)._"]
    breaking = report.get("breaking") or {}
    parity = report.get("parity") or {}
    base = report.get("base") or "no base spec"
    lines.append(
        f"- Breaking vs base (`{base}`): **{_badge(breaking.get('status'))}** "
        f"- {breaking.get('error', 0)} error, {breaking.get('warning', 0)} warning, "
        f"{breaking.get('info', 0)} info (fail-on `{report.get('fail_on', 'ERR')}`)"
    )
    lines.append(
        f"- Frontend copy parity (`{report.get('revision', '?')}` vs "
        f"`{report.get('frontend_copy', '?')}`): **{_badge(parity.get('status'))}**"
    )
    findings = breaking.get("findings") or []
    if findings:
        lines += ["", "| Level | Operation | Change |", "|---|---|---|"]
        for row in findings[:MAX_ROWS]:
            op = f"{row.get('operation', '')} {row.get('path', '')}".strip()
            lines.append(
                f"| {_cell(row.get('level', ''))} | `{_cell(op)}` | {_cell(row.get('text', ''))} |"
            )
        if len(findings) > MAX_ROWS:
            lines.append(
                f"| ... | | {len(findings) - MAX_ROWS} more in the oasdiff report artifact |"
            )
    return lines


def render_schemathesis(report: dict[str, Any] | None) -> list[str]:
    """Markdown block for the Schemathesis report."""
    lines = ["### Schemathesis (OpenAPI property suite)", ""]
    if report is None:
        return [*lines, "_Not run (no `schemathesis.json`; suite is path-filtered)._"]
    counts = report.get("counts") or {}
    lines.append(
        f"- Result: **{_badge(report.get('status'))}** - {counts.get('total', 0)} operations "
        f"({counts.get('passed', 0)} passed, {counts.get('failed', 0)} failed, "
        f"{counts.get('skipped', 0)} skipped)"
    )
    lines.append(
        f"- Budget: `max_examples={report.get('max_examples', '?')}`, "
        f"schemathesis `{report.get('schemathesis_version', '?')}`"
    )
    failed = [r for r in report.get("results") or [] if r.get("outcome") == "failed"]
    if failed:
        lines += ["", "| Operation | Failure |", "|---|---|"]
        for row in failed[:MAX_ROWS]:
            lines.append(
                f"| `{_cell(row.get('operation', ''))}` | {_cell(row.get('detail') or 'see CI log')} |"
            )
        if len(failed) > MAX_ROWS:
            lines.append(
                f"| ... | {len(failed) - MAX_ROWS} more in the schemathesis report artifact |"
            )
    return lines


def overall_status(
    oasdiff: dict[str, Any] | None, schemathesis: dict[str, Any] | None
) -> str:
    """``fail`` if any tool failed, ``pass`` if at least one ran, else ``skipped``."""
    statuses = [r.get("status") for r in (oasdiff, schemathesis) if r is not None]
    if "fail" in statuses:
        return "fail"
    return "pass" if statuses else "skipped"


def build_comment(reports_dir: Path) -> str:
    """Assemble the full sticky comment body."""
    oasdiff = load_report(reports_dir / "oasdiff.json")
    schemathesis = load_report(reports_dir / "schemathesis.json")
    lines = [
        MARKER,
        "## API contract checks",
        "",
        f"Overall: **{_badge(overall_status(oasdiff, schemathesis))}**",
        "",
        *render_oasdiff(oasdiff),
        "",
        *render_schemathesis(schemathesis),
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    """CLI: print the comment for ``argv[1]`` (default ``.quality-reports``)."""
    reports_dir = Path(argv[1] if len(argv) > 1 else DEFAULT_DIR)
    sys.stdout.write(build_comment(reports_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
