"""Segment and decode ICAO METAR/SPECI remarks (RMK coded response).

Reuses ``_explain_metar_speci`` (including remark groups) for plain language.
Does not invent new product CORPUS rows — deepens F9 decode.
[Corpus: product §F9] [Corpus: domain]
"""

from __future__ import annotations

import re

from tac_decoding.decode_explain_metar import _explain_metar_speci
from tac_decoding.decode_patterns import (
    _CA_CLOUD_AMOUNTS,
    _CA_CLOUD_ONE,
    _DAY_MAX_MIN,
    _ICE_ACCRETION,
    _PEAK_WIND,
    _PRECIP_3_6H,
    _PRECIP_24H,
    _PRECIP_AMOUNT,
    _PRESSURE_TENDENCY,
    _RMK_WORD,
    _SHORT_PRECIP,
    _SIG_DIR,
    _SIX_HOUR_MAX,
    _SIX_HOUR_MIN,
    _T_GROUP,
    _T_TEMP_ONLY,
)
from tac_decoding.decode_tokens import _iter_tokens, _wx_began_or_ended
from tac_decoding.models.remarks import RemarkDecodeResult, RemarkGroup
from tac_decoding.remark_plain import explain_remark_plain

_SENSOR_AO = frozenset({"AO1", "A01", "AO2", "A02", "AO2A"})
_SENSOR_STATUS = frozenset({"PWINO", "FZRANO", "TSNO", "RVRNO", "PNO", "$"})
_PRESSURE_RAPID = frozenset({"PRESFR", "PRESRR"})
_SLP_CODE = re.compile(r"^SLP\d{3}$")
_SLP_PREFIX = re.compile(r"^SLP")


def _classify_slp_temp(upper: str) -> tuple[str, bool] | None:
    """
    Classify SLP and temperature coded groups.

    Parameters
    ----------
    upper : str
        One uppercased remarks token.

    Returns
    -------
    tuple[str, bool] | None
        Family and shape-ok flag, or ``None`` when this helper does not match.
    """
    if upper == "SLPNO" or _SLP_CODE.match(upper):
        return "sea_level_pressure", True
    if _SLP_PREFIX.match(upper):
        return "sea_level_pressure", False
    if _T_GROUP.match(upper) or _T_TEMP_ONLY.match(upper):
        return "temperature_tenths", True
    if upper.startswith("T") and len(upper) > 1 and upper[1:].isdigit():
        return "temperature_tenths", False
    if _SIX_HOUR_MAX.match(upper) or _SIX_HOUR_MIN.match(upper):
        return "six_hour_temperature", True
    if _DAY_MAX_MIN.match(upper):
        return "day_max_min", True
    return None


def _classify_precip_pressure_ice(upper: str) -> tuple[str, bool] | None:
    """
    Classify precip, pressure-tendency/rapid, and ice accretion groups.

    Parameters
    ----------
    upper : str
        One uppercased remarks token.

    Returns
    -------
    tuple[str, bool] | None
        Family and shape-ok flag, or ``None`` when this helper does not match.
    """
    if _PRECIP_AMOUNT.match(upper) or _SHORT_PRECIP.match(upper):
        return "precip_hourly", True
    if upper.startswith("P") and upper[1:].isdigit() and len(upper) in {3, 4, 5}:
        return "precip_hourly", False
    if _PRECIP_3_6H.match(upper) or _PRECIP_24H.match(upper):
        return "precip_period", True
    if _PRESSURE_TENDENCY.match(upper):
        return "pressure_tendency", True
    if upper.startswith("5") and len(upper) == 5 and not upper[1:].isdigit():
        return "pressure_tendency", False
    if upper in _PRESSURE_RAPID:
        return "pressure_rapid", True
    if _ICE_ACCRETION.match(upper):
        return "ice_accretion", True
    if upper.startswith("I") and len(upper) > 1 and upper[1:].isdigit():
        return "ice_accretion", False
    return None


