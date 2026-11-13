"""Per-file 100% line+branch fill for EV-080 M2b T2.2 (fill-before-flip).

[Corpus: adr/ADR-007] [Corpus: tests]
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from tac2iwxxm.bulletin import AhlParts, format_ahl, split_bulletin
from tac2iwxxm.decode import (
    _decode_bulletin,
    _explain_advisory,
)
from tac2iwxxm.products import fir_geometry as fg
from tac2iwxxm.profiles import annex3 as a3
from tac2iwxxm.profiles import iwxxm_us as us
from tac2iwxxm.profiles.annex3_emit import sigmet as sig_emit
from tac2iwxxm.profiles.annex3_emit import tca as tca_emit
from tac2iwxxm.slot_builders import metar_speci as ms
from tac2iwxxm.slot_builders import sigmet_airmet as sa


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

    from tac2iwxxm.slot_builders.sigmet_airmet import _parse_convective_sigmet

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
    import tac2iwxxm.profiles.annex3_emit as ap_mod

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
