"""MSC code-ca vocabulary membership validation (EV-069 / #1033)."""

from __future__ import annotations

from typing import Any

import lxml.etree as _lxml_etree

from iwxxm_validate.ca_eccc_layers import STAGE_CODE_CA
from iwxxm_validate.code_ca_registry import code_ca_membership_ok, is_code_ca_href, normalize_code_ca_href
from iwxxm_validate.models import Issue

etree: Any = _lxml_etree
_XLINK_NS = "http://www.w3.org/1999/xlink"


def validate_code_ca_membership(xml_content: str) -> list[Issue]:
    """
    Validate Canadian code list membership for ``xlink:href`` values.

    Parameters
    ----------
    xml_content :
        IWXXM XML document.

    Returns
    -------
    list[Issue]
        Empty when all code-ca hrefs resolve to known vocabulary members.
    """
    try:
        root = etree.fromstring(xml_content.encode("utf-8"))
    except etree.XMLSyntaxError as exc:
        return [
            Issue(
                severity="error",
                code="XML_SYNTAX_ERROR",
                message=f"XML parsing failed: {exc}",
                layer=STAGE_CODE_CA,
            )
        ]

    issues: list[Issue] = []
    seen: set[str] = set()
    for element in root.iter():
        href = element.get(f"{{{_XLINK_NS}}}href")
        if not href or not is_code_ca_href(href):
            continue
        normalized = normalize_code_ca_href(href)
        if normalized in seen:
            continue
        seen.add(normalized)
        if not code_ca_membership_ok(href):
            issues.append(
                Issue(
                    severity="error",
                    code="CODE_CA_UNKNOWN",
                    message=f"Canadian code list member not recognized: {normalized}",
                    layer=STAGE_CODE_CA,
                    location=element.tag,
                )
            )
    return issues


__all__ = ["validate_code_ca_membership"]
