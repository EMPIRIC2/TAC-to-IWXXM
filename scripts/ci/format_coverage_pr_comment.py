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


def _cli(argv: list[str]) -> tuple[Path, list[str], str | None]:
    """Return ``(root, required labels, error)``.

    ``--require`` is a comma-separated list of package labels that must appear
    in the comment at a 100% line rate (#1433).
    """
    positional: list[str] = []
    require: list[str] = []
    args = argv[1:]
    index = 0
    while index < len(args):
        token = args[index]
        if token != "--require":
            positional.append(token)
            index += 1
            continue
        if index + 1 >= len(args):
            return (
                Path(),
                [],
                "error: --require needs a comma-separated package list",
            )
        require.extend(
            part.strip() for part in args[index + 1].split(",") if part.strip()
        )
        index += 2
    root = Path(positional[0] if positional else "coverage-artifacts")
    return root, require, None


def _missing_line_rate(
    rows: list[tuple[str, str, str]], require: list[str]
) -> list[str]:
    """Labels that are absent or whose line cell is not ``100.00%``."""
    by_label = {label: line for label, line, _branch in rows}
    return [label for label in require if by_label.get(label) != "100.00%"]


def main(argv: list[str]) -> int:
    root, require, error = _cli(argv)
    if error:
        print(error, file=sys.stderr)
        return 2
    rows = collect_rows(root) if root.is_dir() else []
    missing = _missing_line_rate(rows, require)

    lines = [
        MARKER,
        "## Coverage summary (EV-036 / EV-080)",
        "",
        "Remote CI keeps the **unit matrix** with coverage gates; Compose/integration "
        "and `validate` run locally (pre-commit / pre-push).",
        "",
        "**Gate:** **100%** line + branch (ADR-007 / EV-080). Scripts: Python cov + bats.",
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
    if missing:
        joined = ", ".join(missing)
        print(
            f"error: coverage comment missing 100% line rate for: {joined}",
            file=sys.stderr,
        )
        return 1
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
