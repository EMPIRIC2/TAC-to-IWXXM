"""Pair TAC groups with the IWXXM elements the converter writes.

Pack match supplies the character offsets. Element names are the local names
the annex3 emitter writes. Occurrence counts earlier elements of the same name
so the second cloud group marks the second cloud layer.
"""

from __future__ import annotations

from typing import TypedDict

from tac_decoding.match import MatchContext, match_tac
from tac_decoding.packs import load_packs

from tac2iwxxm.pack_ir_map import pack_id_for_product

# rule id -> (element local name, line|block, emit|next|previous).
# REPORT means the matched token. next shares the element a later group opens.
# previous shares the element an earlier group already opened.
_Emit = tuple[str, str, str]

_METAR_RULES: dict[str, tuple[_Emit, ...]] = {
    "report_type": (("REPORT", "line", "emit"),),
    "station": (("designator", "line", "emit"),),
    "obs_time": (("observationTime", "block", "emit"),),
    "wind": (("surfaceWind", "block", "emit"),),
    "rvr": (("rvr", "block", "emit"),),
    "weather": (("presentWeather", "line", "emit"),),
    "nsw": (("presentWeather", "line", "emit"),),
    "cloud": (("CloudLayer", "block", "emit"),),
    "nsc": (("cloud", "line", "emit"),),
    "temp_dew": (
        ("airTemperature", "line", "emit"),
        ("dewpointTemperature", "line", "emit"),
    ),
    "qnh": (("qnh", "line", "emit"),),
    "altimeter": (("qnh", "line", "emit"),),
    "trend_kind": (("trendForecast", "block", "emit"),),
    "trend_time": (("timeIndicator", "line", "emit"),),
    "cavok": (("MeteorologicalAerodromeObservation", "line", "emit"),),
    "visibility_sm": (("prevailingVisibility", "line", "emit"),),
    "visibility": (("prevailingVisibility", "line", "emit"),),
    "min_visibility": (("minimumVisibility", "line", "emit"),),
}

_TAF_RULES: dict[str, tuple[_Emit, ...]] = {
    "report_type": (("REPORT", "line", "emit"),),
    "amd": (("TAF", "line", "previous"),),
    "cor": (("TAF", "line", "previous"),),
    "cnl": (("cancelledReportValidPeriod", "block", "emit"),),
    "nil": (("baseForecast", "line", "emit"),),
    "station": (("designator", "line", "emit"),),
    "issue_time": (("issueTime", "block", "emit"),),
    "validity": (("validPeriod", "block", "emit"),),
    "wind": (("surfaceWind", "block", "emit"),),
    "visibility": (("prevailingVisibility", "line", "emit"),),
    "weather": (("weather", "line", "emit"),),
    "cloud": (("CloudLayer", "block", "emit"),),
    "change_indicator": (("changeForecast", "block", "emit"),),
    "from_group": (("changeForecast", "block", "emit"),),
    "probability": (("changeForecast", "block", "next"),),
}

_SIGMET_RULES: dict[str, tuple[_Emit, ...]] = {
    "report_type": (("SIGMET", "line", "emit"),),
    "sequence": (("sequenceNumber", "line", "emit"),),
    "valid": (("validPeriod", "block", "next"),),
    "valid_period": (("validPeriod", "block", "emit"),),
    "intensity": (("SIGMETEvolvingCondition", "line", "emit"),),
    "movement": (("directionOfMotion", "line", "emit"),),
    "cnl": (("cancelledReportValidPeriod", "block", "emit"),),
}

_AIRMET_RULES: dict[str, tuple[_Emit, ...]] = {
    "report_type": (("AIRMET", "line", "emit"),),
    "sequence": (("sequenceNumber", "line", "emit"),),
    "valid": (("validPeriod", "block", "next"),),
    "valid_period": (("validPeriod", "block", "emit"),),
    "obs_or_fcst": (("AIRMETEvolvingConditionCollection", "line", "emit"),),
    "intensity": (("AIRMETEvolvingCondition", "line", "emit"),),
    "cnl": (("cancelledReportValidPeriod", "block", "emit"),),
}

