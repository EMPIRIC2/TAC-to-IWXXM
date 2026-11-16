"""National / regional remark and dialect checks."""

# ruff: noqa: F403, F405
# pyright: reportWildcardImportFromLibrary=false, reportConstantRedefinition=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportInvalidTypeForm=false, reportUnusedImport=false, reportPrivateUsage=false, reportGeneralTypeIssues=false
from __future__ import annotations

from tac_validate.models import Issue
from tac_validate.product_rules_pkg._common.gates import (  # noqa: F401
    _emit_nsc_layer_exclusivity,
    _emit_token_info,
    _forecast_or_obs_segments,
)
from tac_validate.product_rules_pkg._common.helpers import *
from tac_validate.product_rules_pkg._common.patterns import *
from tac_validate.product_rules_pkg._common.phenomenon import *


def _check_us_remarks(
    tokens: list[str],
    *,
    product: str,
    core: str,
    body_start: int,
    body_end: int,
    profile: str = "annex3",
) -> list[Issue]:
    """
    Internal helper ``_check_us_remarks``.

    Parameters
    ----------
    tokens : object
        Argument ``tokens``.
    product : object
        Argument ``product``.
    core : object
        Argument ``core``.
    body_start : object
        Argument ``body_start``.
    body_end : object
        Argument ``body_end``.
    profile : object
        Argument ``profile``.

    Returns
    -------
    object
        Return value.
    """
    if "RMK" not in tokens:
        return []
    rmk_i = tokens.index("RMK")
    remark = tokens[rmk_i + 1 :]
    issues: list[Issue] = []
    saw_us = False
    i = 0
    while i < len(remark):
        tok = remark[i]
        if tok in _RMK_AO:
            saw_us = True
            i += 1
            continue
        if _RMK_SLP_OK.fullmatch(tok):
            saw_us = True
            i += 1
            continue
        if tok.startswith("SLP") and tok[3:].isdigit():
            _append_remark_issue(
                issues,
                code="INVALID_REMARK",
                message=f"{product} malformed remark {tok!r} (SLP needs 3 digits)",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token=tok,
            )
            i += 1
            continue
        if _RMK_P_OK.fullmatch(tok):
            saw_us = True
            i += 1
            continue
        if len(tok) > 1 and tok[0] == "P" and tok[1:].isdigit():
            _append_remark_issue(
                issues,
                code="INVALID_REMARK",
                message=f"{product} malformed remark {tok!r} (P precip needs 4 digits)",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token=tok,
            )
            i += 1
            continue
        if _RMK_T_OK.fullmatch(tok):
            saw_us = True
            i += 1
            continue
        if len(tok) > 1 and tok[0] == "T" and tok[1:].isdigit():
            _append_remark_issue(
                issues,
                code="INVALID_REMARK",
                message=f"{product} malformed remark {tok!r} (T tenths needs 8 digits)",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token=tok,
            )
            i += 1
            continue
        if tok == "PK":
            has_wnd = i + 1 < len(remark) and remark[i + 1] == "WND"
            has_val = has_wnd and i + 2 < len(remark) and _RMK_PK_VAL.fullmatch(remark[i + 2])
            if has_val:
                saw_us = True
                i += 3
                continue
            span_tok = "WND" if has_wnd else "PK"
            _append_remark_issue(
                issues,
                code="INVALID_REMARK",
                message=f"{product} malformed remark PK WND (need dddss/tt)",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token=span_tok,
            )
            if has_wnd:
                i += 2
            else:
                i += 1
            continue
        i += 1

    if saw_us and profile == "iwxxm_us":
        _append_remark_issue(
            issues,
            code="REMARK_US_EXTENSION",
            message=(f"{product} US remarks present (AO1/AO2/SLP/P/T/PK WND) - iwxxm_us profile awareness"),
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="RMK",
        )
    return issues


