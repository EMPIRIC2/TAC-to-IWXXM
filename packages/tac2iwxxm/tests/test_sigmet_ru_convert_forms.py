"""International SIGMET conversion: freezing rain, kilometres per hour, and open lines."""

from __future__ import annotations

from typing import Any

from tac2iwxxm.profiles.annex3_emit.sigmet import _motion_deg_text, _sigmet_motion_xml
from tac2iwxxm.slot_builders.sigmet_airmet import _apply_motion, parse_sigmet

_HEADER = "USTV SIGMET 2 VALID 051330/051730 USTR- USTV TYUMEN FIR "


def test_freezing_rain_keeps_kilometres_and_skips_an_open_line() -> None:
    tac = f"{_HEADER}SEV ICE (FZRA) FCST E OF LINE N6310 E08435 - N6321 E07730 SFC/FL100 MOV NE 20KMH NC="
    ir = parse_sigmet(tac)
    assert ir["phenomenon"] == "SEV_ICE_FZRA"
    assert ir["motion_speed_kmh"] == 20
    assert ir["motion_dir_deg"] == 45
    assert "motion_speed_kt" not in ir
    assert "geometry" not in ir
    xml = _sigmet_motion_xml(ir)
    assert 'uom="km/h">20</iwxxm:speedOfMotion>' in xml
    assert "[kn_i]" not in xml


def test_knots_and_bare_ice_stay_unchanged() -> None:
    tac = f"{_HEADER}SEV ICE FCST WI N6310 E08435 - N6321 E07730 - N6140 E07500 SFC/FL100 MOV NE 20KT NC="
    ir = parse_sigmet(tac)
    assert ir["phenomenon"] == "SEV_ICE"
    assert ir["motion_speed_kt"] == 20
    assert ir["geometry"]["kind"] == "polygon"
    xml = _sigmet_motion_xml(ir)
    assert 'uom="[kn_i]">20</iwxxm:speedOfMotion>' in xml


def test_spaced_kilometres_sixteen_points_and_metres_per_second() -> None:
    spaced = parse_sigmet(f"{_HEADER}SEV TURB FCST SFC/FL100 MOV NNE 30 KMH NC=")
    assert spaced["motion_dir_deg"] == 22.5
    assert spaced["motion_speed_kmh"] == 30
    assert ">22.5</iwxxm:directionOfMotion>" in _sigmet_motion_xml(spaced)

    metres = parse_sigmet(f"{_HEADER}SEV TURB FCST SFC/FL100 MOV E 10MPS NC=")
    assert metres["motion_speed_kmh"] == 36
    assert metres["motion_dir_deg"] == 90

    assert _motion_deg_text(90) == "90"
    assert _motion_deg_text(22.5) == "22.5"


def test_motion_helper_ignores_stationary_and_missing_groups() -> None:
    stationary: dict[str, Any] = {"stationary": True}
    _apply_motion(stationary, "MOV NE 20KMH")
    assert "motion_speed_kmh" not in stationary

    quiet: dict[str, Any] = {"stationary": False}
    _apply_motion(quiet, "SEV ICE FCST NC")
    assert "motion_dir_deg" not in quiet
