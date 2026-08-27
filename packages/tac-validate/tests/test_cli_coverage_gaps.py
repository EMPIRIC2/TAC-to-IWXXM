"""CLI coverage gaps - OSError path, issue spans, ``__main__`` entry."""

from __future__ import annotations

import io
import runpy
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import pytest
from tac_validate.cli import main
from tac_validate.models import Issue, LintReport


def test_cli_read_oserror_returns_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    missing = tmp_path / "nope.tac"
    err = io.StringIO()
    with redirect_stderr(err):
        code = main(["--product", "METAR", str(missing)])
    assert code == 1
    assert "cannot read" in err.getvalue()


def test_cli_prints_issue_spans(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    tac = tmp_path / "x.tac"
    tac.write_text("METAR KJFK=\n", encoding="utf-8")

    report = LintReport(
        ok=False,
        product="METAR",
        issues=[
            Issue(
                severity="error",
                code="MISSING_CCCC",
                message="missing",
                start=0,
                end=5,
            )
        ],
    )
    monkeypatch.setattr("tac_validate.cli.lint", lambda *_a, **_k: report)
    out = io.StringIO()
    with redirect_stdout(out):
        code = main(["--product", "METAR", str(tac)])
    assert code == 1
    assert "[0:5]" in out.getvalue()


def test_cli_omits_incomplete_issue_span(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    tac = tmp_path / "x.tac"
    tac.write_text("METAR KJFK=\n", encoding="utf-8")
    report = LintReport(
        ok=False,
        product="METAR",
        issues=[
            Issue(
                severity="error",
                code="MISSING_CCCC",
                message="missing",
                start=0,
                end=None,
            )
        ],
    )
    monkeypatch.setattr("tac_validate.cli.lint", lambda *_a, **_k: report)
    out = io.StringIO()

    with redirect_stdout(out):
        code = main(["--product", "METAR", str(tac)])

    assert code == 1
    assert "[0:" not in out.getvalue()


def test_cli_module_main_guard(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["tac-validate", "--help"])
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_module("tac_validate.cli", run_name="__main__")
    assert excinfo.value.code == 0
