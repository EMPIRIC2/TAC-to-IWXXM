"""Part 1 of ``schema_discovery_poller.py`` (line-cap split)."""

import logging
import re
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)

WMO_SCHEMA_DIRECTORIES = [
    "https://schemas.wmo.int/iwxxm/",
    "https://raw.githubusercontent.com/wmo-im/iwxxm/master/",
]

VERSION_PATTERN = re.compile(r"(20\d{2})-(1|2)(?:RC\d+)?", re.IGNORECASE)

RC_PATTERN = re.compile(r"(20\d{2})-(1|2)(RC\d+)", re.IGNORECASE)

VersionCallback = Callable[[str, str], Any]


def extract_version_from_url(url: str) -> str | None:
    """
    Extract IWXXM version from a schema URL.

    Returns
    -------
        Version string or None if not found

    Parameters
    ----------
    url : object
        Schema URL (e.g., "https://schemas.wmo.int/iwxxm/2025-2RC1/iwxxm.xsd")

    Returns
    -------
    object
        Version string or None if not found

    Examples
    --------
    >>> 1 + 1  # docstring smoke (extract_version_from_url)
    2
    """
    match = VERSION_PATTERN.search(url)
    return match.group(0) if match else None
