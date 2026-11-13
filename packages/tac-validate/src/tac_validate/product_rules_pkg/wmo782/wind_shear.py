"""Surface wind, gust, high-speed, variation, and wind-shear checks (WMO-No. 782)."""

from __future__ import annotations

import re

from tac_validate.models import Issue
from tac_validate.product_rules_pkg._common import _WIND_DIR_VAR, _WIND_PARSE
from tac_validate.product_rules_pkg.wmo782._emit import emit


def check_wind_shear(
    obs: list[str],
    *,
    product: str,
    core: str,
    body_start: int,
    body_end: int,
) -> list[Issue]:
    """Emit calm/gust/P-indicator/variation and WS format exclusivity issues."""
    issues: list[Issue] = []
    mean_kt: int | None = None

    for tok in obs:
        parsed = _WIND_PARSE.fullmatch(tok)
        if parsed is None:
            continue
        direction = parsed.group("dir")
        speed = int(parsed.group("spd"))
        gust = parsed.group("gust")
        unit = parsed.group("unit")
        mean_kt = speed if unit == "KT" else speed * 2

        if (direction == "000" and speed != 0) or (speed == 0 and direction not in {"000", "VRB"}):
            emit(
                issues,
                "WIND_CALM_MISENCODE",
                f"{product} calm wind must be 00000KT or 00000MPS",
                core=core,
                tok=tok,
                body_start=body_start,
                body_end=body_end,
                location="wind",
            )
        if speed == 0 and (gust or any(_WIND_DIR_VAR.fullmatch(t) for t in obs)):
            emit(
                issues,
                "WIND_CALM_MISENCODE",
                f"{product} calm wind must be 00000KT or 00000MPS",
                core=core,
                tok=tok,
                body_start=body_start,
                body_end=body_end,
                location="wind",
            )
        if gust is not None:
            spread = int(gust) - speed
            spread_kt = spread if unit == "KT" else spread * 2
            if 0 < spread_kt < 10:
                emit(
                    issues,
                    "WIND_GUST_BELOW_THRESHOLD",
                    f"{product} gust is reported when the maximum does not exceed the mean by at least 10 kt",
                    core=core,
                    tok=tok,
                    body_start=body_start,
                    body_end=body_end,
                    location="wind",
                )
        if ("P99" in tok and unit != "KT") or ("P49" in tok and unit != "MPS"):
            emit(
                issues,
                "WIND_HIGH_SPEED_P_INDICATOR",
                f"{product} speeds at or above 100 kt (50 m/s) must use P99KT or P49MPS",
                core=core,
                tok=tok,
                body_start=body_start,
                body_end=body_end,
                location="wind",
            )
        if speed >= 100 and "P99" not in tok and "P49" not in tok:
            emit(
                issues,
                "WIND_HIGH_SPEED_P_INDICATOR",
                f"{product} speeds at or above 100 kt (50 m/s) must use P99KT or P49MPS",
                core=core,
                tok=tok,
                body_start=body_start,
                body_end=body_end,
                location="wind",
            )

    for tok in obs:
        if not _WIND_DIR_VAR.fullmatch(tok):
            continue
        d1, d2 = int(tok[:3]), int(tok[4:7])
        span_deg = (d2 - d1) % 360
        if mean_kt is not None and mean_kt < 3:
            emit(
                issues,
                "WIND_VARIATION_SPAN",
                f"{product} directional variation group requires mean speed at least 3 kt",
                core=core,
                tok=tok,
                body_start=body_start,
                body_end=body_end,
                location="wind",
            )
        if not (60 <= span_deg < 180):
            emit(
                issues,
                "WIND_VARIATION_SPAN",
                f"{product} directional variation group requires a direction span of 60 degrees to less than 180 degrees",
                core=core,
                tok=tok,
                body_start=body_start,
                body_end=body_end,
                location="wind",
            )

    if "WS" in obs:
        ws_i = [i for i, t in enumerate(obs) if t == "WS"]
        has_all = any(i + 2 < len(obs) and obs[i + 1] == "ALL" and obs[i + 2] == "RWY" for i in ws_i)
        has_rwy = any(i + 1 < len(obs) and re.fullmatch(r"R\d{2}[LCR]?", obs[i + 1]) for i in ws_i)
        for i in ws_i:
            if i + 1 >= len(obs) or not (obs[i + 1] == "ALL" or re.fullmatch(r"R\d{2}[LCR]?", obs[i + 1])):
                emit(
                    issues,
                    "WIND_SHEAR_FORMAT",
                    f"{product} wind shear group should be WS RDRDR or WS ALL RWY",
                    core=core,
                    tok="WS",
                    body_start=body_start,
                    body_end=body_end,
                    location="wind_shear",
                )
                break
        if has_all and has_rwy:
            emit(
                issues,
                "WS_ALL_RWY_EXCLUSIVE",
                f"{product} WS ALL RWY with individual WS runway groups",
                core=core,
                tok="WS",
                body_start=body_start,
                body_end=body_end,
                location="wind_shear",
            )
    return issues
