"""Advisory field iteration and plain-value helpers.

[Corpus: product §F9]
"""

from __future__ import annotations

import re

from tac_decoding.decode_explain_advisory import (
    _ADVISORY_PHRASES,
    _ADVISORY_STRUCTURED,
    _COMPASS,
    _COMPASS_RE,
    _MONTHS,
    _SPEED_UNIT,
    _advisory_field_finder,
    _advisory_field_title,
)
from tac_decoding.decode_patterns import *


def _ordinal_day(day: int) -> str:
    """Day of month with an ordinal, such as ``the 1st``.

    Parameters
    ----------
    day : int
        Day of the month.

    Returns
    -------
    str
        ``the`` plus the day and its suffix.
    """
    suffix = "th" if 10 <= day % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return f"the {day}{suffix}"


def _plain_advisory_value(value: str) -> str:
    """Read coded advisory values as plain language.

    Dates, positions, speeds, distances, and a few fixed phrases are expanded.
    Surrounding words stay as written. [Corpus: product §F9]

    Parameters
    ----------
    value : str
        Text after an advisory field label.

    Returns
    -------
    str
        The same text with coded pieces expanded.
    """
    text = " ".join(value.split())
    if not text:
        return ""

    def _dtg(match: re.Match[str]) -> str:
        """Expand ``YYYYMMDD/HHMMZ`` to a clock time and calendar date.

        Parameters
        ----------
        match : re.Match[str]
            Date and time groups.

        Returns
        -------
        str
            Plain time, or the original text when the date is impossible.
        """
        raw, hhmm = match.group(1), match.group(2)
        month, day = int(raw[4:6]), int(raw[6:8])
        if not 1 <= month <= 12 or not 1 <= day <= 31:
            return match.group(0)
        return f"{hhmm[:2]}:{hhmm[2:]} UTC on {day} {_MONTHS[month - 1]} {raw[:4]}"

    def _daytime(match: re.Match[str]) -> str:
        """Expand ``DD/HHMMZ`` to a clock time on that day.

        Parameters
        ----------
        match : re.Match[str]
            Day and time groups.

        Returns
        -------
        str
            Plain time, or the original text when the day is impossible.
        """
        day = int(match.group(1))
        hhmm = match.group(2)
        if not 1 <= day <= 31:
            return match.group(0)
        return f"{hhmm[:2]}:{hhmm[2:]} UTC on {_ordinal_day(day)}"

    def _lat(match: re.Match[str]) -> str:
        """Expand a coded latitude.

        Parameters
        ----------
        match : re.Match[str]
            Hemisphere, degrees, and minutes.

        Returns
        -------
        str
            Degrees and minutes north or south.
        """
        hemi = "north" if match.group(1) == "N" else "south"
        return f"{int(match.group(2))} degrees {match.group(3)} minutes {hemi}"

    def _lon(match: re.Match[str]) -> str:
        """Expand a coded longitude.

        Parameters
        ----------
        match : re.Match[str]
            Hemisphere, degrees, and minutes.

        Returns
        -------
        str
            Degrees and minutes east or west.
        """
        hemi = "east" if match.group(1) == "E" else "west"
        return f"{int(match.group(2))} degrees {match.group(3)} minutes {hemi}"

    def _move(match: re.Match[str]) -> str:
        """Expand a compass direction and speed.

        Parameters
        ----------
        match : re.Match[str]
            Direction, speed, and unit.

        Returns
        -------
        str
            Direction, speed, and unit in words.
        """
        unit = match.group(3).upper()
        return f"{_COMPASS[match.group(1)]} at {int(match.group(2))} {_SPEED_UNIT[unit]}"

    def _speed(match: re.Match[str]) -> str:
        """Expand a bare speed.

        Parameters
        ----------
        match : re.Match[str]
            Speed and unit.

        Returns
        -------
        str
            Speed and unit in words.
        """
        unit = match.group(2).upper()
        return f"{int(match.group(1))} {_SPEED_UNIT[unit]}"

    text = re.sub(r"\b(\d{8})/(\d{4})Z\b", _dtg, text)
    text = re.sub(r"\b(\d{2})/(\d{4})Z\b", _daytime, text)
    text = re.sub(r"\b([NS])(\d{2})(\d{2})\b", _lat, text)
    text = re.sub(r"\b([EW])(\d{2,3})(\d{2})\b", _lon, text)
    text = re.sub(rf"\b({_COMPASS_RE})\s*(\d{{1,3}})\s*(KM/H|KMH|KT|MPS)\b", _move, text)
    text = re.sub(r"\bSFC/FL(\d+)\b", lambda m: f"surface to flight level {int(m.group(1))}", text)
    text = re.sub(
        r"\bFL(\d+)/(\d+)\b",
        lambda m: f"flight level {int(m.group(1))} to {int(m.group(2))}",
        text,
    )
    text = re.sub(r"\bFL(\d+)\b", lambda m: f"flight level {int(m.group(1))}", text)
    text = re.sub(r"\b(\d+)(KM/H|KMH|KT|MPS)\b", _speed, text)
    text = re.sub(r"\b(\d+)HPA\b", lambda m: f"{int(m.group(1))} hectopascals", text)
    text = re.sub(r"\b(\d+)NM\b", lambda m: f"{int(m.group(1))} nautical miles", text)
    text = re.sub(r"\b(\d+)KM\b", lambda m: f"{int(m.group(1))} kilometres", text)
    text = re.sub(r"\b(\d+)M\b", lambda m: f"{int(m.group(1))} metres", text)
    for pattern, phrase in _ADVISORY_PHRASES:
        text = pattern.sub(phrase, text)
    return " ".join(text.split())


