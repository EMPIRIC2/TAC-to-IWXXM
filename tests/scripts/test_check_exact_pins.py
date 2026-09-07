"""Unit coverage for scripts/ci/check-exact-pins.py (EV-049)."""

from __future__ import annotations

import re
import runpy
from pathlib import Path
from typing import Any

import pytest
from tests.scripts.conftest import REPO_ROOT, load_script


@pytest.fixture
def pins() -> Any:
    return load_script("ci/check-exact-pins.py", "check_exact_pins_under_test")


@pytest.mark.unit
def test_load_allowlist_missing(
    pins: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(pins, "ALLOWLIST_PATH", tmp_path / "missing.txt")
    assert pins.load_allowlist() == set()


@pytest.mark.unit
def test_load_allowlist_comments_and_entries(
    pins: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "allow.txt"
    path.write_text("# comment\n\nfoo\nbar:baz\n", encoding="utf-8")
    monkeypatch.setattr(pins, "ALLOWLIST_PATH", path)
    assert pins.load_allowlist() == {"foo", "bar:baz"}


@pytest.mark.unit
def test_allowed_patterns(pins: Any) -> None:
    allow = {"exact:name", "alone", "pkg.json", "prefix:*", "*:starname"}
    assert pins.allowed(allow, "exact", "name")
    assert pins.allowed(allow, "x", "alone")
    assert pins.allowed(allow, "pkg.json", "anything")
    assert pins.allowed(allow, "prefix", "dep")
    assert pins.allowed(allow, "other", "starname")
    assert not pins.allowed(allow, "exact", "other")


@pytest.mark.unit
def test_check_package_json_ranges_and_skips(
    pins: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path
    pkg = root / "package.json"
    pkg.write_text(
        """{
          "dependencies": {
            "exact": "1.2.3",
            "caret": "^1.0.0",
            "filedep": "file:../local",
            "linkdep": "link:../local",
            "ws": "workspace:*"
          },
          "devDependencies": { "tilde": "~2.0.0" },
          "optionalDependencies": "not-a-dict"
        }""",
        encoding="utf-8",
    )
    pins.ROOT = root
    violations: list[str] = []
    pins.check_package_json(pkg, {"package.json:tilde"}, violations)
    assert any("caret" in v for v in violations)
    assert not any("exact" in v for v in violations)
    assert not any("tilde" in v for v in violations)
    assert not any("filedep" in v for v in violations)

    # Force RANGE_RE match on a digit-leading exact-looking version → continue at L66
    monkeypatch.setattr(pins, "RANGE_RE", re.compile(r"."))
    violations2: list[str] = []
    pkg2 = root / "pkg2.json"
    pkg2.write_text('{"dependencies": {"n": "1.2.3"}}', encoding="utf-8")
    pins.check_package_json(pkg2, set(), violations2)
    assert violations2 == []


@pytest.mark.unit
def test_check_pyproject_unpinned_and_exact(
    pins: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path
    py = root / "pyproject.toml"
    py.write_text(
        """
[project]
dependencies = [
  "good==1.0.0",
  "bad>=1.0",
  "bare",
  "!!!",
  "allowedpkg>=1",
  "marked==2.0; python_version>='3.11'",
]
[project.optional-dependencies]
dev = ["ruff==0.1.0", "pytest>=8"]
""",
        encoding="utf-8",
    )
    pins.ROOT = root
    violations: list[str] = []
    pins.check_pyproject(py, {"pyproject.toml:allowedpkg"}, violations)
    joined = "\n".join(violations)
    assert "bad" in joined
    assert "bare" in joined
    assert "pytest" in joined
    assert "good" not in joined
    assert "ruff" not in joined
    assert "marked" not in joined
    assert "allowedpkg" not in joined

    # Hit == exact continue inside PY_RANGE branch (normally unreachable)
    monkeypatch.setattr(pins, "PY_RANGE_RE", re.compile(r"=="))
    violations3: list[str] = []
    py3 = root / "py3.toml"
    py3.write_text('[project]\ndependencies = ["z==9.9.9"]\n', encoding="utf-8")
    pins.check_pyproject(py3, set(), violations3)
    assert violations3 == []


@pytest.mark.unit
def test_check_pyproject_tomli_fallback(
    pins: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import builtins
    import sys
    import tomllib
    from types import ModuleType

    py = tmp_path / "pyproject.toml"
    py.write_text('[project]\ndependencies = ["x==1.0.0"]\n', encoding="utf-8")
    pins.ROOT = tmp_path
    fake_tomli = ModuleType("tomli")
    fake_tomli.loads = tomllib.loads  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "tomli", fake_tomli)
    real_import = builtins.__import__

    def _import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "tomllib":
            raise ImportError("forced")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _import)
    violations: list[str] = []
    pins.check_pyproject(py, set(), violations)
    assert violations == []


@pytest.mark.unit
def test_main_pass_fail_and_skips(
    pins: Any,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "exact-pins-allowlist.txt").write_text("", encoding="utf-8")
    (tmp_path / "package.json").write_text(
        '{"dependencies": {"ok": "1.0.0"}}',
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text(
        '[project]\ndependencies = ["x==1.0.0"]\n',
        encoding="utf-8",
    )
    skipped = tmp_path / "node_modules" / "pkg"
    skipped.mkdir(parents=True)
    (skipped / "package.json").write_text(
        '{"dependencies": {"evil": "^9.0.0"}}',
        encoding="utf-8",
    )
    (skipped / "pyproject.toml").write_text(
        '[project]\ndependencies = ["evil>=1"]\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(pins, "ROOT", tmp_path)
    monkeypatch.setattr(
        pins, "ALLOWLIST_PATH", tmp_path / "config" / "exact-pins-allowlist.txt"
    )
    assert pins.main() == 0
    assert "PASS" in capsys.readouterr().out

    (tmp_path / "package.json").write_text(
        '{"dependencies": {"bad": "^2.0.0"}}',
        encoding="utf-8",
    )
    assert pins.main() == 1
    err = capsys.readouterr().err
    assert "FAILED" in err
    assert "bad" in err


@pytest.mark.unit
def test_check_exact_pins_main_entrypoint() -> None:
    path = REPO_ROOT / "scripts/ci/check-exact-pins.py"
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(path), run_name="__main__")
    assert exc.value.code in (0, 1)
