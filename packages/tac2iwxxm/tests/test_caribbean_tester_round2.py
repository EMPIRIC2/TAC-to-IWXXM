"""Caribbean Met Services round-2 locks.

Covers TAF base-forecast weather (Guyana/Belize), wind sector extremes (TT),
METAR VRB knots (Belize), FM change groups, and SIGMET DECR/CNL (TT).
[Corpus: product §F6] [Corpus: tests]
"""

from __future__ import annotations

from tac2iwxxm import convert

_TAF_BASE_WX = "TAF SYCJ 291100Z 2912/3012 08010KT 8000 VCSH SHRA FEW018TCU BKN020="
_TAF_BASE_VCTS = "TAF TNCM 081200Z 0812/0912 14006KT 9999 VCTS FEW018CB="
_TAF_BASE_VCSH = "TAF TNCM 081200Z 0812/0912 14006KT 9999 VCSH FEW020="
_TAF_TEMPO_TS = "TAF MZBZ 301500Z 3018/0118 11007KT 9999 SCT023 PROB30 TEMPO 3018/3021 TS FEW012CB="
_TAF_FM = "TAF TLPL 081700Z 0818/0918 09012KT 9999 SCT018 FM090200 14008KT 9999 FEW020="
_TAF_TT_CHANGES = (
    "TAF TTPP 081600Z 0818/0918 09012KT 9999 SCT018 BECMG 0902/0904 14008KT TEMPO 0906/0912 4000 -SHRA BKN014="
)
_WIND_VAR = "METAR TTPP 072100Z 12008KT 070V160 7000 FEW024 31/24 Q1012 NOSIG="
_METAR_VRB = "METAR TNCM 081200Z VRB03KT 9999 FEW020 28/24 Q1013="
_BELIZE_VCSH = "METAR MZBZ 250000Z 00000KT 9999 VCSH BKN016 28/25 A2985 Q1010 NOSIG="
_ST_KITTS_TS_VCSH = "METAR TKPK 232000Z 06005KT 9999 TS VCSH FEW006 SCT014CB 29/26 Q1014="
_SPECI_TS_VCSH = "SPECI TKPK 231928Z 06011KT 9999 TS VCSH SCT015CB 30/26 Q1013="
_SIGMET_DECR = (
    "SIGMET 3 VALID 251435/251835 TTPP- "
    "TTZP PIARCO FIR EMBD TS OBS AT 1410Z WI N1800 W05406 - N1800 W05039 - "
    "N1031 W05542 - N1316 W05936 - N1800 W05406 TOP ABV FL380 STNR DECR="
)
_SIGMET_CNL = "TTZP SIGMET A4 VALID 141815/142145 TTPP- TTZP PIARCO FIR CNL SIGMET A3 141545/142145="
_MKJP = "METAR MKJP 072300Z 12012KT //// ////// 30/26 Q1013 RMK CLD FROM CEILOMETER RWY 30 NCD="
_GTS = "SAXX31 TNCM 081200\nMETAR TNCM 081200Z 14006KT 9999 FEW020 28/24 Q1013="


def test_taf_base_forecast_emits_vicinity_showers_and_rain() -> None:
    result = convert(_TAF_BASE_WX, product="TAF", bulletin_date="2026-10-29")
    assert result.ok
    assert result.xml is not None
    base = result.xml.split("changeForecast", 1)[0]
    assert 'weather xlink:href="http://codes.wmo.int/306/4678/VCSH"' in base
    assert 'weather xlink:href="http://codes.wmo.int/306/4678/SHRA"' in base


def test_taf_base_forecast_emits_vicinity_thunderstorms() -> None:
    result = convert(_TAF_BASE_VCTS, product="TAF", bulletin_date="2026-10-08")
    assert result.ok
    assert result.xml is not None
    base = result.xml.split("changeForecast", 1)[0]
    assert 'weather xlink:href="http://codes.wmo.int/306/4678/VCTS"' in base


def test_taf_base_forecast_emits_vicinity_showers_alone() -> None:
    result = convert(_TAF_BASE_VCSH, product="TAF", bulletin_date="2026-10-08")
    assert result.ok
    assert result.xml is not None
    assert 'weather xlink:href="http://codes.wmo.int/306/4678/VCSH"' in result.xml


def test_taf_tempo_thunderstorm_and_prob30_indicator() -> None:
    result = convert(_TAF_TEMPO_TS, product="TAF", bulletin_date="2026-10-30")
    assert result.ok
    assert result.xml is not None
    assert 'weather xlink:href="http://codes.wmo.int/306/4678/TS"' in result.xml
    assert 'changeIndicator="PROBABILITY_30_TEMPORARY_FLUCTUATIONS"' in result.xml


