"""TC-EV066-004 - CA_ECCC MANOBS RMK lint deepen (EV-066 / #916).

[Corpus: product §F36] [Corpus: tests §TC-EV066]
"""

from __future__ import annotations

from pathlib import Path

from tac_validate import lint

FIXTURES = Path(__file__).resolve().parents[2] / "tac2iwxxm" / "tests" / "fixtures" / "profiles" / "CA_ECCC"


def test_tc_ev066_004_presrr_lint_codes() -> None:
    tac = (FIXTURES / "METAR/valid/metar_rmk_presrr.tac").read_text(encoding="utf-8")
    codes = {i.code for i in lint(tac, product="METAR", profile="ca_eccc").issues}
    assert "CA_REMARK_MANOBS" in codes
    assert "CA_REMARK_PRESRR" in codes


def test_tc_ev066_004_altimeter_not_obs_lint() -> None:
    tac = (FIXTURES / "METAR/valid/metar_alt_not_obs.tac").read_text(encoding="utf-8")
    codes = {i.code for i in lint(tac, product="METAR", profile="ca_eccc").issues}
    assert "CA_ALTIMETER_NOT_OBS" in codes
    assert "CA_ALTIMETER_INHG" not in codes


def test_tc_ev066_004_nospeci_lint() -> None:
    tac = (FIXTURES / "METAR/valid/metar_rmk_nospeci.tac").read_text(encoding="utf-8")
    codes = {i.code for i in lint(tac, product="METAR", profile="ca_eccc").issues}
    assert "CA_REMARK_NOSPECI" in codes


def test_tc_ev066_004_sector_vis_lint() -> None:
    tac = (FIXTURES / "METAR/valid/metar_rmk_sector_vis.tac").read_text(encoding="utf-8")
    codes = {i.code for i in lint(tac, product="METAR", profile="ca_eccc").issues}
    assert "CA_REMARK_SECTOR_VIS" in codes
    assert "CA_STATUTE_MILE_VIS" in codes
