"""Product rules - taf."""
# ruff: noqa: F403, F405
# pyright: reportWildcardImportFromLibrary=false, reportUnusedFunction=false
# pyright: reportWildcardImportFromLibrary=false, reportConstantRedefinition=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportInvalidTypeForm=false, reportUnusedImport=false, reportPrivateUsage=false, reportGeneralTypeIssues=false

from __future__ import annotations

import re

from tac_validate.models import Issue
from tac_validate.product_rules_pkg._common import *
from tac_validate.product_rules_pkg.taf.core import *
from tac_validate.station_scoped_policy import accepts_end_tx_tn
from tac_validate.taf_amd import amd_modifier_present
from tac_validate.taf_prob import ProbGroupKind, classify_probability_group


def _check_us_faa_nws_taf(
    tokens: list[str],
    *,
    product: str,
    core: str,
    body_start: int,
    body_end: int,
    profile: str = "annex3",
) -> list[Issue]:
    """
    Internal helper ``_check_us_faa_nws_taf``.

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
    if profile != "iwxxm_us" or product != "TAF":
        return []
    issues: list[Issue] = []
    if "BECMG" in tokens:
        issues.append(
            _issue(
                "US_TAF_BECMG_FORBIDDEN",
                f"{product} BECMG is forbidden under US_FAA_NWS - FMH-1 / FAA GEN 1.7",
                start=body_start,
                end=body_end,
                location="change_group",
            )
        )
    for i, tok in enumerate(tokens):
        if tok != "TEMPO":
            continue
        window = tokens[i + 1] if i + 1 < len(tokens) else ""
        duration_h: int | None = None
        m = re.fullmatch(r"(\d{2})(\d{2})/(\d{2})(\d{2})", window)
        if m is not None:
            start_h = int(m.group(2))
            end_h = int(m.group(4))
            duration_h = (end_h - start_h) if end_h >= start_h else (24 - start_h + end_h)
        elif _TAF_TL.fullmatch(window):
            # TL-only TEMPO without explicit window - cannot compute duration here.
            duration_h = None
        if duration_h is not None and duration_h > 4:
            issues.append(
                _issue(
                    "US_TAF_TEMPO_MAX_4H",
                    f"{product} TEMPO exceeds 4h maximum under US_FAA_NWS - FMH-1",
                    start=body_start,
                    end=body_end,
                    location="change_group",
                )
            )
        break
    return issues


def _taf_first_change_index(tokens: list[str]) -> int | None:
    """
    Internal helper ``_taf_first_change_index``.

    Parameters
    ----------
    tokens : object
        Argument ``tokens``.

    Returns
    -------
    object
        Return value.
    """
    for i, tok in enumerate(tokens):
        if tok in {"BECMG", "TEMPO"} or _TAF_FM.fullmatch(tok) or _TAF_PROB.fullmatch(tok):
            return i
    return None


def _check_taf_t3_elements(
    issues: list[Issue],
    *,
    tokens: list[str],
    product: str,
    core: str,
    body_start: int,
    body_end: int,
    profile: str = "annex3",
) -> None:
    """
    Internal helper ``_check_taf_t3_elements``.

    Parameters
    ----------
    issues : object
        Argument ``issues``.
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
    profile : str, optional
        Lint profile id. ``us_military`` and ``latam_taf`` allow TX/TN after
        change groups.
    """
    change_i = _taf_first_change_index(tokens)
    tx_tn_toks = [(i, t) for i, t in enumerate(tokens) if _TAF_TX_TN.fullmatch(t)]
    if tx_tn_toks:
        on_change = any(change_i is not None and i >= change_i for i, _t in tx_tn_toks)
        first_tok = tx_tn_toks[0][1]
        # us_military / latam_taf: trailing TX/TN is info (EV-station-profile-tx-tn).
        if on_change and not accepts_end_tx_tn(profile):
            _emit_token_info(
                issues,
                code="INVALID_TX_TN",
                message=f"{product} TX/TN allowed on base forecast only - research T3",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token=first_tok,
            )
        else:
            placement = "after change groups" if on_change else "on base"
            _emit_token_info(
                issues,
                code="TX_TN_PRESENT",
                message=f"{product} TX/TN temperature forecasts {placement} - research T3",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token=first_tok,
            )

    if "CAVOK" in tokens:
        _emit_token_info(
            issues,
            code="CAVOK_PRESENT",
            message=f"{product} CAVOK present - research T3 / S1",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="CAVOK",
        )
    if "NSC" in tokens:
        _emit_token_info(
            issues,
            code="NSC_PRESENT",
            message=f"{product} NSC present - research T3 / S1",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="NSC",
        )
        _emit_nsc_layer_exclusivity(
            issues,
            product=product,
            tokens=tokens,
            core=core,
            body_start=body_start,
            body_end=body_end,
        )
    if "NSW" in tokens:
        _emit_token_info(
            issues,
            code="NSW_PRESENT",
            message=f"{product} NSW present - research T3 / S1",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="NSW",
        )
    if "VV///" in tokens:
        _emit_token_info(
            issues,
            code="VV_OMIT",
            message=f"{product} VV/// - omit verticalVisibility without nilReason - research T3",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="VV///",
        )


__all__ = [
    "Issue",
    "ProbGroupKind",
    "_check_taf_t3_elements",
    "_check_us_faa_nws_taf",
    "_taf_first_change_index",
    "accepts_end_tx_tn",
    "amd_modifier_present",
    "classify_probability_group",
]
