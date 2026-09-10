"""Coverage for scripts/pypi/bump_calver.py (EV-1150 / ADR-043)."""

from __future__ import annotations

import runpy
import sys
from datetime import date
from pathlib import Path

import pytest
import scripts.pypi.bump_calver as bump


@pytest.mark.unit
def test_calver_string_base_and_suffixes() -> None:
    assert bump.calver_string(day=date(2026, 9, 10)) == "2026.9.10"
    assert bump.calver_string(day=date(2026, 9, 10), same_day_n=2) == "2026.9.10.2"
    assert bump.calver_string(day=date(2026, 9, 10), dev=7) == "2026.9.10.dev7"
    assert (
        bump.calver_string(day=date(2026, 9, 10), same_day_n=1, dev=3)
        == "2026.9.10.1.dev3"
    )
    assert bump.calver_string(same_day_n=0, dev=0).count(".") >= 2


@pytest.mark.unit
def test_replace_version_missing_raises() -> None:
    with pytest.raises(ValueError, match="version field not found"):
        bump._replace_version("no version here", bump.VERSION_RE, "1.0.0")


@pytest.mark.unit
def test_set_package_version_unknown_raises() -> None:
    with pytest.raises(KeyError):
        bump.set_package_version("not-a-package", "2099.1.1")


@pytest.mark.unit
def test_set_package_version_roundtrip_tac_validate() -> None:
    py = bump.PACKAGES["tac-validate"]["pyproject"]
    init = bump.PACKAGES["tac-validate"]["init"]
    py_orig = py.read_text(encoding="utf-8")
    init_orig = init.read_text(encoding="utf-8")
    try:
        changed = bump.set_package_version("tac-validate", "2099.1.1")
        assert py in changed
        assert init in changed
        assert 'version = "2099.1.1"' in py.read_text(encoding="utf-8")
        assert '__version__ = "2099.1.1"' in init.read_text(encoding="utf-8")
    finally:
        py.write_text(py_orig, encoding="utf-8")
        init.write_text(init_orig, encoding="utf-8")


@pytest.mark.unit
def test_set_package_version_writes_cargo() -> None:
    paths = bump.PACKAGES["iwxxm-validate"]
    originals = {k: p.read_text(encoding="utf-8") for k, p in paths.items()}
    try:
        changed = bump.set_package_version("iwxxm-validate", "2099.2.2")
        assert paths["cargo"] in changed
        assert 'version = "2099.2.2"' in paths["cargo"].read_text(encoding="utf-8")
    finally:
        for key, text in originals.items():
            paths[key].write_text(text, encoding="utf-8")


@pytest.mark.unit
def test_set_package_version_skips_missing_cargo(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    fake = {
        "pyproject": tmp_path / "pyproject.toml",
        "init": tmp_path / "__init__.py",
        "cargo": tmp_path / "missing" / "Cargo.toml",
    }
    fake["pyproject"].write_text('version = "0.1.0"\n', encoding="utf-8")
    fake["init"].write_text('__version__ = "0.1.0"\n', encoding="utf-8")
    monkeypatch.setitem(bump.PACKAGES, "tac-validate", fake)
    changed = bump.set_package_version("tac-validate", "2099.3.3")
    assert fake["cargo"] not in changed
    assert 'version = "2099.3.3"' in fake["pyproject"].read_text(encoding="utf-8")


@pytest.mark.unit
def test_main_print_only(capsys: pytest.CaptureFixture[str]) -> None:
    assert bump.main(["--print-only", "--date", "2026-09-10", "--dev", "3"]) == 0
    assert capsys.readouterr().out.strip() == "2026.9.10.dev3"


@pytest.mark.unit
def test_main_bad_date_errors() -> None:
    with pytest.raises(SystemExit):
        bump.main(["--print-only", "--date", "2026.09"])


@pytest.mark.unit
def test_main_requires_package_or_all() -> None:
    with pytest.raises(SystemExit):
        bump.main([])


@pytest.mark.unit
def test_main_package_flag_writes_and_restores() -> None:
    paths = bump.PACKAGES["tac-validate"]
    originals = {k: p.read_text(encoding="utf-8") for k, p in paths.items()}
    try:
        assert bump.main(["--package", "tac-validate", "--date", "2099.1.2"]) == 0
        assert 'version = "2099.1.2"' in paths["pyproject"].read_text(encoding="utf-8")
    finally:
        for key, text in originals.items():
            paths[key].write_text(text, encoding="utf-8")


@pytest.mark.unit
def test_main_all_writes_and_restores() -> None:
    snapshots: dict[Path, str] = {}
    for paths in bump.PACKAGES.values():
        for path in paths.values():
            snapshots[path] = path.read_text(encoding="utf-8")
    try:
        rc = bump.main(["--all", "--date", "2099.12.31", "--same-day-n", "1"])
        assert rc == 0
        assert 'version = "2099.12.31.1"' in bump.PACKAGES["tac2iwxxm"][
            "pyproject"
        ].read_text(encoding="utf-8")
    finally:
        for path, text in snapshots.items():
            path.write_text(text, encoding="utf-8")


@pytest.mark.unit
def test_module_entrypoint(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        sys, "argv", ["bump_calver.py", "--print-only", "--date", "2026.1.1"]
    )
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_module("scripts.pypi.bump_calver", run_name="__main__")
    assert excinfo.value.code == 0