def _classify_lexicon(upper: str) -> tuple[str, bool] | None:
    """
    Classify weather-time, sensor, peak wind, clouds, and prose groups.

    Parameters
    ----------
    upper : str
        One uppercased remarks token.

    Returns
    -------
    tuple[str, bool] | None
        Family and shape-ok flag, or ``None`` when this helper does not match.
    """
    if _wx_began_or_ended(upper) is not None:
        return "wx_begin_end", True
    if upper in _SENSOR_STATUS:
        return "sensor_status", True
    if _PEAK_WIND.match(upper) or upper in {"PK", "WND"}:
        return "peak_wind", True
    if _CA_CLOUD_AMOUNTS.match(upper) or (_CA_CLOUD_ONE.match(upper) and upper not in _RMK_WORD):
        return "canadian_cloud", True
    if explain_remark_plain(upper) is not None:
        return "plain_national", True
    if upper in _RMK_WORD:
        return "prose", True
    if upper in _SIG_DIR:
        return "direction", True
    return None


def classify_remark_token(token: str) -> tuple[str, bool]:
    """
    Map one remarks token to a catalog family and shape-ok flag.

    Parameters
    ----------
    token : str
        One group from after ``RMK`` (any case).

    Returns
    -------
    tuple[str, bool]
        ``(family, shape_ok)``. ``shape_ok`` is ``False`` when the token looks
        like a known family but fails the coded shape (validation failure).
    """
    upper = token.upper()
    if upper == "RMK":
        return "marker", True
    if upper in _SENSOR_AO:
        return "sensor_ao", True
    for matcher in (_classify_slp_temp, _classify_precip_pressure_ice, _classify_lexicon):
        hit = matcher(upper)
        if hit is not None:
            return hit
    return "unknown", False


def segment_remarks(tac: str) -> list[tuple[int, int, str]]:
    """
    Return token spans for the remarks coded response after ``RMK``.

    Includes the ``RMK`` marker when present. Stops at report terminator ``=``.

    Parameters
    ----------
    tac : str
        Full METAR/SPECI (or fragment containing ``RMK``).

    Returns
    -------
    list[tuple[int, int, str]]
        ``(start, end, text)`` spans, empty when no ``RMK``.
    """
    tokens = _iter_tokens(tac)
    start_idx: int | None = None
    for index, (_start, _end, text) in enumerate(tokens):
        if text.upper() == "RMK":
            start_idx = index
            break
    if start_idx is None:
        return []
    out: list[tuple[int, int, str]] = []
    for start, end, text in tokens[start_idx:]:
        if text == "=":
            break
        out.append((start, end, text))
    return out


def decode_remarks(tac: str) -> RemarkDecodeResult:
    """
    Segment and algorithmically decode remarks code groups.

    Parameters
    ----------
    tac : str
        METAR/SPECI text that may contain ``RMK …``.

    Returns
    -------
    RemarkDecodeResult
        Structured groups with family, validity, and plain-language meaning.
    """
    spans = segment_remarks(tac)
    if not spans:
        return RemarkDecodeResult(groups=[], has_remarks=False)
    seen: dict[str, int] = {}
    groups: list[RemarkGroup] = []
    for start, end, text in spans:
        upper = text.upper()
        family, shape_ok = classify_remark_token(upper)
        explanation = _explain_metar_speci(text, product="METAR", seen=seen) or ""
        if upper == "RMK":
            valid = True
            explanation = explanation or "Remarks section"
        elif shape_ok and explanation:
            valid = True
        elif shape_ok and family != "unknown":
            # Known family shape; explainer may defer across multi-token state.
            valid = True
            explanation = explanation or family.replace("_", " ")
        else:
            valid = False
        groups.append(
            RemarkGroup(
                start=start,
                end=end,
                code=text,
                family=family,
                explanation=explanation,
                valid=valid,
            )
        )
    return RemarkDecodeResult(groups=groups, has_remarks=True)


def shift_remark_groups(groups: list[RemarkGroup], offset: int) -> list[RemarkGroup]:
    """
    Translate remark group offsets into a parent document string.

    Parameters
    ----------
    groups : list[RemarkGroup]
        Groups whose spans are shifted.
    offset : int
        Character offset added to spans.

    Returns
    -------
    list[RemarkGroup]
        Copies with shifted ``start`` / ``end``.
    """
    if offset == 0:
        return list(groups)
    return [
        RemarkGroup(
            start=group.start + offset,
            end=group.end + offset,
            code=group.code,
            family=group.family,
            explanation=group.explanation,
            valid=group.valid,
        )
        for group in groups
    ]


__all__ = [
    "classify_remark_token",
    "decode_remarks",
    "segment_remarks",
    "shift_remark_groups",
]
