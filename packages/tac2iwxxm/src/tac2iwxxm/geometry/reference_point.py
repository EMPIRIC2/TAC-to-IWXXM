"""VOR / airport reference geometry for US SIGMET TAC (EV-080 / #919 M9)."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

_CARDINAL_BEARING_DEG: dict[str, float] = {
    "N": 0.0,
    "NNE": 22.5,
    "NE": 45.0,
    "ENE": 67.5,
    "E": 90.0,
    "ESE": 112.5,
    "SE": 135.0,
    "SSE": 157.5,
    "S": 180.0,
    "SSW": 202.5,
    "SW": 225.0,
    "WSW": 247.5,
    "W": 270.0,
    "WNW": 292.5,
    "NW": 315.0,
    "NNW": 337.5,
}

_CARDINAL_DIRS = "|".join(sorted(_CARDINAL_BEARING_DEG.keys(), key=len, reverse=True))
_SEGMENT = re.compile(
    rf"^(?P<dist>\d{{1,3}})(?P<dir>{_CARDINAL_DIRS})\s+(?P<vor>[A-Z]{{3}})$",
    re.IGNORECASE,
)
_BARE_VOR = re.compile(r"^(?P<vor>[A-Z]{3})$", re.IGNORECASE)
_FROM_CHAIN = re.compile(
    r"\bFROM\s+(?P<chain>[A-Z0-9/\s-]+?)"
    r"(?=\s+AREA\b|\s+MOV\b|\s+TOP\b|\s+TOPS\b|\s+STNR\b|\s+NC\b|\s+WKN\b|\s+INTSF\b"
    r"|\s+MOD\b|\s+BTN\b|\s+CONDS\b|\s+OTLK\b|\s+FRZLVL\.\.\.|=|$)",
    re.IGNORECASE,
)

_EARTH_RADIUS_NM = 3440.065


class UnknownVOR(KeyError):
    """Raised when a VOR identifier is absent from the bundled reference table."""


def _vor_table_path() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "vor_reference_points.json"


def load_vor_reference_points() -> dict[str, dict[str, Any]]:
    """Load bundled VOR reference coordinates."""
    data = json.loads(_vor_table_path().read_text(encoding="utf-8"))
    return {k.upper(): v for k, v in data.get("points", {}).items()}


def resolve_vor(vor_id: str, table: dict[str, dict[str, Any]] | None = None) -> tuple[float, float]:
    """
    Resolve a 3-letter VOR id to ``(lat, lon)`` in degrees.

    Parameters
    ----------
    vor_id :
        Three-letter VOR/VORTAC identifier.
    table :
        Optional override table for tests.

    Returns
    -------
    tuple[float, float]
        Latitude and longitude in decimal degrees (north/east positive).

    Raises
    ------
    UnknownVOR
        When ``vor_id`` is not present in the reference table.
    """
    lookup = table if table is not None else load_vor_reference_points()
    key = vor_id.upper()
    row = lookup.get(key)
    if row is None:
        raise UnknownVOR(key)
    return float(row["lat"]), float(row["lon"])


def offset_nm(lat: float, lon: float, distance_nm: float, cardinal: str) -> tuple[float, float]:
    """
    Compute a point ``distance_nm`` along ``cardinal`` from ``(lat, lon)``.

    Uses a spherical Earth model (aviation NM radius).
    """
    bearing_deg = _CARDINAL_BEARING_DEG.get(cardinal.upper())
    if bearing_deg is None:
        raise ValueError(f"unsupported cardinal: {cardinal}")
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)
    brng = math.radians(bearing_deg)
    angular = distance_nm / _EARTH_RADIUS_NM
    lat2 = math.asin(math.sin(lat1) * math.cos(angular) + math.cos(lat1) * math.sin(angular) * math.cos(brng))
    lon2 = lon1 + math.atan2(
        math.sin(brng) * math.sin(angular) * math.cos(lat1),
        math.cos(angular) - math.sin(lat1) * math.sin(lat2),
    )
    return math.degrees(lat2), math.degrees(lon2)


class ReferencePointGeometryParser:
    """Parse US SIGMET ``FROM`` VOR reference chains into geometry IR."""

    def __init__(self, vor_table: dict[str, dict[str, Any]] | None = None) -> None:
        self._vor_table = vor_table

    def parse_from_body(self, body: str) -> dict[str, Any] | None:
        """Return geometry IR dict when a ``FROM`` chain is present, else ``None``."""
        match = _FROM_CHAIN.search(body)
        if match is None:
            return None
        chain = match.group("chain").strip()
        if not chain:
            return None
        if re.search(r"\s+TO\s+", chain, flags=re.IGNORECASE):
            segments = [part.strip() for part in re.split(r"\s+TO\s+", chain, flags=re.IGNORECASE) if part.strip()]
        else:
            segments = [part.strip() for part in chain.split("-") if part.strip()]
        vertices: list[tuple[float, float]] = []
        refs: list[dict[str, Any]] = []
        for segment in segments:
            seg_match = _SEGMENT.match(segment)
            bare_match = None if seg_match is not None else _BARE_VOR.match(segment)
            if seg_match is not None:
                dist = int(seg_match.group("dist"))
                direction = seg_match.group("dir").upper()
                vor_id = seg_match.group("vor").upper()
                base_lat, base_lon = resolve_vor(vor_id, self._vor_table)
                lat, lon = offset_nm(base_lat, base_lon, dist, direction)
                refs.append({"vor": vor_id, "nm": dist, "dir": direction})
            elif bare_match is not None:
                vor_id = bare_match.group("vor").upper()
                lat, lon = resolve_vor(vor_id, self._vor_table)
                refs.append({"vor": vor_id, "nm": 0, "dir": "AT"})
            else:
                raise ValueError(f"unable to parse VOR reference segment: {segment!r}")
            vertices.append((lat, lon))
        if not vertices:
            return None
        if len(vertices) == 1:
            lat, lon = vertices[0]
            return {
                "kind": "point",
                "lat": lat,
                "lon": lon,
                "reference_points": refs,
            }
        if vertices[0] != vertices[-1]:
            vertices.append(vertices[0])
        pos_list = " ".join(f"{lat:.4f} {lon:.4f}" for lat, lon in vertices)
        return {
            "kind": "polygon",
            "pos_list": pos_list,
            "reference_points": refs,
        }


def parse_vor_reference_geometry(body: str) -> dict[str, Any] | None:
    """Convenience wrapper using the default bundled VOR table."""
    return ReferencePointGeometryParser().parse_from_body(body)
