"""Unit tests for scripts/docs/check_docs_py.py (TC-EVDOC-001..003 fixtures)."""

from __future__ import annotations

from pathlib import Path

from scripts.docs.check_docs_py import check_file, main

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def test_py_ok_fixture_clean() -> None:
    """Happy-path fixture produces zero violations."""
    path = FIXTURES / "py_ok" / "sample.py"
    assert check_file(path) == []


def test_py_bad_fixture_reports_gaps() -> None:
    """Bad fixture reports missing docs / Examples / Parameters."""
    path = FIXTURES / "py_bad" / "sample.py"
    issues = check_file(path)
    joined = "\n".join(issues)
    assert "bare" in joined
    assert "_no_doc" in joined


def test_main_ok_explicit() -> None:
    """CLI with explicit OK path exits 0."""
    assert main([str(ROOT), "--paths", str(FIXTURES / "py_ok" / "sample.py")]) == 0


def test_main_bad_explicit() -> None:
    """CLI with explicit bad path exits 1."""
    assert main([str(ROOT), "--paths", str(FIXTURES / "py_bad" / "sample.py")]) == 1
