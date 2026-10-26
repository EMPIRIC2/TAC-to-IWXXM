"""Join TAF continuation lines into one forecast before convert."""

from __future__ import annotations

import re

_TAF_START = re.compile(
    r"^(?:TAF\s+)?(?:(?:AMD|COR)\s+)?[A-Z][A-Z0-9]{3}\b",
    re.IGNORECASE,
)


def starts_taf_report(line: str) -> bool:
    """
    Return whether ``line`` opens a TAF rather than continuing one.

    Parameters
    ----------
    line : str
        One non-empty TAC line.

    Returns
    -------
    bool
        True when the line begins with a station, optionally after ``TAF``, ``AMD``, or ``COR``.

    Examples
    --------
    >>> starts_taf_report("TAF MKJP 081700Z 0818/0918 09012KT")
    True
    >>> starts_taf_report("BECMG 0902/0904 14008KT")
    False
    """
    return _TAF_START.match(line.strip()) is not None


def join_taf_lines(lines: list[str]) -> list[str]:
    """
    Join continuation lines onto the TAF they belong to.

    Parameters
    ----------
    lines : list[str]
        Non-empty lines in paste order.

    Returns
    -------
    list[str]
        One string per TAF. A line that does not open a report stays attached to the previous TAF.

    Examples
    --------
    >>> join_taf_lines(["TAF MKJP 081700Z 0818/0918 09012KT", "BECMG 0902/0904 14008KT"])
    ['TAF MKJP 081700Z 0818/0918 09012KT BECMG 0902/0904 14008KT']
    """
    joined: list[str] = []
    for line in lines:
        text = line.strip()
        if not text:
            continue
        if joined and not starts_taf_report(text):
            joined[-1] = f"{joined[-1]} {text}"
        else:
            joined.append(text)
    return joined


def join_taf_entries(entries: list[tuple[str, int]]) -> list[tuple[str, int]]:
    """
    Join continuation lines and keep the offset of the line that opened the TAF.

    Parameters
    ----------
    entries : list[tuple[str, int]]
        ``(line, offset)`` pairs. Offsets point at the first character of each line.

    Returns
    -------
    list[tuple[str, int]]
        One pair per TAF. The offset is the start of the opening line.

    Examples
    --------
    >>> join_taf_entries([("TAF MKJP 081700Z", 0), ("TEMPO 0906/0912", 20)])
    [('TAF MKJP 081700Z TEMPO 0906/0912', 0)]
    """
    joined: list[tuple[str, int]] = []
    for text, offset in entries:
        if joined and not starts_taf_report(text):
            previous, start = joined[-1]
            joined[-1] = (f"{previous} {text}", start)
        else:
            joined.append((text, offset))
    return joined
