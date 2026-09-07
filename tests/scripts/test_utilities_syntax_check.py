"""Coverage for scripts/utilities/syntax_check.py."""
# ruff: noqa: SIM117

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import scripts.utilities.syntax_check as syntax_check


@pytest.mark.unit
def test_check_syntax_ok(tmp_path: Path) -> None:
    good = tmp_path / "good.py"
    good.write_text("x = 1\n", encoding="utf-8")
    ok, err = syntax_check.check_syntax(good)
    assert ok is True
    assert err == ""


@pytest.mark.unit
def test_check_syntax_bad(tmp_path: Path) -> None:
    bad = tmp_path / "bad.py"
    bad.write_text("def oops(\n", encoding="utf-8")
    ok, err = syntax_check.check_syntax(bad)
    assert ok is False
    assert err


@pytest.mark.unit
def test_find_python_files_single_non_py(tmp_path: Path) -> None:
    assert syntax_check.find_python_files(tmp_path / "readme.txt") == []


@pytest.mark.unit
def test_find_python_files_single_py(tmp_path: Path) -> None:
    py = tmp_path / "one.py"
    py.write_text("pass\n", encoding="utf-8")
    assert syntax_check.find_python_files(py) == [py]


@pytest.mark.unit
def test_main_missing_path(capsys: pytest.CaptureFixture[str]) -> None:
    with patch.object(sys, "argv", ["syntax_check.py", str(Path("/no/such/path"))]):
        with pytest.raises(SystemExit) as exc:
            syntax_check.main()
    assert exc.value.code == 1
    assert "does not exist" in capsys.readouterr().out


@pytest.mark.unit
def test_main_no_python_files(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    with patch.object(sys, "argv", ["syntax_check.py", str(tmp_path)]):
        with pytest.raises(SystemExit) as exc:
            syntax_check.main()
    assert exc.value.code == 0
    assert "No Python files found" in capsys.readouterr().out


@pytest.mark.unit
def test_main_syntax_errors(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    bad = tmp_path / "bad.py"
    bad.write_text("def oops(\n", encoding="utf-8")
    with patch.object(sys, "argv", ["syntax_check.py", str(bad)]):
        with pytest.raises(SystemExit) as exc:
            syntax_check.main()
    assert exc.value.code == 1
    assert "SYNTAX ERRORS" in capsys.readouterr().out


@pytest.mark.unit
def test_main_all_success(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    root = tmp_path / "proj"
    scripts_dir = root / "scripts"
    (scripts_dir / "utilities").mkdir(parents=True)
    good = scripts_dir / "ok.py"
    good.write_text("x = 1\n", encoding="utf-8")
    monkeypatch.setattr(
        syntax_check,
        "__file__",
        str(scripts_dir / "utilities" / "syntax_check.py"),
    )
    with patch.object(sys, "argv", ["syntax_check.py", "--all"]):
        with pytest.raises(SystemExit) as exc:
            syntax_check.main()
    assert exc.value.code == 0


@pytest.mark.unit
def test_main_relative_path_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    good = tmp_path / "ok.py"
    good.write_text("x = 1\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    with (
        patch.object(
            syntax_check.Path, "relative_to", side_effect=ValueError("outside cwd")
        ),
        patch.object(sys, "argv", ["syntax_check.py", str(good)]),
    ):
        with pytest.raises(SystemExit) as exc:
            syntax_check.main()
    assert exc.value.code == 0


@pytest.mark.unit
def test_main_usage_when_no_args(capsys: pytest.CaptureFixture[str]) -> None:
    with patch.object(sys, "argv", ["syntax_check.py"]):
        with pytest.raises(SystemExit) as exc:
            syntax_check.main()
    assert exc.value.code == 1
    assert "Syntax checker" in capsys.readouterr().out


@pytest.mark.unit
def test_check_syntax_returns_error_message(tmp_path: Path) -> None:
    bad = tmp_path / "bad.py"
    bad.write_text("def oops(\n", encoding="utf-8")
    ok, err = syntax_check.check_syntax(bad)
    assert ok is False
    assert "oops" in err or "SyntaxError" in err
