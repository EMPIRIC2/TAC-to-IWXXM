#!/usr/bin/env python3
"""Fail if any measured source file is under a coverage floor (EV-047 / ADR-007).

Reads ``coverage.json`` produced by ``coverage json`` (or pytest-cov's
``--cov-report=json``). For each file with ``num_statements > 0``, requires
``percent_covered >= min_pct`` (default 100.0).

Usage::

    python scripts/ci/check_per_file_coverage.py coverage.json
    python scripts/ci/check_per_file_coverage.py coverage.json --min-pct 100
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def file_percent(summary: dict[str, Any]) -> float | None:
    """
    Return coverage percent for one file summary, or None if empty.

    Parameters
    ----------
    summary :
        ``coverage.json`` ``files[*].summary`` object.

    Returns
    -------
    float or None
        ``percent_covered`` when the file has statements; otherwise None.
    """
    stmts = int(summary.get("num_statements") or 0)
    if stmts <= 0:
        return None
    pct = summary.get("percent_covered")
    if pct is None:
        return None
    return float(pct)


def files_below_floor(
    report: dict[str, Any],
    *,
    min_pct: float,
) -> list[tuple[str, float]]:
    """
    List ``(path, percent)`` entries below ``min_pct``.

    Parameters
    ----------
    report :
        Parsed ``coverage.json`` document.
    min_pct :
        Inclusive floor (e.g. ``100.0``).

    Returns
    -------
    list of tuple
        Sorted by ascending percent, then path.
    """
    files = report.get("files") or {}
    below: list[tuple[str, float]] = []
    for path, data in files.items():
        if not isinstance(data, dict):
            continue
        summary = data.get("summary") or {}
        if not isinstance(summary, dict):
            continue
        pct = file_percent(summary)
        if pct is None:
            continue
        if pct + 1e-9 < min_pct:
            below.append((str(path), pct))
    below.sort(key=lambda item: (item[1], item[0]))
    return below


def check_report(
    report: dict[str, Any],
    *,
    min_pct: float = 100.0,
) -> int:
    """
    Print a report and return process exit code (0=ok, 1=below floor).

    Parameters
    ----------
    report :
        Parsed ``coverage.json``.
    min_pct :
        Per-file floor.

    Returns
    -------
    int
        ``0`` when every measured file meets the floor; ``1`` otherwise.
    """
    below = files_below_floor(report, min_pct=min_pct)
    if not below:
        print(f"per-file coverage OK — all measured files ≥ {min_pct:.2f}%")
        return 0
    print(
        f"per-file coverage FAIL — {len(below)} file(s) below {min_pct:.2f}%:",
        file=sys.stderr,
    )
    for path, pct in below:
        print(f"  {pct:6.2f}%  {path}", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "coverage_json",
        type=Path,
        help="Path to coverage.json from `coverage json` / pytest --cov-report=json",
    )
    parser.add_argument(
        "--min-pct",
        type=float,
        default=100.0,
        help="Per-file percent_covered floor (default: 100)",
    )
    args = parser.parse_args(argv)
    path: Path = args.coverage_json
    if not path.is_file():
        print(f"error: coverage json not found: {path}", file=sys.stderr)
        return 2
    report = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(report, dict):
        print("error: coverage json root must be an object", file=sys.stderr)
        return 2
    return check_report(report, min_pct=float(args.min_pct))


if __name__ == "__main__":
    raise SystemExit(main())
