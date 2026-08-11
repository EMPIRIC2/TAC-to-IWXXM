"""W3C C14N helpers for Quality metrics match/diff (EV-055 / #982).

Applies **W3C Canonical XML 1.0** (lxml ``method='c14n'``) after removing
whitespace-only text nodes so pretty-print vs compact peers compare equal
without losing semantic text differences.

Does **not** replace ADR-032 ``metar_shared.xml_canonical.canonicalize_xml``.
"""

from __future__ import annotations

from typing import Any

import lxml.etree as _lxml_etree

etree: Any = _lxml_etree


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
    Return W3C C14N 1.0 form of ``xml_content`` (UTF-8 text).

    Parameters
    ----------
    xml_content :
        Well-formed XML document text.

    Returns
    -------
    str
        Canonical XML 1.0 serialization.

    Raises
    ------
    ValueError
        If ``xml_content`` is not well-formed XML.
    """
    try:
        root = etree.fromstring(xml_content.encode("utf-8"))
    except etree.XMLSyntaxError as exc:
        raise ValueError(f"XML parse failed for C14N: {exc}") from exc
    _strip_whitespace_only_text(root)
    return etree.tostring(root, method="c14n").decode("utf-8")


def c14n_equal(left: str, right: str) -> bool:
    """Return True when C14N forms of ``left`` and ``right`` are identical."""
    return c14n_xml(left) == c14n_xml(right)


__all__ = ["c14n_equal", "c14n_xml"]
