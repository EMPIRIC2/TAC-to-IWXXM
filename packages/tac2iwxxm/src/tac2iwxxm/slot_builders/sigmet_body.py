"""Normalize a SIGMET body before the existing encoder.

The encoder already keeps tops, a single movement direction, intensity, and a
bare cancellation. This module only prepares the body those rules already read:
wrapped coordinates, the flight-information-region name, a compound direction,
and a remark on a cancellation.

[Corpus: product §F6] [Corpus: tests]
"""

from __future__ import annotations

import re

_DIRECTIONS: dict[str, float] = {
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
_DIR_TOKEN = "NNE|ENE|ESE|SSE|SSW|WSW|WNW|NNW|NE|SE|SW|NW|N|E|S|W"
_COMPOUND_MOVEMENT = re.compile(
    rf"\bMOV\s+(?P<left>{_DIR_TOKEN})\s*-\s*(?P<right>{_DIR_TOKEN})\b",
    re.IGNORECASE,
)
_FIR_LABEL = re.compile(r"\b(?P<kind>FIR(?:/UIR)?)\b")
_REMARK_TOKEN = re.compile(r"(?<![A-Z0-9])RMK(?![A-Z0-9])")
_NAME_WORD_LIMIT = 4
_HALF_CIRCLE = 180.0
_FULL_CIRCLE = 360.0
_LATITUDE_DIGITS_MIN = 4
_LATITUDE_DIGITS_MAX = 6
_LONGITUDE_DIGITS_MIN = 5
_LONGITUDE_DIGITS_MAX = 7
_SHORT_WORD = 2


def direction_midpoint(left: float, right: float) -> float:
    """
    Return the shorter-arc midpoint between two bearings.

    Parameters
    ----------
    left : float
        First bearing in degrees.
    right : float
        Second bearing in degrees.

    Returns
    -------
    float
        Midpoint in the range 0 to 360.
    """
    clockwise = (right - left) % _FULL_CIRCLE
    if clockwise > _HALF_CIRCLE:
        counterclockwise = _FULL_CIRCLE - clockwise
        mid = left - counterclockwise / 2.0
        if mid < 0.0:
            return mid + _FULL_CIRCLE
        return mid
    return (left + clockwise / 2.0) % _FULL_CIRCLE


def compound_movement_degrees(body: str) -> float | None:
    """
    Return degrees for a hyphenated movement such as ``W-NW``.

    A single token such as ``NW`` is left for the existing movement rule.

    Parameters
    ----------
    body : str
        SIGMET or AIRMET body text.

    Returns
    -------
    float or None
        Midpoint bearing, or ``None`` when the body has no compound group.
    """
    match = _COMPOUND_MOVEMENT.search(body)
    if match is None:
        return None
    left = _DIRECTIONS[match.group("left").upper()]
    right = _DIRECTIONS[match.group("right").upper()]
    return direction_midpoint(left, right)


def use_volcanic_ash_locations(phenomenon: str, body: str) -> bool:
    """
    Return whether the body is a volcanic-ash location list.

    Ordinary thunderstorm text uses the encoder path that already keeps tops,
    movement, and intensity.

    Parameters
    ----------
    phenomenon : str
        Phenomenon code already chosen for the report.
    body : str
        SIGMET body text.

    Returns
    -------
    bool
        True for volcanic ash, including a cloud or an eruption mention.
    """
    if phenomenon.upper() == "VA":
        return True
    upper = body.upper()
    has_cloud = "VA CLD" in upper
    has_eruption = "VA ERUPTION" in upper
    return has_cloud or has_eruption


def without_cancellation_remark(body: str) -> str:
    """
    Drop a remark from a cancellation so it is not read as the phenomenon.

    Parameters
    ----------
    body : str
        Text after the SIGMET or AIRMET header.

    Returns
    -------
    str
        Body with a cancellation remark removed, or the original text.
    """
    upper = body.upper()
    has_sigmet = "CNL SIGMET" in upper
    has_airmet = "CNL AIRMET" in upper
    if not has_sigmet and not has_airmet:
        return body
    remark = _REMARK_TOKEN.search(upper)
    if remark is None:
        return body
    return body[: remark.start()].rstrip()


def flight_information_region_name(body: str, designator: str, watch_office: str = "") -> str:
    """
    Return the named flight information region.

    The meteorological watch office and the region designator are not used as
    the name, so an aerodrome indicator is not written into the region name.

    Parameters
    ----------
    body : str
        SIGMET body text.
    designator : str
        Four-letter region indicator.
    watch_office : str
        Originating meteorological watch office, when the header has one.

    Returns
    -------
    str
        Name ending in ``FIR`` or ``FIR/UIR``, or the designator when no name is present.
    """
    compact = " ".join(body.upper().split())
    match = _FIR_LABEL.search(compact)
    if match is None:
        return designator.upper()
    stop = {designator.upper()}
    office = watch_office.upper().strip()
    if office:
        stop.add(office)
    words: list[str] = []
    for token in reversed(compact[: match.start()].split()):
        if token in stop or len(token) < _SHORT_WORD or not token.isalpha():
            break
        words.append(token)
        if len(words) >= _NAME_WORD_LIMIT:
            break
    if not words:
        return designator.upper()
    words.reverse()
    return f"{' '.join(words)} {match.group('kind')}"


def unwrap_wrapped_coordinates(text: str) -> str:
    """
    Join coordinate pairs that continue on the next line.

    Parameters
    ----------
    text : str
        SIGMET text that may still contain line breaks.

    Returns
    -------
    str
        Text with a split latitude and longitude on one line.
    """
    lines = [line.strip() for line in text.splitlines()]
    pieces: list[str] = []
    skip_next = False
    for index, current in enumerate(lines):
        if skip_next:
            skip_next = False
            continue
        nxt = lines[index + 1] if index + 1 < len(lines) else ""
        joined = _join_coordinate_lines(current, nxt) if nxt else None
        if joined is not None:
            pieces.append(joined)
            skip_next = True
            continue
        if current:
            pieces.append(current)
    return " ".join(pieces)


def is_latitude_token(token: str) -> bool:
    """
    Return whether ``token`` is a latitude such as ``N0829``.

    Parameters
    ----------
    token : str
        One whitespace-separated token, punctuation allowed.

    Returns
    -------
    bool
        True when the token is ``N`` or ``S`` plus 4 to 6 digits.
    """
    cleaned = _clean_token(token)
    if cleaned == "":
        return False
    hemisphere = cleaned[0].upper()
    if hemisphere != "N" and hemisphere != "S":
        return False
    digits = cleaned[1:]
    if not digits.isdigit():
        return False
    count = len(digits)
    return count >= _LATITUDE_DIGITS_MIN and count <= _LATITUDE_DIGITS_MAX


def is_longitude_token(token: str) -> bool:
    """
    Return whether ``token`` is a longitude such as ``W05925``.

    Parameters
    ----------
    token : str
        One whitespace-separated token, punctuation allowed.

    Returns
    -------
    bool
        True when the token is ``E`` or ``W`` plus 5 to 7 digits.
    """
    cleaned = _clean_token(token)
    if cleaned == "":
        return False
    hemisphere = cleaned[0].upper()
    if hemisphere != "E" and hemisphere != "W":
        return False
    digits = cleaned[1:]
    if not digits.isdigit():
        return False
    count = len(digits)
    return count >= _LONGITUDE_DIGITS_MIN and count <= _LONGITUDE_DIGITS_MAX


def _clean_token(token: str) -> str:
    """Drop punctuation stuck to a coordinate token."""
    return token.strip(".,;:")


def _trailing_latitude(line: str) -> str | None:
    """Return a latitude that ends the line, ignoring a glued hyphen."""
    stripped = line.rstrip()
    if stripped.endswith("-"):
        stripped = stripped[:-1].rstrip()
    if not stripped:
        return None
    token = _clean_token(stripped.split()[-1])
    if is_latitude_token(token):
        return token
    return None


def _leading_latitude(line: str) -> str | None:
    """Return a latitude that starts the line."""
    parts = line.split()
    token = _clean_token(parts[0])
    if is_latitude_token(token):
        return token
    return None


def _join_coordinate_lines(current: str, nxt: str) -> str | None:
    """Join two physical lines when they are one coordinate pair or one vertex list."""
    lat = _trailing_latitude(current)
    parts = nxt.split()
    lon_token = _clean_token(parts[0])
    if lat is not None and is_longitude_token(lon_token):
        cut = current.upper().rfind(lat.upper())
        prefix = current[:cut].rstrip(" -")
        rest = f" {' '.join(parts[1:])}" if len(parts) > 1 else ""
        pair = f"{lat} {lon_token}{rest}"
        if not prefix:
            return pair
        return f"{prefix} {pair}"
    if current.rstrip().endswith("-") and _leading_latitude(nxt) is not None:
        return f"{current.rstrip()[:-1].rstrip()} - {nxt.strip()}"
    return None
