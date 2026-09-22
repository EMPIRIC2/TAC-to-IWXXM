"""Coverage for TAC policy overlay check + CLI --check-overlay (#1227)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from tac_validate.cli import main
from tac_validate.overlay_check import check_tac_policy_overlay_dir
from tac_validate.policy import PolicyError

_STARTERS = Path(__file__).resolve().parents[1] / "examples" / "starters"
_INVALID = Path(__file__).resolve().parents[1] / "examples" / "overlays" / "invalid-bad-extends"


def test_check_tac_policy_overlay_dir_loads_starters() -> None:
    check_tac_policy_overlay_dir(_STARTERS)


def test_check_tac_policy_overlay_dir_rejects_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        check_tac_policy_overlay_dir(tmp_path / "nope")


def test_check_tac_policy_overlay_dir_rejects_bad_extends() -> None:
    with pytest.raises(PolicyError):
        check_tac_policy_overlay_dir(_INVALID)


def test_check_tac_policy_overlay_dir_restores_prior_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAC_VALIDATE_POLICY_DIR", "/tmp/prior-overlay")
    check_tac_policy_overlay_dir(_STARTERS)
    assert os.environ.get("TAC_VALIDATE_POLICY_DIR") == "/tmp/prior-overlay"


def test_cli_check_overlay_ok() -> None:
    assert main(["--check-overlay", str(_STARTERS)]) == 0


def test_cli_check_overlay_fails() -> None:
    assert main(["--check-overlay", str(_INVALID)]) == 1


def test_cli_requires_path_and_product_without_check_overlay() -> None:
    with pytest.raises(SystemExit):
        main([])
    with pytest.raises(SystemExit):
        main([str(_STARTERS / "metar-quality-starter.yaml")])
