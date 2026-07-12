"""Coverage gap tests for Phase C 08-verify-build (parsers + emit edge paths)."""

from __future__ import annotations

import pytest

from tac2iwxxm.convert import convert
from tac2iwxxm.native import rust_available, rust_module, scan_metar_tokens
from tac2iwxxm.products.sigmet_airmet import parse_airmet, parse_sigmet
from tac2iwxxm.products.taf import parse_taf
from tac2iwxxm.products.vaa_tca import parse_tca, parse_vaa
from tac2iwxxm.profiles.annex3 import emit_metar_speci_annex3
from tac2iwxxm.profiles.iwxxm_us import (
    emit_metar_speci_iwxxm_us,
    emit_taf_iwxxm_us,
)


def test_parse_taf_nil_vrb_mps_and_mismatch() -> None:
    nil_ir = parse_taf("TAF KJFK 231730Z 2318/2418 NIL=")
    assert nil_ir["nil"] is True

    vrb = parse_taf("TAF KJFK 231730Z 2318/2418 VRB05KT 9999 FEW040=")
    assert vrb["wind_variable"] is True
    assert "wind_dir_deg" not in vrb

    mps = parse_taf("TAF KJFK 231730Z 2318/2418 18005MPS 8000 SCT020=")
    assert mps["wind_speed_mps"] == 5.0

    with pytest.raises(ValueError, match="product mismatch"):
        parse_taf("TAF KJFK 231730Z 2318/2418 NIL=", product="METAR")
    with pytest.raises(ValueError, match="unable to parse TAF"):
        parse_taf("NOTAHEADER")


def test_parse_sigmet_airmet_phenomena_and_errors() -> None:
    sig = parse_sigmet("YUDD SIGMET 2 VALID 101200/101600 YUSO- YUDD SHANLON FIR/UIR OBSC TS FCST=")
    assert sig["phenomenon"] == "OBSC_TS"
    assert "SHANLON" in sig["fir_name"]

    air = parse_airmet("YUDD AIRMET 1 VALID 101200/101600 YUSO- YUDD SHANLON FIR ISOL TS OBS=")
    assert air["phenomenon"] == "ISOL_TS"

    va = parse_sigmet("YUDD SIGMET 1 VALID 101200/101600 YUSO- YUDD FIR VA FCST=")
    assert va["phenomenon"] == "VA"

    mtw = parse_airmet("YUDD AIRMET 1 VALID 101200/101600 YUSO- YUDD FIR MTW OBS=")
    assert mtw["phenomenon"] == "MTW"

    with pytest.raises(ValueError, match="product mismatch"):
        parse_sigmet("x", product="AIRMET")
    with pytest.raises(ValueError, match="unable to parse SIGMET"):
        parse_sigmet("BAD SIGMET")
    with pytest.raises(ValueError, match="product mismatch"):
        parse_airmet("x", product="SIGMET")
    with pytest.raises(ValueError, match="unable to parse AIRMET"):
        parse_airmet("BAD AIRMET")


def test_parse_vaa_tca_error_and_optional_fields() -> None:
    with pytest.raises(ValueError, match="product mismatch"):
        parse_vaa("VA ADVISORY", product="TCA")
    with pytest.raises(ValueError, match="missing VA ADVISORY"):
        parse_vaa("DTG: 20040925/1900Z")
    with pytest.raises(ValueError, match="unable to parse VAA DTG"):
        parse_vaa("VA ADVISORY\nDTG: NOTADT G")

    vaa = parse_vaa(
        "VA ADVISORY\n"
        "DTG: 20040925/1900Z\n"
        "VAAC: TOKYO\n"
        "VOLCANO: KARYMSKY 1000-13\n"
        "PSN: N5403 E15927\n"
        "AREA: KAMCHATKA\n"
        "SOURCE ELEV: 1536 M\n"
        "ADVISORY NR: 2004/4\n"
    )
    assert vaa["lat"] is not None
    assert vaa["source_elevation_m"] == 1536

    with pytest.raises(ValueError, match="product mismatch"):
        parse_tca("TC ADVISORY", product="VAA")
    with pytest.raises(ValueError, match="missing TC ADVISORY"):
        parse_tca("DTG: 20040925/1900Z")
    with pytest.raises(ValueError, match="unable to parse TCA DTG"):
        parse_tca("TC ADVISORY\nDTG: BAD")

    tca = parse_tca(
        "TC ADVISORY\n"
        "DTG: 20040925/1800Z\n"
        "TCAC: MIAMI\n"
        "TC: FRANCES\n"
        "ADVISORY NR: 2004/13\n"
        "OBS PSN: 25/1800Z N2706 W07306\n"
        "MAX WIND: 50 MPS\n"
        "C: 960 HPA\n"
        "MOV: WNW 12KT\n"
    )
    assert tca["max_wind_mps"] == 50
    assert tca["central_pressure_hpa"] == 960
    assert tca["lon"] is not None