def _check_ca_manobs(
    tokens: list[str],
    *,
    product: str,
    core: str,
    body_start: int,
    body_end: int,
    profile: str = "annex3",
) -> list[Issue]:
    """
    Internal helper ``_check_ca_manobs``.

    Parameters
    ----------
    tokens : object
        Argument ``tokens``.
    product : object
        Argument ``product``.
    core : object
        Argument ``core``.
    body_start : object
        Argument ``body_start``.
    body_end : object
        Argument ``body_end``.
    profile : object
        Argument ``profile``.

    Returns
    -------
    object
        Return value.
    """
    if profile != "ca_eccc":
        return []
    issues: list[Issue] = []
    lead = tokens[0].upper() if tokens else ""
    if lead == "LWIS":
        _emit_token_info(
            issues,
            code="CA_METAR_LWIS",
            message=f"{product} Limited Weather Information System (LWIS) report - MANOBS CA overlay",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="LWIS",
        )
    elif lead == "SAWR":
        _emit_token_info(
            issues,
            code="CA_METAR_SAWR",
            message=f"{product} Surface Aviation Weather Report (SAWR) - MANOBS CA overlay",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="SAWR",
        )
    for tok in tokens:
        if tok.endswith("SM"):
            vis_part = tok[:-2]
            if vis_part.isdigit() or (vis_part.startswith("P") and vis_part[1:].isdigit()):
                _emit_token_info(
                    issues,
                    code="CA_STATUTE_MILE_VIS",
                    message=f"{product} statute-mile visibility ({tok}) - MANOBS CA overlay",
                    core=core,
                    body_start=body_start,
                    body_end=body_end,
                    token=tok,
                )
                break
    alt = _ALT_INHG_BODY.search(core)
    if alt is not None:
        _emit_token_info(
            issues,
            code="CA_ALTIMETER_INHG",
            message=f"{product} inch-of-mercury altimeter ({alt.group(0)}) - MANOBS CA overlay",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token=alt.group(0),
        )
    elif _ALT_NOT_OBS_BODY.search(core):
        _emit_token_info(
            issues,
            code="CA_ALTIMETER_NOT_OBS",
            message=f"{product} altimeter not observable (A////) - MANOBS CA overlay",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="A////",
        )
    if "RMK" in tokens:
        rmk_i = tokens.index("RMK")
        remark = tokens[rmk_i + 1 :]
        saw_slp = any(_RMK_SLP_OK.fullmatch(t) for t in remark)
        saw_presfr = any(t == "PRESFR" for t in remark)
        saw_presrr = any(t == "PRESRR" for t in remark)
        saw_nospeci = any(_RMK_NOSPECI.fullmatch(t) for t in remark)
        remark_text = " ".join(remark)
        sector_vis = _RMK_SECTOR_VIS_IN_TEXT.search(remark_text)
        if saw_slp or saw_presfr or saw_presrr:
            _append_remark_issue(
                issues,
                code="CA_REMARK_MANOBS",
                message=f"{product} Canadian REMARKS (SLP/PRESFR/PRESRR) - ca_eccc profile awareness",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token="RMK",
            )
        if saw_presrr:
            _append_remark_issue(
                issues,
                code="CA_REMARK_PRESRR",
                message=f"{product} MANOBS pressure rising rapidly (PRESRR) - ca_eccc profile awareness",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token="PRESRR",
            )
        if saw_presfr:
            _append_remark_issue(
                issues,
                code="CA_REMARK_PRESFR",
                message=f"{product} MANOBS pressure falling rapidly (PRESFR) - ca_eccc profile awareness",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token="PRESFR",
            )
        if saw_nospeci:
            _append_remark_issue(
                issues,
                code="CA_REMARK_NOSPECI",
                message=f"{product} MANOBS no-specials remark (NOSPECI) - ca_eccc profile awareness",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token="NOSPECI",
            )
        if sector_vis is not None:
            _append_remark_issue(
                issues,
                code="CA_REMARK_SECTOR_VIS",
                message=f"{product} MANOBS sector visibility ({sector_vis.group(0)}) - ca_eccc profile awareness",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token=sector_vis.group(0),
            )
    return issues


