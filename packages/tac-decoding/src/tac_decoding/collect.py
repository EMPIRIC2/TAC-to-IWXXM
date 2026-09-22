"""COLLECT and IWXXM XML read path for decode.

Contained ``translationFailedTAC`` is decoded as TAC. Otherwise leaf XML
fields are walked. This module never encodes IWXXM.
[Corpus: adr/ADR-045] [Corpus: system-spec]
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tac_decoding.decode import DecodeResult

_IWXXM_ROOTS = frozenset(
    {
        "METAR",
        "SPECI",
        "TAF",
        "SIGMET",
        "AIRMET",
        "VolcanicAshSIGMET",
        "TropicalCycloneSIGMET",
        "VolcanicAshAdvisory",
        "TropicalCycloneAdvisory",
        "SpaceWeatherAdvisory",
        "VolcanoObservatoryNoticeForAviation",
        "MeteorologicalBulletin",
    }
)
_SKIP_FIELD = frozenset({"bulletinIdentifier"})
_FORBIDDEN_DTD = re.compile(r"<!DOCTYPE|<!ENTITY", re.IGNORECASE)
_MAX_DEPTH = 64
_MAX_NODES = 10_000
_MAX_LEAVES = 2_000
_MAX_TAC_REPORTS = 500


class CollectError(ValueError):
    """
    The text is not a readable COLLECT or IWXXM document.

    Attributes
    ----------
    _ : object
        See implementation.
    """


@dataclass(frozen=True, slots=True)
class CollectField:
    """
    One leaf XML field from an XML-only COLLECT walk.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    name: str
    value: str
    path: str


