"""Bare RESH stays recent showers. It is not rewritten to SHUP."""

from __future__ import annotations

import re

from tac2iwxxm.recent_weather import accept_recent_code
from tac2iwxxm.slot_builders.metar_speci import parse_metar_speci

from tac2iwxxm import convert

_SPECI = "SPECI TNCM 081200Z 14006KT 9999 -SHRA FEW020 28/24 Q1013 RESHRA="
_RESH = "METAR TNCM 081200Z 14006KT 9999 FEW020 28/24 Q1013 RESH="
_RETS = "METAR TNCM 081200Z 14006KT 9999 FEW020 28/24 Q1013 RETS="
_TOKEN = re.compile(r"SHRA|TS|SHUP|RA")


def test_speci_sample_keeps_recent_rain_showers_beside_present_weather() -> None:
    result = convert(_SPECI, product="SPECI", bulletin_date="2026-10-08")
    assert result.ok is True
    assert result.xml is not None
    assert 'presentWeather xlink:href="http://codes.wmo.int/306/4678/-SHRA"' in result.xml
    assert 'recentWeather xlink:href="http://codes.wmo.int/306/4678/SHRA"' in result.xml
    assert "SHUP" not in result.xml


def test_bare_resh_is_recent_showers_and_rets_is_a_recent_thunderstorm() -> None:
    showers = convert(_RESH, product="METAR", bulletin_date="2026-10-08")
    assert showers.ok is True
    assert showers.xml is not None
    assert 'recentWeather xlink:href="http://codes.wmo.int/306/4678/SH"' in showers.xml
    assert "SHUP" not in showers.xml
    storm = convert(_RETS, product="METAR", bulletin_date="2026-10-08")
    assert storm.ok is True
    assert storm.xml is not None
    assert 'recentWeather xlink:href="http://codes.wmo.int/306/4678/TS"' in storm.xml


def test_an_unknown_recent_token_is_left_out() -> None:
    ir = parse_metar_speci(
        "METAR TNCM 081200Z 14006KT 9999 FEW020 28/24 Q1013 REFOO=",
        product="METAR",
    )
    assert "recent_weather" not in ir
    assert accept_recent_code("SH", weather_token=_TOKEN) == "SH"
    assert accept_recent_code("SHRA", weather_token=_TOKEN) == "SHRA"
    assert accept_recent_code("TS", weather_token=_TOKEN) == "TS"
    assert accept_recent_code("SHUP", weather_token=_TOKEN) == "SHUP"
    assert accept_recent_code("FOO", weather_token=_TOKEN) is None
    assert accept_recent_code("", weather_token=_TOKEN) is None
