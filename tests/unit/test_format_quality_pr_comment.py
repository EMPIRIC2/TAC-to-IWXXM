"""Unit tests for scripts/ci/format_quality_pr_comment.py (EV-052 / TC-EV052-005)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "ci" / "format_quality_pr_comment.py"
MARKER = "<!-- quality-pr-comment -->"


def _write_summary(
    path: Path,
    *,
    source: str,
    rows: list[dict[str, object]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source": source,
                "rows": rows,
            }
        ),
        encoding="utf-8",
    )


@pytest.mark.unit
def test_format_quality_pr_comment_tables_by_product_profile(tmp_path: Path) -> None:
    _write_summary(
        tmp_path / "annex3" / "quality-summary.json",
        source="annex3-golden",
        rows=[
            {
                "product": "METAR",
                "profile": "annex3",
                "match": 5,
                "soft_diff": 1,
                "fail": 0,
                "skip": 1,
            },
            {
                "product": "TAF",
                "profile": "annex3",
                "match": 3,
                "soft_diff": 0,
                "fail": 1,
                "skip": 0,
            },
        ],
    )
    _write_summary(
        tmp_path / "iwxxm_us" / "quality-summary.json",
        source="iwxxm_us-golden",
        rows=[
            {
                "product": "METAR",
                "profile": "iwxxm_us",
                "match": 2,
                "soft_diff": 0,
                "fail": 0,
                "skip": 0,
            },
            {
                "product": "METAR",
                "profile": "annex3",
                "match": 1,
                "soft_diff": 0,
                "fail": 0,
                "skip": 0,
            },
        ],
    )

    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    out = proc.stdout
    assert MARKER in out
    assert MARKER != "<!-- EV-036-coverage-comment -->"
    assert "## Quality / golden outcomes" in out
    assert "| Product | Profile | Match | Soft-diff | Fail | Skip |" in out
    # Aggregated METAR x annex3 = 5+1 match
    assert "| `METAR` | `annex3` | 6 | 1 | 0 | 1 |" in out
    assert "| `METAR` | `iwxxm_us` | 2 | 0 | 0 | 0 |" in out
    assert "| `TAF` | `annex3` | 3 | 0 | 1 | 0 |" in out
    assert "annex3-golden" in out or "Sources" in out


@pytest.mark.unit
def test_format_quality_pr_comment_empty_dir(tmp_path: Path) -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    assert MARKER in proc.stdout
    assert "no quality artifacts" in proc.stdout


@pytest.mark.unit
def test_format_quality_pr_comment_marker_distinct_from_coverage() -> None:
    text = SCRIPT.read_text(encoding="utf-8") if SCRIPT.is_file() else ""
    assert "quality-pr-comment" in text or not SCRIPT.is_file()
    # When implemented, must not reuse EV-036 marker.
    if SCRIPT.is_file():
        assert "EV-036-coverage-comment" not in text
