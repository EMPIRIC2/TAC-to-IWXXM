"""Canonical XML helpers for Quality Metrics match and diff.

Canonical XML means W3C Canonical XML 1.0 (also called C14N). This module
strips volatile IWXXM attributes, removes whitespace-only text nodes, then
applies Canonical XML so two documents can match when only formatting differs.

Pipeline (ADR-035 / ``D-S064-c14n-volatile=1``):

1. Strip volatile attributes (same local-name / UUID-href / ``codes.wmo.int`` href
   rules as ADR-032 - duplicated here; do not import ``metar_shared``).
2. Remove whitespace-only text nodes.
3. Apply W3C Canonical XML 1.0 (lxml ``method='c14n'``).

Does **not** replace ADR-032 ``metar_shared.xml_canonical.canonicalize_xml`` (no
sibling reordering; output is real XML, not a Python ``repr``).

Alias names ``c14n_xml`` and ``c14n_equal`` remain for one CalVer window
(EV-layout-dx). Prefer ``to_canonical_xml`` and ``canonical_xml_equal``.
"""

from __future__ import annotations

import re
from typing import Any

import lxml.etree as _lxml_etree

etree: Any = _lxml_etree

# Dynamic IWXXM/GML attributes omitted from Quality-metrics equality (ADR-032 parity).
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


def _local_name(name: str) -> str:
    """Return the local part of an XML attribute or element name."""
    if name.startswith("{"):
        return name.rsplit("}", 1)[-1]
    if ":" in name:
        return name.split(":", 1)[-1]
    return name


def _norm_text(value: str | None) -> str:
    """Collapse whitespace in an attribute value for volatile checks."""
    if value is None:
        return ""
    return " ".join(value.split())


def _is_volatile_attr(key: str, value: str) -> bool:
    """Return True when an attribute must be omitted before Canonical XML."""
    local = _local_name(key)
    if local in VOLATILE_ATTRS:
        return True
    norm_val = _norm_text(value)
    if _UUID_VALUE.match(norm_val):
        return True
    return bool(
        local == "href"
        and (
            _UUID_HREF.match(norm_val)
            or norm_val.startswith("http://codes.wmo.int/")
            or norm_val.startswith("https://codes.wmo.int/")
        )
    )


def _strip_volatile_attributes(node: Any) -> None:
    """Remove volatile attributes from ``node`` and its descendants in place."""
    for key in list(node.attrib):
        if _is_volatile_attr(key, node.attrib.get(key, "")):
            del node.attrib[key]
    for child in node:
        _strip_volatile_attributes(child)


def _strip_whitespace_only_text(node: Any) -> None:
    """Clear whitespace-only element text and tails under ``node``."""
    for child in list(node):
        _strip_whitespace_only_text(child)
    # Element text / tail that is only whitespace is insignificant for IWXXM compare
    if node.text is not None and not node.text.strip():
        node.text = None
    if node.tail is not None and not node.tail.strip():
        node.tail = None


def to_canonical_xml(xml_content: str) -> str:
    """
    Return Canonical XML 1.0 form of ``xml_content`` after volatile-attr strip.

    Parameters
    ----------
    xml_content : str
        Well-formed XML document text.

    Returns
    -------
    str
        Canonical XML 1.0 serialization (post-volatile strip + whitespace strip).

    Raises
    ------
    ValueError
        If ``xml_content`` is not well-formed XML.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (to_canonical_xml)
    2
    """
    try:
        root = etree.fromstring(xml_content.encode("utf-8"))
    except etree.XMLSyntaxError as exc:
        raise ValueError(f"XML parse failed for Canonical XML: {exc}") from exc
    _strip_volatile_attributes(root)
    _strip_whitespace_only_text(root)
    return etree.tostring(root, method="c14n").decode("utf-8")


def canonical_xml_equal(left: str, right: str) -> bool:
    """
    Return True when Canonical XML forms of ``left`` and ``right`` are identical.

    Parameters
    ----------
    left : str
        First XML document text.
    right : str
        Second XML document text.

    Returns
    -------
    bool
        True when Canonical XML forms of ``left`` and ``right`` are identical.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (canonical_xml_equal)
    2
    """
    return to_canonical_xml(left) == to_canonical_xml(right)


# Compatibility aliases (one CalVer window; EV-layout-dx). Prefer the names above.
c14n_xml = to_canonical_xml
c14n_equal = canonical_xml_equal

__all__ = [
    "VOLATILE_ATTRS",
    "c14n_equal",
    "c14n_xml",
    "canonical_xml_equal",
    "to_canonical_xml",
]
