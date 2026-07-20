"""T4.2 convert fidelity — AUTO automatedStation + CAVOK cloudAndVisibilityOK (EV-011)."""

from __future__ import annotations

from tac2iwxxm import convert
from tac2iwxxm.products.metar_speci import parse_metar_speci


def test_auto_sets_ir_and_automated_station_attr() -> None:
    tac = "METAR KJFK 231751Z AUTO 18012KT 10SM FEW040 15/07 A3005="
    ir = parse_metar_speci(tac, product="METAR")
    assert ir.get("auto") is True
    result = convert(tac, product="METAR", profile="annex3", iwxxm_version="2025-2")
    assert result.ok and result.xml
    assert 'automatedStation="true"' in result.xml


def test_cavok_sets_cloud_and_visibility_ok() -> None:
    tac = "METAR KJFK 231751Z 18012KT CAVOK 15/07 Q1013="
    ir = parse_metar_speci(tac, product="METAR")
    assert ir.get("cavok") is True
    result = convert(tac, product="METAR", profile="annex3", iwxxm_version="2025-2")
    assert result.ok and result.xml
    assert 'cloudAndVisibilityOK="true"' in result.xml


def test_iwxxm_us_auto_sets_automated_station() -> None:
    tac = "METAR KJFK 231751Z AUTO 18012KT 10SM CLR 15/07 A3005 RMK AO2 SLP176="
    result = convert(tac, product="METAR", profile="iwxxm_us", iwxxm_version="2025-2")
    assert result.ok and result.xml
    assert 'automatedStation="true"' in result.xml
    assert "iwxxm-us" in result.xml
