"""Coverage for profile overlay check + tac2iwxxm CLI (#1227)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from tac2iwxxm.cli import main
from tac2iwxxm.overlay_check import check_profile_overlay_dir
from tac2iwxxm.profile_resolve import ProfileResolveError

_STARTERS = Path(__file__).resolve().parents[1] / "examples" / "starters"
_INVALID = Path(__file__).resolve().parents[1] / "examples" / "overlays" / "invalid-bad-extends"


def test_check_profile_overlay_dir_loads_starters() -> None:
    check_profile_overlay_dir(_STARTERS)


def test_check_profile_overlay_dir_rejects_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        check_profile_overlay_dir(tmp_path / "nope")


def test_check_profile_overlay_dir_rejects_bad_extends() -> None:
    with pytest.raises(ProfileResolveError):
        check_profile_overlay_dir(_INVALID)


def test_check_profile_overlay_dir_restores_prior_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAC2IWXXM_PROFILE_DIR", "/tmp/prior-overlay")
    check_profile_overlay_dir(_STARTERS)
    assert os.environ.get("TAC2IWXXM_PROFILE_DIR") == "/tmp/prior-overlay"


def test_cli_check_overlay_ok() -> None:
    assert main(["--check-overlay", str(_STARTERS)]) == 0


def test_cli_check_overlay_fails() -> None:
    assert main(["--check-overlay", str(_INVALID)]) == 1


def test_cli_module_main_guard(monkeypatch: pytest.MonkeyPatch) -> None:
    import runpy

    monkeypatch.setattr(sys, "argv", ["tac2iwxxm", "--check-overlay", str(_STARTERS)])
    with pytest.raises(SystemExit) as exc:
        runpy.run_module("tac2iwxxm.cli", run_name="__main__")
    assert exc.value.code == 0
