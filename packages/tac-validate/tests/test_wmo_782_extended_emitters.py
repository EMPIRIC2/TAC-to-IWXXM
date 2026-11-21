"""Emitters for WMO-782 proposed→existing METAR/SPECI combination codes."""

from __future__ import annotations

from tac_validate import lint
from tac_validate.issue_registry import by_code


def _codes(report) -> set[str]:
    return {i.code for i in report.issues}


def test_registry_has_extended_codes() -> None:
    for code in (
        "RVR_MAX_GROUPS",
        "WEATHER_SHPL_FORBIDDEN",
        "CLOUD_HEIGHT_NOT_ASCENDING",
        "TREND_PROB_FORBIDDEN",
        "WIND_CALM_MISENCODE",
        "CAVOK_EXCLUDES_RVR",
        "NATIONAL_RMK_NOT_INTERNATIONAL",
    ):
        assert by_code(code).code == code


def test_rvr_max_groups_and_missing_solidus() -> None:
    tac = "METAR KJFK 211025Z 18005KT 0800 R01/0500 R02/0500 R03/0500 R04/0500 R05/P2000 FEW040 15/07 Q1013="
    report = lint(tac, product="METAR")
    assert "RVR_MAX_GROUPS" in _codes(report)


def test_rvr_missing_solidus() -> None:
    tac = "METAR KJFK 211025Z 18005KT 0800 R24///// FEW040 15/07 Q1013="
    report = lint(tac, product="METAR")
    assert "RVR_MISSING_AS_SOLIDUS" in _codes(report)


def test_weather_shpl_forbidden() -> None:
    tac = "METAR KJFK 211025Z 18005KT 3000 SHPL FEW040 15/07 Q1013="
    report = lint(tac, product="METAR")
    assert "WEATHER_SHPL_FORBIDDEN" in _codes(report)


def test_cavok_excludes_rvr() -> None:
    tac = "METAR KJFK 211025Z 18005KT CAVOK R01/P2000 15/07 Q1013="
    report = lint(tac, product="METAR")
    assert "CAVOK_EXCLUDES_RVR" in _codes(report)


def test_cloud_height_not_ascending() -> None:
    tac = "METAR KJFK 211025Z 18005KT 9999 BKN020 FEW010 15/07 Q1013="
    report = lint(tac, product="METAR")
    assert "CLOUD_HEIGHT_NOT_ASCENDING" in _codes(report)


def test_ncd_requires_auto() -> None:
    tac = "METAR KJFK 211025Z 18005KT 9999 NCD 15/07 Q1013="
    report = lint(tac, product="METAR")
    assert "NCD_REQUIRES_AUTO" in _codes(report)


def test_temp_dewpoint_inversion() -> None:
    tac = "METAR KJFK 211025Z 18005KT 9999 FEW040 10/12 Q1013="
    report = lint(tac, product="METAR")
    assert "TEMP_DEWPOINT_INVERSION" in _codes(report)


def test_wind_calm_misencode() -> None:
    tac = "METAR KJFK 211025Z 18000KT 9999 FEW040 15/07 Q1013="
    report = lint(tac, product="METAR")
    assert "WIND_CALM_MISENCODE" in _codes(report)


def test_wind_gust_below_threshold() -> None:
    tac = "METAR KJFK 211025Z 18010G15KT 9999 FEW040 15/07 Q1013="
    report = lint(tac, product="METAR")
    assert "WIND_GUST_BELOW_THRESHOLD" in _codes(report)


def test_trend_prob_forbidden() -> None:
    tac = "METAR KJFK 211025Z 18005KT 9999 FEW040 15/07 Q1013 BECMG PROB30 2000="
    report = lint(tac, product="METAR")
    assert "TREND_PROB_FORBIDDEN" in _codes(report)


def test_trend_fm_six_digit_forbidden() -> None:
    tac = "METAR KJFK 211025Z 18005KT 9999 FEW040 15/07 Q1013 BECMG FM091200 2000="
    report = lint(tac, product="METAR")
    assert "TREND_FM_FORMAT" in _codes(report)


def test_national_rmk_info() -> None:
    tac = "METAR KJFK 211025Z 18005KT 9999 FEW040 15/07 Q1013 RMK AO2="
    report = lint(tac, product="METAR")
    assert "NATIONAL_RMK_NOT_INTERNATIONAL" in _codes(report)


def test_ws_all_rwy_exclusive() -> None:
    tac = "METAR KJFK 211025Z 18005KT 9999 FEW040 15/07 Q1013 WS ALL RWY WS R24="
    report = lint(tac, product="METAR")
    assert "WS_ALL_RWY_EXCLUSIVE" in _codes(report)


def test_vv_excludes_cloud_layers() -> None:
    tac = "METAR KJFK 211025Z 18005KT 0800 VV003 FEW010 15/07 Q1013="
    report = lint(tac, product="METAR")
    assert "VV_EXCLUDES_CLOUD_LAYERS" in _codes(report)