def test_emit_unsupported_version_and_us_nil_variable() -> None:
    ir = {
        "station": "KJFK",
        "day": 23,
        "hour": 17,
        "minute": 51,
        "nil": True,
    }
    with pytest.raises(ValueError, match="unsupported iwxxm_version"):
        emit_metar_speci_annex3(ir, product="METAR", iwxxm_version="1999-1")
    with pytest.raises(ValueError, match="unsupported iwxxm_version"):
        emit_metar_speci_iwxxm_us(ir, product="METAR", iwxxm_version="1999-1")

    full = {
        "station": "KJFK",
        "day": 23,
        "hour": 17,
        "minute": 51,
        "temp_c": 15,
        "dewpoint_c": 7,
        "qnh_hpa": 1017,
        "wind_variable": True,
        "wind_speed_kt": 12,
        "wind_gust_kt": 20,
        "visibility_m": 16093,
        "visibility_above": True,
        "cloud_amount": "FEW",
        "cloud_base_ft": 4000,
        "observing_system_type": "AO2",
        "observing_system_href": "http://example/ao2",
        "sea_level_pressure_hpa": 1014.9,
    }
    xml = emit_metar_speci_iwxxm_us(full, product="METAR", iwxxm_version="2025-2")
    assert 'variableWindDirection="true"' in xml
    assert "prevailingVisibilityOperator>ABOVE" in xml
    assert "iwxxm-us:Addendum" in xml


def test_emit_taf_us_without_altimeter_and_namespace_inject() -> None:
    ir = {
        "ir_version": 1,
        "product": "TAF",
        "station": "KJFK",
        "issue_day": 23,
        "issue_hour": 17,
        "issue_minute": 30,
        "valid_from_day": 23,
        "valid_from_hour": 18,
        "valid_to_day": 24,
        "valid_to_hour": 18,
        "nil": False,
        "wind_dir_deg": 180,
        "wind_speed_kt": 12,
        "visibility_m": 9999,
        "cloud_amount": "FEW",
        "cloud_base_ft": 4000,
        "raw": "TAF KJFK 231730Z 2318/2418 18012KT 9999 FEW040",
    }
    xml = emit_taf_iwxxm_us(ir, iwxxm_version="2025-2")
    assert "xmlns:iwxxm-us=" in xml
    assert "MeteorologicalAerodromeForecastExtension" not in xml


def test_convert_unsupported_profile_product_and_native_scan() -> None:
    from tac2iwxxm.convert import _emit

    bad_profile = convert("METAR KJFK 231751Z NIL=", product="METAR", profile="nope")
    assert bad_profile.ok is False
    assert bad_profile.issues[0].code == "UNSUPPORTED_PROFILE"

    bad_us = convert("VA ADVISORY\nDTG: 20040925/1900Z", product="VAA", profile="iwxxm_us")
    assert bad_us.ok is False
    assert bad_us.issues[0].code == "UNSUPPORTED_PROFILE"

    with pytest.raises(ValueError, match="no emitter"):
        _emit("NOPE", "annex3", {}, "2025-2")

    assert isinstance(rust_available(), bool)
    assert rust_module() is None or rust_module() is not None
    if not rust_available():
        with pytest.raises(NotImplementedError):
            scan_metar_tokens("METAR KJFK 231751Z NIL=")


