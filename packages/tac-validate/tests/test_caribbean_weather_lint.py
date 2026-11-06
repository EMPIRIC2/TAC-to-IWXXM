"""Lint must not flag Caribbean VCSH / VCTS / TS or MKJP //// as errors.

[Corpus: product §F15] [Corpus: tests]
"""

from __future__ import annotations

from tac_validate import lint


def _codes(tac: str, product: str = "METAR") -> set[str]:
    return {issue.code for issue in lint(tac, product=product).issues}


def test_lint_accepts_vicinity_showers_and_thunderstorms() -> None:
    assert "INVALID_WEATHER" not in _codes("METAR TKPK 081600Z 09015KT 9999 VCSH FEW018 32/25 Q1018=")
    assert "INVALID_WEATHER" not in _codes("METAR MKJS 080900Z 08007KT 9999 VCTS FEW022CB 28/25 Q1014=")
    assert "INVALID_WEATHER" not in _codes("METAR TTPP 080700Z 00000KT 9000 VCSH FEW015 27/24 Q1013 NOSIG=")
    assert "INVALID_WEATHER" not in _codes("METAR TNCM 081200Z 14006KT 9999 TS FEW020 28/24 Q1013=")
    assert "INVALID_WEATHER" not in _codes(
        "SPECI TKPK 231928Z 06011KT 9999 TS VCSH SCT015CB 30/26 Q1013=",
        product="SPECI",
    )


def test_mkjp_slash_visibility_is_not_missing() -> None:
    mkjp = "METAR MKJP 072300Z 12012KT //// ////// 30/26 Q1013 RMK CLD FROM CEILOMETER RWY 30 NCD="
    codes = _codes(mkjp)
    assert "MISSING_VISIBILITY" not in codes
    assert "NCD_PRESENT" not in codes


def test_lint_accepts_taf_and_speci_vicinity_weather() -> None:
    taf = "TAF TNCM 081200Z 0812/0912 14006KT 9999 VCSH FEW020="
    assert "INVALID_WEATHER" not in _codes(taf, product="TAF")
    speci = "SPECI TUPJ 071734Z 12007KT 10SM VCTS FEW012CB SCT017 30/25 A3000="
    assert "INVALID_WEATHER" not in _codes(speci, product="SPECI")


def test_lint_accepts_recent_weather_tokens() -> None:
    assert "INVALID_WEATHER" not in _codes("METAR SYCJ 071600Z 07006KT 9999 FEW014CB 27/24 Q1013 RETS NOSIG=")
    assert "INVALID_WEATHER" not in _codes(
        "SPECI TBPB 081538Z 07015KT 9999 SCT014 28/26 Q1015 RETSRA NOSIG=",
        product="SPECI",
    )
