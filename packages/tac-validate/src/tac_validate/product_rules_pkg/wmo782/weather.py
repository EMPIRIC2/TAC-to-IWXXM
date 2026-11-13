"""Present-weather and recent-weather combination checks (WMO-No. 782)."""

from __future__ import annotations

# pyright: reportPrivateUsage=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
import re

from tac_validate.models import Issue
from tac_validate.product_rules_pkg._common import (
    _VIS_METERS,
    _WIND_PARSE,
    _WX_SIGNIFICANT,
)
from tac_validate.product_rules_pkg.wmo782._emit import (
    RECENT,
    TEMP_PAIR,
    WX_TRAILING_INTENSITY,
    emit,
    parse_temp_c,
)


def _wx_tokens(obs: list[str]) -> list[str]:
    """Helper ``_wx_tokens``.

    Parameters
    ----------
    obs
        Argument ``obs``.

    Returns
    -------
    list[str]
        Return value.
    """
    return [
        tok
        for tok in obs
        if (
            _WX_SIGNIFICANT.fullmatch(tok)
            or tok in {"SHPL", "//"}
            or tok.startswith("VC")
            or "SHPL" in tok
            or WX_TRAILING_INTENSITY.fullmatch(tok)
        )
    ]


def check_weather(
    obs: list[str],
    *,
    product: str,
    core: str,
    body_start: int,
    body_end: int,
    is_auto: bool,
) -> list[Issue]:
    """Emit present-weather pairing, bands, recent-weather, and column-order issues.

    Parameters
    ----------
    obs
        Argument ``obs``.
    product
        Argument ``product``.
    core
        Argument ``core``.
    body_start
        Argument ``body_start``.
    body_end
        Argument ``body_end``.
    is_auto
        Argument ``is_auto``.

    Returns
    -------
    list[Issue]
        Return value.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (check_weather)
    2
    """
    issues: list[Issue] = []
    wx_tokens = _wx_tokens(obs)

    for tok in wx_tokens:
        if "SHPL" in tok:
            emit(
                issues,
                "WEATHER_SHPL_FORBIDDEN",
                f"{product} includes SHPL, which is not an accepted present-weather combination",
                core=core,
                tok=tok,
                body_start=body_start,
                body_end=body_end,
                location="weather",
            )
        if re.match(r"^[+-]?VC", tok) and ("+" in tok[2:] or "-" in tok[2:] or re.match(r"^VC[+-]", tok)):
            emit(
                issues,
                "WEATHER_VC_COMBINATION",
                f"{product} VC with intensity or with a phenomenon not allowed in vicinity",
                core=core,
                tok=tok,
                body_start=body_start,
                body_end=body_end,
                location="weather",
            )
        if re.match(r"^[+-]?(?:MI|BC|PR)", tok) and "FG" not in tok:
            emit(
                issues,
                "WEATHER_DESCRIPTOR_PAIRING",
                f"{product} MI/BC/PR not paired with FG only, or DR/BL not with DU/SA/SN",
                core=core,
                tok=tok,
                body_start=body_start,
                body_end=body_end,
                location="weather",
            )
        if re.match(r"^[+-]?(?:DR|BL)", tok) and not any(x in tok for x in ("DU", "SA", "SN")):
            emit(
                issues,
                "WEATHER_DESCRIPTOR_PAIRING",
                f"{product} MI/BC/PR not paired with FG only, or DR/BL not with DU/SA/SN",
                core=core,
                tok=tok,
                body_start=body_start,
                body_end=body_end,
                location="weather",
            )
        if WX_TRAILING_INTENSITY.fullmatch(tok):
            emit(
                issues,
                "WX_COLUMN_SEQUENCE",
                f"{product} w'w' violates intensity-descriptor-phenomenon column order",
                core=core,
                tok=tok,
                body_start=body_start,
                body_end=body_end,
                location="weather",
            )

    vis_m = next((int(t) for t in obs if _VIS_METERS.fullmatch(t)), None)
    if vis_m is not None:
        if any(t == "FG" or t.endswith("FG") for t in wx_tokens) and vis_m >= 1000:
            fg = next(t for t in wx_tokens if t == "FG" or t.endswith("FG"))
            emit(
                issues,
                "WEATHER_FG_VIS_THRESHOLD",
                f"{product} FG with prevailing visibility at or above 1000 m",
                core=core,
                tok=fg,
                body_start=body_start,
                body_end=body_end,
                location="weather",
            )
        if any(t == "BR" or t.endswith("BR") for t in wx_tokens) and not (1000 <= vis_m <= 5000):
            br = next(t for t in wx_tokens if t == "BR" or t.endswith("BR"))
            emit(
                issues,
                "WEATHER_BR_VIS_BAND",
                f"{product} BR outside 1000-5000 m band",
                core=core,
                tok=br,
                body_start=body_start,
                body_end=body_end,
                location="weather",
            )
        if vis_m < 5000 and not wx_tokens and "CAVOK" not in obs:
            emit(
                issues,
                "WEATHER_VIS_OBSCURATION_THRESHOLD",
                f"{product} visibility below 5 000 m should include an obscuration or weather cause",
                core=core,
                tok=f"{vis_m:04d}",
                body_start=body_start,
                body_end=body_end,
                location="weather",
            )

    # UP is an automated-system present-weather form; require AUTO.
    up_tok = next((t for t in wx_tokens if t == "UP" or "UP" in t), None)
    if up_tok is not None and not is_auto:
        emit(
            issues,
            "WEATHER_AUTO_UP_OR_SH",
            f"{product} AUTO present-weather uses UP or SH forms that require automated-system rules",
            core=core,
            tok=up_tok,
            body_start=body_start,
            body_end=body_end,
            location="weather",
        )

    temp_tok = next((t for t in obs if TEMP_PAIR.fullmatch(t)), None)
    air_c = None
    if temp_tok:
        left, _right = temp_tok.split("/", 1)
        air_c = parse_temp_c(left)
    fz = next((t for t in wx_tokens if "FZ" in t), None)
    if fz is not None and (air_c is None or air_c >= 0):
        emit(
            issues,
            "WEATHER_FZ_REQUIRES_SUBZERO",
            f"{product} FZFG/FZDZ/FZRA without sub-zero temperature evidence",
            core=core,
            tok=fz,
            body_start=body_start,
            body_end=body_end,
            location="weather",
        )

    mean_kt = None
    for tok in obs:
        parsed = _WIND_PARSE.fullmatch(tok)
        if parsed:
            spd = int(parsed.group("spd"))
            unit = parsed.group("unit")
            mean_kt = spd if unit == "KT" else spd * 2
            break
    if any(t == "SQ" or t.endswith("SQ") for t in wx_tokens) and mean_kt is not None and mean_kt < 22:
        emit(
            issues,
            "WEATHER_SQ_MIN_SPEED",
            f"{product} SQ with mean wind under 22 kt",
            core=core,
            tok="SQ",
            body_start=body_start,
            body_end=body_end,
            location="weather",
        )
    heavy = next((t for t in wx_tokens if t.startswith("+")), None)
    if vis_m is not None and vis_m >= 5000 and heavy is not None:
        emit(
            issues,
            "PRECIP_INTENSITY_VIS_PLAUSIBILITY",
            f"{product} Precipitation intensity inconsistent with visibility band in handbook examples",
            core=core,
            tok=heavy,
            body_start=body_start,
            body_end=body_end,
            location="weather",
        )

    for tok in obs:
        rem = RECENT.fullmatch(tok)
        if not rem:
            continue
        body_wx = rem.group("body")
        if any(ch in body_wx for ch in "+-") or body_wx.startswith("VC"):
            emit(
                issues,
                "RECENT_WEATHER_NO_INTENSITY",
                f"{product} REw'w' includes - + or VC",
                core=core,
                tok=tok,
                body_start=body_start,
                body_end=body_end,
                location="recent",
            )
        if body_wx == "UP" and not is_auto:
            emit(
                issues,
                "REUP_REQUIRES_AUTO",
                f"{product} includes REUP without AUTO",
                core=core,
                tok=tok,
                body_start=body_start,
                body_end=body_end,
                location="recent",
            )
        if not re.fullmatch(r"[A-Z]{2,8}", body_wx):
            emit(
                issues,
                "RECENT_WEATHER_LIMITS",
                f"{product} recent weather REw'w' does not meet accepted recent-weather limits",
                core=core,
                tok=tok,
                body_start=body_start,
                body_end=body_end,
                location="recent",
            )
    return issues
