"""CAVOK TAF baseForecast must still emit surfaceWind (TAF.TAF-7).

Schematron TAF.TAF-7 requires ``iwxxm:surfaceWind`` whenever baseForecast is
non-empty. Emit previously skipped wind when ``cloudAndVisibilityOK`` was true,
matching ~179 live-map CAVOK TAF validate fails in the 30d eval.

Product-rule fix in tac2iwxxm TAF emit — not a severity soften.

[Corpus: product §F6] [Corpus: tests]
"""

from __future__ import annotations

import re

from tac2iwxxm import convert

# Live-map CAVOK sample pattern (Europe/NA CAVOK TAF traffic).
_ENBR_CAVOK = "TAF ENBR 021100Z 0212/0312 36005KT CAVOK"

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


def test_cavok_taf_base_forecast_emits_surface_wind() -> None:
    result = convert(
        _ENBR_CAVOK, product="TAF", iwxxm_version="2025-2", profile="annex3"
    )
    assert result.ok is True
    assert result.xml is not None
    attrs, body = _base_forecast(result.xml)
    assert 'cloudAndVisibilityOK="true"' in attrs
    assert "<iwxxm:surfaceWind>" in body
    assert 'variableWindDirection="false"' in body
    assert '<iwxxm:meanWindDirection uom="deg">360</iwxxm:meanWindDirection>' in body
    assert '<iwxxm:meanWindSpeed uom="[kn_i]">5</iwxxm:meanWindSpeed>' in body
    # CAVOK still omits visibility/cloud blocks
    assert "prevailingVisibility" not in body
    assert "<iwxxm:cloud>" not in body


def test_cavok_with_vrb_wind_emits_variable_surface_wind() -> None:
    tac = "TAF DAOB 021100Z 0212/0312 VRB02KT CAVOK"
    result = convert(tac, product="TAF", iwxxm_version="2025-2", profile="annex3")
    assert result.ok is True
    assert result.xml is not None
    _attrs, body = _base_forecast(result.xml)
    assert "<iwxxm:surfaceWind>" in body
    assert 'variableWindDirection="true"' in body
    assert "meanWindDirection" not in body
    assert '<iwxxm:meanWindSpeed uom="[kn_i]">2</iwxxm:meanWindSpeed>' in body
