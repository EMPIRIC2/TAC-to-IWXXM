"""CAVOK, RVR, and visibility combination checks (WMO-No. 782)."""

from __future__ import annotations

# pyright: reportPrivateUsage=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
import re

from tac_validate.models import Issue
from tac_validate.product_rules_pkg._common import (
    _RVR,
    _RVR_RUNWAY_STATE,
    _VIS_SOLIDUS,
)
from tac_validate.product_rules_pkg.wmo782._emit import (
    RVR_TOKEN,
    emit,
    rvr_value_on_scale,
)


def check_cavok_rvr_vis(
    obs: list[str],
    *,
    product: str,
    core: str,
    body_start: int,
    body_end: int,
    is_auto: bool,
) -> list[Issue]:
    """Emit CAVOK exclusivity, RVR family, and visibility solidus / NDV issues."""
    issues: list[Issue] = []

    if "CAVOK" in obs and any(_RVR.match(t) for t in obs):
        emit(
            issues,
            "CAVOK_EXCLUDES_RVR",
            f"{product} CAVOK present with RVR groups",
            core=core,
            tok="CAVOK",
            body_start=body_start,
            body_end=body_end,
            location="cavok",
        )

    # 9999 + NSC/NCD is the boundary case where CAVOK would replace those groups.
    if "CAVOK" not in obs and "9999" in obs and any(t in {"NSC", "NCD"} for t in obs):
        emit(
            issues,
            "CAVOK_NSC_BOUNDARY",
            f"{product} uses 9999 with NSC or NCD when CAVOK would replace visibility, weather, and cloud",
            core=core,
            tok="9999",
            body_start=body_start,
            body_end=body_end,
            location="cavok",
        )

    for tok in obs:
        if _VIS_SOLIDUS.fullmatch(tok) and not is_auto:
            emit(
                issues,
                "VISIBILITY_MISSING_AS_SOLIDUS",
                f"{product} encodes missing or temporarily incorrect visibility as {tok}",
                core=core,
                tok=tok,
                body_start=body_start,
                body_end=body_end,
                location="visibility",
            )
            break
    if "NDV" in obs and not is_auto:
        emit(
            issues,
            "NDV_REQUIRES_AUTO",
            f"{product} NDV directional-visibility marker without AUTO",
            core=core,
            tok="NDV",
            body_start=body_start,
            body_end=body_end,
            location="visibility",
        )

    rvr_tokens = [t for t in obs if _RVR.match(t) and not _RVR_RUNWAY_STATE.fullmatch(t)]
    if len(rvr_tokens) > 4:
        emit(
            issues,
            "RVR_MAX_GROUPS",
            f"{product} includes more than four RVR groups",
            core=core,
            tok=rvr_tokens[4],
            body_start=body_start,
            body_end=body_end,
            location="rvr",
        )
    for tok in rvr_tokens:
        if re.search(r"/{4,5}", tok):
            emit(
                issues,
                "RVR_MISSING_AS_SOLIDUS",
                f"{product} encodes missing RVR digits with solidi in {tok!r}",
                core=core,
                tok=tok,
                body_start=body_start,
                body_end=body_end,
                location="rvr",
            )
        parsed = RVR_TOKEN.fullmatch(tok)
        if parsed is None:
            continue
        tend = parsed.group("tend") or ""
        if tend and tend.lstrip("/") not in {"U", "D", "N"}:
            emit(
                issues,
                "RVR_TENDENCY_FORMAT",
                f"{product} RVR tendency must be U, D, or N when a tendency is reported",
                core=core,
                tok=tok,
                body_start=body_start,
                body_end=body_end,
                location="rvr",
            )
        body_v = parsed.group("body")
        if body_v and body_v != "/////" and not rvr_value_on_scale(body_v):
            emit(
                issues,
                "RVR_SCALE_STEP",
                f"{product} RVR value does not follow the accepted reporting steps",
                core=core,
                tok=tok,
                body_start=body_start,
                body_end=body_end,
                location="rvr",
            )
    return issues
