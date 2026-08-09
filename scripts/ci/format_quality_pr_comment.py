#!/usr/bin/env python3
"""Format sticky PR quality/golden markdown from summary JSON artifacts (EV-052).

Reads ``quality-summary.json`` (and ``*-quality-summary.json``) under a directory
tree. Each file uses schema_version 1 with rows of
product / profile / match / soft_diff / fail / skip counts.

Prints markdown including sticky marker for github-script (distinct from EV-036).
"""

from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

MARKER = "<!-- quality-pr-comment -->"

RowKey = tuple[str, str]
Counts = tuple[int, int, int, int]  # match, soft_diff, fail, skip


def _as_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def parse_summary(path: Path) -> tuple[str, list[tuple[RowKey, Counts]]]:
    """
    Parse one quality-summary JSON file.

    Parameters
    ----------
    path : Path
        Path to a ``*quality-summary.json`` file.

    Returns
    -------
    tuple[str, list[tuple[RowKey, Counts]]]
        Source label and row tuples.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    source = str(data.get("source") or path.parent.name or "unknown")
    rows_out: list[tuple[RowKey, Counts]] = []
    for row in data.get("rows") or []:
        if not isinstance(row, dict):
            continue
        product = str(row.get("product") or "").strip() or "?"
        profile = str(row.get("profile") or "").strip() or "?"
        counts: Counts = (
            _as_int(row.get("match")),
            _as_int(row.get("soft_diff")),
            _as_int(row.get("fail")),
            _as_int(row.get("skip")),
        )
        rows_out.append(((product, profile), counts))
    return source, rows_out


def collect_rows(root: Path) -> tuple[dict[RowKey, list[int]], list[str]]:
    """
    Aggregate counts by product x profile across summary files.

    Parameters
    ----------
    root : Path
        Artifact tree root.

    Returns
    -------
    tuple[dict[RowKey, list[int]], list[str]]
        Aggregated counts and distinct source labels.
    """
    agg: dict[RowKey, list[int]] = defaultdict(lambda: [0, 0, 0, 0])
    sources: list[str] = []
    seen_sources: set[str] = set()

    paths = sorted(
        {
            *root.rglob("quality-summary.json"),
            *root.rglob("*-quality-summary.json"),
        }
    )
    for path in paths:
        source, rows = parse_summary(path)
        if source not in seen_sources:
            seen_sources.add(source)
            sources.append(source)
        for key, counts in rows:
            bucket = agg[key]
            for i, n in enumerate(counts):
                bucket[i] += n
    return dict(agg), sources


def format_markdown(
    agg: dict[RowKey, list[int]],
    sources: list[str],
) -> str:
    """
    Render sticky PR markdown for aggregated quality outcomes.

    Parameters
    ----------
    agg : dict[RowKey, list[int]]
        Counts keyed by (product, profile).
    sources : list[str]
        Source labels included in the artifact tree.

    Returns
    -------
    str
        Markdown body including sticky marker.
    """
    lines = [
        MARKER,
        "## Quality / golden outcomes",
        "",
        "Match / soft-diff / fail / skip by **product x profile** "
        "(quality-matrix + annex3 / `iwxxm_us` goldens).",
        "",
        "| Product | Profile | Match | Soft-diff | Fail | Skip |",
        "|---------|---------|------:|----------:|-----:|-----:|",
    ]
    if not agg:
        lines.append("| _(no quality artifacts)_ | — | — | — | — | — |")
    else:
        for product, profile in sorted(agg.keys(), key=lambda k: (k[0], k[1])):
            m, s, f, sk = agg[(product, profile)]
            lines.append(f"| `{product}` | `{profile}` | {m} | {s} | {f} | {sk} |")

    if sources:
        lines.extend(
            [
                "",
                "**Sources:** " + ", ".join(f"`{s}`" for s in sources),
            ]
        )

    lines.extend(
        [
            "",
            f"[Workflow run]({_run_url()})",
            "",
            "_Sticky comment — updated on each PR push (separate from coverage)._",
            "",
        ]
    )
    return "\n".join(lines)


def _run_url() -> str:
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    repo = os.environ.get("GITHUB_REPOSITORY", "EMPIRIC2/TAC-to-IWXXM")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    if run_id:
        return f"{server}/{repo}/actions/runs/{run_id}"
    return f"{server}/{repo}/actions"


def main(argv: list[str]) -> int:
    root = Path(argv[1] if len(argv) > 1 else "quality-artifacts")
    agg, sources = collect_rows(root) if root.is_dir() else ({}, [])
    sys.stdout.write(format_markdown(agg, sources))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
