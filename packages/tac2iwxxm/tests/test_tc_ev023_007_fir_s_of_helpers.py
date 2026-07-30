"""TC-EV023-007 — SIGMET FIR / "S OF" polygon helpers (S030 / EV-023 T6.1).

Unit tests for pure FIR-boundary intersection helpers (APAC FAQ §3.3).
Prefer explicit WI polygon TAC over FIR-boundary-only when both appear.
Full Tropical-cyclone SIGMET product quality remains [#738](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/738).
"""

from __future__ import annotations

import re

import pytest

# Synthetic rectangular FIR (closed ring) used as injected boundary — not a live FIR DB.
# Rough SHANLON-style box: lat 50–58 N, lon 16–8 W.
_FIR_RING: list[tuple[float, float]] = [
    (50.0, -16.0),
    (50.0, -8.0),
    (58.0, -8.0),
    (58.0, -16.0),
    (50.0, -16.0),
]

_WI_BODY = (
    "YUDD SHANLON FIR/UIR OBSC TS FCST WI N5400 W01200 - N5400 W00800 - N5000 W00800 - N5000 W01200 TOP FL390 WKN"
)
_RELATIVE_BODY = "YUDD SHANLON FIR/UIR OBSC TS FCST S OF N54 AND E OF W012 TOP FL390 MOV E 20KT WKN"
_BOTH_BODY = (
    "YUDD SHANLON FIR/UIR OBSC TS FCST WI N5400 W01200 - N5400 W00800 - "
    "N5000 W00800 - N5000 W01200 S OF N54 AND E OF W012 TOP FL390 WKN"
)
_ENTIRE_BODY = "YUDD SHANLON FIR/UIR OBSC TS FCST ENTIRE FIR TOP FL390 STNR WKN"


def _parse_pos_list(pos_list: str) -> list[tuple[float, float]]:
    nums = [float(x) for x in pos_list.split()]
    assert len(nums) % 2 == 0 and len(nums) >= 6
    return list(zip(nums[0::2], nums[1::2], strict=True))


def test_tc_ev023_007_select_prefers_wi_polygon_over_relative() -> None:
    """FAQ §3.3 — prefer polygon TAC when WI and relative phrases both appear."""
    from tac2iwxxm.products.fir_geometry import select_horizontal_geometry_kind

    assert select_horizontal_geometry_kind(_BOTH_BODY) == "wi_polygon"
    assert select_horizontal_geometry_kind(_WI_BODY) == "wi_polygon"
    assert select_horizontal_geometry_kind(_RELATIVE_BODY) == "relative"
    assert select_horizontal_geometry_kind(_ENTIRE_BODY) == "entire_fir"
    assert select_horizontal_geometry_kind("YUDD FIR OBSC TS FCST TOP FL100=") == "none"


def test_tc_ev023_007_parse_s_of_and_e_of_constraints() -> None:
    """Parse WMO A6-1a-TS style ``S OF N54 AND E OF W012`` into half-plane constraints."""
    from tac2iwxxm.products.fir_geometry import parse_relative_geometry_phrase

    phrase = parse_relative_geometry_phrase(_RELATIVE_BODY)
    assert phrase is not None
    assert phrase.kind == "relative"
    assert len(phrase.constraints) == 2
    by_axis = {c.axis: c for c in phrase.constraints}
    assert by_axis["lat"].value == pytest.approx(54.0)
    assert by_axis["lat"].keep == "south"
    assert by_axis["lon"].value == pytest.approx(-12.0)
    assert by_axis["lon"].keep == "east"


def test_tc_ev023_007_parse_entire_fir() -> None:
    from tac2iwxxm.products.fir_geometry import parse_relative_geometry_phrase

    phrase = parse_relative_geometry_phrase(_ENTIRE_BODY)
    assert phrase is not None
    assert phrase.kind == "entire_fir"
    assert phrase.constraints == ()


