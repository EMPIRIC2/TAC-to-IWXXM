"""W3C C14N helpers for Quality metrics match/diff (EV-055 / #982).

Pipeline (ADR-035 / ``D-S064-c14n-volatile=1``):

1. Strip volatile attributes (same local-name / UUID-href / ``codes.wmo.int`` href
   rules as ADR-032 — duplicated here; do not import ``metar_shared``).
2. Remove whitespace-only text nodes.
3. Apply **W3C Canonical XML 1.0** (lxml ``method='c14n'``).

Does **not** replace ADR-032 ``metar_shared.xml_canonical.canonicalize_xml`` (no sibling
reordering; output is real XML, not a Python ``repr``).
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
    """Return the local part of a Clark-notation or prefixed attribute/tag name."""
    if name.startswith("{"):
        return name.rsplit("}", 1)[-1]
    if ":" in name:
        return name.split(":", 1)[-1]
    return name


def _norm_text(value: str | None) -> str:
    if value is None:
        return ""
    return " ".join(value.split())


def _is_volatile_attr(key: str, value: str) -> bool:
    """Return True when ``key``/``value`` should be omitted from Quality-metrics compare."""
    local = _local_name(key)
    if local in VOLATILE_ATTRS:
        return True
    norm_val = _norm_text(value)
    if _UUID_VALUE.match(norm_val):
        return True
    if local == "href" and (
        _UUID_HREF.match(norm_val)
        or norm_val.startswith("http://codes.wmo.int/")
        or norm_val.startswith("https://codes.wmo.int/")
    ):
        return True
    return False


def _strip_volatile_attributes(node: Any) -> None:
    """Remove volatile attributes from an lxml element tree in place."""
    for key in list(node.attrib):
        if _is_volatile_attr(key, node.attrib.get(key, "")):
            del node.attrib[key]
    for child in node:
        _strip_volatile_attributes(child)


def _strip_whitespace_only_text(node: Any) -> None:
    """Remove insignificant whitespace-only text nodes (in-place)."""
    for child in list(node):
        _strip_whitespace_only_text(child)
    # Element text / tail that is only whitespace is insignificant for IWXXM compare
    if node.text is not None and not node.text.strip():
        node.text = None
    if node.tail is not None and not node.tail.strip():
        node.tail = None


def c14n_xml(xml_content: str) -> str:
    """
    Return W3C C14N 1.0 form of ``xml_content`` after volatile-attr strip (UTF-8 text).

    Parameters
    ----------
    xml_content :
        Well-formed XML document text.

    Returns
    -------
    str
        Canonical XML 1.0 serialization (post–volatile strip + whitespace strip).

    Raises
    ------
    ValueError
        If ``xml_content`` is not well-formed XML.
    """
    try:
        root = etree.fromstring(xml_content.encode("utf-8"))
    except etree.XMLSyntaxError as exc:
        raise ValueError(f"XML parse failed for C14N: {exc}") from exc
    _strip_volatile_attributes(root)
    _strip_whitespace_only_text(root)
    return etree.tostring(root, method="c14n").decode("utf-8")


def c14n_equal(left: str, right: str) -> bool:
    """Return True when C14N forms of ``left`` and ``right`` are identical."""
    return c14n_xml(left) == c14n_xml(right)


__all__ = ["VOLATILE_ATTRS", "c14n_equal", "c14n_xml"]
