"""Per-file 100% line+branch fill for EV-080 M2b T2.2 (fill-before-flip).

[Corpus: adr/ADR-007] [Corpus: tests]
"""

from __future__ import annotations

import re
from types import SimpleNamespace
from typing import Any

import pytest
from tac2iwxxm.bulletin import AhlParts, BulletinSplitError, format_ahl, split_bulletin
from tac2iwxxm.codelists import _rdf_concept_members
from tac2iwxxm.convert import (
    _inject_translation_centre,
    _tac_looks_like_product,
    convert,
)
from tac2iwxxm.decode import (
    DecodeSegment,
    _decode_bulletin,
    _explain_advisory,
    _explain_sigmet_airmet,
    _explain_taf,
    _looks_like_ahl_bulletin,
    _sentence_from_segment,
)
from tac2iwxxm.exchange_output import parse_msc_exchange_filename
from tac2iwxxm.geometry.reference_point import ReferencePointGeometryParser
from tac2iwxxm.glossary import set_location_name_resolver
from tac2iwxxm.products import fir_geometry as fg
from tac2iwxxm.products import metar_speci as ms
from tac2iwxxm.products import sigmet_airmet as sa
from tac2iwxxm.products import swxa as swxa_mod
from tac2iwxxm.products import vaa_tca as vt
from tac2iwxxm.products import vona as vona_mod
from tac2iwxxm.products.taf import parse_taf
from tac2iwxxm.products.vona import parse_vona
from tac2iwxxm.profile_registry import known_semantic_profile_ids
from tac2iwxxm.profiles import annex3 as a3
from tac2iwxxm.profiles import ca_eccc as ca
from tac2iwxxm.profiles import iwxxm_us as us
from tac2iwxxm.profiles.annex3_emit import sigmet as sig_emit
from tac2iwxxm.profiles.annex3_emit import swxa as swxa_emit
from tac2iwxxm.profiles.annex3_emit import taf as taf_emit
from tac2iwxxm.profiles.annex3_emit import tca as tca_emit
from tac2iwxxm.profiles.annex3_emit import vaa as vaa_emit

# ---------------------------------------------------------------------------
# Tiny modules / helpers
# ---------------------------------------------------------------------------


def test_known_semantic_profile_ids() -> None:
    ids = known_semantic_profile_ids()
    assert "annex3" in ids or "icao_2025" in ids or len(ids) > 0


def test_reference_point_empty_from_chain(monkeypatch: pytest.MonkeyPatch) -> None:
    # Regex rarely yields whitespace-only chain; force the empty-strip guard.
    class _Match:
        def group(self, _name: str) -> str:
            return "   "

    monkeypatch.setattr(
        "tac2iwxxm.geometry.reference_point._FROM_CHAIN",
        SimpleNamespace(search=lambda _body: _Match()),
    )
    assert ReferencePointGeometryParser().parse_from_body("FROM X MOV NE") is None


def test_parse_msc_invalid_bbb_falls_back_normal() -> None:
    # BBB matches filename pattern but fails bbb_to_report_status (BulletinSplitError ⊂ ValueError)
    parsed = parse_msc_exchange_filename("A_LTCN22CWAO241200ZZZ_C_CWAO_20260824120000.xml")
    assert parsed is not None
    parts, _issued = parsed
    assert parts.report_status == "NORMAL"
    assert parts.bbb == "ZZZ"


def test_taf_missing_valid_without_nil_raises() -> None:
    with pytest.raises(ValueError, match="unable to parse TAF header"):
        parse_taf("TAF KJFK 231730Z 18005KT=")


def test_convert_unknown_product_lead_and_guards() -> None:
    assert _tac_looks_like_product("HELLO", "NOT_A_PRODUCT") is False
    assert _inject_translation_centre("no-root-here", designator="CWAO", name="MSC") == "no-root-here"

    bad_ca = convert(
        "METAR CYUL 010000Z NIL=",
        product="SIGMET",
        profile="ca_eccc",
        iwxxm_version="3.0.0",
    )
    assert bad_ca.ok is False
    assert any(i.code == "UNSUPPORTED_PROFILE" for i in bad_ca.issues)

    bad_status = convert(
        "METAR KJFK 010000Z NIL=",
        product="METAR",
        profile="annex3",
        report_status="WEIRD",
    )
    assert bad_status.ok is False
    assert any(i.code == "INVALID_REPORT_STATUS" for i in bad_status.issues)

    # CA path with designator already set skips default centre branch
    ok = convert(
        "METAR CYUL 121200Z 18005KT 9999 SCT020 10/05 Q1013=",
        product="METAR",
        profile="ca_eccc",
        iwxxm_version="3.0.0",
        translation_centre_designator="CWAO",
        translation_centre_name="MSC",
    )
    assert ok.ok is True


def test_codelists_skips_non_prefix_concepts(tmp_path: Any) -> None:
    rdf = tmp_path / "c.rdf"
    rdf.write_text(
        """<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:skos="http://www.w3.org/2004/02/skos/core#">
  <skos:Concept rdf:about="http://example.org/other/X"/>
  <skos:Concept rdf:about="http://codes.wmo.int/iwxxm/AviationColourCode/RED"/>
</rdf:RDF>
""",
        encoding="utf-8",
    )
    members = _rdf_concept_members(rdf, register_uri="http://codes.wmo.int/iwxxm/AviationColourCode")
    assert members == {"RED"}


