"""In-document TAF forecast time links and the failed-preview element name."""

from __future__ import annotations

import re

VALID_PERIOD_ID = "t.valid"

_GML_ID = re.compile(r"""\bgml:id=["']([^"']+)["']""")
_HASH_HREF = re.compile(r"""\bxlink:href=["']#([^"']+)["']""")


def forecast_time_href(target_id: str) -> str:
    """
    Return an in-document fragment for a forecast time id.

    Parameters
    ----------
    target_id :
        ``gml:id`` of a time object in the same TAF document.

    Returns
    -------
    str
        ``#`` plus ``target_id``, or an empty string when ``target_id`` is empty.

    Examples
    --------
    >>> forecast_time_href("t.valid")
    '#t.valid'
    >>> forecast_time_href("")
    ''
    """
    if not target_id:
        return ""
    return f"#{target_id}"


def base_forecast_phenomenon_href() -> str:
    """
    Return the base-forecast phenomenon time link.

    The base forecast covers the TAF valid period, so the link target is that
    period's id.

    Returns
    -------
    str
        Fragment ``#t.valid``.

    Examples
    --------
    >>> base_forecast_phenomenon_href()
    '#t.valid'
    """
    return forecast_time_href(VALID_PERIOD_ID)


def unresolved_internal_hrefs(xml: str) -> tuple[str, ...]:
    """
    Return hash links whose targets are missing from the same document.

    Parameters
    ----------
    xml :
        IWXXM document text.

    Returns
    -------
    tuple[str, ...]
        Target ids that have no matching ``gml:id``.

    Examples
    --------
    >>> unresolved_internal_hrefs('<a gml:id="t.valid"/><b xlink:href="#t.valid"/>')
    ()
    """
    ids = set(_GML_ID.findall(xml))
    missing = [href for href in _HASH_HREF.findall(xml) if href not in ids]
    return tuple(missing)


def failed_preview_nil_element(product: str) -> str:
    """
    Return the nil body element for a soft-preview failure shell.

    Parameters
    ----------
    product :
        Product code such as ``TAF`` or ``METAR``.

    Returns
    -------
    str
        ``baseForecast`` for a TAF. ``observation`` for every other product.

    Examples
    --------
    >>> failed_preview_nil_element("TAF")
    'baseForecast'
    >>> failed_preview_nil_element("METAR")
    'observation'
    """
    if product.upper() == "TAF":
        return "baseForecast"
    return "observation"
