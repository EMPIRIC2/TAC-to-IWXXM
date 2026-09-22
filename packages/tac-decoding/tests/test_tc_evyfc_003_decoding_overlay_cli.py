"""Coverage for pack overlay check + CLI --check-overlay (#1227)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from tac_decoding.cli import main
from tac_decoding.overlay_check import check_pack_overlay_dir
from tac_decoding.packs import PackSchemaError

_STARTERS = Path(__file__).resolve().parents[1] / "examples" / "starters"
_INVALID = Path(__file__).resolve().parents[1] / "examples" / "overlays" / "invalid-bad-extends"


def test_check_pack_overlay_dir_loads_starters() -> None:
    check_pack_overlay_dir(_STARTERS)


def test_check_pack_overlay_dir_rejects_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        check_pack_overlay_dir(tmp_path / "nope")


def test_check_pack_overlay_dir_rejects_bad_extends() -> None:
    with pytest.raises(PackSchemaError, match="unknown builtin"):
        check_pack_overlay_dir(_INVALID)


def test_check_pack_overlay_dir_restores_prior_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TAC_DECODING_PACK_DIR", "/tmp/prior-overlay")
    check_pack_overlay_dir(_STARTERS)
    assert os.environ.get("TAC_DECODING_PACK_DIR") == "/tmp/prior-overlay"


def test_cli_check_overlay_ok() -> None:
    assert main(["--check-overlay", str(_STARTERS)]) == 0


def test_cli_check_overlay_fails() -> None:
    assert main(["--check-overlay", str(_INVALID)]) == 1


def test_cli_requires_path_without_check_overlay() -> None:
    with pytest.raises(SystemExit):
        main([])


def test_cli_decode_summary_and_json(tmp_path: Path) -> None:
    tac = tmp_path / "sample.tac"
    tac.write_text("METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=", encoding="utf-8")
    assert main([str(tac)]) == 0
    assert main(["--json", str(tac)]) == 0
