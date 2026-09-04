"""Readable item-by-item decode from IWXXM XML for POST /validate.

Produces the same code | explanation row shape as TAC decode. Does not dump raw XML.
"""

from __future__ import annotations

from dataclasses import dataclass
from xml.etree import ElementTree as ET

from tac2iwxxm import decode_tac as tac2iwxxm_decode_tac

from .iwxxm_pass_through import looks_like_xml

_UOM_DISPLAY: dict[str, str] = {
    "Cel": "°C",
    "deg": "deg",
    "[kn_i]": "kt",
    "kt": "kt",
    "hPa": "hPa",
    "m": "m",
    "[ft_i]": "ft",
    "ft": "ft",
    "km": "km",
}

_FIELD_LABELS: dict[str, str] = {
    "locationIndicatorICAO": "Aerodrome",
    "designator": "Aerodrome",
    "meanWindDirection": "Mean wind direction",
    "meanWindSpeed": "Mean wind speed",
    "meanWindGustSpeed": "Mean wind gust",
    "airTemperature": "Air temperature",
    "dewpointTemperature": "Dewpoint temperature",
    "qnh": "QNH",
    "prevailingVisibility": "Prevailing visibility",
    "prevailingVisibilityOperator": "Visibility operator",
    "runwayVisualRange": "Runway visual range",
    "presentWeather": "Present weather",
    "recentWeather": "Recent weather",
    "seaSurfaceTemperature": "Sea-surface temperature",
}

_SKIP_LOCAL: frozenset[str] = frozenset(
    {
        "timeSlice",
        "AirportHeliport",
        "AirportHeliportTimeSlice",
        "validTime",
        "interpretation",
        "TimeInstant",
        "MeteorologicalAerodromeObservation",
        "AerodromeSurfaceWind",
        "AerodromeHorizontalVisibility",
        "AerodromeCloud",
        "CloudLayer",
        "observation",
        "aerodrome",
        "surfaceWind",
        "visibility",
        "cloud",
        "layer",
        "issueTime",
        "observationTime",
    }
)


@dataclass(frozen=True)
class ReadableDecodeSegment:
    """One code | explanation row (same shape as TAC decode)."""

    start: int
    end: int
    code: str
    explanation: str


@dataclass(frozen=True)
class ReadableDecode:
    """Optional validate-path decode; empty when no meteorological fields exist."""

    segments: list[ReadableDecodeSegment]
    summary: str


def _local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[-1]
    if ":" in tag:
        return tag.split(":", 1)[-1]
    return tag


def _attr(elem: ET.Element, local: str) -> str | None:
    for key, value in elem.attrib.items():
        if _local_name(key) == local and value:
            return value
    return None


def _href_code(href: str) -> str:
    trimmed = href.rstrip("/")
    if "/" in trimmed:
        return trimmed.rsplit("/", 1)[-1]
    return trimmed


def _format_measure(text: str, uom: str | None) -> str:
    value = text.strip()
    if not value:
        return ""
    if not uom:
        return value
    unit = _UOM_DISPLAY.get(uom, uom)
    return f"{value} {unit}"


def _offsets(xml: str, needle: str) -> tuple[int, int]:
    if not needle:
        return 0, 0
    idx = xml.find(needle)
    if idx < 0:
        return 0, 0
    return idx, idx + len(needle)


def _parent_is(parents: tuple[ET.Element, ...], name: str) -> bool:
    return any(_local_name(p.tag) == name for p in parents)