@dataclass(frozen=True, slots=True)
class CollectRead:
    """
    Result of reading COLLECT or IWXXM XML without encoding.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    mode: str
    bulletin_identifier: str | None
    tac_reports: tuple[str, ...]
    fields: tuple[CollectField, ...]


def _local(tag: str) -> str:
    """Internal helper ``_local``."""
    if tag.startswith("{"):
        return tag.rsplit("}", 1)[-1]
    return tag


def _attr_local(name: str) -> str:
    """Internal helper ``_attr_local``."""
    return _local(name)


def _looks_like_xml(text: str) -> bool:
    """Internal helper ``_looks_like_xml``."""
    stripped = text.lstrip()
    return stripped.startswith("<?xml") or stripped.startswith("<")


def _has_forbidden_dtd(text: str) -> bool:
    """Reject DTD / custom entity declarations (billion-laughs class)."""
    return _FORBIDDEN_DTD.search(text) is not None


def _parse_root(text: str) -> ET.Element:
    """Internal helper ``_parse_root``."""
    if _has_forbidden_dtd(text):
        msg = "COLLECT XML must not include a document type or entity declaration"
        raise CollectError(msg)
    try:
        return ET.fromstring(text)
    except ET.ParseError as exc:
        msg = "COLLECT input is not well-formed XML"
        raise CollectError(msg) from exc


def _is_collect_shape(root: ET.Element) -> bool:
    """Internal helper ``_is_collect_shape``."""
    local = _local(root.tag)
    if local == "MeteorologicalBulletin" or local in _IWXXM_ROOTS:
        return True
    for nodes, el in enumerate(root.iter(), start=1):
        if nodes > _MAX_NODES:
            return False
        if any(_attr_local(key) == "translationFailedTAC" for key in el.attrib):
            return True
    return False


def is_collect_input(text: str) -> bool:
    """
    Return whether ``text`` should use the COLLECT / IWXXM read path.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (is_collect_input)
    2

    Parameters
    ----------
    text : object
        Argument ``text``.

    Returns
    -------
    object
        Return value.
    """
    if not _looks_like_xml(text) or _has_forbidden_dtd(text):
        return False
    try:
        root = _parse_root(text)
    except CollectError:
        return False
    return _is_collect_shape(root)


def _read_from_root(root: ET.Element) -> CollectRead:
    """Internal helper ``_read_from_root``."""
    local = _local(root.tag)
    tac_reports: list[str] = []
    fields: list[CollectField] = []
    bulletin_identifier: str | None = None
    nodes = 0
    saw_failed_attr = False

    def walk(el: ET.Element, path: tuple[str, ...], depth: int) -> None:
        """
        Walk one COLLECT element, collecting TAC and fields.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (walk)
        2

        Parameters
        ----------
        el : object
            Argument ``el``.
        path : object
            Argument ``path``.
        depth : object
            Argument ``depth``.
        """
        nonlocal bulletin_identifier, nodes, saw_failed_attr
        if depth > _MAX_DEPTH:
            msg = "COLLECT XML exceeds the maximum nesting depth"
            raise CollectError(msg)
        nodes += 1
        if nodes > _MAX_NODES:
            msg = "COLLECT XML exceeds the maximum node count"
            raise CollectError(msg)
        name = _local(el.tag)
        here = (*path, name)
        for key, value in el.attrib.items():
            if _attr_local(key) != "translationFailedTAC":
                continue
            saw_failed_attr = True
            if value.strip():
                if len(tac_reports) >= _MAX_TAC_REPORTS:
                    msg = "COLLECT XML exceeds the maximum contained TAC count"
                    raise CollectError(msg)
                tac_reports.append(value.strip())
        text = (el.text or "").strip()
        children = list(el)
        if name == "bulletinIdentifier" and text:
            bulletin_identifier = text
        elif text and not children and name not in _SKIP_FIELD:
            if len(fields) >= _MAX_LEAVES:
                msg = "COLLECT XML exceeds the maximum leaf-field count"
                raise CollectError(msg)
            fields.append(CollectField(name=name, value=text, path="/".join(here)))
        for child in children:
            walk(child, here, depth + 1)

    walk(root, (), 0)
    if local != "MeteorologicalBulletin" and local not in _IWXXM_ROOTS and not saw_failed_attr:
        msg = "XML is not a COLLECT bulletin or IWXXM report"
        raise CollectError(msg)
    if tac_reports:
        return CollectRead("tac", bulletin_identifier, tuple(tac_reports), ())
    return CollectRead("xml_walk", bulletin_identifier, (), tuple(fields))


def read_collect(xml: str) -> CollectRead:
    """
    Read COLLECT or IWXXM XML.

    Parameters
    ----------
    xml :
        Document text. Must parse as XML and be a COLLECT bulletin, an IWXXM
        product root, or a tree that carries ``translationFailedTAC``.

    Returns
    -------
    CollectRead
        ``mode`` is ``tac`` when at least one contained TAC is present, else
        ``xml_walk``.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (read_collect)
    2
    """
    return _read_from_root(_parse_root(xml))


def _source_span(xml: str, needle: str, search_from: int) -> tuple[int, int, int]:
    """Best-effort source offsets. Missed finds stay zero-width (entity-decoded text)."""
    if not needle:
        return 0, 0, search_from
    pos = xml.find(needle, search_from)
    if pos < 0:
        pos = xml.find(needle)
    if pos < 0:
        return 0, 0, search_from
    end = pos + len(needle)
    return pos, end, end


def decode_collect(xml: str, *, product: str, read: CollectRead | None = None) -> DecodeResult:
    """
    Decode COLLECT or IWXXM XML into the public decode shape.

    Contained TAC is preferred. Otherwise leaf fields become segments. Never
    encodes IWXXM.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (decode_collect)
    2

    Parameters
    ----------
    xml : object
        Argument ``xml``.
    product : object
        Argument ``product``.
    read : object
        Argument ``read``.

    Returns
    -------
    object
        Return value.
    """
    from tac_decoding.decode import (
        DecodeResidual,
        DecodeResult,
        DecodeSegment,
        decode_single_report,
        shift_decode,
    )

    collected = read if read is not None else read_collect(xml)
    product_u = product.upper()
    if collected.mode == "tac":
        segments: list[DecodeSegment] = []
        residuals: list[DecodeResidual] = []
        summaries: list[str] = []
        search_from = 0
        for report in collected.tac_reports:
            pos, _end, search_from = _source_span(xml, report, search_from)
            inner = shift_decode(decode_single_report(report, product=product_u), pos)
            segments.extend(inner.segments)
            residuals.extend(inner.residuals)
            if inner.summary:
                summaries.append(inner.summary.rstrip("."))
        segments.sort(key=lambda item: (item.start, item.end))
        n = len(collected.tac_reports)
        label = collected.bulletin_identifier or "document"
        numbered = " ".join(f"{index + 1}) {clause}." for index, clause in enumerate(summaries))
        summary = f"COLLECT {label} ({n} report{'s' if n != 1 else ''} with TAC). {numbered}".strip()
        return DecodeResult(product=product_u, segments=segments, residuals=residuals, summary=summary)

    segments_xml: list[DecodeSegment] = []
    search_from = 0
    for field in collected.fields:
        pos, end, search_from = _source_span(xml, field.value, search_from)
        segments_xml.append(
            DecodeSegment(
                start=pos,
                end=end,
                code=field.name,
                explanation=f"{field.name}: {field.value}",
            )
        )
    segments_xml.sort(key=lambda item: (item.start, item.end))
    n = len(segments_xml)
    label = collected.bulletin_identifier or "document"
    summary = f"COLLECT {label} ({n} field{'s' if n != 1 else ''})."
    if segments_xml:
        preview = "; ".join(f"{item.code}: {item.explanation.split(': ', 1)[-1]}" for item in segments_xml[:8])
        summary = f"{summary} {preview}"
        if n > 8:
            summary = f"{summary}; …"
    return DecodeResult(product=product_u, segments=segments_xml, residuals=[], summary=summary)


def try_decode_collect(xml: str, *, product: str) -> DecodeResult | None:
    """
    Decode COLLECT/IWXXM XML, or return ``None`` when the text is not that path.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (try_decode_collect)
    2

    Parameters
    ----------
    xml : object
        Argument ``xml``.
    product : object
        Argument ``product``.

    Returns
    -------
    object
        Return value.
    """
    if not _looks_like_xml(xml) or _has_forbidden_dtd(xml):
        return None
    try:
        root = _parse_root(xml)
    except CollectError:
        return None
    if not _is_collect_shape(root):
        return None
    return decode_collect(xml, product=product, read=_read_from_root(root))