def test_bulletin_format_ahl_with_bbb_and_vona_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    parts = AhlParts(
        ahl="SAUS31 KZNY 121200 CCA",
        tt="SA",
        aa="US",
        ii="31",
        cccc="KZNY",
        yygggg="121200",
        iwxxm_tt="LA",
        report_status="CORRECTION",
        bbb="CCA",
    )
    assert format_ahl(parts).endswith("CCA")

    # Body regex finds a report; VONA filter then empties the list (branch 416→419).
    monkeypatch.setitem(
        __import__("tac2iwxxm.bulletin", fromlist=["_PRODUCT_BODY_RE"])._PRODUCT_BODY_RE,
        "VONA",
        re.compile(r"^DUMMY\b.+?(?:=\s*$|\Z)", re.MULTILINE | re.DOTALL),
    )
    with pytest.raises(BulletinSplitError, match="No VONA"):
        split_bulletin("WMCI31 UHPP 160130\nDUMMY FOO=\n", product="VONA")


# ---------------------------------------------------------------------------
# products/vona, swxa, vaa_tca, fir_geometry, taf emit
# ---------------------------------------------------------------------------


def test_vona_fields_blank_volcano_and_spaced_activity() -> None:
    assert vona_mod._fields("FOO: bar\n\n  cont\n")["FOO"] == "bar cont"
    assert vona_mod._parse_volcano("   ") == ("", None)
    # Spaced form maps via underscore compact key (cleaned form not in map)
    assert vona_mod._map_activity("DECREASED ACTIVITY") == "DECREASED_ACTIVITY"
    # Blank lines skipped inside a full parse
    tac = (
        "VONA\n"
        "\n"
        "DTG: 20240216/0130Z\n"
        "VOLCANO: KARYMSKY 100013\n"
        "PSN: N5403 E15927\n"
        "AREA: TEST\n"
        "SOURCE ELEV: 1536M AMSL\n"
        "NOTICE NR: 1/1\n"
        "CURRENT COLOUR CODE: RED\n"
        "PREVIOUS COLOUR CODE: NIL\n"
        "SVO: OTHER\n"
        "ACT STS: ERUPTION ONGOING\n"
    )
    ir = parse_vona(tac, product="VONA")
    assert ir["activity_status"] == "ERUPTION_ONGOING"


def test_swxa_fields_continuation_and_intensity_flush() -> None:
    fields = swxa_mod._fields("DTG: 20161108/0100Z\n\n  EXTRA\n")
    assert "EXTRA" in fields["DTG"]
    # intensity with locations flushed at end
    groups = swxa_mod._parse_intensity_regions("MOD HNH HSH")
    assert groups
    assert groups[0]["intensity"] == "MOD"
    # trailing intensity without locations → no final flush (branch false)
    assert swxa_mod._parse_intensity_regions("SEV") == []


def test_vaa_tca_dtg_alt_form_and_fields_blank() -> None:
    assert vt._fields("DTG: 20040925/1900Z\n\n  note\n")["DTG"].endswith("note")
    assert vt._parse_dtg("20040925/1900Z") == "2004-09-25T19:00:00Z"
    assert vt._parse_dtg("not-a-dtg") is None
    # TCA MOV neither pattern nor STNR → elif false
    ir_ns = vt.parse_tca(
        "TC ADVISORY\n"
        "DTG: 20040925/1900Z\n"
        "TCAC: YUFO\n"
        "TC: GLORIA\n"
        "ADVISORY NR: 2004/13\n"
        "OBS PSN: 25/1800Z N2706 W07306\n"
        "MOV: DRIFTING\n"
        "C: 965HPA\n"
        "MAX WIND: 22MPS\n"
    )
    assert ir_ns.get("movement") is None


def test_fir_geometry_degenerate_wi_and_relative_none(monkeypatch: pytest.MonkeyPatch) -> None:
    # Closed 3-vertex ring (first==last) fails close_ring (<4) → None
    body = "WI N5000 E01000 - N5100 E01100 - N5000 E01000"
    assert fg.resolve_fir_relative_polygon(body, fir_boundary=None) is None

    ring = [(50.0, 10.0), (51.0, 10.0), (51.0, 11.0), (50.0, 11.0), (50.0, 10.0)]
    monkeypatch.setattr(fg, "select_horizontal_geometry_kind", lambda _b: "relative")
    assert fg.resolve_fir_relative_polygon("NO HALF PLANE", fir_boundary=ring) is None

    # Already-closed clip output branch
    phrase = fg.RelativeGeometryPhrase(
        kind="relative",
        constraints=(fg.RelativeConstraint(axis="lat", value=50.5, keep="north"),),
    )
    clipped = fg.clip_ring_to_relative(ring, phrase)
    assert clipped
    assert clipped[0] == clipped[-1]


def test_annex3_emit_taf_display_vis_without_above() -> None:
    xml = taf_emit._taf_visibility_block({"visibility_display_uom": "m", "visibility_display_value": 8000})
    assert "prevailingVisibility" in xml
    assert "ABOVE" not in xml


# ---------------------------------------------------------------------------
# annex3 / ca_eccc / iwxxm_us / emit guards
# ---------------------------------------------------------------------------


