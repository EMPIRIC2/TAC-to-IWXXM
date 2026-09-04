"""Product rules - tca."""

# pyright: reportWildcardImportFromLibrary=false, reportUnusedFunction=false

from __future__ import annotations

import re

from tac_validate.models import Issue
from tac_validate.product_rules_pkg._common import *


def _check_us_faa_nws_tca_overlay(body: str, *, profile: str) -> list[Issue]:
    """US national TCA policy - observed CB not provided (#919 thin validation)."""
    # ruff: noqa: F403, F405
    if profile != "iwxxm_us":
        return []
    issues: list[Issue] = []
    cb_m = _CB_LINE.search(body)
    if cb_m is None:
        return issues
    cb_val = cb_m.group(1).strip().rstrip("=").upper()
    if cb_val and cb_val != "NIL":
        issues.append(
            _issue(
                "US_TCA_OBSERVED_CB_NOT_PROVIDED",
                "TCA observed CB must be NIL under US_FAA_NWS - observed CB not provided",
                start=cb_m.start(1),
                end=cb_m.end(1),
                location="cb",
            )
        )
    return issues


def _check_us_faa_nws_swxa_overlay(body: str, *, start: int, profile: str) -> list[Issue]:
    """US national SWXA policy - SATCOM not issued (#919 thin validation)."""
    if profile != "iwxxm_us":
        return []
    issues: list[Issue] = []
    effect_m = _SWX_EFFECT_LINE.search(body)
    if effect_m is not None:
        effect_raw = effect_m.group(1).strip().rstrip("=")
        if effect_raw.upper() == "SATCOM":
            issues.append(
                _issue(
                    "US_SWXA_SATCOM_NOT_ISSUED",
                    "SWXA SATCOM is not issued under US_FAA_NWS",
                    start=start + effect_m.start(1),
                    end=start + effect_m.end(1),
                    location="swx_effect",
                )
            )
    obs_m = _OBS_SWX_LINE.search(body)
    if obs_m is not None and re.search(r"\bSATCOM\b", obs_m.group(1), re.IGNORECASE):
        issues.append(
            _issue(
                "US_SWXA_SATCOM_NOT_ISSUED",
                "SWXA SATCOM is not issued under US_FAA_NWS",
                start=start + obs_m.start(1),
                end=start + obs_m.end(1),
                location="obs_swx",
            )
        )
    return issues


def _check_tca(tac: str, *, profile: str = "annex3") -> list[Issue]:
    start, end, body = _body_span(tac)
    issues: list[Issue] = []
    if not _DTG_LINE.search(body):
        issues.append(
            _issue(
                "MISSING_DTG",
                "TCA missing DTG: template field - A2-2",
                start=start,
                end=end,
                location="dtg",
            )
        )
    if not _MAX_WIND_LINE.search(body):
        issues.append(
            _issue(
                "MISSING_MAX_WIND",
                "TCA missing MAX WIND: template field - A2-2",
                start=start,
                end=end,
                location="max_wind",
            )
        )
    # F27 theme T1 - exceptional cyclone / CB / remarks / next-msg cues (#737).
    tc_m = _TC_LINE.search(body)
    if not tc_m:
        issues.append(
            _issue(
                "MISSING_TC",
                "TCA missing TC: template field - F27 theme T1 / A2-2",
                start=start,
                end=end,
                location="tropical_cyclone",
            )
        )
    else:
        tc_val = tc_m.group(1).strip().upper()
        t_start, t_end = tc_m.start(1), tc_m.end(1)
        if not tc_val:
            issues.append(
                _issue(
                    "MISSING_TC",
                    "TCA missing TC: template field - F27 theme T1 / A2-2",
                    start=tc_m.start(),
                    end=tc_m.end(),
                    location="tropical_cyclone",
                )
            )
        elif tc_val.split()[0] == "UNNAMED":
            issues.append(
                _issue(
                    "TCA_CYCLONE_UNNAMED",
                    "TCA TC UNNAMED - exceptional name allowed (F27 theme T1)",
                    start=t_start,
                    end=t_end,
                    location="tropical_cyclone",
                )
            )
    cb_m = _CB_LINE.search(body)
    if cb_m:
        cb_val = cb_m.group(1).strip().rstrip("=").upper()
        if cb_val == "NIL":
            issues.append(
                _issue(
                    "TCA_CB_NIL",
                    "TCA CB NIL - CB missing (F27 theme T1)",
                    start=cb_m.start(1),
                    end=cb_m.end(1),
                    location="cb",
                )
            )
    rmk_m = _RMK_LINE.search(body)
    if rmk_m:
        rmk_val = rmk_m.group(1).strip().rstrip("=").upper()
        if rmk_val == "NIL":
            issues.append(
                _issue(
                    "TCA_RMK_NIL",
                    "TCA RMK NIL - remarks inapplicable (F27 theme T1)",
                    start=rmk_m.start(1),
                    end=rmk_m.end(1),
                    location="remarks",
                )
            )
    nxt_m = _NXT_MSG_LINE.search(body)
    if nxt_m and "NO MSG EXP" in nxt_m.group(1).upper():
        issues.append(
            _issue(
                "TCA_NO_MSG_EXP",
                "TCA NXT MSG NO MSG EXP - next time inapplicable (F27 theme T1)",
                start=nxt_m.start(1),
                end=nxt_m.end(1),
                location="next_advisory",
            )
        )
    issues.extend(_check_us_faa_nws_tca_overlay(body, profile=profile))
    return issues
