"""Per-file coverage gaps for EV-047 (≥95% Cover on every measured file)."""

from __future__ import annotations

import types
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from tac2iwxxm.bulletin import (
    AhlParts,
    BulletinSplitError,
    format_ahl,
    iwxxm_filename,
    map_t1t2,
    parse_ahl,
    split_bulletin,
)
from tac2iwxxm.codelists import (
    aviation_colour_href,
    load_aviation_colour_members,
    load_nil_members,
)
from tac2iwxxm.glossary import (
    resolve_location_name,
    set_location_name_resolver,
)
from tac2iwxxm.products.fir_geometry import (
    RelativeConstraint,
    RelativeGeometryPhrase,
    _clip_ring_one,
    _intersect,
    clip_ring_to_relative,
    resolve_fir_relative_polygon,
)
from tac2iwxxm.products.sigmet_airmet import parse_airmet, parse_sigmet
from tac2iwxxm.products.swxa import parse_swxa
from tac2iwxxm.products.taf import parse_taf
from tac2iwxxm.profiles import annex3_products as ap

import tac2iwxxm
from tac2iwxxm import native


def test_native_success_paths_with_fake_rust(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = types.SimpleNamespace(scan_metar_tokens=lambda tac: tac.split())
    monkeypatch.setattr(tac2iwxxm, "_rust", fake, raising=False)
    assert native.rust_available() is True
    assert native.rust_module() is fake
    assert native.scan_metar_tokens("A B") == ["A", "B"]


def test_native_import_error_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    import builtins

    real_import = builtins.__import__

    def _import(name: str, globals=None, locals=None, fromlist=(), level=0):
        mod = real_import(name, globals, locals, fromlist, level)
        if name == "tac2iwxxm" and fromlist and "_rust" in fromlist:
            raise ImportError("forced missing tac2iwxxm._rust")
        return mod

    monkeypatch.setattr(builtins, "__import__", _import)
    assert native.rust_available() is False
    assert native.rust_module() is None


def test_glossary_packaged_overlay_fallbacks(monkeypatch: pytest.MonkeyPatch) -> None:
    set_location_name_resolver(lambda _icao: (_ for _ in ()).throw(RuntimeError("boom")))
    assert resolve_location_name("KJFK") is None
    set_location_name_resolver(None)

    class _Data:
        def is_file(self) -> bool:
            return False

    class _Root:
        def joinpath(self, *parts: str) -> _Data:
            return _Data()

    monkeypatch.setattr(
        "tac2iwxxm.glossary.resources.files",
        lambda _name: _Root(),
    )
    tokens = tac2iwxxm.glossary._packaged_overlay_tokens()
    assert isinstance(tokens, dict)

    def _boom(_name: str) -> Any:
        raise ModuleNotFoundError("no package")

    monkeypatch.setattr("tac2iwxxm.glossary.resources.files", _boom)
    tokens2 = tac2iwxxm.glossary._packaged_overlay_tokens()
    assert isinstance(tokens2, dict)


def test_codelists_error_edges(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(ValueError, match="unknown colour"):
        load_aviation_colour_members("nope")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="unknown nil"):
        load_nil_members("nope")  # type: ignore[arg-type]

    empty = tmp_path / "empty.rdf"
    empty.write_text("<rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'/>", encoding="utf-8")
    from tac2iwxxm import codelists as cl

    with pytest.raises(ValueError, match="no skos:Concept"):
        cl._rdf_concept_members(
            empty,
            register_uri="http://codes.wmo.int/iwxxm/AviationColourCode",
        )

    monkeypatch.setattr(
        "tac2iwxxm.codelists._rule_dir",
        lambda _v: tmp_path / "missing-rule",
    )
    load_aviation_colour_members.cache_clear()
    load_nil_members.cache_clear()
    with pytest.raises(FileNotFoundError, match=r".*"):
        load_aviation_colour_members("iwxxm", iwxxm_version="2025-2")
    with pytest.raises(FileNotFoundError, match=r".*"):
        load_nil_members("common", iwxxm_version="2025-2")


def test_bulletin_validation_edges() -> None:
    with pytest.raises(ValueError, match="unsupported TAC T1T2"):
        map_t1t2("ZZ")
    with pytest.raises(BulletinSplitError, match="Empty AHL"):
        parse_ahl("   ")
    with pytest.raises(BulletinSplitError, match="Cannot parse"):
        parse_ahl("NOT AN AHL")
    with pytest.raises(BulletinSplitError, match="Unsupported TAC T1T2"):
        parse_ahl("ZZUS31 KZNY 121200")

    parts = AhlParts(
        ahl="SAUS31 KZNY 121200",
        tt="S",
        aa="US",
        ii="31",
        cccc="KZNY",
        yygggg="121200",
        iwxxm_tt="LA",
        report_status="NORMAL",
        bbb=None,
    )
    with pytest.raises(BulletinSplitError, match="invalid AHL tt"):
        format_ahl(parts)
    parts = AhlParts(
        ahl="x",
        tt="SA",
        aa="U",
        ii="31",
        cccc="KZNY",
        yygggg="121200",
        iwxxm_tt="LA",
        report_status="NORMAL",
        bbb=None,
    )
    with pytest.raises(BulletinSplitError, match="invalid AHL aa"):
        format_ahl(parts)
    parts = AhlParts(
        ahl="x",
        tt="SA",
        aa="US",
        ii="3",
        cccc="KZNY",
        yygggg="121200",
        iwxxm_tt="LA",
        report_status="NORMAL",
        bbb=None,
    )
    with pytest.raises(BulletinSplitError, match="invalid AHL ii"):
        format_ahl(parts)
    parts = AhlParts(
        ahl="x",
        tt="SA",
        aa="US",
        ii="31",
        cccc="KZN",
        yygggg="121200",
        iwxxm_tt="LA",
        report_status="NORMAL",
        bbb=None,
    )
    with pytest.raises(BulletinSplitError, match="invalid AHL cccc"):
        format_ahl(parts)
    parts = AhlParts(
        ahl="x",
        tt="SA",
        aa="US",
        ii="31",
        cccc="KZNY",
        yygggg="1212",
        iwxxm_tt="LA",
        report_status="NORMAL",
        bbb=None,
    )
    with pytest.raises(BulletinSplitError, match="invalid AHL yygggg"):
        format_ahl(parts)

    good = parse_ahl("SAUS31 KZNY 121200")
    name = iwxxm_filename(
        good,
        issued_at=datetime(2024, 1, 2, 3, 4, 5, tzinfo=UTC),
        gzip=True,
        fractional="000001",
    )
    assert name.endswith(".xml.gz")
    assert "_000001" in name

    with pytest.raises(BulletinSplitError, match="Unsupported product"):
        split_bulletin("SAUS31 KZNY 121200\nMETAR KJFK=", product="NOPE")
    with pytest.raises(BulletinSplitError, match="Cannot parse WMO AHL"):
        split_bulletin("\n\nMETAR KJFK 121151Z NIL=\n", product="METAR")
    with pytest.raises(BulletinSplitError, match="does not match product"):
        split_bulletin("FCUS31 KZNY 121200\nTAF KJFK 121200Z NIL=\n", product="METAR")


def test_taf_nil_without_valid_period() -> None:
    # Header with NIL body and no valid-from/to group (NIL_ONLY fast path).
    ir = parse_taf("TAF KJFK 231730Z NIL=")
    assert ir["nil"] is True
    # Same via _TAF + body NIL (token after issue prevents NIL_ONLY).
    ir2 = parse_taf("TAF KJFK 231730Z PROB30 NIL=")
    assert ir2["nil"] is True


def test_taf_kt_gust_wx_and_empty_change_groups() -> None:
    ir = parse_taf("TAF KJFK 231730Z 2318/2418 18010G20KT 8000 -RA SCT020 FM241800=")
    assert ir.get("wind_gust_kt") == 20
    assert ir.get("weather") == ["-RA"]
    # FM without trailing body whitespace fails _FM.match → no change_forecasts.
    assert "change_forecasts" not in ir

    # BECMG with odd validity still parses without raising.
    ir_b = parse_taf("TAF KJFK 231730Z 2318/2418 18010KT 9999 BECMG 9999/9999 NOSIG=")
    assert ir_b.get("station") == "KJFK"
    # Forecast body with weather-only (no cloud) is accepted.
    ir_wx = parse_taf("TAF KJFK 231730Z 2318/2418 18010KT 8000 TSRA=")
    assert ir_wx.get("weather") == ["TSRA"]
    assert "clouds" not in ir_wx


def test_swxa_parser_edges() -> None:
    from tac2iwxxm.products.swxa import _day_hhmm_to_iso, _fields, _parse_intensity_regions

    with pytest.raises(ValueError, match="expected product SWXA"):
        parse_swxa("SWX ADVISORY", product="VAA")
    with pytest.raises(ValueError, match="missing SWX ADVISORY"):
        parse_swxa("DTG: 20161108/0100Z\nSWXC: DONLON")
    with pytest.raises(ValueError, match="missing/invalid DTG"):
        parse_swxa("SWX ADVISORY\nDTG: BAD\nSWXC: DONLON")
    with pytest.raises(ValueError, match="missing SWXC"):
        parse_swxa("SWX ADVISORY\nDTG: 20161108/0100Z")

    # Blank lines + continuation lines in _fields; location-before-intensity → MOD.
    assert _fields("FOO: one\n\n  continued\n")["FOO"] == "one continued"
    assert _day_hhmm_to_iso("not-a-stamp", issue_iso="2016-11-08T01:00:00Z") is None
    groups = _parse_intensity_regions("HNH EQN")
    assert groups
    assert groups[0]["intensity"] == "MOD"

    tac = """SWX ADVISORY
DTG: 20161108/0100Z
SWXC: DONLON
ADVISORY NR: 2016/2
NR RPLC: 2016/1
SWX EFFECT: HF COM MOD
OBS SWX: 08/0100Z SEV HSN EQN MOD DAYSIDE
FCST SWX +6 HR: 08/0700Z NO SWX EXP
RMK: NIL
NXT ADVISORY: NO FURTHER ADVISORIES
"""
    ir = parse_swxa(tac)
    assert ir["swxc"] == "DONLON"
    assert ir["remarks_nil"] is True
    assert ir["next_advisory_nil"] is True
    assert any(g.get("no_swx_exp") for g in ir.get("forecasts") or [])


def test_fir_geometry_edge_helpers() -> None:
    # Vertical edge (same lat) + horizontal edge (same lon) intersections.
    c_lat = RelativeConstraint(axis="lat", value=50.0, keep="north")
    assert _intersect((50.0, 0.0), (50.0, 10.0), c_lat)[0] == 50.0
    c_lon = RelativeConstraint(axis="lon", value=10.0, keep="east")
    assert _intersect((0.0, 10.0), (5.0, 10.0), c_lon)[1] == 10.0

    assert _clip_ring_one([], c_lat) == []
    open_ring = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
    clipped = _clip_ring_one(open_ring, RelativeConstraint(axis="lat", value=5.0, keep="north"))
    assert clipped

    assert clip_ring_to_relative([], RelativeGeometryPhrase(kind="entire_fir", constraints=())) == []
    assert resolve_fir_relative_polygon("WI N1000 E01000 N1100 E01100=", fir_boundary=[(0, 0), (1, 0)]) is None
    box = [(0.0, 0.0), (0.0, 20.0), (20.0, 20.0), (20.0, 0.0), (0.0, 0.0)]
    assert resolve_fir_relative_polygon("S OF N10 ENTIRE FIR", fir_boundary=None) is None
    got = resolve_fir_relative_polygon("ENTIRE FIR", fir_boundary=box)
    assert got is not None
    assert got["kind"] == "polygon"


def test_sigmet_airmet_geometry_edges() -> None:
    # WI polygon + TOP BLW + SFC/FL + MOV (non-VA path).
    tac = (
        "YUDD SIGMET 1 VALID 101200/101600 YUSO- YUDD SHANLON FIR "
        "OBSC TS WI N1000 E01000 - N1100 E01100 - N1000 E01200 - N1000 E01000 "
        "TOP BLW FL350 MOV E 20KT="
    )
    ir = parse_sigmet(tac)
    assert ir.get("geometry", {}).get("kind") == "polygon"
    assert ir.get("top_qualifier") == "BLW"

    sfc = (
        "YUDD SIGMET 1 VALID 101200/101600 YUSO- YUDD FIR "
        "OBSC TS WI N1000 E01000 - N1100 E01100 - N1000 E01200 - N1000 E01000 "
        "SFC/FL100 MOV N 10KT="
    )
    ir2 = parse_sigmet(sfc)
    assert ir2.get("lower_surface") == "SFC"

    # SE box + N OF S geometries (match _SE_BOX / _N_OF_S patterns).
    se = "YUDD SIGMET 1 VALID 101200/101600 YUSO- YUDD FIR TS S OF N20 AND E OF W050="
    assert parse_sigmet(se).get("geometry", {}).get("kind") == "polygon"
    n_of = "YUDD AIRMET 1 VALID 101200/101600 YUSO- YUDD FIR ISOL TS N OF S20="
    assert parse_airmet(n_of).get("geometry", {}).get("kind") == "polygon"


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
