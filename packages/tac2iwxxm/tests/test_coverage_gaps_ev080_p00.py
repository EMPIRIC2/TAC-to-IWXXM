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
from tac2iwxxm.profile_registry import known_semantic_profile_ids
from tac2iwxxm.profiles import annex3 as a3
from tac2iwxxm.profiles import ca_eccc as ca
from tac2iwxxm.profiles import iwxxm_us as us
from tac2iwxxm.profiles.annex3_emit import swxa as swxa_emit
from tac2iwxxm.profiles.annex3_emit import taf as taf_emit
from tac2iwxxm.profiles.annex3_emit import tca as tca_emit
from tac2iwxxm.profiles.annex3_emit import vaa as vaa_emit
from tac2iwxxm.slot_builders import swxa as swxa_mod
from tac2iwxxm.slot_builders import vaa_tca as vt
from tac2iwxxm.slot_builders import vona as vona_mod
from tac2iwxxm.slot_builders.taf import parse_taf
from tac2iwxxm.slot_builders.vona import parse_vona


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
        product="TCA",
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
