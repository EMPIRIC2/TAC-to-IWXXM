"""Fill remaining WMO-782 helper / shim coverage branches."""

from __future__ import annotations

from tac_validate.models import Issue
from tac_validate.product_rules_pkg import wmo782_extended
from tac_validate.product_rules_pkg.wmo782._emit import (
    dedupe,
    parse_temp_c,
    rvr_value_on_scale,
    split_obs_trend,
)
from tac_validate.product_rules_pkg.wmo782.quality_core import (
    _check_wmo782_first_groups_and_modifiers,
    _check_wmo782_visibility_quality,
    _vis_meters_on_reporting_scale,
)
from tac_validate.product_rules_pkg.wmo782.weather import check_weather
from tac_validate.product_rules_pkg.wmo782.wind_shear import check_wind_shear


def test_wmo782_extended_shim_exports_checker() -> None:
    assert callable(wmo782_extended.check_wmo782_extended)
    assert "check_wmo782_extended" in wmo782_extended.__all__


def test_emit_helpers_scale_temp_trend_and_dedupe() -> None:
    assert rvr_value_on_scale("/////") is True
    assert rvr_value_on_scale("ABCD") is False
    assert rvr_value_on_scale("P1500") is False
    assert rvr_value_on_scale("P2000") is True
    assert rvr_value_on_scale("0375") is True
    assert rvr_value_on_scale("0376") is False
    assert rvr_value_on_scale("0450") is True
    assert rvr_value_on_scale("1600") is True
    assert rvr_value_on_scale("2100") is False

    assert parse_temp_c("M05") == -5
    assert parse_temp_c("//") is None

    obs, trend = split_obs_trend(["18005KT", "9999", "BECMG", "2000"])
    assert obs == ["18005KT", "9999"]
    assert trend[0] == "BECMG"
    assert split_obs_trend(["18005KT", "9999"])[1] == []

    issue = Issue(
        severity="error",
        code="X",
        message="dup",
        start=0,
        end=1,
        location="x",
    )
    assert len(dedupe([issue, issue])) == 1


def test_visibility_scale_helper_and_empty_identity() -> None:
    assert _vis_meters_on_reporting_scale(9999) is True
    assert _vis_meters_on_reporting_scale(10000) is False
    assert _vis_meters_on_reporting_scale(850) is False
    assert _vis_meters_on_reporting_scale(5000) is True
    assert _vis_meters_on_reporting_scale(5500) is False

    assert (
        _check_wmo782_first_groups_and_modifiers(
            [],
            product="METAR",
            core="",
            body_start=0,
            body_end=0,
        )
        == []
    )
    issues = _check_wmo782_first_groups_and_modifiers(
        ["METAR"],
        product="METAR",
        core="METAR",
        body_start=0,
        body_end=5,
    )
    assert any(i.code == "FIRST_GROUPS_FORMAT" for i in issues)


def test_directional_visibility_off_scale_and_cavok_low_vis() -> None:
    issues = _check_wmo782_visibility_quality(
        ["1234SW"],
        product="METAR",
        core="1234SW",
        body_start=0,
        body_end=6,
        is_auto=False,
    )
    assert any(i.code == "DIRECTIONAL_VISIBILITY_FORMAT" for i in issues)

    from tac_validate.product_rules_pkg.wmo782.quality_core import (
        _check_wmo782_metar_speci_quality,
    )

    cavok_issues = _check_wmo782_metar_speci_quality(
        ["METAR", "KJFK", "211025Z", "18005KT", "CAVOK", "4000", "15/07", "Q1013"],
        product="METAR",
        core="METAR KJFK 211025Z 18005KT CAVOK 4000 15/07 Q1013",
        body_start=0,
        body_end=52,
    )
    assert any(i.code == "CAVOK_CONDITIONS_NOT_MET" for i in cavok_issues)


def test_weather_dr_bl_pairing_branch() -> None:
    # DR/BL must pair with DU/SA/SN; DRDZ is significant weather but invalid pairing.
    issues = check_weather(
        ["DRDZ"],
        product="METAR",
        core="DRDZ",
        body_start=0,
        body_end=4,
        is_auto=False,
    )
    assert any(i.code == "WEATHER_DESCRIPTOR_PAIRING" for i in issues)


def test_wind_calm_gust_p_indicator_and_variation_branches() -> None:
    calm = check_wind_shear(
        ["00000KT", "180V270"],
        product="METAR",
        core="00000KT 180V270",
        body_start=0,
        body_end=16,
    )
    assert any(i.code == "WIND_CALM_MISENCODE" for i in calm)

    high = check_wind_shear(
        ["270100KT"],
        product="METAR",
        core="270100KT",
        body_start=0,
        body_end=8,
    )
    assert any(i.code == "WIND_HIGH_SPEED_P_INDICATOR" for i in high)

    # Mean < 3 kt and span outside 60..180.
    low_mean_narrow = check_wind_shear(
        ["18002KT", "010V050"],
        product="METAR",
        core="18002KT 010V050",
        body_start=0,
        body_end=16,
    )
    assert any(i.code == "WIND_VARIATION_SPAN" for i in low_mean_narrow)

    # Mean >= 3 kt with valid span (no variation issue) plus WS format / exclusivity.
    ok_var = check_wind_shear(
        ["18005KT", "090V180"],
        product="METAR",
        core="18005KT 090V180",
        body_start=0,
        body_end=16,
    )
    assert not any(i.code == "WIND_VARIATION_SPAN" for i in ok_var)

    bad_ws = check_wind_shear(
        ["18005KT", "WS", "XX"],
        product="METAR",
        core="18005KT WS XX",
        body_start=0,
        body_end=13,
    )
    assert any(i.code == "WIND_SHEAR_FORMAT" for i in bad_ws)

    exclusive = check_wind_shear(
        ["18005KT", "WS", "ALL", "RWY", "WS", "R24"],
        product="METAR",
        core="18005KT WS ALL RWY WS R24",
        body_start=0,
        body_end=26,
    )
    assert any(i.code == "WS_ALL_RWY_EXCLUSIVE" for i in exclusive)