_VAA_RULES: dict[str, tuple[_Emit, ...]] = {
    "dtg": (("issueTime", "block", "emit"),),
    "vaac": (("issuingVolcanicAshAdvisoryCentre", "block", "emit"),),
    "volcano": (("volcano", "block", "emit"),),
    "area": (("stateOrRegion", "line", "emit"),),
    "source_elev": (("sourceElevationAMSL", "line", "emit"),),
    "advisory_nr": (("advisoryNumber", "line", "emit"),),
    "info_source": (("informationSource", "line", "emit"),),
    "eruption_details": (("eruptionDetails", "line", "emit"),),
    "obs_va_dtg": (("VolcanicAshObservedOrEstimatedConditions", "block", "emit"),),
    "obs_va_cld": (("VolcanicAshCloudObservedOrEstimated", "block", "emit"),),
    "fcst_va_cld_6_hr": (("VolcanicAshForecastConditions", "block", "emit"),),
    "fcst_va_cld_12_hr": (("VolcanicAshForecastConditions", "block", "emit"),),
    "fcst_va_cld_18_hr": (("VolcanicAshForecastConditions", "block", "emit"),),
    "rmk": (("remarks", "line", "emit"),),
    "nxt_advisory": (("nextAdvisoryTime", "block", "emit"),),
}

_TCA_RULES: dict[str, tuple[_Emit, ...]] = {
    "dtg": (("issueTime", "block", "emit"),),
    "tcac": (("issuingTropicalCycloneAdvisoryCentre", "block", "emit"),),
    "tc": (("tropicalCycloneName", "block", "emit"),),
    "advisory_nr": (("advisoryNumber", "line", "emit"),),
    "obs_psn": (("TropicalCycloneObservedConditions", "block", "emit"),),
    "cb": (("cumulonimbusCloudLocation", "block", "emit"),),
    "mov": (("movement", "line", "emit"),),
    "intst_change": (("intensityChange", "line", "emit"),),
    "c": (("centralPressure", "line", "emit"),),
    "max_wind": (("maximumSurfaceWindSpeed", "line", "emit"),),
    "fcst_psn_6_hr": (("TropicalCycloneForecastConditions", "block", "emit"),),
    "fcst_psn_12_hr": (("TropicalCycloneForecastConditions", "block", "emit"),),
    "fcst_psn_18_hr": (("TropicalCycloneForecastConditions", "block", "emit"),),
    "fcst_psn_24_hr": (("TropicalCycloneForecastConditions", "block", "emit"),),
    "fcst_max_wind_6_hr": (("maximumSurfaceWindSpeed", "line", "emit"),),
    "fcst_max_wind_12_hr": (("maximumSurfaceWindSpeed", "line", "emit"),),
    "fcst_max_wind_18_hr": (("maximumSurfaceWindSpeed", "line", "emit"),),
    "fcst_max_wind_24_hr": (("maximumSurfaceWindSpeed", "line", "emit"),),
    "rmk": (("remarks", "line", "emit"),),
    "nxt_msg": (("nextAdvisoryTime", "block", "emit"),),
}

_SWXA_RULES: dict[str, tuple[_Emit, ...]] = {
    "dtg": (("issueTime", "block", "emit"),),
    "swxc": (("issuingSpaceWeatherCentre", "block", "emit"),),
    "swx_effect": (("effect", "line", "emit"),),
    "advisory_nr": (("advisoryNumber", "line", "emit"),),
    "obs_swx": (("SpaceWeatherAnalysis", "block", "emit"),),
    "fcst_swx_6_hr": (("SpaceWeatherAnalysis", "block", "emit"),),
    "fcst_swx_12_hr": (("SpaceWeatherAnalysis", "block", "emit"),),
    "fcst_swx_18_hr": (("SpaceWeatherAnalysis", "block", "emit"),),
    "fcst_swx_24_hr": (("SpaceWeatherAnalysis", "block", "emit"),),
    "rmk": (("remarks", "line", "emit"),),
    "nxt_advisory": (("nextAdvisoryTime", "block", "emit"),),
}

