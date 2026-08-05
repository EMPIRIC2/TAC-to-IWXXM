#!/usr/bin/env python3
"""Format sticky PR coverage markdown from downloaded coverage artifacts (EV-036).

Reads Cobertura ``coverage.xml`` (pytest-cov) and Vitest ``coverage-summary.json``
under a directory tree. Prints markdown including sticky marker for github-script.
"""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

MARKER = "<!-- EV-036-coverage-comment -->"


def _pct_from_rate(rate: str | None) -> float | None:
    if rate is None:
        return None
    try:
        return round(float(rate) * 100.0, 2)
    except ValueError:
        return None


def parse_cobertura(path: Path) -> tuple[float | None, float | None]:
    """Return (line_pct, branch_pct) from coverage.xml."""
    root = ET.parse(path).getroot()
    line = _pct_from_rate(root.attrib.get("line-rate"))
    branch = _pct_from_rate(root.attrib.get("branch-rate"))
    return line, branch


def parse_vitest_summary(path: Path) -> float | None:
    data = json.loads(path.read_text(encoding="utf-8"))
    total = data.get("total") or {}
    lines = total.get("lines") or {}
    pct = lines.get("pct")
    if pct is None:
        return None
    return round(float(pct), 2)


def package_label(path: Path, root: Path) -> str:
    rel = path.relative_to(root).as_posix()
    if "apps/backend" in rel or path.parent.name == "backend":
        return "backend"
    if "packages/" in rel:
        parts = Path(rel).parts
        try:
            i = parts.index("packages")
            return parts[i + 1]
        except (ValueError, IndexError):
            pass
    if "frontend" in rel:
        return "frontend"
    return path.parent.name


def collect_rows(root: Path) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    seen: set[str] = set()

    for xml_path in sorted(root.rglob("coverage.xml")):
        label = package_label(xml_path, root)
        if label in seen:
            continue
        line, branch = parse_cobertura(xml_path)
        seen.add(label)
        line_s = f"{line:.2f}%" if line is not None else "—"
        branch_s = f"{branch:.2f}%" if branch is not None else "—"
        rows.append((label, line_s, branch_s))

    for summary in sorted(root.rglob("coverage-summary.json")):
        label = (
            "frontend"
            if "frontend" in summary.as_posix()
            else package_label(summary, root)
        )
        if label in seen:
            continue
        pct = parse_vitest_summary(summary)
        seen.add(label)
        line_s = f"{pct:.2f}%" if pct is not None else "—"
        rows.append((label, line_s, "—"))

    return rows


def main(argv: list[str]) -> int:
    root = Path(argv[1] if len(argv) > 1 else "coverage-artifacts")
    rows = collect_rows(root) if root.is_dir() else []

    lines = [
        MARKER,
        "## Coverage summary (EV-036)",
        "",
        "Remote CI keeps the **unit matrix** with coverage gates; Compose/integration "
        "and `validate` run locally (pre-commit / pre-push).",
        "",
        "| Package | Lines | Branches |",
        "|---------|------:|---------:|",
    ]
    if not rows:
        lines.append("| _(no coverage artifacts)_ | — | — |")
    else:
        for label, line_s, branch_s in rows:
            lines.append(f"| `{label}` | {line_s} | {branch_s} |")

    lines.extend(
        [
            "",
            f"[Workflow run]({_run_url()})",
            "",
            "_Sticky comment — updated on each PR push. Codecov not used (EV-028)._",
            "",
        ]
    )
    sys.stdout.write("\n".join(lines))
    return 0


def _run_url() -> str:
    server = __import__("os").environ.get("GITHUB_SERVER_URL", "https://github.com")
    repo = __import__("os").environ.get("GITHUB_REPOSITORY", "EMPIRIC2/TAC-to-IWXXM")
    run_id = __import__("os").environ.get("GITHUB_RUN_ID", "")
    if run_id:
        return f"{server}/{repo}/actions/runs/{run_id}"
    return f"{server}/{repo}/actions"


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
