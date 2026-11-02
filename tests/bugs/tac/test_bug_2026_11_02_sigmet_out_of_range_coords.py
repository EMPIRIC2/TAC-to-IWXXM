"""BUG-2026-11-02 — Out-of-range SIGMET coordinates must not enter posList.

Latitudes beyond ±90 and longitudes beyond ±180 are accepted and serialized
into ``gml:posList`` on a successful convert.

[Corpus: product §F6] [Corpus: tests]
"""

from __future__ import annotations

import re

import pytest

from tac2iwxxm import convert

_LAT95 = """\
YUDD SIGMET 2 VALID 101200/101600 YUSO-
YUDD SHANLON FIR/UIR SEV ICE FCST WI N9500 E01000 - N9600 E01200 - N9500 E01400 - N9500 E01000 FL100/200 STNR NC=
"""

_LON190 = """\
YUDD SIGMET 2 VALID 101200/101600 YUSO-
YUDD SHANLON FIR/UIR SEV ICE FCST WI N5400 E19000 - N5500 E19100 - N5400 E19200 - N5400 E19000 FL100/200 STNR NC=
"""


def _pos_lists(xml: str) -> list[str]:
    return re.findall(r"<gml:posList[^>]*>([^<]*)</gml:posList>", xml or "")


def _coords(pos_list: str) -> list[float]:
    return [float(tok) for tok in pos_list.split() if tok]


@pytest.mark.parametrize(
    ("tac", "illegal"),
    [
        (_LAT95, 95.0),
        (_LON190, 190.0),
    ],
)
def test_bug_2026_11_02_out_of_range_coords_must_not_encode(
    tac: str, illegal: float
) -> None:
    """Convert must fail closed or omit illegal latitudes/longitudes from geometry."""
    result = convert(tac, product="SIGMET", profile="annex3", iwxxm_version="2025-2")
    lists = _pos_lists(result.xml or "")
    flat = [value for block in lists for value in _coords(block)]
    assert illegal not in flat, f"illegal coordinate {illegal} present in {lists!r}"
    if result.ok and lists:
        for value in flat:
            # lat/lon interleaved; reject any absolute value that cannot be a lon either
            # when clearly the illegal sentinel survived.
            assert abs(value) <= 180.0
