"""Station health TAC signals: maintenance tags, formats, issue ids (F39).

Maintenance and sensor-outage tokens follow FMH-1 / tac-decoding glossary
meanings already used in the product. File formats reflect what the live
station-health store actually records (TAC bodies, bulletin wrappers, rare XML).
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Final

from src.services.station_health_types import StationRecord

# FMH-1 `$` plus common sensor-outage / problem tags from tac-decoding.
MAINTENANCE_PROBLEM_TAGS: Final[frozenset[str]] = frozenset(
    {
        "$",
        "FZRANO",
        "TSNO",
        "RVRNO",
        "PWINO",
        "PNO",
        "SLPNO",
        "VISNO",
        "CHINO",
        "FROIN",
    }
)

_TOKEN_RE = re.compile(r"[A-Z0-9$]+")
_BULLETIN_HEADING_RE = re.compile(
    r"^[A-Z]{4}\d{2}\s+[A-Z]{4}\s+\d{6}",
    re.MULTILINE,
)
_XML_RE = re.compile(r"^\s*<\?xml|\s*<[A-Za-z][\w:.-]*[\s>]", re.IGNORECASE)

VALID_FILE_FORMATS: Final[frozenset[str]] = frozenset({"tac", "bulletin", "iwxxm_xml", "unknown"})


def detect_file_format(payload: str, *, source: str | None = None) -> str:
    """
    Classify one stored payload into a file-format token.

    Parameters
    ----------
    payload : str
        Stored body (usually TAC text).
    source : str | None
        Optional writer label (unused for classification; kept for callers).

    Returns
    -------
    str
        One of ``tac``, ``bulletin``, ``iwxxm_xml``, or ``unknown``.

    """
    _ = source
    text = payload or ""
    stripped = text.lstrip()
    if not stripped:
        return "unknown"
    if _XML_RE.match(stripped):
        return "iwxxm_xml"
    if _BULLETIN_HEADING_RE.search(text):
        return "bulletin"
    return "tac"


def extract_maintenance_tags(tac_text: str) -> tuple[str, ...]:
    """
    Return maintenance / problem tags found in TAC text.

    Parameters
    ----------
    tac_text : str
        Raw TAC body.

    Returns
    -------
    tuple[str, ...]
        Sorted unique tags from ``MAINTENANCE_PROBLEM_TAGS``.

    """
    tokens = set(_TOKEN_RE.findall((tac_text or "").upper()))
    # Standalone `$` may appear with surrounding spaces; regex keeps `$`.
    found = sorted(tag for tag in MAINTENANCE_PROBLEM_TAGS if tag in tokens)
    return tuple(found)


def normalize_issue_codes(codes: list[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    """
    Normalize catalog issue ids for storage and counts.

    Parameters
    ----------
    codes : list[str] | tuple[str, ...] | None
        Raw issue codes from lint or validation.

    Returns
    -------
    tuple[str, ...]
        Deduplicated, uppercased codes (max 64).

    """
    if not codes:
        return ()
    seen: list[str] = []
    for raw in codes:
        code = str(raw or "").strip().upper()
        if not code or code in seen:
            continue
        seen.append(code)
        if len(seen) >= 64:
            break
    return tuple(seen)


def count_maintenance_tags(rows: list[StationRecord]) -> dict[str, int]:
    """
    Count maintenance / problem tag occurrences across observations.

    Parameters
    ----------
    rows : list[StationRecord]
        Windowed station records.

    Returns
    -------
    dict[str, int]
        Tag → occurrence count (reports containing the tag).

    """
    counts: Counter[str] = Counter()
    for row in rows:
        tags = row.maintenance_tags
        if not tags:
            tags = extract_maintenance_tags(row.tac_text)
        for tag in tags:
            counts[tag] += 1
    return dict(sorted(counts.items()))


def count_file_formats(rows: list[StationRecord]) -> dict[str, int]:
    """
    Count file formats across observations.

    Parameters
    ----------
    rows : list[StationRecord]
        Windowed station records.

    Returns
    -------
    dict[str, int]
        Format → count.

    """
    counts: Counter[str] = Counter()
    for row in rows:
        fmt = row.file_format
        if fmt not in VALID_FILE_FORMATS:
            fmt = detect_file_format(row.tac_text, source=row.source)
        counts[fmt] += 1
    return dict(sorted(counts.items()))


def count_issue_codes(rows: list[StationRecord]) -> dict[str, int]:
    """
    Count lint / validation issue id occurrences across observations.

    Parameters
    ----------
    rows : list[StationRecord]
        Windowed station records.

    Returns
    -------
    dict[str, int]
        Issue code → count (per observation that listed the code).

    """
    counts: Counter[str] = Counter()
    for row in rows:
        for code in row.issue_codes:
            counts[code] += 1
    return dict(sorted(counts.items()))


__all__ = [
    "MAINTENANCE_PROBLEM_TAGS",
    "VALID_FILE_FORMATS",
    "count_file_formats",
    "count_issue_codes",
    "count_maintenance_tags",
    "detect_file_format",
    "extract_maintenance_tags",
    "normalize_issue_codes",
]