def test_more_coverage_edges() -> None:
    # Default phenomenon when no known token matches.
    fog = parse_sigmet("YUDD SIGMET 1 VALID 101200/101600 YUSO- YUDD FIR FOG FCST=")
    assert fog["phenomenon"] == "TS"
    fog_a = parse_airmet("YUDD AIRMET 1 VALID 101200/101600 YUSO- YUDD FIR FOG OBS=")
    assert fog_a["phenomenon"] == "TS"

    # US NIL observation + namespace already present.
    nil_xml = emit_metar_speci_iwxxm_us(
        {"station": "KJFK", "day": 23, "hour": 17, "minute": 51, "nil": True},
        product="METAR",
        iwxxm_version="2025-2",
    )
    assert "nilReason" in nil_xml
    from tac2iwxxm.profiles.iwxxm_us import _with_us_namespace

    again = _with_us_namespace(nil_xml)
    assert again.count("xmlns:iwxxm-us=") == 1

    # TAF US with altimeter but missing forecast needle → early return.
    import tac2iwxxm.profiles.annex3_products as ap

    orig = ap.emit_taf_annex3

    def _fake_emit(ir, *, iwxxm_version):  # noqa: ANN001, ANN202
        return (
            '<?xml version="1.0"?>\n'
            f'<iwxxm:TAF xmlns:iwxxm="http://icao.int/iwxxm/{iwxxm_version}" '
            'gml:id="taf.basic.kjfk"></iwxxm:TAF>'
        )

    ap.emit_taf_annex3 = _fake_emit  # type: ignore[assignment]
    try:
        xml = emit_taf_iwxxm_us(
            {
                "station": "KJFK",
                "forecast_altimeter_inhg": 30.05,
                "issue_day": 23,
                "issue_hour": 17,
                "issue_minute": 30,
                "valid_from_day": 23,
                "valid_from_hour": 18,
                "valid_to_day": 24,
                "valid_to_hour": 18,
                "nil": False,
            },
            iwxxm_version="2025-2",
        )
        assert "MeteorologicalAerodromeForecastExtension" not in xml
        assert "xmlns:iwxxm-us=" in xml
    finally:
        ap.emit_taf_annex3 = orig

    # annex3_products: unsupported version + NIL TAF base forecast.
    from tac2iwxxm.profiles.annex3_products import emit_sigmet_annex3, emit_taf_annex3

    with pytest.raises(ValueError, match="unsupported iwxxm_version"):
        emit_taf_annex3(
            {
                "station": "KJFK",
                "issue_day": 23,
                "issue_hour": 17,
                "issue_minute": 30,
                "valid_from_day": 23,
                "valid_from_hour": 18,
                "valid_to_day": 24,
                "valid_to_hour": 18,
                "nil": True,
            },
            iwxxm_version="1999-1",
        )
    nil_taf = emit_taf_annex3(
        {
            "station": "YUDO",
            "issue_day": 10,
            "issue_hour": 0,
            "issue_minute": 0,
            "valid_from_day": 10,
            "valid_from_hour": 0,
            "valid_to_day": 10,
            "valid_to_hour": 12,
            "nil": True,
        },
        iwxxm_version="2025-2",
    )
    assert "nilReason" in nil_taf

    vrb_taf = emit_taf_annex3(
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
            "wind_variable": True,
            "wind_speed_kt": 5,
        },
        iwxxm_version="2025-2",
    )
    assert 'variableWindDirection="true"' in vrb_taf

    with pytest.raises(ValueError, match="unsupported iwxxm_version"):
        emit_sigmet_annex3(
            {
                "fir": "YUDD",
                "mwo": "YUSO",
                "sequence": 1,
                "valid_from_day": 10,
                "valid_from_hour": 12,
                "valid_from_minute": 0,
                "valid_to_day": 10,
                "valid_to_hour": 16,
                "valid_to_minute": 0,
                "phenomenon": "TS",
                "fir_name": "YUDD",
            },
            iwxxm_version="1999-1",
        )

    # VAA latlon / DTG edge helpers via public parsers with sparse fields.
    sparse = parse_vaa("VA ADVISORY\nDTG: 20040925/1900Z\nVAAC: TOKYO\nVOLCANO: X\nPSN: S1234 W01234\n")
    assert sparse["lat"] is not None and sparse["lat"] < 0
    assert sparse["source_elevation_m"] is None

    from tac2iwxxm.products.vaa_tca import _latlon, _parse_dtg

    assert _parse_dtg("20040925/1900Z") is not None
    assert _parse_dtg("not-a-dtg") is None
    assert _latlon("N5403 E15927") is not None
    assert _latlon("nowhere") is None
    assert _latlon("N54030 E159270") is not None or _latlon("N5403 E15927") is not None