def test_tc_ev023_007_clip_fir_to_s_of_and_e_of() -> None:
    """Relative phrase closes against injected FIR boundary (not a synthetic free box)."""
    from tac2iwxxm.products.fir_geometry import (
        clip_ring_to_relative,
        parse_relative_geometry_phrase,
        ring_to_pos_list,
    )

    phrase = parse_relative_geometry_phrase(_RELATIVE_BODY)
    assert phrase is not None
    clipped = clip_ring_to_relative(_FIR_RING, phrase)
    assert len(clipped) >= 4
    assert clipped[0] == clipped[-1]
    for lat, lon in clipped:
        assert lat <= 54.0 + 1e-9
        assert lon >= -12.0 - 1e-9
    # Must retain the SE corner of the FIR (inside both half-planes).
    assert any(abs(lat - 50.0) < 1e-6 and abs(lon - (-8.0)) < 1e-6 for lat, lon in clipped)
    # Must not retain the NW corner (outside both half-planes).
    assert not any(abs(lat - 58.0) < 1e-6 and abs(lon - (-16.0)) < 1e-6 for lat, lon in clipped)
    pos = ring_to_pos_list(clipped)
    assert re.fullmatch(r"(-?\d+(?:\.\d+)?\s+)+(-?\d+(?:\.\d+)?)", pos)
    ring = _parse_pos_list(pos)
    assert ring[0] == ring[-1]


def test_tc_ev023_007_entire_fir_returns_closed_boundary() -> None:
    from tac2iwxxm.products.fir_geometry import resolve_fir_relative_polygon

    geom = resolve_fir_relative_polygon(_ENTIRE_BODY, fir_boundary=_FIR_RING)
    assert geom is not None
    assert geom["kind"] == "polygon"
    ring = _parse_pos_list(geom["pos_list"])
    assert ring[0] == ring[-1]
    # Same vertices as FIR (order may rotate; compare as sets of points).
    assert {(round(lat, 4), round(lon, 4)) for lat, lon in ring} == {
        (round(lat, 4), round(lon, 4)) for lat, lon in _FIR_RING
    }


def test_tc_ev023_007_relative_without_fir_boundary_returns_none() -> None:
    """Helpers must not invent a planet-scale box when FIR geometry is absent (#738 coord)."""
    from tac2iwxxm.products.fir_geometry import resolve_fir_relative_polygon

    assert resolve_fir_relative_polygon(_RELATIVE_BODY, fir_boundary=None) is None
    assert resolve_fir_relative_polygon(_RELATIVE_BODY, fir_boundary=[]) is None


def test_tc_ev023_007_resolve_prefers_wi_even_with_fir_boundary() -> None:
    from tac2iwxxm.products.fir_geometry import resolve_fir_relative_polygon

    geom = resolve_fir_relative_polygon(_BOTH_BODY, fir_boundary=_FIR_RING)
    assert geom is not None
    assert geom["kind"] == "polygon"
    ring = _parse_pos_list(geom["pos_list"])
    # WI vertices (degrees) — not the full FIR NW corner.
    assert any(abs(lat - 54.0) < 0.02 and abs(lon - (-12.0)) < 0.02 for lat, lon in ring)
    assert not any(abs(lat - 58.0) < 1e-6 and abs(lon - (-16.0)) < 1e-6 for lat, lon in ring)


def test_tc_ev023_007_single_axis_constraints() -> None:
    from tac2iwxxm.products.fir_geometry import (
        clip_ring_to_relative,
        parse_relative_geometry_phrase,
    )

    north = parse_relative_geometry_phrase("N OF S50 TOP FL100")
    assert north is not None
    assert north.kind == "relative"
    assert len(north.constraints) == 1
    assert north.constraints[0].axis == "lat"
    assert north.constraints[0].value == pytest.approx(-50.0)
    assert north.constraints[0].keep == "north"

    west = parse_relative_geometry_phrase("W OF E010 TOP FL100")
    assert west is not None
    clipped = clip_ring_to_relative(
        [(0.0, 0.0), (0.0, 20.0), (10.0, 20.0), (10.0, 0.0), (0.0, 0.0)],
        west,
    )
    for _lat, lon in clipped:
        assert lon <= 10.0 + 1e-9