def test_taf_from_group_keeps_caribbean_fm_change() -> None:
    result = convert(_TAF_FM, product="TAF", bulletin_date="2026-10-08")
    assert result.ok
    assert result.xml is not None
    assert 'changeIndicator="FROM"' in result.xml


def test_taf_tt_becmg_and_tempo_change_indicators() -> None:
    result = convert(_TAF_TT_CHANGES, product="TAF", bulletin_date="2026-10-08")
    assert result.ok
    assert result.xml is not None
    assert 'changeIndicator="BECOMING"' in result.xml
    assert 'changeIndicator="TEMPORARY_FLUCTUATIONS"' in result.xml
    assert 'weather xlink:href="http://codes.wmo.int/306/4678/-SHRA"' in result.xml


def test_metar_wind_variation_emits_extreme_directions() -> None:
    result = convert(_WIND_VAR, product="METAR", bulletin_date="2026-10-07")
    assert result.ok
    assert result.xml is not None
    assert '<iwxxm:extremeClockwiseWindDirection uom="deg">160</iwxxm:extremeClockwiseWindDirection>' in result.xml
    assert (
        '<iwxxm:extremeCounterClockwiseWindDirection uom="deg">70</iwxxm:extremeCounterClockwiseWindDirection>'
        in result.xml
    )


def test_metar_variable_wind_keeps_knots() -> None:
    result = convert(_METAR_VRB, product="METAR", bulletin_date="2026-10-08")
    assert result.ok
    assert result.xml is not None
    assert '<iwxxm:meanWindSpeed uom="[kn_i]">3</iwxxm:meanWindSpeed>' in result.xml


def test_caribbean_metar_present_weather_locks() -> None:
    belize = convert(_BELIZE_VCSH, product="METAR", bulletin_date="2026-10-25")
    assert belize.ok
    assert belize.xml is not None
    assert 'presentWeather xlink:href="http://codes.wmo.int/306/4678/VCSH"' in belize.xml

    kitts = convert(_ST_KITTS_TS_VCSH, product="METAR", bulletin_date="2026-10-23")
    assert kitts.ok
    assert kitts.xml is not None
    assert 'presentWeather xlink:href="http://codes.wmo.int/306/4678/TS"' in kitts.xml
    assert 'presentWeather xlink:href="http://codes.wmo.int/306/4678/VCSH"' in kitts.xml

    speci = convert(_SPECI_TS_VCSH, product="SPECI", bulletin_date="2026-10-23")
    assert speci.ok
    assert speci.xml is not None
    assert 'presentWeather xlink:href="http://codes.wmo.int/306/4678/TS"' in speci.xml


def test_sigmet_decr_weakens_and_keeps_top_flight_level() -> None:
    result = convert(_SIGMET_DECR, product="SIGMET", bulletin_date="2026-10-25")
    assert result.ok
    assert result.xml is not None
    assert 'intensityChange="WEAKEN"' in result.xml
    assert 'uom="FL">380</aixm:upperLimit>' in result.xml


def test_sigmet_cancellation_is_cancel_report() -> None:
    result = convert(_SIGMET_CNL, product="SIGMET", bulletin_date="2026-10-14")
    assert result.ok
    assert result.xml is not None
    assert 'isCancelReport="true"' in result.xml


def test_mkjp_unobserved_visibility_still_converts() -> None:
    result = convert(_MKJP, product="METAR", bulletin_date="2026-10-08")
    assert result.ok is True
    assert result.xml is not None
    assert "notObservable" in result.xml


def test_gts_heading_before_metar_converts() -> None:
    result = convert(_GTS, product="METAR", bulletin_date="2026-10-08")
    assert result.ok
    assert result.xml is not None


def test_gts_heading_before_taf_converts() -> None:
    tac = "FTXX31 TNCM 081200\nTAF TNCM 081200Z 0812/0912 14006KT 9999 FEW020="
    result = convert(tac, product="TAF", bulletin_date="2026-10-08")
    assert result.ok is True
    assert result.xml is not None
    assert "TNCM" in result.xml


def test_gts_heading_before_speci_converts() -> None:
    tac = "SPXX31 TNCM 081230\nSPECI TNCM 081230Z 14006KT 9999 FEW020 28/24 Q1013="
    result = convert(tac, product="SPECI", bulletin_date="2026-10-08")
    assert result.ok is True
    assert result.xml is not None
    assert "TNCM" in result.xml
