"""AFS COLLECT + multi-version IWXXM namespace hooks (F16-F19 / EV-023 T6.3).

APAC FAQ §3.4 / §14.7: all AFS IWXXM must use COLLECT before send; when a
bulletin mixes IWXXM package lines, each member group must declare
``http://icao.int/iwxxm/{version}``.

These helpers are **dissemination / bulletin** path hooks - not single-report
``tac2iwxxm.convert`` SoT (S02.M2). Full COLLECT packaging remains ops/F16-F19.
"""

from __future__ import annotations

import re
from typing import Final

COLLECT_NS: Final[str] = "http://def.wmo.int/collect/2014"
IWXXM_NS_PREFIX: Final[str] = "http://icao.int/iwxxm/"
# FAQ §3.4 - AFS exchange mandates COLLECT wrap (informative ops mandate).
AFS_REQUIRES_COLLECT: Final[bool] = True

_IWXXM_NS_DECL = re.compile(
    r'xmlns(?::\w+)?\s*=\s*"(?P<uri>http://icao\.int/iwxxm/[^"]+)"',
    re.IGNORECASE,
)
_COLLECT_ROOT = re.compile(
    r"<(?:\w+:)?MeteorologicalBulletin\b",
    re.IGNORECASE,
)
_COLLECT_NS_PRESENT = re.compile(
    r"https?://def\.wmo\.int/collect/2014",
    re.IGNORECASE,
)


def iwxxm_namespace_uri(version: str) -> str:
    """
    Return the ICAO IWXXM package namespace for a release line.

    Parameters
    ----------
    version : str
        IWXXM package version (e.g. ``"2025-2"``).

    Returns
    -------
    str
        ``http://icao.int/iwxxm/{version}``.

    Raises
    ------
    ValueError
        If ``version`` is empty or contains path separators.
    """
    v = version.strip()
    if not v or "/" in v or "\\" in v or " " in v:
        raise ValueError(f"invalid IWXXM version for namespace: {version!r}")
    return f"{IWXXM_NS_PREFIX}{v}"


def is_collect_bulletin(xml: str) -> bool:
    """
    Return whether XML looks like a WMO ``collect:MeteorologicalBulletin``.

    Parameters
    ----------
    xml : str
        Document text.

    Returns
    -------
    bool
        True when the COLLECT root and collect namespace appear.
    """
    return bool(_COLLECT_ROOT.search(xml) and _COLLECT_NS_PRESENT.search(xml))


def member_iwxxm_namespace_uris(xml: str) -> list[str]:
    """
    Collect distinct ``http://icao.int/iwxxm/{version}`` declarations in order.

    Parameters
    ----------
    xml : str
        COLLECT bulletin or member fragment.

    Returns
    -------
    list of str
        Unique namespace URIs in document order of first appearance.
    """
    seen: set[str] = set()
    out: list[str] = []
    for match in _IWXXM_NS_DECL.finditer(xml):
        uri = match.group("uri")
        if uri not in seen:
            seen.add(uri)
            out.append(uri)
    return out


def collect_namespace_issues(xml: str) -> list[str]:
    """
    Return human-readable issues for COLLECT multi-version namespace policy.

    Parameters
    ----------
    xml : str
        Expected COLLECT bulletin XML.

    Returns
    -------
    list of str
        Empty when the document is a COLLECT bulletin and every IWXXM member
        declaration uses ``http://icao.int/iwxxm/{version}``. Non-empty when
        the root is not COLLECT, COLLECT has no IWXXM member NS, or a
        declaration is malformed.
    """
    issues: list[str] = []
    if not is_collect_bulletin(xml):
        issues.append("not a collect:MeteorologicalBulletin (AFS COLLECT mandate)")
        return issues

    uris = member_iwxxm_namespace_uris(xml)
    if not uris:
        issues.append("COLLECT has no http://icao.int/iwxxm/{version} member declarations")
        return issues

    for uri in uris:
        suffix = uri[len(IWXXM_NS_PREFIX) :] if uri.startswith(IWXXM_NS_PREFIX) else ""
        if not suffix or "/" in suffix:
            issues.append(f"malformed IWXXM namespace URI: {uri}")
    return issues
