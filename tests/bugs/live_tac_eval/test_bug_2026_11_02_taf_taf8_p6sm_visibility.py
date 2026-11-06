"""Live TAF P6SM must emit baseForecast prevailingVisibility (TAF.TAF-8).

NA TAF with statute-mile visibility (e.g. CYBC ``P6SM`` + clouds) converted with
``cloudAndVisibilityOK=false`` but omitted ``prevailingVisibility``, failing
Schematron TAF.TAF-8 (~77% of 30d IWXXM validate fails).

Product-rule fix in tac2iwxxm TAF emit — not a severity soften.

[Corpus: product §F6] [Corpus: tests]
"""

from __future__ import annotations

import re

from tac2iwxxm.slot_builders.taf import parse_taf
from tac2iwxxm.visibility_measure import prevailing_from_statute_miles

from tac2iwxxm import convert

# Live-tac-eval-30d resample (CYBC / TAF.TAF-8).
_CYBC_P6SM = (
    "TAF CYBC 021340Z 0214/0302 03005KT P6SM SCT050 "
    "BECMG 0214/0216 28012G22KT "
    "FM022100 28010KT P6SM FEW050 BKN140 "
    "RMK FCST BASED ON AUTO OBS. NXT FCST BY 022000Z"
)

_BASE_FCST = re.compile(
    r"<iwxxm:baseForecast>\s*"
    r"<iwxxm:MeteorologicalAerodromeForecast\b(?P<attrs>[^>]*)>"
    r"(?P<body>.*?)"
    r"</iwxxm:MeteorologicalAerodromeForecast>\s*"
    r"</iwxxm:baseForecast>",
    re.DOTALL,
)


def _base_forecast(xml: str) -> tuple[str, str]:
    match = _BASE_FCST.search(xml)
    assert match is not None, "expected non-nil baseForecast"
    return match.group("attrs"), match.group("body")


def test_cybc_p6sm_ir_keeps_statute_mile_record_without_metres() -> None:
    """Parser contract from TC-F6-053: P6SM stays SM-only in IR."""
    ir = parse_taf(_CYBC_P6SM, product="TAF")
    assert ir["visibility_sm"] == 6
    assert ir["visibility_above"] is True
    assert "visibility_m" not in ir
    assert ir.get("cavok") is not True
    assert ir.get("clouds")


def test_cybc_p6sm_base_forecast_emits_prevailing_visibility() -> None:
    result = convert(
        _CYBC_P6SM, product="TAF", iwxxm_version="2025-2", profile="annex3"
    )
    assert result.ok is True
    assert result.xml is not None
    attrs, body = _base_forecast(result.xml)
    assert 'cloudAndVisibilityOK="false"' in attrs
    metres, _ = prevailing_from_statute_miles(6)
    assert (
        f'<iwxxm:prevailingVisibility uom="m">{metres}</iwxxm:prevailingVisibility>'
        in body
    )
    assert (
        "<iwxxm:prevailingVisibilityOperator>ABOVE</iwxxm:prevailingVisibilityOperator>"
        in body
    )
    assert "<iwxxm:cloud>" in body


def test_taf_whole_sm_below_ten_also_emits_metres_visibility() -> None:
    """6SM (no P) likewise lacked visibility_m and must still emit for TAF-8."""
    tac = "TAF CYBC 021340Z 0214/0302 03005KT 6SM SCT050="
    result = convert(tac, product="TAF", iwxxm_version="2025-2", profile="annex3")
    assert result.ok is True
    assert result.xml is not None
    _attrs, body = _base_forecast(result.xml)
    metres, _ = prevailing_from_statute_miles(6)
    assert (
        f'<iwxxm:prevailingVisibility uom="m">{metres}</iwxxm:prevailingVisibility>'
        in body
    )
    assert "prevailingVisibilityOperator" not in body
