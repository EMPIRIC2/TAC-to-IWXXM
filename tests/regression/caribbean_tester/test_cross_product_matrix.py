"""Issue-class matrix across METAR, SPECI, TAF, and SIGMET.

Pins, soft preview, lint, and decode stay in the same spirit as the tester
questionnaire. [Corpus: product §F6] [Corpus: product §F9] [Corpus: product §F15]
[Corpus: tests]
"""

from __future__ import annotations

import pytest
from tac2iwxxm.convert import convert
from tac_decoding import decode_tac
from tac_validate import lint

_VCSH = {
    "METAR": "METAR TTPP 080700Z 00000KT 9000 VCSH FEW015 27/24 Q1013 NOSIG=",
    "SPECI": "SPECI TKPK 231928Z 06011KT 9999 TS VCSH SCT015CB 30/26 Q1013=",
    "TAF": "TAF TNCM 081200Z 0812/0912 14006KT 9999 VCSH FEW020=",
}
_VCTS = {
    "METAR": "METAR TUPJ 072300Z 08004KT 10SM VCTS FEW012CB SCT020 29/26 A3001=",
    "SPECI": "SPECI TUPJ 071734Z 12007KT 10SM TS VCSH FEW012CB SCT017 30/25 A3000=",
    "TAF": "TAF TNCM 081200Z 0812/0912 14006KT 9999 VCTS FEW018CB=",
}
_TS = {
    "METAR": "METAR TKPK 232000Z 06005KT 9999 TS FEW006 SCT014CB 29/26 Q1014=",
    "SPECI": "SPECI TKPK 231928Z 06011KT 9999 TS SCT015CB 30/26 Q1013=",
    "TAF": (
        "TAF MZBZ 301500Z 3018/0118 11007KT 9999 SCT023 "
        "PROB30 TEMPO 3018/3021 TS FEW012CB="
    ),
}
_RECENT = {
    "METAR": "METAR SYCJ 071600Z 07006KT 9999 FEW014CB 27/24 Q1013 RETS NOSIG=",
    "SPECI": "SPECI TBPB 081538Z 07015KT 9999 -SHRA VCSH SCT010CB 28/26 Q1015 RETSRA NOSIG=",
}
_VRB = {
    "METAR": "METAR TNCM 081200Z VRB03KT 9999 FEW020 28/24 Q1013=",
    "SPECI": "SPECI TNCM 081230Z VRB02KT 9999 FEW020 28/24 Q1013=",
    "TAF": "TAF TNCM 081200Z 0812/0912 VRB03KT 9999 FEW020=",
}
_WIND_VAR = {
    "METAR": "METAR TTPP 072100Z 12008KT 070V160 7000 FEW024 31/24 Q1012 NOSIG=",
    "SPECI": "SPECI TTPP 072130Z 12008KT 070V160 7000 FEW024 31/24 Q1012=",
}
_GTS = {
    "METAR": "SAXX31 TNCM 081200\nMETAR TNCM 081200Z 14006KT 9999 FEW020 28/24 Q1013=",
    "SPECI": "SPXX31 TNCM 081230\nSPECI TNCM 081230Z 14006KT 9999 FEW020 28/24 Q1013=",
    "TAF": "FTXX31 TNCM 081200\nTAF TNCM 081200Z 0812/0912 14006KT 9999 FEW020=",
}
_LOWER = {
    "METAR": "metar tncm 081200z 14006kt 9999 few020 28/24 q1013=",
    "SPECI": "speci tncm 081230z 14006kt 9999 few020 28/24 q1013=",
    "TAF": "taf tncm 081200z 0812/0912 14006kt 9999 few020=",
}
_PINS = ("2023-1", "2025-2")
_PROFILES = ("annex3", "iwxxm_us")


@pytest.mark.parametrize(("product", "tac"), list(_VCSH.items()))
@pytest.mark.parametrize("iwxxm_version", _PINS)
def test_vcsh_converts_on_annex3_pins(
    product: str, tac: str, iwxxm_version: str
) -> None:
    result = convert(
        tac, product=product, iwxxm_version=iwxxm_version, bulletin_date="2026-10-08"
    )
    assert result.ok is True
    assert result.xml is not None
    assert "4678/VCSH" in result.xml or "VCSH" in result.xml


@pytest.mark.parametrize(("product", "tac"), list(_VCTS.items()))
def test_vcts_converts_and_is_not_invalid_weather(product: str, tac: str) -> None:
    result = convert(tac, product=product, bulletin_date="2026-10-08")
    assert result.ok is True
    assert result.xml is not None
    codes = {issue.code for issue in lint(tac, product=product).issues}
    assert "INVALID_WEATHER" not in codes


@pytest.mark.parametrize(("product", "tac"), list(_TS.items()))
def test_ts_present_or_change_group_emits(product: str, tac: str) -> None:
    result = convert(tac, product=product, bulletin_date="2026-10-30")
    assert result.ok is True
    assert result.xml is not None
    assert "4678/TS" in result.xml


@pytest.mark.parametrize(("product", "tac"), list(_RECENT.items()))
def test_recent_weather_decodes_and_converts(product: str, tac: str) -> None:
    decoded = decode_tac(tac, product=product)
    codes = {segment.code for segment in decoded.segments}
    assert any(code.startswith("RE") for code in codes)
    result = convert(tac, product=product, bulletin_date="2026-10-08")
    assert result.ok is True
    assert result.xml is not None


