"""Coverage helpers for ``vaa_tca`` parse branches (T6.2 / cov-fail-under=95).

Hits S/W points, empty polygons, NO VA EXP, FL/SFC bands, TCA MOV uom
variants, and STNR - paths not exercised by the WMO A7-2 / A2-2 goldens alone.
"""

from __future__ import annotations

from pathlib import Path

from tac2iwxxm.glossary import (
    _tokens_from_mapping,
    resolve_location_name,
    set_location_name_resolver,
)
from tac2iwxxm.products.vaa_tca import (
    _parse_ash_clouds,
    _parse_dtg,
    _point_to_pair,
    _pos_list,
    parse_tca,
    parse_vaa,
)


def test_parse_dtg_forms() -> None:
    assert _parse_dtg("20040925/1900Z") == "2004-09-25T19:00:00Z"
    assert _parse_dtg("not-a-dtg") is None


def test_point_to_pair_southern_western_hemisphere() -> None:
    lat, lon = _point_to_pair("S", "2706", "W", "07306")
    assert lat < 0
    assert lon < 0


def test_pos_list_empty_and_open_ring() -> None:
    assert _pos_list([]) == ""
    closed = _pos_list([(1.0, 2.0), (3.0, 4.0)])
    assert closed.startswith("1.00 2.00")
    assert closed.endswith("1.00 2.00")


def test_parse_ash_clouds_no_va_exp_and_skip_empty_chunk() -> None:
    assert _parse_ash_clouds("NO VA EXP") == []
    assert _parse_ash_clouds("FL250/300 NO POINTS HERE") == []


def test_parse_ash_clouds_fl_band_and_sfc() -> None:
    fl = _parse_ash_clouds("FL250/300 N5400 E15930 - N5400 E16100 - N5300 E15945 - N5300 E16000 MOV SE 20KT")
    assert len(fl) == 1
    assert fl[0]["lower_fl"] == 250
    assert fl[0]["motion_speed_kt"] == 20

    sfc = _parse_ash_clouds("SFC/FL200 N5130 E16130 - N5130 E16230 - N5230 E16230 - N5230 E16130")
    assert len(sfc) == 1
    assert sfc[0]["lower"] == "GND"


def test_parse_vaa_continuation_line() -> None:
    tac = """\
VA ADVISORY
DTG: 20240923/0130Z
VAAC: TOKYO
VOLCANO: KARYMSKY 1000-13
PSN: N5403 E15927
AREA: RUSSIA
SOURCE ELEV: 1536M AMSL
ADVISORY NR: 2024/4
INFO SOURCE: HIMAWARI
ERUPTION DETAILS: ERUPTION AT 20240923/0000Z FL300 REPORTED
OBS VA DTG: 23/0100Z
OBS VA CLD: FL250/300 N5400 E15930 - N5400 E16100 - N5300 E15945
            N5300 E16000 MOV SE 20KT
FCST VA CLD +6 HR: 23/0700Z NO VA EXP
RMK: NIL
NXT ADVISORY: NO FURTHER ADVISORIES
"""
    ir = parse_vaa(tac)
    assert ir["product"] == "VAA"
    assert ir["observation_clouds"]
    assert ir["forecasts"]


def test_parse_tca_mps_and_stationary_movement() -> None:
    tac = """\
TC ADVISORY
DTG: 20040925/1900Z
TCAC: YUFO
TC: GLORIA
ADVISORY NR: 2004/13
OBS PSN: 25/1800Z N2706 W07306
CB: NIL
MOV: STNR
INTST CHANGE: WKN
C: 965HPA
MAX WIND: 22MPS
FCST PSN +6 HR: 25/2200Z N2748 W07350
FCST MAX WIND +6 HR: 22MPS
RMK: NIL
NXT MSG: NO MSG EXP
"""
    ir = parse_tca(tac)
    assert ir["movement"]["status"] == "STATIONARY"
    assert ir["cb"]["nil"] is True

    moving = tac.replace("MOV: STNR", "MOV: NW 10MPS")
    ir2 = parse_tca(moving)
    assert ir2["movement"]["speed_uom"] == "m/s"


def test_glossary_tokens_from_mapping_guards() -> None:
    assert _tokens_from_mapping(None) == {}
    assert _tokens_from_mapping({"tokens": "nope"}) == {}
    assert _tokens_from_mapping({"tokens": {"OBSC": "obscured", 1: "x", "EMPTY": ""}}) == {"OBSC": "obscured"}


def test_glossary_location_resolver_soft_fail(tmp_path: Path) -> None:
    set_location_name_resolver(None)
    assert resolve_location_name("KJFK") is None

    def _boom(_icao: str) -> str:
        raise RuntimeError("lookup failed")

    set_location_name_resolver(_boom)
    try:
        assert resolve_location_name("KJFK") is None
    finally:
        set_location_name_resolver(None)

    missing = tmp_path / "missing.yaml"
    from tac2iwxxm.glossary import _load_yaml_tokens

    assert _load_yaml_tokens(missing) == {}


def test_convert_content_bounds_and_remark_span_miss() -> None:
    from tac2iwxxm.convert import _content_bounds, _remark_span

    assert _content_bounds("") == (0, 0)
    assert _content_bounds("   \n") == (0, 4)
    assert _content_bounds("  METAR  ")[0] == 2
    # Needle present but pattern does not match → fall through to (None, None)
    assert _remark_span("METAR KJFK NOSIG", "malformed AO token") == (None, None)
    # Needle + match → span
    start, end = _remark_span("METAR KJFK RMK AO9", "malformed AO token")
    assert start is not None
    assert end is not None
    assert end > start