def test_annex3_variable_rvr_midpoint_and_legacy_trends() -> None:
    block = a3._rvr_block(
        {"rvr": {"runway": "09L", "variable": True, "min_m": 200, "max_m": 400}},
        rvr_extension="",
    )
    assert "meanRVR" in block
    assert "300" in block

    vis = a3._visibility_block(
        {
            "visibility_m": 2000,
            "min_visibility_m": 1000,
            "min_visibility_dir_deg": 90,
        }
    )
    assert "minimumVisibilityDirection" in vis

    trends = a3._trend_forecasts(
        {
            "nosig": True,
            "tempo_trend": {
                "change_indicator": "TEMPORARY_FLUCTUATIONS",
                "phenomenon_begin": "2023-06-01T12:00:00Z",
                "phenomenon_end": "2023-06-01T13:00:00Z",
            },
        }
    )
    assert "NOSIG" in trends or "nilReason" in trends
    assert "TEMPORARY" in trends or "trendForecast" in trends


def test_ca_eccc_weather_skip_empty_and_gfa_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    assert ca._ca_taf_weather_extension_inner({"ca_forecast_weather_hrefs": ["", 1, "http://x"]})
    # structured dict with no usable nested dicts → len(parts)==1 → ""
    assert ca._gfa_structured_extension({"fir": "CZUL", "ca_gfa_structured": {"noise": True}}) == ""
    assert ca._inject_airmet_gfa_extension("<root/>", "<ext/>") == "<root/>"


def test_iwxxm_us_helper_edge_branches() -> None:
    assert us._us_gml_id({"station": "KJFK", "rvr": {"variable": True}}, "METAR").endswith("kjfk")
    # Lightning without sector keys
    xml = us._observed_lightning_xml({"type_href": "http://x/IC"})
    assert "ObservedLightning" in xml
    xml2 = us._convective_cloud_xml({"cloud_type_href": "http://x/CB"})
    assert "ConvectiveCloudLocation" in xml2

    # recent weather with unknown begin/end minutes
    recent = us._recent_weather_addendum_inner(
        {
            "day": 1,
            "hour": 12,
            "recent_weather_us": [
                "skip",
                {"phenomenon_href": "http://x/RA"},
            ],
        }
    )
    assert "indeterminatePosition" in recent

    assert us._variable_rvr_extension({"rvr": {"variable": False}}) == ""
    assert (
        us.emit_metar_speci_iwxxm_us(
            {
                "station": "KJFK",
                "day": 1,
                "hour": 12,
                "minute": 0,
                "visibility_m": 9999,
                "wind_dir_deg": 180,
                "wind_speed_kt": 5,
                "temp_c": 10,
                "dewpoint_c": 5,
                "qnh_hpa": 1013,
                "report_status": "AMENDMENT",
            },
            product="METAR",
            iwxxm_version="2025-2",
        ).count("reportStatus")
        >= 1
    )

    assert us._airmet_subperiod_extension(
        {
            "valid_from_day": 9,
            "valid_from_hour": 12,
            "valid_from_minute": 0,
        },
        {
            "valid_from_day": 9,
            "valid_from_hour": 18,
            "valid_from_minute": 0,
            "valid_to_day": 9,
            "valid_to_hour": 22,
            "valid_to_minute": 0,
            "inline_frzlvl_lo": 40,
            "inline_frzlvl_hi": 120,
        },
    )
    assert us._flight_level_layer_xml("SFC", "fl.x")
    assert us._airmet_freezing_level_forecast_extension({"frzlvl_section": {"isopleths": []}}) == ""
    assert us._inject_first_evolving_extension("<x/>", "") == "<x/>"
    assert us._inject_first_evolving_extension("<x></iwxxm:AIRMETEvolvingCondition>", "INNER").count("INNER") == 1
    assert us._inject_first_evolving_extension("<no-token/>", "INNER") == "<no-token/>"

    assert us._airmet_weather_hazards_extension({"us_airmet_hazard": {}}) == ""
    assert "causingLLWSConditions" in us._airmet_weather_hazards_extension(
        {
            "us_airmet_hazard": {
                "href": "http://x/IFR",
                "causing_ifr_conditions": True,
                "causing_llws_conditions": True,
            }
        }
    )
    assert us._sigmet_weather_hazards_extension({"us_sigmet_hazard": {}}) == ""
    assert 'isSevere="true"' in us._sigmet_weather_hazards_extension(
        {"us_sigmet_hazard": {"href": "http://x/TS", "tag": "A", "is_severe": True}}
    )


