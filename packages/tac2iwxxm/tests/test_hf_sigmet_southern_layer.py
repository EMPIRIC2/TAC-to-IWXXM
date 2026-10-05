"""Southern SIGMET polygon, feet-to-flight-level layer, and preview pairing."""

from __future__ import annotations

import re

from tac2iwxxm.convert import convert
from tac2iwxxm.group_trace import trace_emitted_groups
from tac2iwxxm.slot_builders.sigmet_airmet import _point_lat_lon

_TAC = """WSPSZ1 NZKL 050806
NZZO SIGMET 2 VALID 050811/051211 NZKL-
NZZO AUCKLAND OCEANIC FIR SEV TURB FCST WI S7520
W14200 - S7728 W13100 - S7700 W14410 - S7520 W14200
9000FT/FL290 MOV
S 20KT INTSF="""


def test_southern_oceanic_sigmet_keeps_polygon_and_feet_layer() -> None:
    result = convert(_TAC, product="SIGMET", preview=True, profile="us_faa_nws")
    assert result.ok
    assert result.xml
    assert "PARSE_ERROR" not in [issue.code for issue in result.issues]
    assert "-75.3333 -142.0000" in result.xml
    assert 'uom="[ft_i]">9000</aixm:lowerLimit>' in result.xml
    assert 'uom="FL">290</aixm:upperLimit>' in result.xml
    assert result.xml.count('uom="FL">290</aixm:upperLimit>') == 1


def test_metres_to_flight_level_uses_metre_lower_limit() -> None:
    tac = (
        "YUDD SIGMET 2 VALID 101200/101600 YUSO- "
        "YUDD AMSWELL FIR SEV TURB FCST WI S1000 W02000 - S1000 W01000 - "
        "S2000 W01000 - S1000 W02000 1000M/FL100 MOV E 10KT NC="
    )
    result = convert(tac, product="SIGMET", preview=True)
    assert result.ok
    assert result.xml
    assert 'uom="m">1000</aixm:lowerLimit>' in result.xml
    assert 'uom="FL">100</aixm:upperLimit>' in result.xml


def test_preview_pairing_follows_the_selected_token() -> None:
    rows = trace_emitted_groups(_TAC, "SIGMET")
    latitude = next(row for row in rows if row["token"] == "S7520")
    level = next(row for row in rows if row["token"] == "9000FT/FL290")
    separator = next(row for row in rows if row["token"] == "-")
    office = next(row for row in rows if row["token"] == "NZKL-")
    assert latitude["element"] == "posList"
    assert latitude["scope"] == "line"
    assert [level["element"], rows[rows.index(level) + 1]["element"]] == [
        "lowerLimit",
        "upperLimit",
    ]
    assert separator["element"] == "posList"
    assert office["element"] == "originatingMeteorologicalWatchOffice"


def test_point_without_latitude_hemisphere_stays_north() -> None:
    match = re.match(
        r"N(?P<lat_deg>\d{2})(?P<lat_min>\d{2})\s+(?P<lon_hemi>[EW])(?P<lon_deg>\d{3})(?P<lon_min>\d{2})",
        "N1020 E01000",
    )
    assert match is not None
    lat, lon = _point_lat_lon(match)
    assert lat > 0
    assert lon > 0
