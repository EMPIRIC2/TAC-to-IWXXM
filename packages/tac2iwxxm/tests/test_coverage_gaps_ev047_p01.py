"""Per-file coverage gaps for EV-047 (≥95% Cover on every measured file)."""

from __future__ import annotations

import pytest
from tac2iwxxm.codelists import (
    aviation_colour_href,
)
from tac2iwxxm.profiles import annex3_emit as ap


def test_annex3_helper_coverage() -> None:
    assert ap._fmt_taf_speed(5.5) == "5.5"
    assert ap._fmt_taf_speed(5.0) == "5"

    # TAF visibility ABOVE path.
    xml = ap.emit_taf_annex3(
        {
            "station": "KJFK",
            "issue_day": 23,
            "issue_hour": 17,
            "issue_minute": 30,
            "valid_from_day": 23,
            "valid_from_hour": 18,
            "valid_to_day": 24,
            "valid_to_hour": 18,
            "nil": False,
            "visibility_m": 10000,
            "visibility_above": True,
            "wind_speed_kt": 10,
            "wind_dir_deg": 180,
        },
        iwxxm_version="2025-2",
    )
    assert "prevailingVisibilityOperator" in xml

    assert (
        ap._is_wmo_sigmet_multi_location_va_yudd(
            {"product": "SIGMET", "phenomenon": "VA", "fir": "YUDD", "mwo": "YUSO", "locations": "bad"}
        )
        is False
    )
    assert (
        ap._is_wmo_sigmet_va_eggx(
            {
                "product": "SIGMET",
                "phenomenon": "VA",
                "fir": "EGGX",
                "mwo": "EGRR",
                "sequence": 4,
                "valid_to_hour": 21,
                "valid_to_minute": 0,
            }
        )
        is False
    )
    assert (
        ap._is_wmo_sigmet_va_eggx(
            {
                "product": "SIGMET",
                "phenomenon": "VA",
                "fir": "EGGX",
                "mwo": "EGRR",
                "sequence": 4,
                "valid_to_hour": 22,
                "valid_to_minute": 0,
                "volcano": "not-a-dict",
            }
        )
        is False
    )
    assert (
        ap._is_wmo_sigmet_va_eggx(
            {
                "product": "SIGMET",
                "phenomenon": "VA",
                "fir": "EGGX",
                "mwo": "EGRR",
                "sequence": 4,
                "valid_to_hour": 22,
                "valid_to_minute": 0,
                "volcano": {"name": "MT HEKLA"},
                "locations": [],
            }
        )
        is False
    )
    assert (
        ap._is_wmo_sigmet_va_eggx(
            {
                "product": "SIGMET",
                "phenomenon": "VA",
                "fir": "EGGX",
                "mwo": "EGRR",
                "sequence": 4,
                "valid_to_hour": 22,
                "valid_to_minute": 0,
                "volcano": {"name": "MT HEKLA"},
                "locations": ["bad"],
            }
        )
        is False
    )

    assert ap._wmo_multi_location_va_pos_list("1 2 3") == "1 2 3"
    assert ap._wmo_multi_location_va_pos_list("1.0 2.0 3.0 4.0") == "1.0 2.0 3.0 4.0"
    # Odd-length tokens after split → early return; short open ring after unclose.
    assert ap._wmo_multi_location_va_pos_list("1 2 3 4 5 6 1 2")  # closed triangle-ish

    # Geometry: top_fl fills upper_fl; BLW qualifier branch.
    geom_xml = ap._sigmet_geometry_xml(
        {
            "top_fl": 350,
            "top_qualifier": "BLW",
            "geometry": {"kind": "polygon", "pos_list": "0 0 1 0 1 1 0 0"},
        },
        fir="YUDD",
    )
    assert "minimumLimit" in geom_xml or "upperLimit" in geom_xml

    assert ap._sigmet_volcano_xml({}) == ""
    assert ap._sigmet_volcano_xml({"volcano": {"name": ""}}) == ""
    assert ap._sigmet_tropical_cyclone_xml({}) == ""
    assert ap._sigmet_tc_position_xml({}, gid="x") == ""
    assert ap._sigmet_tc_forecast_xml({}, fir="YUDD", end="2012-08-10T16:00:00Z") == ""
    # Forecast time clamped when after end.
    fcst_xml = ap._sigmet_tc_forecast_xml(
        {
            "tropical_cyclone_forecast": {"lat": 10.0, "lon": -20.0, "hhmm": "1800"},
            "valid_to_day": 10,
            "valid_to_hour": 16,
            "valid_to_minute": 0,
        },
        fir="YUDD",
        end="2012-08-10T16:00:00Z",
    )
    assert "2012-08-10T16:00:00Z" in fcst_xml

    with pytest.raises(ValueError, match="expected product VAA"):
        ap.emit_vaa_annex3({"product": "TCA", "vaac": "X", "volcano": "Y", "issue_time": "t"}, iwxxm_version="2025-2")
    with pytest.raises(ValueError, match="forbidden iwxxm_root"):
        ap.emit_vaa_annex3(
            {
                "product": "VAA",
                "iwxxm_root": "VolcanicAshSIGMET",
                "vaac": "X",
                "volcano": "Y",
                "issue_time": "t",
            },
            iwxxm_version="2025-2",
        )
    with pytest.raises(ValueError, match="unexpected iwxxm_root"):
        ap.emit_vaa_annex3(
            {
                "product": "VAA",
                "iwxxm_root": "METAR",
                "vaac": "X",
                "volcano": "Y",
                "issue_time": "t",
            },
            iwxxm_version="2025-2",
        )
    with pytest.raises(ValueError, match="missing TropicalCycloneAdvisory"):
        ap._assert_tca_advisory_xml("<root/>")
    with pytest.raises(ValueError, match="TropicalCycloneSIGMET"):
        ap._assert_tca_advisory_xml(
            '<iwxxm:TropicalCycloneAdvisory xmlns:iwxxm="x"></iwxxm:TropicalCycloneAdvisory>'
            '<iwxxm:TropicalCycloneSIGMET xmlns:iwxxm="x"/>'
        )

    with pytest.raises(ValueError, match="expected product TCA"):
        ap.emit_tca_annex3({"product": "VAA", "tcac": "X", "tc_name": "Y", "issue_time": "t"}, iwxxm_version="2025-2")
    with pytest.raises(ValueError, match="forbidden iwxxm_root"):
        ap.emit_tca_annex3(
            {
                "product": "TCA",
                "iwxxm_root": "TropicalCycloneSIGMET",
                "tcac": "X",
                "tc_name": "Y",
                "issue_time": "t",
            },
            iwxxm_version="2025-2",
        )
    with pytest.raises(ValueError, match="unexpected iwxxm_root"):
        ap.emit_tca_annex3(
            {
                "product": "TCA",
                "iwxxm_root": "METAR",
                "tcac": "X",
                "tc_name": "Y",
                "issue_time": "t",
            },
            iwxxm_version="2025-2",
        )

    # Sparse TCA IR → fallback observation path.
    tca_xml = ap.emit_tca_annex3(
        {
            "product": "TCA",
            "tcac": "MIAMI",
            "tc_name": "FRANCES",
            "issue_time": "2004-09-25T18:00:00Z",
            "lat": 27.0,
            "lon": -73.0,
            "central_pressure_hpa": 960,
            "max_wind_mps": 50,
            "advisory_number": "2004/13",
        },
        iwxxm_version="2025-2",
    )
    assert "TropicalCycloneAdvisory" in tca_xml
    assert "centralPressure" in tca_xml

    # SWXA analysis helpers + emitter guards / remarks / next.
    assert "nothingOfOperationalSignificance" in ap._swxa_analysis_xml(
        {"time": "2016-11-08T01:00:00Z", "no_swx_exp": True},
        time_indicator="FORECAST",
        slug="x",
        idx=1,
    )
    assert "nil/missing" in ap._swxa_analysis_xml(
        {"time": "2016-11-08T01:00:00Z", "groups": []},
        time_indicator="OBSERVATION",
        slug="x",
        idx=0,
    )
    # Group with intensity but empty locations → missing iar.
    assert "nil/missing" in ap._swxa_analysis_xml(
        {"time": "t", "groups": [{"intensity": "SEV", "locations": []}]},
        time_indicator="OBSERVATION",
        slug="x",
        idx=0,
    )
    assert "SpaceWeatherIntensityAndRegion" in ap._swxa_analysis_xml(
        {"time": "t", "groups": [{"intensity": "MOD", "locations": ["HNH"]}]},
        time_indicator="OBSERVATION",
        slug="x",
        idx=0,
    )

    with pytest.raises(ValueError, match="expected product SWXA"):
        ap.emit_swxa_annex3({"product": "VAA", "swxc": "X", "issue_time": "t"}, iwxxm_version="2025-2")
    with pytest.raises(ValueError, match="forbidden iwxxm_root"):
        ap.emit_swxa_annex3(
            {
                "product": "SWXA",
                "iwxxm_root": "SIGMET",
                "swxc": "X",
                "issue_time": "t",
            },
            iwxxm_version="2025-2",
        )
    with pytest.raises(ValueError, match="unexpected iwxxm_root"):
        ap.emit_swxa_annex3(
            {
                "product": "SWXA",
                "iwxxm_root": "METAR",
                "swxc": "X",
                "issue_time": "t",
            },
            iwxxm_version="2025-2",
        )

    swxa_xml = ap.emit_swxa_annex3(
        {
            "product": "SWXA",
            "swxc": "DONLON",
            "issue_time": "2016-11-08T01:00:00Z",
            "effect": "HF_COM_MOD",
            "advisory_number": "2016/2",
            "remarks_nil": True,
            "next_advisory_nil": True,
            "observation": {
                "time": "2016-11-08T01:00:00Z",
                "groups": [{"intensity": "MOD", "locations": ["HNH"]}],
            },
        },
        iwxxm_version="2025-2",
    )
    assert "SpaceWeatherAdvisory" in swxa_xml
    assert "nilReason" in swxa_xml

    swxa_next = ap.emit_swxa_annex3(
        {
            "product": "SWXA",
            "swxc": "DONLON",
            "issue_time": "2016-11-08T01:00:00Z",
            "remarks": "see text",
            "next_advisory_time": "2016-11-08T07:00:00Z",
        },
        iwxxm_version="2025-2",
    )
    assert "remarks" in swxa_next
    assert "nextAdvisoryTime" in swxa_next

    with pytest.raises(ValueError, match="missing SpaceWeatherAdvisory"):
        ap._assert_swxa_advisory_xml("<root/>")
    with pytest.raises(ValueError, match="must not appear"):
        ap._assert_swxa_advisory_xml(
            '<iwxxm:SpaceWeatherAdvisory xmlns:iwxxm="x"></iwxxm:SpaceWeatherAdvisory>'
            '<iwxxm:VolcanicAshAdvisory xmlns:iwxxm="x"/>'
        )

    assert ap._vona_ash_movement_token(None) is None
    assert ap._vona_ash_movement_token("  ") is None
    assert ap._vona_ash_movement_token("NE") == "NE"

    with pytest.raises(ValueError, match="missing VolcanoObservatoryNoticeForAviation"):
        ap._assert_vona_xml("<root/>")
    with pytest.raises(ValueError, match="must not appear"):
        ap._assert_vona_xml(
            '<iwxxm:VolcanoObservatoryNoticeForAviation xmlns:iwxxm="x"></iwxxm:VolcanoObservatoryNoticeForAviation>'
            '<iwxxm:VolcanicAshAdvisory xmlns:iwxxm="x"/>'
        )
    with pytest.raises(ValueError, match="AviationColourCode"):
        ap._assert_vona_xml(
            '<iwxxm:VolcanoObservatoryNoticeForAviation xmlns:iwxxm="x">'
            "49-2/AviationColourCode"
            "</iwxxm:VolcanoObservatoryNoticeForAviation>"
        )


def test_aviation_colour_href_smoke() -> None:
    href = aviation_colour_href("RED", iwxxm_version="2025-2")
    assert "RED" in href