_VONA_RULES: dict[str, tuple[_Emit, ...]] = {
    "dtg": (("issueTime", "block", "emit"),),
    "volcano": (("Volcano", "block", "emit"),),
    "area": (("stateOrRegion", "line", "emit"),),
    "source_elev": (("sourceElevation", "block", "emit"),),
    "notice_nr": (("noticeNumber", "line", "emit"),),
    "current_colour_code": (("currentColourCode", "line", "emit"),),
    "previous_colour_code": (("previousColourCode", "line", "emit"),),
    "svo": (("originatingCentre", "block", "emit"),),
    "act_sts": (("activityStatus", "line", "emit"),),
    "ctc": (("contacts", "line", "emit"),),
    "rmk": (("remarks", "line", "emit"),),
    "nxt_notice": (("nextNotice", "line", "emit"),),
}

_PACK_RULES: dict[str, dict[str, tuple[_Emit, ...]]] = {
    "metar": _METAR_RULES,
    "speci": _METAR_RULES,
    "taf": _TAF_RULES,
    "sigmet": _SIGMET_RULES,
    "va_sigmet": {
        **_SIGMET_RULES,
        "report_type": (("VolcanicAshSIGMET", "line", "emit"),),
    },
    "tc_sigmet": {
        **_SIGMET_RULES,
        "report_type": (("TropicalCycloneSIGMET", "line", "emit"),),
    },
    "airmet": _AIRMET_RULES,
    "vaa": _VAA_RULES,
    "tca": _TCA_RULES,
    "swxa": _SWXA_RULES,
    "vona": _VONA_RULES,
}

_BARE_CLOUD = frozenset({"NSC", "SKC", "CLR"})


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


def _emits_for(pack_id: str, rule_id: str, token: str) -> tuple[_Emit, ...]:
    """
    Choose the elements one matched group writes.

    Parameters
    ----------
    pack_id :
        Builtin pack id.
    rule_id :
        Pack rule that matched the group.
    token :
        TAC text of the group.

    Returns
    -------
    tuple[_Emit, ...]
        Element, scope, and whether it opens a new element or shares one.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (_emits_for)
    2
    """
    if pack_id == "taf" and rule_id == "visibility" and token.strip().upper() == "CAVOK":
        return (("MeteorologicalAerodromeForecast", "line", "emit"),)
    if pack_id == "taf" and rule_id == "cloud" and token.strip().upper() in _BARE_CLOUD:
        return (("cloud", "line", "emit"),)
    table = _PACK_RULES.get(pack_id)
    if table is None:
        return ()
    return table.get(rule_id, ())


def _occurrence(counts: dict[str, int], name: str, mode: str) -> int:
    """
    Number of earlier elements with this name, then record a newly opened one.

    Parameters
    ----------
    counts :
        Elements already opened, by local name.
    name :
        Element local name.
    mode :
        ``emit`` opens one. ``next`` and ``previous`` share an open element.

    Returns
    -------
    int
        Zero-based occurrence the preview should mark.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (_occurrence)
    2
    """
    if mode == "next":
        return counts.get(name, 0)
    if mode == "previous":
        return max(counts.get(name, 1) - 1, 0)
    occurrence = counts.get(name, 0)
    counts[name] = occurrence + 1
    return occurrence


def trace_emitted_groups(tac: str, product: str) -> list[GroupTraceRow]:
    """
    List groups in TAC order with the element each one writes.

    A product without an emit map returns an empty list. A match failure also
    returns an empty list so conversion can continue.

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
    if not tac.strip():
        return []
    try:
        packs = {item.id: item for item in load_packs()}
        pack_id = pack_id_for_product(product_u, tac)
        pack = packs.get(pack_id)
        if pack is None or pack_id not in _PACK_RULES:
            return []
        matched = match_tac(tac, pack, context=MatchContext())
    except (OSError, ValueError, TypeError, KeyError):
        return []

    counts: dict[str, int] = {}
    rows: list[GroupTraceRow] = []
    for span in matched.spans:
        token = tac[span.start : span.end]
        emits = _emits_for(pack_id, span.rule_id, token)
        for element, scope, mode in emits:
            name = token if element == "REPORT" else element
            rows.append(
                {
                    "start": span.start,
                    "end": span.end,
                    "token": token,
                    "element": name,
                    "occurrence": _occurrence(counts, name, mode),
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
