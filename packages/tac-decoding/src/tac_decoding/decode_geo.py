"""Coordinate and convective-area helpers.

[Corpus: product §F9]
"""

from __future__ import annotations

from tac_decoding.decode_patterns import *


def _in_convective_area(seen: dict[str, int]) -> bool:
    """True on the convective area line, after validity and before ``FROM``.

    Parameters
    ----------
    seen : dict[str, int]
        Tokens already accepted while decoding this report.

    Returns
    -------
    bool
        Whether a state or lake abbreviation is part of the area line.
    """
    return bool(
        seen.get("convective")
        and seen.get("until")
        and not seen.get("from_line")
        and not seen.get("area")
        and not seen.get("tops")
    )


def _coord_token(token: str) -> str:
    """Drop a polygon hyphen glued to a latitude or longitude.

    Parameters
    ----------
    token : str
        One coordinate group, with or without a trailing hyphen.

    Returns
    -------
    str
        The coordinate without a glued hyphen.
    """
    bare = token
    if len(bare) > 1 and bare.endswith("-"):
        candidate = bare[:-1]
        if _SIG_LAT.match(candidate) or _SIG_LON.match(candidate) or _SIG_LATLON.match(candidate):
            bare = candidate
    if len(bare) > 1 and bare.startswith("-"):
        candidate = bare[1:]
        if _SIG_LAT.match(candidate) or _SIG_LON.match(candidate) or _SIG_LATLON.match(candidate):
            bare = candidate
    return bare


def _boundary_points(token: str) -> str | None:
    """Explain a navaid boundary such as ``50WSW`` or ``MSS-30S``.

    Parameters
    ----------
    token : str
        One whitespace-delimited group.

    Returns
    -------
    str | None
        A plain-language boundary, or None when the group is not one.
    """
    parts = token.split("-")
    rendered: list[str] = []
    saw_distance = False
    for part in parts:
        match = _BOUNDARY_PART.match(part)
        if match is None:
            return None
        dist = match.group("dist")
        direction = match.group("dir")
        fix = match.group("fix")
        if dist and direction:
            saw_distance = True
            place = f" of {fix}" if fix else ""
            rendered.append(f"{int(dist)} nm {_SIG_DIR_NAME[direction]}{place}")
        elif fix and not dist:
            rendered.append(fix)
        else:
            return None
    if not saw_distance:
        return None
    return "Boundary " + " to ".join(rendered)


def _lat_lon_phrase(lat: str, lon: str) -> str | None:
    """Plain language for one glued latitude and longitude.

    Parameters
    ----------
    lat : str
        Latitude token such as ``N1346``.
    lon : str
        Longitude token such as ``W09652``.

    Returns
    -------
    str | None
        Both coordinates, or None when either half does not match.
    """
    lat_match = _SIG_LAT.match(lat)
    lon_match = _SIG_LON.match(lon)
    if lat_match is None or lon_match is None:
        return None
    lat_hemi = "North" if lat_match.group("hemi") == "N" else "South"
    lon_hemi = "East" if lon_match.group("hemi") == "E" else "West"
    lat_min = lat_match.group("min") or "00"
    lon_min = lon_match.group("min") or "00"
    return (
        f"Latitude {int(lat_match.group('deg'))}°{lat_min}' {lat_hemi[0]}, "
        f"longitude {int(lon_match.group('deg'))}°{lon_min}' {lon_hemi[0]}"
    )
