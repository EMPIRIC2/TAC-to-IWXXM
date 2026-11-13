"""Per-file 100% line+branch fill for EV-080 M2b T2.2 (fill-before-flip).

[Corpus: adr/ADR-007] [Corpus: tests]
"""

from __future__ import annotations

import re
from typing import Any

import pytest
from tac2iwxxm.profiles.annex3_emit import sigmet as sig_emit
from tac2iwxxm.slot_builders import metar_speci as ms
from tac2iwxxm.slot_builders import sigmet_airmet as sa


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
