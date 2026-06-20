"""Canonical XML normalization for TC-M003 golden regression (REQ-018).

Produces deterministic strings for whitespace- and order-insensitive comparison
of IWXXM conversion output.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from collections.abc import Iterable
from xml.dom import minidom

# Dynamic IWXXM/GML attributes omitted from structural comparison.
VOLATILE_ATTRS: frozenset[str] = frozenset(
    {
        "id",
        "gml:id",
        "schemaLocation",
        "translatedBulletinID",
        "translationCentreName",
        "translationCentreDesignator",
        "translationTime",
        "translatedBulletinReceptionTime",
        "translationFailedTAC",
        "permissibleUsage",
        "permissibleUsageReason",
        "permissibleUsageSupplementary",
    }
)

_UUID_HREF = re.compile(r"#uuid\.[0-9a-f-]+", re.IGNORECASE)
_UUID_VALUE = re.compile(
    r"^uuid\.[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def local_name(tag: str) -> str:
    """Return the local part of a Clark-notation tag."""
    if tag.startswith("{"):
        return tag.rsplit("}", 1)[-1]
    if ":" in tag:
        return tag.split(":", 1)[-1]
    return tag


def _norm_text(value: str | None) -> str:
    if value is None:
        return ""
    return " ".join(value.split())


def _filter_volatile_attrs(attrib: dict[str, str]) -> dict[str, str]:
    filtered: dict[str, str] = {}
    for key, value in attrib.items():
        if local_name(key) in VOLATILE_ATTRS:
            continue
        norm_val = _norm_text(value)
        if _UUID_VALUE.match(norm_val):
            continue
        if local_name(key) == "href" and (
            _UUID_HREF.match(norm_val)
            or norm_val.startswith("http://codes.wmo.int/")
            or norm_val.startswith("https://codes.wmo.int/")
        ):
            continue
        filtered[local_name(key)] = norm_val
    return filtered


def _canonicalize_element(elem: ET.Element) -> tuple[str, ...]:
    """Return a nested tuple representation for stable ordering and comparison."""
    tag = local_name(elem.tag)
    attrs = tuple(sorted(_filter_volatile_attrs(elem.attrib).items()))
    text = _norm_text(elem.text)
    children = sorted(
        (_canonicalize_element(child) for child in list(elem)),
        key=lambda node: node,
    )
    return (tag, attrs, text, tuple(children))


# Wrapper for IWXXM fragments emitted by GIFTs (no namespace declarations on root).
_FRAGMENT_NS_WRAPPER = (
    "<_canonical_wrapper "
    'xmlns:iwxxm="http://icao.int/iwxxm/2025-2" '
    'xmlns:gml="http://www.opengis.net/gml/3.2" '
    'xmlns:aixm="http://www.aixm.aero/schema/5.1.1" '
    'xmlns:xlink="http://www.w3.org/1999/xlink">'
    "{content}</_canonical_wrapper>"
)


def _parse_root_element(xml_content: str) -> ET.Element:
    """Parse XML content, wrapping namespace-prefixed fragments when needed."""
    stripped = xml_content.strip()
    attempts = [stripped]
    if "xmlns" not in stripped and not stripped.startswith("<?xml"):
        attempts.append(_FRAGMENT_NS_WRAPPER.format(content=stripped))

    last_error: Exception | None = None
    for candidate in attempts:
        try:
            doc = minidom.parseString(candidate)
            pretty = doc.toprettyxml(indent="  ")
            if pretty.startswith("<?xml"):
                pretty = "\n".join(pretty.splitlines()[1:])
            root = ET.fromstring(pretty.strip().encode("utf-8"))
            if local_name(root.tag) == "_canonical_wrapper" and len(root) == 1:
                return root[0]
            return root
        except (ET.ParseError, Exception) as exc:
            last_error = exc

    if last_error is not None:
        raise ValueError(f"Cannot parse XML for canonicalization: {last_error}") from last_error
    raise ValueError("Cannot parse XML for canonicalization")


def canonicalize_xml(xml_content: str) -> str:
    """Normalize XML to a canonical string for diffing.

    Args:
        xml_content: Raw or prettified XML.

    Returns:
        Deterministic canonical representation.
    """
    root = _parse_root_element(xml_content)
    canonical = _canonicalize_element(root)
    return repr(canonical)


def compare_canonical_xml(expected: str, actual: str) -> bool:
    """Return True when two XML documents match after canonicalization."""
    return canonicalize_xml(expected) == canonicalize_xml(actual)


def diff_canonical_xml(expected: str, actual: str) -> str | None:
    """Return a short diff summary when canonical forms differ."""
    exp = canonicalize_xml(expected)
    act = canonicalize_xml(actual)
    if exp == act:
        return None
    exp_preview = exp[:240] + ("..." if len(exp) > 240 else "")
    act_preview = act[:240] + ("..." if len(act) > 240 else "")
    return f"expected canonical preview: {exp_preview}\nactual canonical preview:   {act_preview}"


def strip_volatile_attributes(elem: ET.Element) -> None:
    """Remove volatile attributes from an element tree in place."""
    for key in list(elem.attrib):
        if local_name(key) in VOLATILE_ATTRS or (
            local_name(key) == "href"
            and (
                _UUID_HREF.match(elem.attrib.get(key, ""))
                or elem.attrib.get(key, "").startswith("http://codes.wmo.int/")
                or elem.attrib.get(key, "").startswith("https://codes.wmo.int/")
            )
        ):
            del elem.attrib[key]
    for child in elem:
        strip_volatile_attributes(child)


def iter_local_names(elem: ET.Element) -> Iterable[str]:
    """Yield local tag names in document order (testing helper)."""
    yield local_name(elem.tag)
    for child in elem:
        yield from iter_local_names(child)
