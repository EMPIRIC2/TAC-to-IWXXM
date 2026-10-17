"""SIGMET and VAA movement and line geometry.

[Corpus: product §F6] [Corpus: product §F23]
"""

from __future__ import annotations

import pytest
from tac2iwxxm.slot_builders.sigmet_airmet import _DIR_DEG as SIGMET_DIRECTIONS
from tac2iwxxm.slot_builders.sigmet_airmet import parse_sigmet
from tac2iwxxm.slot_builders.sigmet_body import _DIRECTIONS as SIGMET_BODY_DIRECTIONS
from tac2iwxxm.slot_builders.vaa_tca import _DIR_DEG as VAA_DIRECTIONS
from tac2iwxxm.slot_builders.vaa_tca import _parse_ash_clouds

_HEADER = "USTV SIGMET 2 VALID 051330/051730 USTR- USTV TYUMEN FIR "
_ASH_CLOUD = "FL250/300 N5400 E15930 - N5400 E16100 - N5300 E15945"
_LINE = "N6310 E08435 - N6321 E07730"
_SIXTEEN_POINTS = (
    ("N", 0.0),
    ("NNE", 22.5),
    ("NE", 45.0),
    ("ENE", 67.5),
    ("E", 90.0),
    ("ESE", 112.5),
    ("SE", 135.0),
    ("SSE", 157.5),
    ("S", 180.0),
    ("SSW", 202.5),
    ("SW", 225.0),
    ("WSW", 247.5),
    ("W", 270.0),
    ("WNW", 292.5),
    ("NW", 315.0),
    ("NNW", 337.5),
)


def _sigmet(body: str) -> dict[str, object]:
    return parse_sigmet(f"{_HEADER}{body}")


@pytest.mark.parametrize(
    ("direction", "degrees"),
    [("NW", 315.0), ("E", 90.0)],
)
def test_sigmet_movement_without_speed_keeps_direction(direction: str, degrees: float) -> None:
    ir = _sigmet(f"SEV TURB FCST SFC/FL100 MOV {direction} NC=")
    assert ir["motion_dir_deg"] == degrees
    assert "motion_speed_kmh" not in ir
    assert "motion_speed_kt" not in ir


def test_sigmet_slash_kilometres_per_hour_is_kept() -> None:
    glued = _sigmet("SEV TURB FCST SFC/FL100 MOV E 25KM/H NC=")
    spaced = _sigmet("SEV TURB FCST SFC/FL100 MOV E 25 KM/H NC=")
    compact = _sigmet("SEV TURB FCST SFC/FL100 MOV E 20KMH NC=")
    assert glued["motion_speed_kmh"] == 25
    assert spaced["motion_speed_kmh"] == 25
    assert compact["motion_speed_kmh"] == 20
    assert "motion_speed_kt" not in glued
    assert "motion_speed_kt" not in compact


@pytest.mark.parametrize("side", ["E", "N"])
def test_line_side_builds_a_horizontal_surface(side: str) -> None:
    ir = _sigmet(f"SEV TURB FCST {side} OF LINE {_LINE} SFC/FL100 NC=")
    geometry = ir["geometry"]
    assert isinstance(geometry, dict)
    assert geometry["kind"] == "polygon"
    positions = str(geometry["pos_list"]).split()
    assert positions[:2] == positions[-2:]
    latitudes = [float(value) for value in positions[0::2]]
    longitudes = [float(value) for value in positions[1::2]]
    if side == "E":
        assert max(longitudes) > 84.5833
    else:
        assert max(latitudes) > 63.35


@pytest.mark.parametrize(("token", "degrees"), _SIXTEEN_POINTS)
def test_vaa_ash_cloud_accepts_sixteen_compass_points(token: str, degrees: float) -> None:
    clouds = _parse_ash_clouds(f"{_ASH_CLOUD} MOV {token} 12KT")
    assert clouds[0]["motion_dir_deg"] == degrees
    assert clouds[0]["motion_speed_kt"] == 12


@pytest.mark.parametrize(
    ("group", "speed_key", "speed"),
    [
        ("20KMH", "motion_speed_kmh", 20),
        ("20 KM/H", "motion_speed_kmh", 20),
        ("20KM/H", "motion_speed_kmh", 20),
        ("15KT", "motion_speed_kt", 15),
        ("10MPS", "motion_speed_kmh", 36),
    ],
)
def test_vaa_ash_cloud_accepts_speed_units(group: str, speed_key: str, speed: int) -> None:
    clouds = _parse_ash_clouds(f"{_ASH_CLOUD} MOV E {group}")
    assert clouds[0][speed_key] == speed
    other = "motion_speed_kt" if speed_key == "motion_speed_kmh" else "motion_speed_kmh"
    assert other not in clouds[0]


def test_nne_bearing_is_twenty_two_point_five() -> None:
    assert SIGMET_DIRECTIONS["NNE"] == 22.5
    assert SIGMET_BODY_DIRECTIONS["NNE"] == 22.5
    assert VAA_DIRECTIONS["NNE"] == 22.5
    assert _sigmet("SEV TURB FCST SFC/FL100 MOV NNE NC=")["motion_dir_deg"] == 22.5
    clouds = _parse_ash_clouds(f"{_ASH_CLOUD} MOV NNE 30KMH")
    assert clouds[0]["motion_dir_deg"] == 22.5
    assert clouds[0]["motion_speed_kmh"] == 30