def _iter_advisory_fields(
    tac: str,
    *,
    product: str,
) -> list[tuple[int, int, str, str, int]]:
    """
    Internal helper ``_iter_advisory_fields``.

    Parameters
    ----------
    tac : str
        Argument ``tac``.

    product : str
        Argument ``product``.

    Returns
    -------
    list[tuple[int, int, str, str, int]]
        Return value.
    """
    if product not in _ADVISORY_STRUCTURED:
        return []
    # Collect all label hits; when spans overlap prefer the longer (earlier-spec) label.
    hits: list[tuple[int, int, str, str, re.Match[str]]] = []
    for pattern, title_template in _advisory_field_finder(product):
        for m in pattern.finditer(tac):
            label = m.group("label")
            code = re.sub(r"\s+", " ", label.strip())
            hits.append((m.start(), m.end(), code, title_template, m))
    if not hits:
        return []
    hits.sort(key=lambda h: (h[0], -(h[1] - h[0])))
    # Drop overlapping shorter matches (same start or nested under a longer label).
    selected: list[tuple[int, int, str, str, re.Match[str]]] = []
    for hit in hits:
        start, end, _code, _title, _m = hit
        if any(start < prev_end and end > prev_start for prev_start, prev_end, *_ in selected):
            continue
        selected.append(hit)
    selected.sort(key=lambda h: h[0])

    out: list[tuple[int, int, str, str]] = []
    for i, (start, label_end, code, title_template, match) in enumerate(selected):
        value_start = label_end
        value_end = selected[i + 1][0] if i + 1 < len(selected) else len(tac)
        raw_value = tac[value_start:value_end]
        trim = len(raw_value.rstrip())
        body = raw_value[:trim]
        lead = len(body) - len(body.lstrip())
        value_text = " ".join(body.split())
        plain = _plain_advisory_value(value_text)
        title = _advisory_field_title(code, title_template, match)
        explanation = f"{title}: {plain}" if plain else title
        mark_start = value_start + lead
        mark_end = value_start + trim
        if mark_end <= mark_start:
            mark_start, mark_end = start, label_end
        out.append((mark_start, mark_end, code, explanation, start))
    return out


def _token_indices_covering(
    tokens: list[tuple[int, int, str]],
    spans: list[tuple[int, int]],
) -> set[int]:
    """
    Internal helper ``_token_indices_covering``.

    Parameters
    ----------
    tokens : list[tuple[int, int, str]]
        Argument ``tokens``.

    spans : list[tuple[int, int]]
        Argument ``spans``.

    Returns
    -------
    set[int]
        Return value.
    """
    covered: set[int] = set()
    for idx, (tstart, tend, _) in enumerate(tokens):
        for start, end in spans:
            if tstart < end and tend > start:
                covered.add(idx)
                break
    return covered
