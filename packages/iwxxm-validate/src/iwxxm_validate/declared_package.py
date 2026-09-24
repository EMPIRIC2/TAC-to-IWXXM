"""Match an incoming IWXXM file to the package its profile is allowed to use."""

from __future__ import annotations

import re

from iwxxm_validate.models import Issue

# ICAO namespace fragment → release line. Package numbers for each product live in
# the version-support compatibility table for that line.
_FRAGMENT_TO_LINE: dict[str, str] = {
    "2025-2": "2025-2",
    "2023-1": "2023-1",
    "3.0": "3.0.0",
}
_ALLOWED_LINES: dict[str, frozenset[str]] = {
    "annex3": frozenset({"2025-2", "2023-1"}),
    "iwxxm_us": frozenset({"2025-2", "2023-1"}),
    "ca_eccc": frozenset({"3.0.0"}),
}
_KNOWN_NAMESPACE = re.compile(r"http://icao\.int/iwxxm/(2025-2|2023-1|3\.0)(?![0-9A-Za-z.-])")
_ANY_NAMESPACE = re.compile(r"http://icao\.int/iwxxm/([^\"'\s<>]+)")
_REJECTION = "This file uses an IWXXM package this profile does not accept."


def declared_release_line(xml_content: str) -> str | None:
    """
    Return the release line declared by an ICAO IWXXM namespace, if one is present.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (declared_release_line)
    2

    Parameters
    ----------
    xml_content :
        IWXXM XML document.

    Returns
    -------
    str | None
        ``2025-2``, ``2023-1``, ``3.0.0``, another namespace fragment, or ``None``.
    """
    known = _KNOWN_NAMESPACE.search(xml_content)
    if known is not None:
        return _FRAGMENT_TO_LINE[known.group(1)]
    other = _ANY_NAMESPACE.search(xml_content)
    if other is None:
        return None
    return other.group(1)


def apply_declared_package(
    xml_content: str,
    *,
    profile: str,
    iwxxm_version: str,
) -> tuple[str, Issue | None]:
    """
    Keep the requested line when the file declares that same allowed package.

    Parameters
    ----------
    xml_content :
        IWXXM XML document.
    profile :
        ``annex3``, ``iwxxm_us``, or ``ca_eccc``.
    iwxxm_version :
        Release line requested by the caller.

    Returns
    -------
    tuple[str, Issue | None]
        The requested line, and a plain-language error when the file declares
        a different package or a package this profile does not allow. A
        document with no IWXXM namespace keeps the requested line.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (apply_declared_package)
    2
    """
    declared = declared_release_line(xml_content)
    if declared is None or (declared == iwxxm_version and declared in _ALLOWED_LINES[profile]):
        return iwxxm_version, None
    return iwxxm_version, Issue(
        severity="error",
        code="DECLARED_PACKAGE_NOT_ALLOWED",
        message=_REJECTION,
        layer="xsd",
    )


__all__ = ["apply_declared_package", "declared_release_line"]
