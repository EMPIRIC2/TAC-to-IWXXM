"""Bare wind-shear runway (WS R14R) must not emit INVALID_RVR.

Covers detector YAML select and legacy ``_check_r8_pack`` skip (``/`` required).

[Corpus: product §F15] [Corpus: tests]
"""

from __future__ import annotations

import pytest
from tac_validate.product_rules_pkg.metar_speci import _check_metar_speci

_SKBO_WS = "METAR SKBO 021500Z 06006KT 360V110 9999 BKN040 17/11 Q1029 WS R14R NOSIG"


@pytest.mark.parametrize("mode", ["detector", "legacy"])
def test_ws_runway_not_invalid_rvr(monkeypatch: pytest.MonkeyPatch, mode: str) -> None:
    monkeypatch.setenv("TAC_VALIDATE_DETECTOR_MODE", mode)
    issues = _check_metar_speci(_SKBO_WS, "METAR", profile="annex3")
    assert "INVALID_RVR" not in {i.code for i in issues}
