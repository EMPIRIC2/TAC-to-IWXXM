"""EV-080 M4 — 100% coverage for scripts/ci/format_quality_pr_comment.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from scripts.ci import format_quality_pr_comment as mod

ROOT = Path(__file__).resolve().parents[2]


def test_as_int_branches() -> None:
    assert mod._as_int("3") == 3
    assert mod._as_int(None) == 0
    assert mod._as_int("x") == 0


def test_parse_summary_and_collect_rows(tmp_path: Path) -> None:
    path = tmp_path / "annex3" / "quality-summary.json"
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "source": "annex3-golden",
                "rows": [
                    {"product": "", "profile": "", "match": 1},
                    "not-a-row",
                    {
                        "product": "METAR",
                        "profile": "annex3",
                        "match": 2,
                        "soft_diff": 1,
                        "fail": 0,
                        "skip": 0,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    source, rows = mod.parse_summary(path)
    assert source == "annex3-golden"
    assert rows[0][0] == ("?", "?")
    assert rows[1] == (("METAR", "annex3"), (2, 1, 0, 0))

    alt = tmp_path / "extra-quality-summary.json"
    alt.write_text(
        json.dumps(
            {
                "source": "alt",
                "rows": [{"product": "TAF", "profile": "annex3", "match": 1}],
            }
        ),
        encoding="utf-8",
    )
    agg, sources = mod.collect_rows(tmp_path)
    assert agg[("METAR", "annex3")][0] == 2
    assert agg[("TAF", "annex3")][0] == 1
    assert "annex3-golden" in sources
    assert "alt" in sources


def test_format_markdown_branches(monkeypatch: pytest.MonkeyPatch) -> None:
    empty = mod.format_markdown({}, [])
    assert "no quality artifacts" in empty
    assert mod.MARKER in empty

    md = mod.format_markdown({("METAR", "annex3"): [1, 0, 0, 0]}, ["annex3-golden"])
    assert "**Sources:**" in md
    assert "`annex3-golden`" in md

    monkeypatch.setenv("GITHUB_RUN_ID", "99")
    md_run = mod.format_markdown({("METAR", "annex3"): [1, 0, 0, 0]}, ["src"])
    assert "/actions/runs/99" in md_run


def test_main_paths(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert mod.main(["script", str(tmp_path / "missing")]) == 0
    captured = capsys.readouterr()
    assert "no quality artifacts" in captured.out

    summary = tmp_path / "q" / "quality-summary.json"
    summary.parent.mkdir(parents=True)
    summary.write_text(
        json.dumps(
            {
                "source": "x",
                "rows": [{"product": "METAR", "profile": "annex3", "match": 1}],
            }
        ),
        encoding="utf-8",
    )
    assert mod.main(["script", str(tmp_path)]) == 0
    captured = capsys.readouterr()
    assert "`METAR`" in captured.out
    assert "`annex3`" in captured.out
    assert "| 1 |" in captured.out


def test_collect_rows_duplicate_source(tmp_path: Path) -> None:
    for name in ("quality-summary.json", "extra-quality-summary.json"):
        path = tmp_path / name
        path.write_text(
            json.dumps(
                {
                    "source": "dup",
                    "rows": [{"product": "METAR", "profile": "annex3", "match": 1}],
                }
            ),
            encoding="utf-8",
        )
    _agg, sources = mod.collect_rows(tmp_path)
    assert sources.count("dup") == 1


def test_main_entrypoint_subprocess(tmp_path: Path) -> None:

    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/ci/format_quality_pr_comment.py"),
            str(tmp_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
