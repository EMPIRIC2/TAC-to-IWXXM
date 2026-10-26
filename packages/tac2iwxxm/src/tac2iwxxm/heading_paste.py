"""Peel a pasted abbreviated heading into reports for the main convert path."""

from __future__ import annotations

from dataclasses import dataclass

from tac2iwxxm.bulletin import BulletinSplitError, parse_ahl, split_bulletin

MALFORMED_HEADING = (
    "The abbreviated heading is not valid. Use TTAAii CCCC YYGGgg (optional BBB), then one or more TAC reports."
)
EMPTY_HEADING = "No TAC reports found after the abbreviated heading."


class HeadingPasteError(Exception):
    """Raised when a pasted heading cannot be converted.

    Attributes
    ----------
    code : str
        ``empty_bulletin`` when the heading has no report, otherwise ``INVALID_AHL``.
    message : str
        Operator-facing explanation.
    """

    def __init__(self, code: str, message: str) -> None:
        """
        Store the heading failure.

        Parameters
        ----------
        code : str
            Stable error code.

        message : str
            Operator-facing explanation.
        """
        self.code = code
        self.message = message
        super().__init__(message)


@dataclass
class PastedHeading:
    """Reports taken from a paste that opens with an abbreviated heading.

    Attributes
    ----------
    reports : tuple[tuple[str, int], ...]
        TAC report text and its start offset in the original paste.
    heading_start : int
        Start offset of the heading line.
    leading_blank : bool
        True when a blank line precedes the heading.
    """

    reports: tuple[tuple[str, int], ...]
    heading_start: int
    leading_blank: bool


def http_status_for_heading_error(code: str) -> int:
    """
    Return the HTTP status for a heading paste failure.

    Parameters
    ----------
    code : str
        ``empty_bulletin`` or ``INVALID_AHL``.

    Returns
    -------
    int
        400 when the heading has no report, otherwise 422.

    Examples
    --------
    >>> http_status_for_heading_error("empty_bulletin")
    400
    >>> http_status_for_heading_error("INVALID_AHL")
    422
    """
    if code == "empty_bulletin":
        return 400
    return 422


def _opening_line(text: str) -> tuple[str, int]:
    """
    Return the first non-empty line and its start offset.

    Parameters
    ----------
    text : str
        Paste buffer.

    Returns
    -------
    tuple[str, int]
        Stripped line and offset. The line is empty when the buffer has no content.
    """
    offset = 0
    for line in text.splitlines(keepends=True):
        content = line.rstrip("\r\n")
        stripped = content.strip()
        if stripped != "":
            lead = len(content) - len(content.lstrip(" \t"))
            return stripped, offset + lead
        offset = offset + len(line)
    return "", offset


def _has_leading_blank(text: str) -> bool:
    """
    Return whether a blank line precedes the first content line.

    Parameters
    ----------
    text : str
        Paste buffer.

    Returns
    -------
    bool
        True when at least one opening line is blank.
    """
    blanks = 0
    for line in text.splitlines():
        if line.strip() != "":
            break
        blanks = blanks + 1
    return blanks > 0


def _classify_opening(line: str) -> str:
    """
    Return ``heading`` or ``plain``, or raise when the line is a bad heading.

    Parameters
    ----------
    line : str
        First non-empty line.

    Returns
    -------
    str
        ``heading`` when the line is an abbreviated heading, otherwise ``plain``.

    Raises
    ------
    HeadingPasteError
        When the line has heading shape but is not a valid heading.
    """
    try:
        parse_ahl(line)
    except BulletinSplitError as exc:
        matched = exc.code == "bulletin_split_failed" and exc.message.startswith("Cannot parse")
        if not matched:
            raise HeadingPasteError("INVALID_AHL", MALFORMED_HEADING) from exc
        return "plain"
    return "heading"


def reports_for_convert(text: str, product: str) -> PastedHeading | None:
    """
    Return bulletin reports when the paste opens with an abbreviated heading.

    Parameters
    ----------
    text : str
        Operator paste, heading line first, then one or more TAC reports.

    product : str
        Convert product, such as ``METAR``, ``SPECI``, ``TAF``, or ``SIGMET``.

    Returns
    -------
    PastedHeading | None
        Reports and offsets, or None when the paste is not a heading bulletin.

    Raises
    ------
    HeadingPasteError
        When the heading is malformed, does not match ``product``, or has no report.

    Examples
    --------
    >>> plain = "METAR TNCM 081200Z 14006KT 9999 FEW020 28/24 Q1013="
    >>> reports_for_convert(plain, "METAR") is None
    True
    """
    line, heading_start = _opening_line(text)
    if line == "":
        return None
    kind = _classify_opening(line)
    if kind != "heading":
        return None
    try:
        split = split_bulletin(text, product=product)
    except BulletinSplitError as exc:
        if exc.code == "empty_bulletin":
            raise HeadingPasteError("empty_bulletin", EMPTY_HEADING) from exc
        raise HeadingPasteError("INVALID_AHL", MALFORMED_HEADING) from exc
    cursor = heading_start
    located: list[tuple[str, int]] = []
    for report in split.reports:
        found = text.find(report, cursor)
        located.append((report, found))
        cursor = found + len(report)
    return PastedHeading(
        reports=tuple(located),
        heading_start=heading_start,
        leading_blank=_has_leading_blank(text),
    )
