"""Hydra shortcut for the national convert allowlist."""

from __future__ import annotations

import pytest
import scripts.tac2iwxxm
from scripts.tac2iwxxm.compose_convert_allowlist import main


def test_script_prints_packaged_allowlist(capsys: pytest.CaptureFixture[str]) -> None:
    assert scripts.tac2iwxxm.__doc__
    assert main([]) == 0
    captured = capsys.readouterr()
    assert "iwxxm_us:" in captured.out
    assert "VAA" in captured.out


def test_script_applies_hydra_override(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--override", "profiles.au_bom=[METAR,TAF]"]) == 0
    captured = capsys.readouterr()
    assert "au_bom: METAR, TAF" in captured.out
