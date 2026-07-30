"""FIR / relative-phrase horizontal geometry helpers (APAC FAQ §3.3 / EV-023).

Pure functions for clipping an injected FIR boundary ring against relative
phrases (``S OF``, ``N OF``, ``E OF``, ``W OF``, ``ENTIRE FIR``) and for
preferring explicit ``WI`` polygon TAC when both styles appear.

Full Tropical-cyclone SIGMET product quality remains on issue #738 — these
helpers are the shared F6 deepen surface coordinated with that backlog.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal, Sequence

_WI_BLOCK = re.compile(
    r"\bWI\b(?P<body>.*?)(?=\bSFC/|\bTOP\b|\bMOV\b|\bSTNR\b|\bNC\b|\bWKN\b|\bINTSF\b|"
    r"\bS OF\b|\bN OF\b|\bE OF\b|\bW OF\b|\bENTIRE\b|=|$)",
    re.IGNORECASE | re.DOTALL,
)
_POINT = re.compile(
    r"\b(?P<lat_hemi>[NS])(?P<lat_deg>\d{2})(?P<lat_min>\d{2})(?:\d{2})?\s+"
    r"(?P<lon_hemi>[EW])(?P<lon_deg>\d{3})(?P<lon_min>\d{2})(?:\d{2})?\b",
    re.IGNORECASE,
)
_ENTIRE_FIR = re.compile(r"\bENTIRE\s+FIR\b", re.IGNORECASE)
# Half-plane tokens: S OF N54, N OF S50, E OF W012, W OF E010
_HALF = re.compile(
    r"\b(?P<side>N|S|E|W)\s+OF\s+"
    r"(?:(?P<lat_hemi>[NS])(?P<lat>\d{1,2}(?:\.\d+)?)|"
    r"(?P<lon_hemi>[EW])(?P<lon>\d{1,3}(?:\.\d+)?))\b",
    re.IGNORECASE,
)

GeometryKind = Literal["wi_polygon", "relative", "entire_fir", "none"]
KeepSide = Literal["north", "south", "east", "west"]


@dataclass(frozen=True)
class RelativeConstraint:
    """One axis-aligned half-plane retained after a relative phrase."""

    axis: Literal["lat", "lon"]
    value: float
    keep: KeepSide


@dataclass(frozen=True)
class RelativeGeometryPhrase:
    """Parsed relative / ENTIRE FIR geometry intent from TAC body text."""

    kind: Literal["relative", "entire_fir"]
    constraints: tuple[RelativeConstraint, ...]


def _point_lat_lon(match: re.Match[str]) -> tuple[float, float]:
    lat = int(match.group("lat_deg")) + int(match.group("lat_min")) / 60.0
    lon = int(match.group("lon_deg")) + int(match.group("lon_min")) / 60.0
    if match.group("lat_hemi").upper() == "S":
        lat = -lat
    if match.group("lon_hemi").upper() == "W":
        lon = -lon
    return lat, lon


def _wi_points(body: str) -> list[tuple[float, float]]:
    wi = _WI_BLOCK.search(body)
    if wi is None:
        return []
    pts = [_point_lat_lon(m) for m in _POINT.finditer(wi.group("body"))]
    return pts


def select_horizontal_geometry_kind(body: str) -> GeometryKind:
    """
    Choose horizontal geometry source for a SIGMET/AIRMET body (FAQ §3.3).

    Prefers explicit ``WI`` polygons over relative FIR phrases when both appear.

    Parameters
    ----------
    body : str
        Hazard body text (with or without SIGMET header).

    Returns
    -------
    GeometryKind
        ``wi_polygon``, ``relative``, ``entire_fir``, or ``none``.
    """
    if len(_wi_points(body)) >= 3:
        return "wi_polygon"
    if _ENTIRE_FIR.search(body):
        return "entire_fir"
    if _HALF.search(body):
        return "relative"
    return "none"


def _constraint_from_half(match: re.Match[str]) -> RelativeConstraint:
    side = match.group("side").upper()
    if match.group("lat") is not None:
        value = float(match.group("lat"))
        if match.group("lat_hemi").upper() == "S":
            value = -value
        keep: KeepSide
        if side == "N":
            keep = "north"
        elif side == "S":
            keep = "south"
        else:
            raise ValueError(f"lat half-plane cannot use side {side}")
        return RelativeConstraint(axis="lat", value=value, keep=keep)

    value = float(match.group("lon"))
    if match.group("lon_hemi").upper() == "W":
        value = -value
    if side == "E":
        keep = "east"
    elif side == "W":
        keep = "west"
    else:
        raise ValueError(f"lon half-plane cannot use side {side}")
    return RelativeConstraint(axis="lon", value=value, keep=keep)


def parse_relative_geometry_phrase(body: str) -> RelativeGeometryPhrase | None:
    """
    Parse ``ENTIRE FIR`` or ``S/N/E/W OF …`` relative geometry phrases.

    Parameters
    ----------
    body : str
        TAC body fragment.

    Returns
    -------
    RelativeGeometryPhrase or None
        Parsed phrase, or ``None`` when no relative/ENTIRE FIR cue is present.
        ``WI``-only bodies return ``None`` (use :func:`select_horizontal_geometry_kind`).
    """
    if _ENTIRE_FIR.search(body):
        return RelativeGeometryPhrase(kind="entire_fir", constraints=())
    constraints = tuple(_constraint_from_half(m) for m in _HALF.finditer(body))
    if not constraints:
        return None
    return RelativeGeometryPhrase(kind="relative", constraints=constraints)


def _inside(point: tuple[float, float], constraint: RelativeConstraint) -> bool:
    lat, lon = point
    if constraint.axis == "lat":
        if constraint.keep == "north":
            return lat >= constraint.value - 1e-12
        return lat <= constraint.value + 1e-12
    if constraint.keep == "east":
        return lon >= constraint.value - 1e-12
    return lon <= constraint.value + 1e-12


def _intersect(
    a: tuple[float, float],
    b: tuple[float, float],
    constraint: RelativeConstraint,
) -> tuple[float, float]:
    """Intersect segment AB with the constraint boundary line."""
    ax, ay = a  # lat, lon
    bx, by = b
    if constraint.axis == "lat":
        # horizontal line lat = value
        if abs(bx - ax) < 1e-15:
            return (constraint.value, ay)
        t = (constraint.value - ax) / (bx - ax)
        return (constraint.value, ay + t * (by - ay))
    if abs(by - ay) < 1e-15:
        return (ax, constraint.value)
    t = (constraint.value - ay) / (by - ay)
    return (ax + t * (bx - ax), constraint.value)


def _clip_ring_one(
    ring: Sequence[tuple[float, float]],
    constraint: RelativeConstraint,
) -> list[tuple[float, float]]:
    """Sutherland–Hodgman clip of a closed ring against one half-plane."""
    if not ring:
        return []
    pts = list(ring)
    if pts[0] != pts[-1]:
        pts.append(pts[0])
    output: list[tuple[float, float]] = []
    for i in range(len(pts) - 1):
        cur = pts[i]
        nxt = pts[i + 1]
        cur_in = _inside(cur, constraint)
        nxt_in = _inside(nxt, constraint)
        if cur_in and nxt_in:
            output.append(nxt)
        elif cur_in and not nxt_in:
            output.append(_intersect(cur, nxt, constraint))
        elif not cur_in and nxt_in:
            output.append(_intersect(cur, nxt, constraint))
            output.append(nxt)
    if not output:
        return []
    if output[0] != output[-1]:
        output.append(output[0])
    return output


def close_ring(points: Sequence[tuple[float, float]]) -> list[tuple[float, float]]:
    """
    Return a closed ring (first point repeated at end).

    Parameters
    ----------
    points : sequence of (lat, lon)
        Open or closed ring.

    Returns
    -------
    list of (lat, lon)
        Closed ring, or empty when fewer than three distinct vertices.
    """
    if len(points) < 3:
        return []
    out = list(points)
    if out[0] != out[-1]:
        out.append(out[0])
    if len(out) < 4:
        return []
    return out


def ring_to_pos_list(points: Sequence[tuple[float, float]], *, precision: int = 4) -> str:
    """
    Format a ring as a GML ``posList`` string (lat lon pairs).

    Parameters
    ----------
    points : sequence of (lat, lon)
        Ring vertices (will be closed if needed).
    precision : int, optional
        Decimal places (default 4).

    Returns
    -------
    str
        Space-separated coordinates.
    """
    ring = close_ring(points)
    return " ".join(f"{lat:.{precision}f} {lon:.{precision}f}" for lat, lon in ring)


def clip_ring_to_relative(
    fir_boundary: Sequence[tuple[float, float]],
    phrase: RelativeGeometryPhrase,
) -> list[tuple[float, float]]:
    """
    Clip an FIR boundary ring to the half-planes of a relative phrase.

    Parameters
    ----------
    fir_boundary : sequence of (lat, lon)
        Closed or open FIR polygon ring (injected; not looked up by ICAO).
    phrase : RelativeGeometryPhrase
        Parsed relative / ENTIRE FIR phrase.

    Returns
    -------
    list of (lat, lon)
        Closed clipped ring. Empty when the intersection is empty.
    """
    ring = close_ring(fir_boundary)
    if not ring:
        return []
    if phrase.kind == "entire_fir":
        return ring
    for constraint in phrase.constraints:
        ring = _clip_ring_one(ring, constraint)
        if not ring:
            return []
    return ring


def resolve_fir_relative_polygon(
    body: str,
    *,
    fir_boundary: Sequence[tuple[float, float]] | None,
) -> dict[str, Any] | None:
    """
    Resolve hazard horizontal geometry from TAC body + optional FIR ring.

    Prefers ``WI`` polygons. Relative / ``ENTIRE FIR`` phrases require a
    non-empty ``fir_boundary``; otherwise returns ``None`` (no invented box).

    Parameters
    ----------
    body : str
        SIGMET/AIRMET body text.
    fir_boundary : sequence of (lat, lon) or None
        Injected FIR polygon for clipping / ENTIRE FIR.

    Returns
    -------
    dict or None
        ``{"kind": "polygon", "pos_list": "..."}`` or ``None``.
    """
    kind = select_horizontal_geometry_kind(body)
    if kind == "wi_polygon":
        pts = _wi_points(body)
        ring = close_ring(pts)
        if not ring:
            return None
        return {"kind": "polygon", "pos_list": ring_to_pos_list(ring)}

    if kind in {"relative", "entire_fir"}:
        if not fir_boundary:
            return None
        phrase = parse_relative_geometry_phrase(body)
        if phrase is None:
            return None
        clipped = clip_ring_to_relative(fir_boundary, phrase)
        if len(clipped) < 4:
            return None
        return {"kind": "polygon", "pos_list": ring_to_pos_list(clipped)}

    return None
