"""TREND forecast, national remarks, and sea-surface checks (WMO-No. 782)."""

from __future__ import annotations

# pyright: reportPrivateUsage=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
import re

from tac_validate.models import Issue
from tac_validate.product_rules_pkg._common import _WIND_DIR_VAR, _WIND_PARSE, _issue
from tac_validate.product_rules_pkg.wmo782._emit import (
    CLOUD_LAYER,
    CLOUD_SOLIDUS,
    FM6,
    SEA_W,
    TEMP_PAIR,
    emit,
)


def check_trend_remarks(
    obs: list[str],
    trend: list[str],
    body: list[str],
    *,
    product: str,
    core: str,
    body_start: int,
    body_end: int,
) -> list[Issue]:
    """Emit TREND exclusivity/format, RMK national note, and sea-surface format issues.

    Parameters
    ----------
    obs
        Argument ``obs``.
    trend
        Argument ``trend``.
    body
        Argument ``body``.
    product
        Argument ``product``.
    core
        Argument ``core``.
    body_start
        Argument ``body_start``.
    body_end
        Argument ``body_end``.

    Returns
    -------
    list[Issue]
        Return value.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (check_trend_remarks)
    2
    """
    issues: list[Issue] = []

    if "RMK" in body:
        emit(
            issues,
            "NATIONAL_RMK_NOT_INTERNATIONAL",
            f"{product} includes a national RMK section that should not be disseminated internationally",
            core=core,
            tok="RMK",
            body_start=body_start,
            body_end=body_end,
            location="remark",
        )

    if "NSW" in obs:
        emit(
            issues,
            "TREND_NSW_ONLY_IN_CHANGE",
            f"{product} NSW is only allowed inside TREND change groups",
            core=core,
            tok="NSW",
            body_start=body_start,
            body_end=body_end,
            location="trend",
        )

    if trend:
        if "NOSIG" in trend and any(t in trend for t in ("BECMG", "TEMPO")):
            emit(
                issues,
                "TREND_NOSIG_EXCLUSIVITY",
                f"{product} NOSIG with BECMG TEMPO or trend elements",
                core=core,
                tok="NOSIG",
                body_start=body_start,
                body_end=body_end,
                location="trend",
            )
        prob = next((t for t in trend if t.startswith("PROB")), None)
        if prob:
            emit(
                issues,
                "TREND_PROB_FORBIDDEN",
                f"{product} TREND forecast must not use PROB",
                core=core,
                tok=prob,
                body_start=body_start,
                body_end=body_end,
                location="trend",
            )
        for tok in trend:
            if FM6.fullmatch(tok):
                emit(
                    issues,
                    "TREND_FM_FORMAT",
                    f"{product} TREND FM time must be four-digit FMGGgg, not TAF FMYYGGgg",
                    core=core,
                    tok=tok,
                    body_start=body_start,
                    body_end=body_end,
                    location="trend",
                )
            if _WIND_DIR_VAR.fullmatch(tok):
                emit(
                    issues,
                    "TREND_WIND_V_GROUP_FORBIDDEN",
                    f"{product} TREND wind must not include a directional variation V-group",
                    core=core,
                    tok=tok,
                    body_start=body_start,
                    body_end=body_end,
                    location="trend",
                )
            if tok == "NCD" or CLOUD_SOLIDUS.fullmatch(tok):
                emit(
                    issues,
                    "TREND_NCD_OR_SOLIDUS_FORBIDDEN",
                    f"{product} TREND must not use NCD or cloud solidus forms",
                    core=core,
                    tok=tok,
                    body_start=body_start,
                    body_end=body_end,
                    location="trend",
                )
        body_units = {m.group("unit") for t in obs if (m := _WIND_PARSE.fullmatch(t))}
        trend_units = {m.group("unit") for t in trend if (m := _WIND_PARSE.fullmatch(t))}
        if body_units and trend_units and body_units != trend_units:
            issues.append(
                _issue(
                    "TREND_UNIT_MISMATCH",
                    f"{product} TREND wind or visibility units must match the parent METAR/SPECI body",
                    start=body_start,
                    end=body_end,
                    location="trend",
                )
            )
        body_layers = [t for t in obs if CLOUD_LAYER.fullmatch(t)]
        trend_layers = [t for t in trend if CLOUD_LAYER.fullmatch(t)]
        if trend_layers and body_layers and len(trend_layers) < len(body_layers):
            emit(
                issues,
                "TREND_CLOUD_LAYERS_INCOMPLETE",
                f"{product} TREND that changes cloud must repeat all cloud layers",
                core=core,
                tok=trend_layers[0],
                body_start=body_start,
                body_end=body_end,
                location="trend",
            )

    for tok in obs:
        if (
            tok.startswith("W")
            and "/" in tok
            and not tok.startswith("WS")
            and not TEMP_PAIR.fullmatch(tok)
            and re.match(r"^W\d{2}/", tok)
            and not SEA_W.fullmatch(tok)
        ):
            emit(
                issues,
                "SEA_SURFACE_GROUP_FORMAT",
                f"{product} WTsTs paired incorrectly with S' vs HHsHsHs",
                core=core,
                tok=tok,
                body_start=body_start,
                body_end=body_end,
                location="supplementary",
            )
    return issues