def _check_ca_manair(
    tokens: list[str],
    *,
    product: str,
    core: str,
    body_start: int,
    body_end: int,
    profile: str = "annex3",
) -> list[Issue]:
    """
    Internal helper ``_check_ca_manair``.

    Parameters
    ----------
    tokens : object
        Argument ``tokens``.
    product : object
        Argument ``product``.
    core : object
        Argument ``core``.
    body_start : object
        Argument ``body_start``.
    body_end : object
        Argument ``body_end``.
    profile : object
        Argument ``profile``.

    Returns
    -------
    object
        Return value.
    """
    if profile != "ca_eccc" or product != "TAF":
        return []
    issues: list[Issue] = []
    for tok in tokens:
        if _NCLWS_TAC.fullmatch(tok):
            _emit_token_info(
                issues,
                code="CA_TAF_NCLWS",
                message=f"{product} MANAIR low-level wind shear ({tok}) - ca_eccc profile awareness",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token=tok,
            )
            break
        if _TAF_VIS_SM.fullmatch(tok):
            _emit_token_info(
                issues,
                code="CA_STATUTE_MILE_VIS",
                message=f"{product} statute-mile visibility ({tok}) - MANAIR CA overlay",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token=tok,
            )
    return issues


def _check_in_imd_taf(
    tokens: list[str],
    *,
    product: str,
    core: str,
    body_start: int,
    body_end: int,
    profile: str = "annex3",
) -> list[Issue]:
    """
    Internal helper ``_check_in_imd_taf``.

    Parameters
    ----------
    tokens : object
        Argument ``tokens``.
    product : object
        Argument ``product``.
    core : object
        Argument ``core``.
    body_start : object
        Argument ``body_start``.
    body_end : object
        Argument ``body_end``.
    profile : object
        Argument ``profile``.

    Returns
    -------
    object
        Return value.
    """
    if profile != "in_imd" or product != "TAF":
        return []
    if any(_TAF_TX_TN.fullmatch(tok) for tok in tokens):
        return []
    issues: list[Issue] = []
    issues.append(
        _issue(
            "IN_TAF_TX_TN_OMITTED",
            (
                f"{product} does not include TX/TN temperature forecast groups. "
                "Informational: India Meteorological Department TAFs often omit temperature "
                "extremes; this does not by itself block conversion."
            ),
            start=body_start,
            end=body_end,
            location="body",
        )
    )
    return issues


def _check_ca_gfa_airmet(
    *,
    product: str,
    core: str,
    body_start: int,
    body_end: int,
    profile: str = "annex3",
) -> list[Issue]:
    """
    Internal helper ``_check_ca_gfa_airmet``.

    Parameters
    ----------
    product : object
        Argument ``product``.
    core : object
        Argument ``core``.
    body_start : object
        Argument ``body_start``.
    body_end : object
        Argument ``body_end``.
    profile : object
        Argument ``profile``.

    Returns
    -------
    object
        Return value.
    """
    if profile != "ca_eccc" or product != "AIRMET":
        return []
    issues: list[Issue] = []
    phenom = _CA_GFA_PHENOM.search(core)
    if phenom is not None:
        _emit_token_info(
            issues,
            code="CA_AIRMET_GFA",
            message=f"{product} MANAIR GFA compound phenomenon ({phenom.group(0).strip()}) - ca_eccc profile awareness",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token=phenom.group(0).strip(),
        )
    chart = _GFA_CHART.search(core)
    if chart is not None:
        _emit_token_info(
            issues,
            code="CA_AIRMET_GFA",
            message=f"{product} GFA chart remark ({chart.group(0).strip()}) - ca_eccc profile awareness",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token=chart.group(0).strip(),
        )
    return issues


__all__ = [
    "Issue",
    "_check_ca_gfa_airmet",
    "_check_ca_manair",
    "_check_ca_manobs",
    "_check_in_imd_taf",
    "_check_us_remarks",
]
