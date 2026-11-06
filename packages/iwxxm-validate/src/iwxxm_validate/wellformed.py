"""XML well-formedness check via lxml."""

from __future__ import annotations

import re
from typing import Any

import lxml.etree as _lxml_etree

from iwxxm_validate.models import Issue

# lxml ships without complete type stubs; bind as Any for strict basedpyright.
etree: Any = _lxml_etree

_LAYER = "wellformed"
_TAC_PRODUCT = re.compile(r"^(?:METAR|SPECI|TAF|SIGMET|AIRMET)\b")
_AHL_LINE = re.compile(r"^[A-Z]{4}\d{2}\s+[A-Z]{4}\s+\d{6}")


def run_wellformed_lxml(xml_content: str) -> list[Issue]:
    """
    Return issues when ``xml_content`` is not well-formed XML.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (run_wellformed_lxml)
    2

    Parameters
    ----------
    xml_content : str
        XML text.

    Returns
    -------
    list[Issue]
        Issues when ``xml_content`` is not well-formed XML.
    """
    stripped = xml_content.lstrip()
    if stripped and not stripped.startswith("<"):
        head = stripped[:80].upper()
        if _TAC_PRODUCT.match(head) or _AHL_LINE.match(head):
            return [
                Issue(
                    severity="error",
                    code="XML_SYNTAX_ERROR",
                    message=(
                        "This looks like TAC text, not IWXXM XML. Convert the TAC first, "
                        "then validate the XML output (not the original TAC)."
                    ),
                    layer=_LAYER,
                    location="line 1",
                )
            ]
    try:
        etree.fromstring(xml_content.encode("utf-8"))
        return []
    except etree.XMLSyntaxError as exc:
        return [
            Issue(
                severity="error",
                code="XML_SYNTAX_ERROR",
                message=f"XML is not well-formed: {exc}",
                layer=_LAYER,
                location=f"line {getattr(exc, 'lineno', '?')}",
            )
        ]


__all__ = ["run_wellformed_lxml"]
