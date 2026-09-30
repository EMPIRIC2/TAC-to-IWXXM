"""Pair METAR and SPECI groups with the IWXXM elements the converter writes.

Pack match supplies the character offsets. Element names are the local names
the METAR/SPECI emitter writes. Occurrence counts earlier elements of the same
name so the second cloud group marks the second cloud layer.
"""

from __future__ import annotations

from typing import TypedDict

from tac_decoding.match import MatchContext, match_tac
from tac_decoding.packs import load_packs

from tac2iwxxm.pack_ir_map import pack_id_for_product

_METAR_SPECI = frozenset({"METAR", "SPECI"})

# rule id -> one or more (element local name, line|block).
# REPORT means the matched token (METAR or SPECI).
_RULES: dict[str, tuple[tuple[str, str], ...]] = {
    "report_type": (("REPORT", "line"),),
    "station": (("designator", "line"),),
    "obs_time": (("observationTime", "block"),),
    "wind": (("surfaceWind", "block"),),
    "rvr": (("rvr", "block"),),
    "weather": (("presentWeather", "line"),),
    "nsw": (("presentWeather", "line"),),
    "cloud": (("CloudLayer", "block"),),
    "nsc": (("cloud", "line"),),
    "temp_dew": (("airTemperature", "line"), ("dewpointTemperature", "line")),
    "qnh": (("qnh", "line"),),
    "altimeter": (("qnh", "line"),),
    "trend_kind": (("trendForecast", "block"),),
    "trend_time": (("timeIndicator", "line"),),
    "cavok": (("MeteorologicalAerodromeObservation", "line"),),
    "visibility_sm": (("prevailingVisibility", "line"),),
    "visibility": (("prevailingVisibility", "line"),),
    "min_visibility": (("minimumVisibility", "line"),),
}


class GroupTraceRow(TypedDict):
    """
    One TAC group and the IWXXM element it produced.

    Attributes
    ----------
    start :
        Inclusive offset into the TAC that was matched.
    end :
        Exclusive offset into that TAC.
    token :
        The TAC text of the group.
    element :
        Local element name, without a namespace prefix.
    occurrence :
        How many earlier groups used this element name.
    scope :
        ``line`` marks the opening tag. ``block`` marks through the closing tag.
    """

    start: int
    end: int
    token: str
    element: str
    occurrence: int
    scope: str


def trace_emitted_groups(tac: str, product: str) -> list[GroupTraceRow]:
    """
    List METAR/SPECI groups in TAC order with the element each one writes.

    Other products return an empty list. A match failure also returns an empty
    list so conversion can continue.

    Parameters
    ----------
    tac :
        One TAC report.
    product :
        Convert product id.

    Returns
    -------
    list[GroupTraceRow]
        Rows the preview can use to mark XML. Empty when this product has no
        emit map or the report does not match.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (trace_emitted_groups)
    2
    """
    product_u = product.strip().upper()
    if product_u not in _METAR_SPECI or not tac.strip():
        return []
    try:
        packs = {item.id: item for item in load_packs()}
        pack = packs.get(pack_id_for_product(product_u, tac))
        if pack is None:
            return []
        matched = match_tac(tac, pack, context=MatchContext())
    except (OSError, ValueError, TypeError, KeyError):
        return []

    counts: dict[str, int] = {}
    rows: list[GroupTraceRow] = []
    for span in matched.spans:
        rules = _RULES.get(span.rule_id)
        if rules is None:
            continue
        token = tac[span.start : span.end]
        for element, scope in rules:
            name = token if element == "REPORT" else element
            occurrence = counts.get(name, 0)
            counts[name] = occurrence + 1
            rows.append(
                {
                    "start": span.start,
                    "end": span.end,
                    "token": token,
                    "element": name,
                    "occurrence": occurrence,
                    "scope": scope,
                }
            )
    return rows


def trace_entries(entries: list[tuple[str, int]], product: str) -> list[GroupTraceRow]:
    """
    Trace each report and shift offsets by its position in the original text.

    Parameters
    ----------
    entries :
        ``(report text, offset into the editor text)`` pairs.
    product :
        Convert product id.

    Returns
    -------
    list[GroupTraceRow]
        Rows whose offsets refer to the original text.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (trace_entries)
    2
    """
    shifted: list[GroupTraceRow] = []
    for text, offset in entries:
        shifted.extend(
            {
                "start": row["start"] + offset,
                "end": row["end"] + offset,
                "token": row["token"],
                "element": row["element"],
                "occurrence": row["occurrence"],
                "scope": row["scope"],
            }
            for row in trace_emitted_groups(text, product)
        )
    return shifted
