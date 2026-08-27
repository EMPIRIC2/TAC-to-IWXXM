"""Product rules - swxa."""

# pyright: reportWildcardImportFromLibrary=false, reportUnusedFunction=false, reportPrivateUsage=false

from __future__ import annotations

import re

from tac_validate import membership
from tac_validate.models import Issue
from tac_validate.product_rules_pkg._common import *
from tac_validate.product_rules_pkg.tca import _check_us_faa_nws_swxa_overlay


def _check_swxa_spacewx_membership(body: str, *, start: int) -> list[Issue]:
    """Map SWX EFFECT + OBS severity to SpaceWxPhenomena membership (EV-050)."""
    # ruff: noqa: F403, F405
    issues: list[Issue] = []
    effect_m = _SWX_EFFECT_LINE.search(body)
    if effect_m is None:
        return issues
    effect_raw = effect_m.group(1).strip().rstrip("=")
    effect_key = " ".join(effect_raw.upper().split())
    prefix = _SWX_EFFECT_PREFIX.get(effect_key)
    e_start, e_end = start + effect_m.start(1), start + effect_m.end(1)
    if prefix is None:
        issues.append(
            _membership_issue(
                product="SWXA",
                token=effect_raw,
                family="spacewx_phenomena",
                start=e_start,
                end=e_end,
                location="effect",
            )
        )
        return issues
    obs_m = _OBS_SWX_LINE.search(body)
    severity: str | None = None
    if obs_m is not None:
        obs_upper = obs_m.group(1).upper()
        if re.search(r"\bSEV\b", obs_upper):
            severity = "SEV"
        elif re.search(r"\bMOD\b", obs_upper):
            severity = "MOD"
    if severity is None:
        return issues
    notation = f"{prefix}_{severity}"
    if not membership.is_member("spacewx_phenomena", notation):
        issues.append(
            _membership_issue(
                product="SWXA",
                token=notation,
                family="spacewx_phenomena",
                start=e_start,
                end=e_end,
                location="effect",
            )
        )
    return issues


def _check_swxa(tac: str, *, profile: str = "annex3") -> list[Issue]:
    start, end, body = _body_span(tac)
    issues: list[Issue] = []
    if not _DTG_LINE.search(body):
        issues.append(
            _issue(
                "MISSING_DTG",
                "SWXA missing DTG: template field - A2-3",
                start=start,
                end=end,
                location="dtg",
            )
        )
    if not _SWXC_LINE.search(body):
        issues.append(
            _issue(
                "MISSING_SWXC",
                "SWXA missing SWXC: template field - F28 theme SX1 / A2-3",
                start=start,
                end=end,
                location="swxc",
            )
        )
    issues.extend(_check_swxa_spacewx_membership(body, start=start))
    # F28 theme SX1 - exceptional remarks / forecast / next-advisory cues (#740).
    rmk_m = _RMK_LINE.search(body)
    if rmk_m:
        rmk_val = rmk_m.group(1).strip().rstrip("=").upper()
        if rmk_val == "NIL":
            issues.append(
                _issue(
                    "SWXA_RMK_NIL",
                    "SWXA RMK NIL - remarks inapplicable (F28 theme SX1)",
                    start=rmk_m.start(1),
                    end=rmk_m.end(1),
                    location="remarks",
                )
            )
    no_swx = _NO_SWX_EXP.search(body)
    if no_swx is not None:
        issues.append(
            _issue(
                "SWXA_FCST_NO_SWX_EXP",
                "SWXA forecast NO SWX EXP - no space weather expected (F28 theme SX1)",
                start=no_swx.start(),
                end=no_swx.end(),
                location="forecast",
            )
        )
    nxt_m = _NXT_ADVISORY_LINE.search(body)
    if nxt_m and "NO FURTHER" in nxt_m.group(1).upper():
        issues.append(
            _issue(
                "SWXA_NO_FURTHER_ADVISORIES",
                "SWXA NXT ADVISORY NO FURTHER ADVISORIES - next time inapplicable (F28 theme SX1)",
                start=nxt_m.start(1),
                end=nxt_m.end(1),
                location="next_advisory",
            )
        )
    issues.extend(_check_us_faa_nws_swxa_overlay(body, start=start, profile=profile))
    return issues