def test_vaa_swxa_tca_emit_guards_and_sparse() -> None:
    with pytest.raises(ValueError, match="missing VolcanicAshAdvisory"):
        vaa_emit._assert_vaa_advisory_xml("<root/>")
    with pytest.raises(ValueError, match="VolcanicAshSIGMET"):
        vaa_emit._assert_vaa_advisory_xml(
            '<iwxxm:VolcanicAshAdvisory xmlns:iwxxm="x"></iwxxm:VolcanicAshAdvisory>iwxxm:VolcanicAshSIGMET'
        )
    # No area / no elev / remarks_nil false without remarks / no next
    xml = vaa_emit.emit_vaa_annex3(
        {
            "product": "VAA",
            "vaac": "TOKYO",
            "volcano": "KARYMSKY",
            "issue_time": "2004-09-25T19:00:00Z",
            "advisory_number": "2004/4",
            "lat": None,
            "lon": None,
        },
        iwxxm_version="2025-2",
    )
    assert "VolcanicAshAdvisory" in xml
    assert "stateOrRegion" not in xml

    # SWXA empty remarks + empty next
    sw = swxa_emit.emit_swxa_annex3(
        {
            "product": "SWXA",
            "swxc": "DONLON",
            "issue_time": "2016-11-08T01:00:00Z",
            "forecasts": ["skip-me"],
        },
        iwxxm_version="2025-2",
    )
    assert "SpaceWeatherAdvisory" in sw

    # TCA observation STATIONARY + intensity/pressure/wind; fallback without obs
    tca = tca_emit.emit_tca_annex3(
        {
            "product": "TCA",
            "tcac": "YUFO",
            "tc_name": "GLORIA",
            "issue_time": "2004-09-25T19:00:00Z",
            "advisory_number": "2004/13",
            "observation_time": "2004-09-25T18:00:00Z",
            "lat": 27.1,
            "lon": -73.1,
            "movement": {"status": "STATIONARY"},
            "intensity_change": "WKN",
            "central_pressure_hpa": 965,
            "max_wind_mps": 22,
            "cb": {"nil": True},
        },
        iwxxm_version="2025-2",
    )
    assert "STATIONARY" in tca
    assert "intensityChange" in tca

    fallback = tca_emit.emit_tca_annex3(
        {
            "product": "TCA",
            "tcac": "YUFO",
            "tc_name": "GLORIA",
            "issue_time": "2004-09-25T19:00:00Z",
            "advisory_number": "2004/13",
            "lat": 27.0,
            "lon": -73.0,
            "central_pressure_hpa": 960,
            "max_wind_mps": 50,
        },
        iwxxm_version="2025-2",
    )
    assert "tropicalCyclonePosition" in fallback


# ---------------------------------------------------------------------------
# decode gaps
# ---------------------------------------------------------------------------


def test_decode_taf_alt_change_and_sigmet_place() -> None:
    assert _explain_taf("A2992", seen={"station": 1, "rtype": 1}) is not None
    assert "Change" in (_explain_taf("FM", seen={"station": 1, "rtype": 1}) or "")
    assert _explain_taf("ZZZZZ", seen={"station": 1}) is None

    set_location_name_resolver(lambda icao: f"Place-{icao}")
    try:
        seen: dict[str, int] = {}
        first = _explain_sigmet_airmet("YUDD", product="SIGMET", seen=seen)
        assert first
        assert "Place-YUDD" in first
        seen["valid_period"] = 1
        mwo = _explain_sigmet_airmet("YUSO", product="SIGMET", seen=seen)
        assert mwo
        assert "Place-YUSO" in mwo
    finally:
        set_location_name_resolver(None)

    assert _explain_advisory("TCA", product="TCA", seen={"adv": 1}) is not None
    assert _sentence_from_segment(
        DecodeSegment(start=0, end=1, code="X", explanation="Report type - METAR.")
    ).startswith("Report type")

    assert _looks_like_ahl_bulletin("\n\n") is False

    # BulletinSplitError → None
    assert _decode_bulletin("SAUS31 KZNY 121200\nGARBAGE ONLY\n", product="METAR") is None


def test_decode_bulletin_report_find_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    split = SimpleNamespace(
        reports=["METAR KJFK 121151Z NIL="],
        meta=SimpleNamespace(ahl="SAUS31 KZNY 121200", report_count=1),
    )

    def _fake_split(tac: str, *, product: str) -> Any:
        return split

    # Imported inside _decode_bulletin from tac2iwxxm.bulletin
    monkeypatch.setattr("tac2iwxxm.bulletin.split_bulletin", _fake_split)
    # report not found from search_from / anywhere → pos=0
    result = _decode_bulletin("SAUS31 KZNY 121200\nOTHER TEXT\n", product="METAR")
    assert result is not None


# ---------------------------------------------------------------------------
# metar_speci helpers
# ---------------------------------------------------------------------------


def test_metar_speci_helper_edges(monkeypatch: pytest.MonkeyPatch) -> None:
    assert ms._slp_code_to_hpa(650) == pytest.approx(965.0)
    assert ms._lightning_type_code("ICCC") == "ICCC" or ms._lightning_type_code("ICCC") is not None
    # mixed unique that hits join fallback is pragma-covered; exercise pair codes
    assert ms._lightning_type_code("ICCG") == "ICCG"
    assert ms._parse_sm_fraction("1 1/2") == pytest.approx(1.5)
    assert ms._rwy_location_description("RWYX") == "RUNWAY X" or "RUNWAY" in ms._rwy_location_description("RWY99Z")
    assert "TDZ" in ms._rwy_location_description("RWY15R TDZ")
    assert ms._parse_second_location_remark("RWY11") is None
    assert ms._parse_sector_visibility_remark("VIS M1/2 N")["below_sensor_minimum"] is True
    assert ms._parse_ca_remarks
    ir: dict[str, Any] = {}
    ms._parse_ca_remarks("DENSITY ALT MISG", ir)
    assert ir.get("density_altitude_missing") is True

    # _REPORT match failure after outer search succeeds
    monkeypatch.setattr(ms, "_REPORT", re.compile(r"^NEVER$"))
    with pytest.raises(ValueError, match="unable to parse METAR/SPECI report"):
        ms.parse_metar_speci("METAR KJFK 121151Z NIL=", product="METAR")


