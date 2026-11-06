"""Vicinity showers, bare thunderstorms, recent weather, unknown cloud base."""

from __future__ import annotations

from tac2iwxxm import convert


def test_convert_keeps_vicinity_showers_and_a_bare_thunderstorm() -> None:
    showers = convert(
        "METAR TNCM 081200Z 14006KT 9999 VCSH FEW020 28/24 Q1013=",
        product="METAR",
    )
    assert showers.ok
    assert showers.xml is not None
    assert 'presentWeather xlink:href="http://codes.wmo.int/306/4678/VCSH"' in showers.xml

    storm = convert(
        "METAR TNCM 081200Z 14006KT 9999 TS FEW020 28/24 Q1013=",
        product="METAR",
    )
    assert storm.ok
    assert storm.xml is not None
    assert 'presentWeather xlink:href="http://codes.wmo.int/306/4678/TS"' in storm.xml

    vicinity = convert(
        "METAR TNCM 081200Z 14006KT 9999 VCTS FEW020 28/24 Q1013=",
        product="METAR",
    )
    assert vicinity.ok
    assert vicinity.xml is not None
    assert 'presentWeather xlink:href="http://codes.wmo.int/306/4678/VCTS"' in vicinity.xml


def test_convert_writes_recent_weather_on_the_default_profile() -> None:
    result = convert(
        "SPECI TNCM 262321Z 10007KT 9999 VCSH SCT014 23/21 Q1017 RESHRA=",
        product="SPECI",
    )
    assert result.ok
    assert result.xml is not None
    assert 'recentWeather xlink:href="http://codes.wmo.int/306/4678/SHRA"' in result.xml
    assert 'presentWeather xlink:href="http://codes.wmo.int/306/4678/VCSH"' in result.xml


def test_convert_writes_recent_thunderstorm_and_bare_showers() -> None:
    recent = convert(
        "METAR TNCM 081200Z 14006KT 9999 FEW020 28/24 Q1013 RETS=",
        product="METAR",
    )
    assert recent.ok
    assert recent.xml is not None
    assert 'recentWeather xlink:href="http://codes.wmo.int/306/4678/TS"' in recent.xml

    bare = convert(
        "METAR TNCM 081200Z 14006KT 9999 FEW020 28/24 Q1013 RESH=",
        product="METAR",
    )
    assert bare.ok
    assert bare.xml is not None
    assert 'recentWeather xlink:href="http://codes.wmo.int/306/4678/SH"' in bare.xml
    assert "SHUP" not in bare.xml


def test_taf_keeps_an_unknown_cloud_base_with_cumulonimbus() -> None:
    result = convert(
        "TAF TNCM 081200Z 0812/0912 14006KT 9999 FEW///CB=",
        product="TAF",
    )
    assert result.ok
    assert result.xml is not None
    assert 'nilReason="http://codes.wmo.int/common/nil/notObservable"' in result.xml
    assert 'cloudType xlink:href="http://codes.wmo.int/49-2/SigConvectiveCloudType/CB"' in result.xml


def test_convert_keeps_an_unknown_cloud_base_with_cumulonimbus() -> None:
    result = convert(
        "METAR TNCM 081200Z 14006KT 9999 FEW///CB 28/24 Q1013=",
        product="METAR",
    )
    assert result.ok
    assert result.xml is not None
    assert 'nilReason="http://codes.wmo.int/common/nil/notObservable"' in result.xml
    assert 'cloudType xlink:href="http://codes.wmo.int/49-2/SigConvectiveCloudType/CB"' in result.xml