def test_tc_ev023_007_wi_southern_western_hemisphere_points() -> None:
    """WI points south/west of equator/prime meridian keep signed lat/lon."""
    from tac2iwxxm.products.fir_geometry import resolve_fir_relative_polygon

    body = "YUDD FIR OBSC TS FCST WI S1000 W02000 - S1000 W01000 - S2000 W01000 - S2000 W02000 TOP FL100"
    geom = resolve_fir_relative_polygon(body, fir_boundary=None)
    assert geom is not None
    ring = _parse_pos_list(geom["pos_list"])
    assert any(lat < 0 and lon < 0 for lat, lon in ring)


def test_tc_ev023_007_parse_none_and_invalid_half_plane_sides() -> None:
    from tac2iwxxm.products import fir_geometry as fg
    from tac2iwxxm.products.fir_geometry import (
        _constraint_from_half,
        parse_relative_geometry_phrase,
    )

    assert parse_relative_geometry_phrase("YUDD FIR OBSC TS FCST TOP FL100=") is None

    bad_lat = fg._HALF.search("E OF N54 TOP")
    assert bad_lat is not None
    with pytest.raises(ValueError, match="lat half-plane"):
        _constraint_from_half(bad_lat)

    bad_lon = fg._HALF.search("N OF W012 TOP")
    assert bad_lon is not None
    with pytest.raises(ValueError, match="lon half-plane"):
        _constraint_from_half(bad_lon)


def test_tc_ev023_007_close_ring_and_clip_edge_cases() -> None:
    from tac2iwxxm.products.fir_geometry import (
        RelativeConstraint,
        RelativeGeometryPhrase,
        _clip_ring_one,
        _intersect,
        clip_ring_to_relative,
        close_ring,
    )

    assert close_ring([]) == []
    assert close_ring([(0.0, 0.0), (1.0, 0.0)]) == []
    # Three identical vertices → closed length < 4 after dedupe path
    assert close_ring([(1.0, 1.0), (1.0, 1.0), (1.0, 1.0)]) == []

    open_box = [(0.0, 0.0), (0.0, 10.0), (10.0, 10.0), (10.0, 0.0)]
    closed = close_ring(open_box)
    assert closed[0] == closed[-1]

    assert _clip_ring_one([], RelativeConstraint("lat", 5.0, "north")) == []

    # Vertical segment (same lon) + lat constraint hits vertical intersect branch
    a, b = (0.0, 5.0), (10.0, 5.0)
    assert _intersect(a, b, RelativeConstraint("lat", 4.0, "south"))[0] == pytest.approx(4.0)

    # Horizontal segment (same lat) + lon constraint
    c, d = (5.0, 0.0), (5.0, 10.0)
    assert _intersect(c, d, RelativeConstraint("lon", 3.0, "east"))[1] == pytest.approx(3.0)

    # Clip that empties the ring (keep north of 100 on a box below 10)
    phrase = RelativeGeometryPhrase(
        kind="relative",
        constraints=(RelativeConstraint("lat", 100.0, "north"),),
    )
    assert clip_ring_to_relative(open_box, phrase) == []


def test_tc_ev023_007_resolve_none_and_degenerate_wi() -> None:
    from tac2iwxxm.products.fir_geometry import resolve_fir_relative_polygon

    assert resolve_fir_relative_polygon("YUDD FIR OBSC TS FCST TOP FL100=", fir_boundary=_FIR_RING) is None

    # Two WI points → kind none / not wi_polygon
    two_pts = "YUDD FIR OBSC TS FCST WI N5400 W01200 - N5000 W00800 TOP FL100"
    assert resolve_fir_relative_polygon(two_pts, fir_boundary=_FIR_RING) is None

    # Relative with FIR that clips to empty
    empty = resolve_fir_relative_polygon(
        "S OF N10 TOP FL100",
        fir_boundary=[(50.0, 0.0), (50.0, 1.0), (51.0, 1.0), (51.0, 0.0), (50.0, 0.0)],
    )
    assert empty is None
