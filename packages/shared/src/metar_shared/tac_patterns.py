"""Shared TAC token regex helpers [Corpus: system-spec] [Corpus: product §F12].

Used by ``tac-validate``, ``tac2iwxxm``, and related packages so station / AHL
shapes stay consistent without package-boundary imports between convert and lint.
"""

from __future__ import annotations

import re
from typing import Final

from metar_shared.models.tac_tokens import AhlHeadingParts, StationIcao

# Letter-first location indicator; digits allowed (US METAR e.g. K10U).
STATION_ICAO_TOKEN: Final[re.Pattern[str]] = re.compile(r"\b[A-Z][A-Z0-9]{3}\b")
STATION_ICAO_FULLMATCH: Final[re.Pattern[str]] = re.compile(r"^[A-Z][A-Z0-9]{3}$")

# WMO AHL heading: TTAAii CCCC YYGGgg [BBB]
# BBB is 1-3 letters when present (lint detectors use exactly 3; convert allows 1-3).
AHL_HEADING_LINE: Final[re.Pattern[str]] = re.compile(
    r"^[A-Z]{2}[A-Z]{2}\d{2}\s+[A-Z]{4}\s+\d{6}(?:\s+[A-Z]{1,3})?\s*$"
)
AHL_HEADING_LINE_BBB3: Final[re.Pattern[str]] = re.compile(
    r"^[A-Z]{2}[A-Z]{2}\d{2}\s+[A-Z]{4}\s+\d{6}(?:\s+[A-Z]{3})?\s*$"
)
_AHL_PARTS: Final[re.Pattern[str]] = re.compile(
    r"^(?P<ttaaii>[A-Z]{2}[A-Z]{2}\d{2})\s+"
    r"(?P<cccc>[A-Z]{4})\s+"
    r"(?P<yygggg>\d{6})"
    r"(?:\s+(?P<bbb>[A-Z]{1,3}))?\s*$"
)


def is_station_icao(token: str) -> bool:
    """
    Return True when ``token`` is a letter-first four-character station id.

    Parameters
    ----------
    token : str
        Candidate token (case-insensitive).

    Returns
    -------
    bool
        True when the upper-cased token matches ``STATION_ICAO_FULLMATCH``.
    """
    return STATION_ICAO_FULLMATCH.fullmatch(token.strip().upper()) is not None


def parse_station_icao(token: str) -> StationIcao:
    """
    Parse a station ICAO token into a typed model.

    Parameters
    ----------
    token : str
        Candidate station id.

    Returns
    -------
    StationIcao
        Normalized upper-case station.

    Raises
    ------
    ValueError
        When ``token`` is not a valid letter-first ICAO.
    """
    return StationIcao(token)


def is_ahl_heading_line(line: str, *, require_bbb3: bool = False) -> bool:
    """
    Return True when ``line`` matches a WMO AHL heading shape.

    Parameters
    ----------
    line : str
        Single line (leading/trailing whitespace ignored).
    require_bbb3 : bool, optional
        When True, optional BBB must be exactly three letters (lint window shape).
        By default False.

    Returns
    -------
    bool
        True when the stripped upper-cased line matches the AHL pattern.
    """
    stripped = line.strip("\n").strip("\r").strip().upper()
    pattern = AHL_HEADING_LINE_BBB3 if require_bbb3 else AHL_HEADING_LINE
    return pattern.fullmatch(stripped) is not None


def parse_ahl_heading_line(line: str) -> AhlHeadingParts:
    """
    Parse a WMO AHL heading line into typed parts.

    Parameters
    ----------
    line : str
        Single heading line.

    Returns
    -------
    AhlHeadingParts
        Normalized heading parts.

    Raises
    ------
    ValueError
        When ``line`` is not a valid AHL heading.
    """
    stripped = line.strip("\n").strip("\r").strip().upper()
    match = _AHL_PARTS.fullmatch(stripped)
    if match is None:
        msg = f"invalid AHL heading line: {line!r}"
        raise ValueError(msg)
    return AhlHeadingParts(
        ttaaii=match.group("ttaaii"),
        cccc=match.group("cccc"),
        yygggg=match.group("yygggg"),
        bbb=match.group("bbb"),
    )


def replace_ahl_heading_mapping(
    values: dict[str, object],
    *,
    key: str,
    parts: AhlHeadingParts,
) -> dict[str, object]:
    """
    Return a shallow copy of ``values`` with ``key`` set to serialized AHL parts.

    Owned nested-dict helper for callers that still pass mapping bags until fully
    migrated to models.

    Parameters
    ----------
    values : dict[str, object]
        Existing mapping.
    key : str
        Key to set.
    parts : AhlHeadingParts
        Typed heading.

    Returns
    -------
    dict[str, object]
        New mapping (does not mutate ``values``).
    """
    out = dict(values)
    payload: dict[str, object] = {
        "ttaaii": parts.ttaaii,
        "cccc": parts.cccc,
        "yygggg": parts.yygggg,
    }
    if parts.bbb is not None:
        payload["bbb"] = parts.bbb
    out[key] = payload
    return out


__all__ = [
    "AHL_HEADING_LINE",
    "AHL_HEADING_LINE_BBB3",
    "STATION_ICAO_FULLMATCH",
    "STATION_ICAO_TOKEN",
    "is_ahl_heading_line",
    "is_station_icao",
    "parse_ahl_heading_line",
    "parse_station_icao",
    "replace_ahl_heading_mapping",
]