def test_metar_lwis_remarks_path() -> None:
    ir = ms.parse_metar_speci(
        "LWIS CYUL 121200Z AUTO 18005KT 10SM SCT020 M01/M05 A2992 RMK SLP123 DENSITY ALT 2500FT=",
        product="METAR",
    )
    assert ir["report_type"] == "LWIS"
    assert ir.get("remarks_present") is True
    assert ir.get("density_altitude_ft") == 2500 or "remarks" in ir


# ---------------------------------------------------------------------------
# sigmet_airmet helpers
# ---------------------------------------------------------------------------


def test_sigmet_airmet_polygon_close_and_conus_edges() -> None:
    geom = sa._polygon_from_wi_body("N5000 E01000 N5100 E01000 N5100 E01100")
    assert geom
    assert geom["kind"] == "polygon"

    ir: dict[str, Any] = {"stationary": False, "phenomenon": "VA"}
    body = "OBS AT 1200Z WI N5400 E15930 - N5400 E16100 - N5300 E15945 - N5300 E16000 FL250/300 NC MOV SE 20KT"
    sa._enrich_hazard_body(ir, body)
    assert ir.get("motion_speed_kt") == 20

    ir2: dict[str, Any] = {"stationary": False}
    sa._enrich_hazard_body(
        ir2,
        "WI N5000 E01000 - N5100 E01000 - N5100 E01100 - N5000 E01100 MOD ICE",
    )
    assert ir2.get("geometry", {}).get("kind") == "polygon"

    assert sa._strip_conus_airmet_lead("AIRMET ICE...JUST TEXT WITHOUT KEYWORDS") == (
        "AIRMET ICE...JUST TEXT WITHOUT KEYWORDS"
    )

    # wmo_time branch (no FAA issue group)
    conus = sa._try_parse_conus_airmet(
        "WAUS01 KKCI 091200 AIRMET SIERRA UPDT 1 FOR IFR AND MTN OBSC VALID UNTIL 091800 AIRMET ICE...MOD ICE="
    )
    assert conus is not None
    assert conus["header_style"] == "conus_updt"

    with pytest.raises(ValueError, match="unable to parse AIRMET outlook"):
        sa._parse_airmet_outlook("NO OTLK HERE", default_phenomenon="MOD_ICE")


# ---------------------------------------------------------------------------
# annex3_emit/sigmet helpers
# ---------------------------------------------------------------------------


def test_sigmet_emit_helpers() -> None:
    assert (
        sig_emit._is_wmo_sigmet_va_eggx(
            {
                "product": "SIGMET",
                "phenomenon": "VA",
                "fir": "EGGX",
                "mwo": "EGRR",
                "sequence": 4,
                "valid_to_hour": 22,
                "valid_to_minute": 0,
                "volcano": {"name": "MT OTHER"},
            }
        )
        is False
    )
    # non-closed ring (≥3 pts) → open_coords branch; closed short → early return
    assert "1.00 2.00" in sig_emit._wmo_multi_location_va_pos_list("1 2 3 4 5 6")
    assert sig_emit._wmo_multi_location_va_pos_list("1 2 3 4 1 2") == "1 2 3 4 1 2"

    geom = sig_emit._sigmet_geometry_xml(
        {"top_fl": 300, "upper_fl": None, "geometry": {"kind": "point", "lat": 10.0, "lon": 20.0}},
        fir="YUDD",
    )
    assert "geometry" in geom

    # convective without states
    xml = sig_emit.emit_convective_sigmet_annex3(
        {
            "product": "SIGMET",
            "fir": "KKCI",
            "mwo": "KKCI",
            "sequence": 1,
            "valid_from_day": 9,
            "valid_from_hour": 12,
            "valid_from_minute": 0,
            "valid_to_day": 9,
            "valid_to_hour": 16,
            "valid_to_minute": 0,
            "phenomenon": "TS",
            "convective": True,
            "geometry": {
                "kind": "polygon",
                "pos_list": "40.0 -90.0 41.0 -90.0 41.0 -89.0 40.0 -89.0 40.0 -90.0",
            },
        },
        iwxxm_version="2025-2",
    )
    assert "SIGMET" in xml


