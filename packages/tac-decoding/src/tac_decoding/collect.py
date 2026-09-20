"""COLLECT and IWXXM XML read path for decode.

Contained ``translationFailedTAC`` is decoded as TAC. Otherwise leaf XML
fields are walked. This module never encodes IWXXM.
[Corpus: adr/ADR-045] [Corpus: system-spec]
"""

from __future__ import annotations

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


class CollectError(ValueError):
    """The text is not a readable COLLECT or IWXXM document."""


@dataclass(frozen=True, slots=True)
class CollectField:
    """One leaf XML field from an XML-only COLLECT walk."""

    name: str
    value: str
    path: str


@dataclass(frozen=True, slots=True)
class CollectRead:
    """Result of reading COLLECT or IWXXM XML without encoding."""

    mode: str
    bulletin_identifier: str | None
    tac_reports: tuple[str, ...]
    fields: tuple[CollectField, ...]


def _local(tag: str) -> str:
    if tag.startswith("{"):
        return tag.rsplit("}", 1)[-1]
    return tag


def _attr_local(name: str) -> str:
    return _local(name)


def _looks_like_xml(text: str) -> bool:
    stripped = text.lstrip()
    return stripped.startswith("<?xml") or stripped.startswith("<")


def is_collect_input(text: str) -> bool:
    """Return whether ``text`` should use the COLLECT / IWXXM read path."""
    if not _looks_like_xml(text):
        return False
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return False
    local = _local(root.tag)
    if local == "MeteorologicalBulletin":
        return True
    if local in _IWXXM_ROOTS:
        return True
    return any(_attr_local(key) == "translationFailedTAC" for el in root.iter() for key in el.attrib)


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
    """
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as exc:
        msg = "COLLECT input is not well-formed XML"
        raise CollectError(msg) from exc

    local = _local(root.tag)
    has_failed = any(_attr_local(key) == "translationFailedTAC" for el in root.iter() for key in el.attrib)
    if local != "MeteorologicalBulletin" and local not in _IWXXM_ROOTS and not has_failed:
        msg = "XML is not a COLLECT bulletin or IWXXM report"
        raise CollectError(msg)

    tac_reports: list[str] = []
    fields: list[CollectField] = []
    bulletin_identifier: str | None = None

    def walk(el: ET.Element, path: tuple[str, ...]) -> None:
        nonlocal bulletin_identifier
        name = _local(el.tag)
        here = (*path, name)
        for key, value in el.attrib.items():
            if _attr_local(key) == "translationFailedTAC" and value.strip():
                tac_reports.append(value.strip())
        text = (el.text or "").strip()
        children = list(el)
        if name == "bulletinIdentifier" and text:
            bulletin_identifier = text
        elif text and not children and name not in _SKIP_FIELD:
            fields.append(CollectField(name=name, value=text, path="/".join(here)))
        for child in children:
            walk(child, here)

    walk(root, ())
    if tac_reports:
        return CollectRead("tac", bulletin_identifier, tuple(tac_reports), ())
    return CollectRead("xml_walk", bulletin_identifier, (), tuple(fields))


def decode_collect(xml: str, *, product: str) -> DecodeResult:
    """
    Decode COLLECT or IWXXM XML into the public decode shape.

    Contained TAC is preferred. Otherwise leaf fields become segments. Never
    encodes IWXXM.
    """
    from tac_decoding.decode import (
        DecodeResidual,
        DecodeResult,
        DecodeSegment,
        decode_single_report,
        shift_decode,
    )

    read = read_collect(xml)
    product_u = product.upper()
    if read.mode == "tac":
        segments: list[DecodeSegment] = []
        residuals: list[DecodeResidual] = []
        summaries: list[str] = []
        search_from = 0
        for report in read.tac_reports:
            pos = xml.find(report, search_from)
            if pos < 0:
                pos = xml.find(report)
            if pos < 0:
                pos = 0
            inner = shift_decode(decode_single_report(report, product=product_u), pos)
            segments.extend(inner.segments)
            residuals.extend(inner.residuals)
            if inner.summary:
                summaries.append(inner.summary.rstrip("."))
            search_from = pos + len(report)
        segments.sort(key=lambda item: (item.start, item.end))
        n = len(read.tac_reports)
        label = read.bulletin_identifier or "document"
        numbered = " ".join(f"{index + 1}) {clause}." for index, clause in enumerate(summaries))
        summary = f"COLLECT {label} ({n} report{'s' if n != 1 else ''} with TAC). {numbered}".strip()
        return DecodeResult(product=product_u, segments=segments, residuals=residuals, summary=summary)

    segments_xml: list[DecodeSegment] = []
    search_from = 0
    for field in read.fields:
        pos = xml.find(field.value, search_from)
        if pos < 0:
            pos = xml.find(field.value)
        if pos < 0:
            pos = 0
            end = 0
        else:
            end = pos + len(field.value)
            search_from = end
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
    label = read.bulletin_identifier or "document"
    summary = f"COLLECT {label} ({n} field{'s' if n != 1 else ''})."
    if segments_xml:
        preview = "; ".join(f"{item.code}: {item.explanation.split(': ', 1)[-1]}" for item in segments_xml[:8])
        summary = f"{summary} {preview}"
        if n > 8:
            summary = f"{summary}; …"
    return DecodeResult(product=product_u, segments=segments_xml, residuals=[], summary=summary)


def try_decode_collect(xml: str, *, product: str) -> DecodeResult | None:
    """Decode COLLECT/IWXXM XML, or return ``None`` when the text is not that path."""
    if not is_collect_input(xml):
        return None
    return decode_collect(xml, product=product)
