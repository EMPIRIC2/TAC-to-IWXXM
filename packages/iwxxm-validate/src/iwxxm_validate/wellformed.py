"""XML well-formedness check via lxml."""

from __future__ import annotations

from typing import Any

import lxml.etree as _lxml_etree

from iwxxm_validate.models import Issue

# lxml ships without complete type stubs; bind as Any for strict basedpyright.
etree: Any = _lxml_etree

_LAYER = "wellformed"


def run_wellformed_lxml(xml_content: str) -> list[Issue]:
    """Return issues when ``xml_content`` is not well-formed XML."""
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
