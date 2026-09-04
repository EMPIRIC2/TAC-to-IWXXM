"""Exchange packaging overlays (F36 / #921 / GLOBAL_AFS).

Post-convert hooks that wrap single-report IWXXM for AFS COLLECT bulletin
exchange. Invoked on packaging paths only - not on convert-only routes.
"""

from __future__ import annotations

import re
import uuid

from dissemination.collect_namespaces import COLLECT_NS, is_collect_bulletin
from dissemination.exchange_registry import (
    CANONICAL_AFI,
    CANONICAL_APAC_ROBEX,
    CANONICAL_CAR_SAM,
    CANONICAL_EUR_RODEX,
    CANONICAL_GLOBAL_AFS,
    resolve_exchange_profile,
)

_XML_DECL = re.compile(r"^\s*<\?xml[^?]*\?>\s*", re.IGNORECASE)


def apply_exchange_packaging(
    xml: str,
    *,
    exchange_profile: str,
    bulletin_identifier: str | None = None,
) -> str:
    """
    Apply an exchange overlay to single-report IWXXM XML.

    Parameters
    ----------
    xml :
        Converted IWXXM document (one product root).
    exchange_profile :
        Exchange profile wire id (e.g. ``GLOBAL_AFS``).
    bulletin_identifier :
        Optional FTBP ``collect:bulletinIdentifier`` value.

    Returns
    -------
    str
        Packaged XML (COLLECT wrap for ``GLOBAL_AFS`` when not already COLLECT).

    Raises
    ------
    ValueError
        When the exchange profile is unknown or not implemented.
    """
    resolved = resolve_exchange_profile(exchange_profile)
    if resolved is None:
        raise ValueError(f"unknown exchange profile: {exchange_profile!r}")
    if resolved.canonical in (
        CANONICAL_GLOBAL_AFS,
        CANONICAL_APAC_ROBEX,
        CANONICAL_EUR_RODEX,
        CANONICAL_AFI,
        CANONICAL_CAR_SAM,
    ):
        # Regional P0 stubs: same COLLECT baseline as GLOBAL_AFS; handbook rules deepen later.
        return wrap_global_afs_collect(xml, bulletin_identifier=bulletin_identifier)
    raise ValueError(f"exchange profile not implemented: {exchange_profile!r}")


def wrap_global_afs_collect(
    xml: str,
    *,
    bulletin_identifier: str | None = None,
) -> str:
    """
    Wrap member IWXXM in a ``collect:MeteorologicalBulletin`` shell.

    Parameters
    ----------
    xml :
        Single-report IWXXM XML.
    bulletin_identifier :
        Optional ``collect:bulletinIdentifier`` (defaults to placeholder).

    Returns
    -------
    str
        COLLECT bulletin XML; unchanged when input is already COLLECT.
    """
    if is_collect_bulletin(xml):
        return xml

    member = _XML_DECL.sub("", xml.strip())
    bid = bulletin_identifier or "A_UNKNOWN.xml"
    gid = f"uuid.{uuid.uuid4()}"
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f"<collect:MeteorologicalBulletin\n"
        f'    xmlns:collect="{COLLECT_NS}"\n'
        f'    xmlns:gml="http://www.opengis.net/gml/3.2"\n'
        f'    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
        f'    gml:id="{gid}">\n'
        f"    <collect:meteorologicalInformation>\n"
        f"{member}\n"
        f"    </collect:meteorologicalInformation>\n"
        f"    <collect:bulletinIdentifier>{bid}</collect:bulletinIdentifier>\n"
        f"</collect:MeteorologicalBulletin>"
    )


__all__ = [
    "apply_exchange_packaging",
    "wrap_global_afs_collect",
]
