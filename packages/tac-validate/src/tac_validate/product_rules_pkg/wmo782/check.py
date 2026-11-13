"""Orchestrate extended WMO-782 METAR/SPECI combination emitters."""

from __future__ import annotations

# pyright: reportPrivateUsage=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
from tac_validate.models import Issue
from tac_validate.product_rules_pkg.wmo782._emit import dedupe, split_obs_trend
from tac_validate.product_rules_pkg.wmo782.cavok_rvr_vis import check_cavok_rvr_vis
from tac_validate.product_rules_pkg.wmo782.cloud_temp_qnh import check_cloud_temp_qnh
from tac_validate.product_rules_pkg.wmo782.trend_remarks import check_trend_remarks
from tac_validate.product_rules_pkg.wmo782.weather import check_weather
from tac_validate.product_rules_pkg.wmo782.wind_shear import check_wind_shear


def check_wmo782_extended(
    tokens: list[str],
    *,
    product: str,
    core: str,
    body_start: int,
    body_end: int,
) -> list[Issue]:
    """Emit extended WMO-782 METAR/SPECI combination issues."""
    issues: list[Issue] = []
    is_auto = "AUTO" in tokens
    body = tokens
    if "RMK" in body:
        body = body[: body.index("RMK")]

    obs, trend = split_obs_trend(body)
    issues.extend(
        check_cavok_rvr_vis(
            obs,
            is_auto=is_auto,
            product=product,
            core=core,
            body_start=body_start,
            body_end=body_end,
        )
    )
    issues.extend(
        check_weather(
            obs,
            is_auto=is_auto,
            product=product,
            core=core,
            body_start=body_start,
            body_end=body_end,
        )
    )
    issues.extend(
        check_cloud_temp_qnh(
            obs,
            is_auto=is_auto,
            product=product,
            core=core,
            body_start=body_start,
            body_end=body_end,
        )
    )
    issues.extend(
        check_wind_shear(
            obs,
            product=product,
            core=core,
            body_start=body_start,
            body_end=body_end,
        )
    )
    issues.extend(
        check_trend_remarks(
            obs,
            trend,
            tokens,
            product=product,
            core=core,
            body_start=body_start,
            body_end=body_end,
        )
    )
    return dedupe(issues)
