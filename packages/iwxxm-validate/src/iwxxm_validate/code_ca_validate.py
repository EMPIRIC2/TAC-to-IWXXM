"""MSC code-ca vocabulary membership + deviation checks (EV-069 / #1033 / #1034)."""

from __future__ import annotations

from typing import Any

import lxml.etree as _lxml_etree

from iwxxm_validate.ca_eccc_layers import STAGE_CODE_CA
from iwxxm_validate.code_ca_registry import code_ca_membership_ok, is_code_ca_href, normalize_code_ca_href
from iwxxm_validate.code_list_policy import load_code_list_policy
from iwxxm_validate.models import Issue

etree: Any = _lxml_etree
_XLINK_NS = "http://www.w3.org/1999/xlink"
_DEFAULT_PROFILE = "CA_ECCC"


def validate_code_ca_membership(xml_content: str, *, profile: str = _DEFAULT_PROFILE) -> list[Issue]:
    """
    Validate Canadian code list membership and disallowed global URIs.

    Parameters
    ----------
    xml_content : str
        IWXXM XML document.
    profile : str
        Semantic profile id (default ``CA_ECCC``).

    Returns
    -------
    list[Issue]
        Empty when code-ca hrefs are known and no disallowed global URIs appear.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (validate_code_ca_membership)
    2
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

    policy = load_code_list_policy(profile)
    disallowed = policy.disallowed_global_uris()
    issues: list[Issue] = []
    seen_ca: set[str] = set()
    seen_global: set[str] = set()
    for element in root.iter():
        href = element.get(f"{{{_XLINK_NS}}}href")
        if not href:
            continue
        normalized = normalize_code_ca_href(href)
        if is_code_ca_href(href):
            if normalized in seen_ca:
                continue
            seen_ca.add(normalized)
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
            continue
        if normalized in disallowed and normalized not in seen_global:
            seen_global.add(normalized)
            issues.append(
                Issue(
                    severity="error",
                    code="CODE_LIST_GLOBAL_DISALLOWED",
                    message=(
                        f"Global code URI disallowed under profile {policy.profile}; "
                        f"use the national code-list URI instead: {normalized}"
                    ),
                    layer=STAGE_CODE_CA,
                    location=element.tag,
                )
            )
    return issues


__all__ = ["validate_code_ca_membership"]