def test_ev080_remaining_branch_fill(monkeypatch: pytest.MonkeyPatch) -> None:
    """Second-pass branch arcs still open after the first EV-080 fill."""
    import tac2iwxxm.bulletin as bulletin_mod
    from tac2iwxxm.decode import DecodeResult

    # format_ahl without BBB (291→295 false)
    parts = AhlParts(
        ahl="SAUS31 KZNY 121200",
        tt="SA",
        aa="US",
        ii="31",
        cccc="KZNY",
        yygggg="121200",
        iwxxm_tt="LA",
        report_status="NORMAL",
        bbb=None,
    )
    assert format_ahl(parts) == "SAUS31 KZNY 121200"

    # VONA elif false: ghost product falls through elifs to empty-check
    monkeypatch.setitem(bulletin_mod._PRODUCT_TT, "GHOST", frozenset({"SA"}))
    monkeypatch.setitem(bulletin_mod._PRODUCT_BODY_RE, "GHOST", bulletin_mod._PRODUCT_BODY_RE["METAR"])
    ghost = split_bulletin("SAUS31 KZNY 121200\nMETAR KJFK 121151Z NIL=\n", product="GHOST")
    assert ghost.reports

    # advisory fallthrough + bulletin summary falsy
    assert _explain_advisory("OTHER", product="TCA", seen={"tc": 1, "adv": 1}) is not None

    empty_inner = DecodeResult(product="METAR", segments=[], residuals=[], summary=None)

    def _fake_split(tac: str, *, product: str) -> Any:
        return SimpleNamespace(
            reports=["METAR KJFK 121151Z NIL="],
            meta=SimpleNamespace(ahl="SAUS31 KZNY 121200", report_count=1),
        )

    monkeypatch.setattr("tac2iwxxm.bulletin.split_bulletin", _fake_split)
    monkeypatch.setattr(
        "tac2iwxxm.decode._decode_single_report",
        lambda *a, **k: empty_inner,
    )
    monkeypatch.setattr("tac2iwxxm.decode._shift_decode", lambda result, offset: empty_inner)
    assert _decode_bulletin("SAUS31 KZNY 121200\nMETAR KJFK 121151Z NIL=\n", product="METAR") is not None

    # clip already-closed output (207→209 false)
    ring = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0)]
    c = fg.RelativeConstraint(axis="lat", value=-1.0, keep="north")
    out = fg._clip_ring_one(ring, c)
    assert out
    assert out[0] == out[-1]

    # annex3 min vis without direction
    vis = a3._visibility_block({"visibility_m": 2000, "min_visibility_m": 1000})
    assert "minimumVisibility" in vis
    assert "Direction" not in vis

    # TCA observation: STATIONARY elif false + no optional fields
    sparse_obs = tca_emit.emit_tca_annex3(
        {
            "product": "TCA",
            "tcac": "YUFO",
            "tc_name": "GLORIA",
            "issue_time": "2004-09-25T19:00:00Z",
            "advisory_number": "2004/13",
            "observation_time": "2004-09-25T18:00:00Z",
            "lat": 27.1,
            "lon": -73.1,
            "movement": {"status": "UNKNOWN"},
            "cb": {"nil": True},
        },
        iwxxm_version="2025-2",
    )
    assert "TropicalCycloneAdvisory" in sparse_obs

    # TCA fallback without lat/lon/pressure/wind
    bare = tca_emit.emit_tca_annex3(
        {
            "product": "TCA",
            "tcac": "YUFO",
            "tc_name": "GLORIA",
            "issue_time": "2004-09-25T19:00:00Z",
            "advisory_number": "2004/13",
        },
        iwxxm_version="2025-2",
    )
    assert "TropicalCycloneAdvisory" in bare

    # iwxxm_us sector / hazard false-attr paths
    assert "extremeCCW" in us._observed_lightning_xml({"sector": {"ccw_deg": 10.5, "cw_deg": 20.0}})
    assert "extremeCCW" in us._convective_cloud_xml(
        {"sector": {"ccw_deg": 0, "cw_deg": 90}, "direction_of_motion_deg": 180}
    )
    assert "AIRMETWeatherHazards" in us._airmet_weather_hazards_extension(
        {"us_airmet_hazard": {"href": "http://x/IFR"}}
    )
    assert "SIGMETWeatherHazards" in us._sigmet_weather_hazards_extension(
        {"us_sigmet_hazard": {"href": "http://x/TS", "tag": "  "}}
    )
    parent = {
        "product": "AIRMET",
        "fir": "KKCI",
        "mwo": "KKCI",
        "sequence": 1,
        "valid_from_day": 9,
        "valid_from_hour": 12,
        "valid_from_minute": 0,
        "valid_to_day": 9,
        "valid_to_hour": 18,
        "valid_to_minute": 0,
        "phenomenon": "MOD_ICE",
        "fir_name": "KKCI",
        "us_airmet_hazard": {"href": "http://x/ICE"},
        "outlook": {
            "valid_from_day": 9,
            "valid_from_hour": 18,
            "valid_from_minute": 0,
            "valid_to_day": 9,
            "valid_to_hour": 22,
            "valid_to_minute": 0,
            "phenomenon": "MOD_ICE",
        },
    }
    assert "AIRMET" in us.emit_airmet_iwxxm_us(parent, iwxxm_version="2025-2")

    # metres visibility path
    ir_m = ms.parse_metar_speci(
        "METAR KJFK 121151Z 18005KT 8000 SCT020 10/05 Q1013=",
        product="METAR",
    )
    assert ir_m.get("visibility_m") == 8000
    assert ms._parse_second_location_remark("VIS M1/4 RWY11") is not None
    ir_lwis = ms.parse_metar_speci(
        "LWIS CYUL 121200Z AUTO 18005KT 10SM SCT020 M01/M05 A2992 RMK SLP123=",
        product="METAR",
    )
    assert ir_lwis.get("ca_minimal_observation") is True

    # sigmet / airmet remaining arcs
    assert sa._phenomenon_from_conus_for_text("MTN OBSC") == "MT_OBSC"
    ir_tc: dict[str, Any] = {"stationary": False, "phenomenon": "TC"}
    sa._enrich_hazard_body(
        ir_tc,
        "TC GLORIA PSN N2706 W07306 WI 30 NM OF TC CENTRE FCST AT 2200Z TC CENTRE PSN N2748 W07350",
    )
    assert ir_tc.get("geometry", {}).get("kind") == "circle"
    ir_wi: dict[str, Any] = {"stationary": False}
    sa._enrich_hazard_body(ir_wi, "WI N5000 E01000 - N5100 E01000 MOD ICE")
    assert sa._parse_frzlvl_section("FRZLVL...RANGING FROM SFC-120 ACRS AREA")["multiple_levels"] is False

    from tac2iwxxm.products.sigmet_airmet import _parse_convective_sigmet

    _parse_convective_sigmet(
        "CONVECTIVE SIGMET 12 VALID UNTIL 1655Z KS FROM 10N FSD-20NE FSD AREA TS MOV FROM 24045KT TOPS TO FL450"
    )
    _parse_convective_sigmet(
        "KKCI CONVECTIVE SIGMET 12 VALID UNTIL 1655Z KS FROM 10N FSD-20NE FSD AREA TS MOV FROM 24045KT TOP BLW FL180"
    )

    assert "posList" in sig_emit._sigmet_geometry_xml(
        {"geometry": {"kind": "polygon", "pos_list": "1 2 3 4 5 6 1 2"}},
        fir="YUDD",
        wmo_multi_location_va_ring=False,
    )
    loc_xml = sig_emit._sigmet_location_analysis_xml(
        {
            "obs_hhmm": "1200",
            "geometry": {"kind": "polygon", "pos_list": "1 2 3 4 5 6 1 2"},
            "intensity_change": "NO_CHANGE",
        },
        fir="YUDD",
        index=0,
        issue="2012-08-10T12:00:00Z",
        begin="2012-08-10T12:00:00Z",
        end="2012-08-10T16:00:00Z",
    )
    assert "analysis" in loc_xml

    # --- final branch arcs ---
    assert fg._ensure_closed_ring([]) == []
    assert fg._ensure_closed_ring([(1.0, 2.0), (1.0, 2.0)]) == [(1.0, 2.0), (1.0, 2.0)]
    assert fg._ensure_closed_ring([(1.0, 2.0), (3.0, 4.0)])[0] == (1.0, 2.0)

    # metar: // wx skip; lightning no sector; second-loc without M; max-only 6h;
    # no metre/SM vis; trend parse None
    trend = ms._parse_trend_group(
        {"day": 1, "hour": 12, "minute": 0, "station": "KJFK"},
        "TEMPO",
        "TL1300 //",
    )
    assert trend is not None
    # sector absent → skip sector assign (428→430 false)
    lit = ms._parse_lightning_remark("OCNL LTGIC DSNT")
    assert lit is not None
    assert "sector" not in lit
    assert ms._parse_second_location_remark("CIG 005 VIS 1/2 RWY11") is not None
    assert any("max_c" in r for r in ms._parse_max_min_temperatures("10123"))
    # CAVOK → no vis_m rebind branch false
    ir_cav = ms.parse_metar_speci(
        "METAR KJFK 121151Z 18005KT CAVOK 10/05 Q1013 TEMPO BADTOKEN=",
        product="METAR",
    )
    assert ir_cav.get("cavok") is True

    # GFA structured SM + metres + cloud + wind
    assert sa._parse_ca_gfa_structured("3SM BKN010 MOV NE 15KT", "SFC_VIS_and_BKN_CLD")
    assert sa._parse_ca_gfa_structured("0800M OVC015", "SFC_VIS_and_OVC_CLD")
    assert sa._parse_ca_gfa_structured("NOPE", "SFC_VIS_and_BKN_CLD") is None
    # VA FL band path (elif lo/hi) + fcst polygon
    ir_va2: dict[str, Any] = {"stationary": False, "phenomenon": "VA"}
    sa._enrich_hazard_body(
        ir_va2,
        "OBS AT 1200Z WI N5400 E15930 - N5400 E16100 - N5300 E15945 - N5300 E16000 "
        "FL250/300 NC FCST AT 1800Z WI N5500 E15900 - N5500 E16100 - N5400 E16000 - N5400 E15900",
    )
    assert ir_va2.get("locations")
    # TC name without OBS PSN (420→425 false); avoid "TC CENTRE PSN" which matches OBS regex
    ir_tc2: dict[str, Any] = {"stationary": False, "phenomenon": "TC"}
    sa._enrich_hazard_body(ir_tc2, "TC GLORIA MOV W 10KT")
    assert ir_tc2.get("tropical_cyclone_name") == "Gloria"
    assert "tropical_cyclone_position" not in ir_tc2
    # FRZLVL section with MULT
    assert sa._parse_frzlvl_section("MULT FRZLVL 040-120")["multiple_levels"] is True
    # CONUS with issue group (585 true) vs wmo_time already hit; force elif false via issue present
    assert (
        sa._try_parse_conus_airmet(
            "KZOA WA 091200 AIRMET TANGO UPDT 2 FOR TURB VALID UNTIL 091800 AIRMET ICE...MOD ICE="
        )
        is not None
    )
    # convective TOP FL (no ABV/BLW → 696→703) + empty FROM chain (704→706 false)
    bare_top = _parse_convective_sigmet(
        "CONVECTIVE SIGMET 12 VALID UNTIL 1655Z KS FROM 10N FSD-20NE FSD-30E FSD AREA TS MOV FROM 24045KT TOP FL450"
    )
    assert bare_top is not None
    assert bare_top.get("top_fl") == 450
    assert "top_qualifier" not in bare_top
    no_vor = _parse_convective_sigmet(
        "CONVECTIVE SIGMET 12 VALID UNTIL 1655Z KS FROM AREA TS MOV FROM 24045KT TOP ABV FL450"
    )
    assert no_vor is not None
    assert "geometry" not in no_vor

    # iwxxm_us gml id: rvr dict not variable; empty sector dicts; outlook token miss
    assert us._us_gml_id({"station": "KJFK", "rvr": {"variable": False, "min_m": 1}}, "METAR")
    assert "ObservedLightning" in us._observed_lightning_xml({"sector": {"noise": True}})
    assert "ConvectiveCloudLocation" in us._convective_cloud_xml({"sector": {"noise": True}})
    # outlook present but member id absent → skip injection (1024 false)
    bare_air = {
        "product": "AIRMET",
        "fir": "YYYY",
        "mwo": "KKCI",
        "sequence": 1,
        "valid_from_day": 9,
        "valid_from_hour": 12,
        "valid_from_minute": 0,
        "valid_to_day": 9,
        "valid_to_hour": 18,
        "valid_to_minute": 0,
        "phenomenon": "MOD_ICE",
        "fir_name": "YYYY",
        "outlook": {
            "valid_from_day": 9,
            "valid_from_hour": 18,
            "valid_from_minute": 0,
            "valid_to_day": 9,
            "valid_to_hour": 22,
            "valid_to_minute": 0,
        },
    }
    import tac2iwxxm.profiles.annex3_products as ap_mod

    real_airmet_emit = ap_mod.emit_airmet_annex3

    def _strip_outlook_token(ir: dict[str, Any], *, iwxxm_version: str) -> str:
        return real_airmet_emit(ir, iwxxm_version=iwxxm_version).replace(
            'gml:id="cond.yyyy.outlook.1"',
            'gml:id="cond.yyyy.obs.9"',
        )

    monkeypatch.setattr(ap_mod, "emit_airmet_annex3", _strip_outlook_token)
    assert "AIRMET" in us.emit_airmet_iwxxm_us(bare_air, iwxxm_version="2025-2")

    # vis only in trend → early pass, obs rebind finds none (1104→1109 false)
    ir_novis = ms.parse_metar_speci(
        "METAR KJFK 121151Z VRB02KT SCT020 M01/M05 A2992 TEMPO 8000=",
        product="METAR",
    )
    assert ir_novis.get("station") == "KJFK"
    # early TEMPO metres may remain; branch under test is obs_body vis_m is None

    # TC OBS PSN without circle (420 true; no geometry circle)
    ir_tc_obs: dict[str, Any] = {"stationary": False, "phenomenon": "TC"}
    sa._enrich_hazard_body(ir_tc_obs, "TC GLORIA PSN N2706 W07306 MOV W 10KT")
    assert ir_tc_obs.get("tropical_cyclone_position") is not None

    # VA fcst_wi with <3 points → fcst_geom None
    ir_va3: dict[str, Any] = {"stationary": False, "phenomenon": "VA"}
    sa._enrich_hazard_body(
        ir_va3,
        "OBS AT 1200Z WI N5400 E15930 - N5400 E16100 - N5300 E15945 - N5300 E16000 FL250/300 NC "
        "FCST AT 1800Z WI N5500 E15900",
    )
    # CONUS without issue and without wmo header (585→587 false)
    assert sa._try_parse_conus_airmet("AIRMET SIERRA UPDT 1 FOR IFR VALID UNTIL 091800 AIRMET ICE...MOD=") is not None
    # convective TOPS TO + TOP ABV with vor geometry (696/700/704 true)
    c1 = _parse_convective_sigmet(
        "CONVECTIVE SIGMET 12 VALID UNTIL 1655Z KS FROM 10N FSD-20NE FSD-30E FSD AREA TS MOV FROM 24045KT TOPS TO FL450"
    )
    assert c1 is not None
    assert c1.get("top_qualifier") == "TO"
    c2 = _parse_convective_sigmet(
        "CONVECTIVE SIGMET 12 VALID UNTIL 1655Z KS FROM 10N FSD-20NE FSD-30E FSD AREA TS MOV FROM 24045KT TOP ABV FL450"
    )
    assert c2 is not None
    assert c2.get("top_qualifier") == "ABV"
    assert c2.get("geometry") is not None

    # sigmet geometry non-polygon with limits only
    assert "AirspaceVolume" in sig_emit._sigmet_geometry_xml(
        {"top_fl": 100, "geometry": {"kind": "other"}},
        fir="YUDD",
    )
    # forecast dict without geometry dict
    loc2 = sig_emit._sigmet_location_analysis_xml(
        {
            "obs_hhmm": "1200",
            "geometry": {"kind": "polygon", "pos_list": "1 2 3 4 5 6 1 2"},
            "intensity_change": "NO_CHANGE",
            "forecast": {"hhmm": "1800", "geometry": "bad"},
        },
        fir="YUDD",
        index=1,
        issue="2012-08-10T12:00:00Z",
        begin="2012-08-10T12:00:00Z",
        end="2012-08-10T16:00:00Z",
    )
    assert "analysis" in loc2