def readable_decode_from_iwxxm(xml: str) -> ReadableDecode:
    """
    Extract item-by-item meteorological rows from IWXXM XML.

    Parameters
    ----------
    xml :
        IWXXM document text.

    Returns
    -------
    ReadableDecode
        Segments and summary, or empty when XML is not parseable / has no fields.
    """
    stripped = (xml or "").strip()
    if not stripped or not looks_like_xml(stripped):
        return ReadableDecode(segments=[], summary="")
    try:
        root = ET.fromstring(stripped)
    except ET.ParseError:
        return ReadableDecode(segments=[], summary="")

    segments: list[ReadableDecodeSegment] = []
    seen_codes: set[str] = set()
    facts: list[str] = []
    root_kind = _local_name(root.tag)

    def add(code: str, explanation: str) -> None:
        """Append a readable decode segment when ``code`` is new and non-XML."""
        token = code.strip()
        if not token or token in seen_codes:
            return
        if token.startswith("<") or "<?xml" in token:
            return
        seen_codes.add(token)
        start, end = _offsets(stripped, token)
        segments.append(
            ReadableDecodeSegment(
                start=start,
                end=end,
                code=token,
                explanation=explanation,
            )
        )

    def walk(elem: ET.Element, parents: tuple[ET.Element, ...] = ()) -> None:
        """Recursively extract human-readable tokens from IWXXM XML elements."""
        local = _local_name(elem.tag)
        href = _attr(elem, "href")
        uom = _attr(elem, "uom")
        nil = _attr(elem, "nil")
        text = (elem.text or "").strip()

        if local == "timePosition" and text:
            if _parent_is(parents, "issueTime"):
                add(text, "Issue time")
                facts.append(f"Issued {text}")
            elif _parent_is(parents, "observationTime"):
                add(text, "Observation time")
            else:
                add(text, "Time")
        elif local in _FIELD_LABELS:
            if nil == "true":
                return
            if href:
                code = _href_code(href)
                add(code, _FIELD_LABELS[local])
            elif text:
                add(_format_measure(text, uom), _FIELD_LABELS[local])
        elif local == "amount" and href:
            sibling_base: str | None = None
            parent = parents[-1] if parents else None
            if parent is not None:
                for sib in list(parent):
                    if _local_name(sib.tag) == "base" and (sib.text or "").strip():
                        sibling_base = _format_measure((sib.text or "").strip(), _attr(sib, "uom"))
            code = _href_code(href)
            if sibling_base:
                add(f"{code} {sibling_base}", "Cloud layer")
            else:
                add(code, "Cloud amount")
        elif local == "base" and text and not _parent_is(parents, "CloudLayer"):
            add(_format_measure(text, uom), "Cloud base")
        elif local not in _SKIP_LOCAL and href and local not in {"amount"}:
            add(_href_code(href), local.replace("_", " "))

        cavok = _attr(elem, "cloudAndVisibilityOK")
        if cavok == "true":
            add("CAVOK", "Cloud and visibility OK")

        for child in list(elem):
            walk(child, (*parents, elem))

    walk(root)

    icao = next((s.code for s in segments if s.explanation == "Aerodrome"), "")
    wind = next((s.code for s in segments if s.explanation == "Mean wind direction"), "")
    spd = next((s.code for s in segments if s.explanation == "Mean wind speed"), "")
    temp = next((s.code for s in segments if s.explanation == "Air temperature"), "")
    summary_parts: list[str] = []
    if icao:
        known = {"METAR", "SPECI", "TAF", "SIGMET", "AIRMET", "VAA", "TCA"}
        kind = root_kind if root_kind in known else "IWXXM"
        summary_parts.append(f"{icao} {kind}.")
    if wind and spd:
        summary_parts.append(f"Wind {wind} at {spd}.")
    elif wind:
        summary_parts.append(f"Wind {wind}.")
    if temp:
        summary_parts.append(f"Temperature {temp}.")
    summary_parts.extend(facts[:1])
    summary = " ".join(summary_parts).strip()
    return ReadableDecode(segments=segments, summary=summary)


def _from_tac(tac_text: str) -> ReadableDecode:
    result = tac2iwxxm_decode_tac(tac_text, product="METAR")
    return ReadableDecode(
        segments=[
            ReadableDecodeSegment(
                start=s.start,
                end=s.end,
                code=s.code,
                explanation=s.explanation,
            )
            for s in result.segments
        ],
        summary=result.summary or "",
    )


def decode_for_validate(*, xml_content: str = "", manual_text: str = "") -> ReadableDecode:
    """
    Build optional decode rows for a validate request.

    Prefers IWXXM field rows when XML is present; otherwise decodes TAC text.

    Parameters
    ----------
    xml_content :
        IWXXM XML submitted to validate.
    manual_text :
        Optional TAC used when XML is absent or has no meteorological fields.

    Returns
    -------
    ReadableDecode
        Empty segments/summary when no readable decode exists.
    """
    xml = (xml_content or "").strip()
    tac = (manual_text or "").strip()
    if xml and looks_like_xml(xml):
        decoded = readable_decode_from_iwxxm(xml)
        if decoded.segments:
            return decoded
    if tac and not looks_like_xml(tac):
        return _from_tac(tac)
    return ReadableDecode(segments=[], summary="")


__all__ = [
    "ReadableDecode",
    "ReadableDecodeSegment",
    "decode_for_validate",
    "readable_decode_from_iwxxm",
]