@pytest.mark.parametrize(("product", "tac"), list(_VRB.items()))
def test_variable_wind_keeps_knots_across_products(product: str, tac: str) -> None:
    result = convert(tac, product=product, bulletin_date="2026-10-08")
    assert result.ok is True
    assert result.xml is not None
    assert "[kn_i]" in result.xml


@pytest.mark.parametrize(("product", "tac"), list(_WIND_VAR.items()))
def test_wind_variation_extremes_across_metar_speci(product: str, tac: str) -> None:
    result = convert(tac, product=product, bulletin_date="2026-10-07")
    assert result.ok is True
    assert result.xml is not None
    assert "extremeClockwiseWindDirection" in result.xml
    assert "extremeCounterClockwiseWindDirection" in result.xml


@pytest.mark.parametrize(("product", "tac"), list(_GTS.items()))
def test_gts_heading_strips_for_metar_speci_taf(product: str, tac: str) -> None:
    result = convert(tac, product=product, bulletin_date="2026-10-08")
    assert result.ok is True
    assert result.xml is not None


@pytest.mark.parametrize(("product", "tac"), list(_LOWER.items()))
def test_lowercase_keywords_convert(product: str, tac: str) -> None:
    result = convert(tac, product=product, bulletin_date="2026-10-08")
    assert result.ok is True
    assert result.xml is not None


@pytest.mark.parametrize("profile", _PROFILES)
@pytest.mark.parametrize("iwxxm_version", _PINS)
def test_metar_vcsh_on_profiles_and_pins(profile: str, iwxxm_version: str) -> None:
    tac = _VCSH["METAR"]
    result = convert(
        tac,
        product="METAR",
        profile=profile,
        iwxxm_version=iwxxm_version,
        bulletin_date="2026-10-08",
    )
    assert result.ok is True
    assert result.xml is not None


def test_sigmet_decr_and_cnl_on_both_pins() -> None:
    decr = (
        "SIGMET 3 VALID 251435/251835 TTPP- "
        "TTZP PIARCO FIR EMBD TS OBS AT 1410Z WI N1800 W05406 - N1800 W05039 - "
        "N1031 W05542 - N1316 W05936 - N1800 W05406 TOP ABV FL380 STNR DECR="
    )
    cnl = (
        "TTZP SIGMET A4 VALID 141815/142145 TTPP- "
        "TTZP PIARCO FIR CNL SIGMET A3 141545/142145="
    )
    for pin in _PINS:
        weaken = convert(
            decr, product="SIGMET", iwxxm_version=pin, bulletin_date="2026-10-25"
        )
        assert weaken.ok is True
        assert weaken.xml is not None
        assert 'intensityChange="WEAKEN"' in weaken.xml
        cancel = convert(
            cnl, product="SIGMET", iwxxm_version=pin, bulletin_date="2026-10-14"
        )
        assert cancel.ok is True
        assert cancel.xml is not None
        assert 'isCancelReport="true"' in cancel.xml


def test_soft_preview_still_emits_xml_on_parse_failure() -> None:
    bad = "METAR TKPK 232100Z VBR02KT 9999 FEW014CB 29/25 Q1013="
    hard = convert(bad, product="METAR", bulletin_date="2026-10-23")
    soft = convert(bad, product="METAR", preview=True, bulletin_date="2026-10-23")
    assert any(issue.message == "missing wind group" for issue in hard.issues)
    assert soft.xml is not None
    assert soft.ok is False


def test_mkjp_unobserved_visibility_and_incomplete_dewpoint_fail_closed() -> None:
    mkjp = "METAR MKJP 072300Z 12012KT //// ////// 30/26 Q1013="
    ok = convert(mkjp, product="METAR", bulletin_date="2026-10-08")
    assert ok.ok is True
    assert ok.xml is not None
    assert "notObservable" in ok.xml

    incomplete = "METAR TRPG 081100Z 13013KT 080V150 9999 BKN019 27/ Q1016"
    bad = convert(incomplete, product="METAR", bulletin_date="2026-10-08")
    assert any("temperature/dewpoint" in issue.message for issue in bad.issues)


def test_taf_amd_not_sked_and_multiline() -> None:
    amd = "TAF AMD TTPP 081600Z 0818/0918 09012KT 9999 SCT018="
    result = convert(amd, product="TAF", bulletin_date="2026-10-08")
    assert result.ok is True
    multiline = (
        "TAF TTPP 081600Z 0818/0918 09012KT 9999 SCT018\nFM090200 14008KT 9999 FEW020="
    )
    multi = convert(multiline, product="TAF", bulletin_date="2026-10-08")
    assert multi.ok is True
    assert multi.xml is not None
    assert 'changeIndicator="FROM"' in multi.xml


def test_speci_without_trend_still_converts() -> None:
    tac = "SPECI TNCM 061126Z 09008KT 2000E SHRA BKN016 27/24 Q1016="
    result = convert(tac, product="SPECI", bulletin_date="2026-10-06")
    assert result.ok is True
    assert result.xml is not None
