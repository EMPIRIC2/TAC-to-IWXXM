"""NSC, R8, field-order, and multi-report gates."""

# ruff: noqa: F403, F405
# pyright: reportWildcardImportFromLibrary=false, reportConstantRedefinition=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportInvalidTypeForm=false, reportUnusedImport=false, reportPrivateUsage=false, reportGeneralTypeIssues=false
from __future__ import annotations

from tac_validate.models import Issue
from tac_validate.product_rules_pkg._common.helpers import *
from tac_validate.product_rules_pkg._common.patterns import *


def _emit_token_info(
    issues: list[Issue],
    *,
    code: str,
    message: str,
    core: str,
    body_start: int,
    body_end: int,
    token: str,
) -> None:
    """
    Internal helper ``_emit_token_info``.

    Parameters
    ----------
    issues : object
        Argument ``issues``.
    code : object
        Argument ``code``.
    message : object
        Argument ``message``.
    core : object
        Argument ``core``.
    body_start : object
        Argument ``body_start``.
    body_end : object
        Argument ``body_end``.
    token : object
        Argument ``token``.
    """
    span = _token_span_in_core(core, token, body_start)
    if span is None:
        start, end = body_start, body_end
    else:
        start, end = span
    issues.append(_issue(code, message, start=start, end=end, location="modifier"))


def _forecast_or_obs_segments(tokens: list[str]) -> list[list[str]]:
    """
    Internal helper ``_forecast_or_obs_segments``.

    Parameters
    ----------
    tokens : object
        Argument ``tokens``.

    Returns
    -------
    object
        Return value.
    """
    segments: list[list[str]] = []
    current: list[str] = []
    for tok in tokens:
        # INTER is an AU change-group opener (FAQ §14.3 exclusivity is same-group only).
        if tok in {"TEMPO", "BECMG", "NOSIG", "INTER"} or _TAF_FM.fullmatch(tok) or _TAF_PROB.fullmatch(tok):
            if current:
                segments.append(current)
            current = [tok]
        else:
            current.append(tok)
    if current:
        segments.append(current)
    return segments


def _emit_nsc_layer_exclusivity(
    issues: list[Issue],
    *,
    product: str,
    tokens: list[str],
    core: str,
    body_start: int,
    body_end: int,
) -> None:
    """
    Internal helper ``_emit_nsc_layer_exclusivity``.

    Parameters
    ----------
    issues : object
        Argument ``issues``.
    product : object
        Argument ``product``.
    tokens : object
        Argument ``tokens``.
    core : object
        Argument ``core``.
    body_start : object
        Argument ``body_start``.
    body_end : object
        Argument ``body_end``.
    """
    for segment in _forecast_or_obs_segments(tokens):
        if "NSC" not in segment:
            continue
        layer = next((t for t in segment if _LAYER_CLOUD_TOKEN.fullmatch(t)), None)
        if layer is None:
            continue
        span = _token_span_in_core(core, "NSC", body_start)
        if span is None:
            start, end = body_start, body_end
        else:
            start, end = span
        issues.append(
            _issue(
                "NSC_WITH_CLOUD_LAYERS",
                f"{product} NSC with FEW/SCT/BKN/OVC in same group - FAQ §14.3 exclusivity",
                start=start,
                end=end,
                location="cloud",
            )
        )
        break


def _check_r8_pack(
    tokens: list[str],
    *,
    product: str,
    core: str,
    body_start: int,
    body_end: int,
) -> list[Issue]:
    """
    Internal helper ``_check_r8_pack``.

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

    Returns
    -------
    object
        Return value.
    """
    issues: list[Issue] = []
    if "AUTO" in tokens:
        _emit_token_info(
            issues,
            code="AUTO_PRESENT",
            message=f"{product} AUTO modifier present - research R8",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="AUTO",
        )
    if "COR" in tokens:
        _emit_token_info(
            issues,
            code="COR_PRESENT",
            message=f"{product} COR modifier present - research R8",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="COR",
        )
    if "NOSIG" in tokens:
        _emit_token_info(
            issues,
            code="NOSIG_PRESENT",
            message=f"{product} NOSIG trend present - research R8",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="NOSIG",
        )
    if "TEMPO" in tokens:
        _emit_token_info(
            issues,
            code="TEMPO_PRESENT",
            message=f"{product} TEMPO trend present - research R8",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="TEMPO",
        )

    for tok in tokens:
        if not _RVR.match(tok):
            continue
        # Bare R14R after WS is a wind-shear runway designator, not an RVR group.
        # True RVR always has '/' after the runway (R14R/P2000N).
        if "/" not in tok:
            continue
        if _RVR_RUNWAY_STATE.fullmatch(tok):
            continue
        if _RVR_OK.fullmatch(tok):
            _emit_token_info(
                issues,
                code="RVR_PRESENT",
                message=f"{product} RVR group {tok!r} present - research R8",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token=tok,
            )
        else:
            _emit_token_info(
                issues,
                code="INVALID_RVR",
                message=f"{product} invalid RVR token {tok!r} - research R8",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token=tok,
            )

    wind_tokens = [t for t in tokens if t == "CALM" or t.endswith(("KT", "MPS"))]
    bad_winds = [t for t in wind_tokens if not _WIND.fullmatch(t)]
    good_winds = [t for t in wind_tokens if _WIND.fullmatch(t)]
    for tok in bad_winds:
        _emit_token_info(
            issues,
            code="INVALID_WIND",
            message=f"{product} invalid wind token {tok!r} - research R8",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token=tok,
        )
    for tok in good_winds:
        if tok.startswith("VRB") or "G" in tok:
            _emit_token_info(
                issues,
                code="WIND_VRB_OR_GUST",
                message=f"{product} wind {tok!r} uses VRB and/or gust - research R8",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token=tok,
            )
            break
    return issues


def _check_metar_speci_field_order(
    tokens: list[str],
    *,
    product: str,
    start: int,
    end: int,
) -> Issue | None:
    """
    Internal helper ``_check_metar_speci_field_order``.

    Parameters
    ----------
    tokens : object
        Argument ``tokens``.
    product : object
        Argument ``product``.
    start : object
        Argument ``start``.
    end : object
        Argument ``end``.

    Returns
    -------
    object
        Return value.
    """
    cccc_i = _first_icao_index(tokens, _METAR_SPECI_SKIP)
    time_i = _token_index(tokens, _OBS_TIME)
    wind_i = _token_index(tokens, _WIND)
    present = [(i, name) for i, name in ((cccc_i, "CCCC"), (time_i, "time"), (wind_i, "wind")) if i is not None]
    if len(present) < 2:
        return None
    indices = [i for i, _ in present]
    if indices == sorted(indices):
        return None
    return _issue(
        "ODD_FIELD_ORDER",
        f"{product} groups out of A3-2 order (CCCC → ddhhmmZ → wind) - research R1",
        start=start,
        end=end,
        location="order",
    )


def _report_segment_count(body: str) -> int:
    """
    Internal helper ``_report_segment_count``.

    Parameters
    ----------
    body : object
        Argument ``body``.

    Returns
    -------
    object
        Return value.
    """
    return sum(1 for part in body.split("=") if part.strip())


def _check_c1_multi_report(tac: str, product: str) -> list[Issue]:
    """
    Internal helper ``_check_c1_multi_report``.

    Parameters
    ----------
    tac : object
        Argument ``tac``.
    product : object
        Argument ``product``.

    Returns
    -------
    object
        Return value.
    """
    start, end, body = _body_span(tac)
    if _report_segment_count(body) < 2:
        return []
    return [
        _issue(
            "MULTI_REPORT_BULLETIN",
            f"{product} bulletin has multiple TAC reports - one IWXXM report per TAC (Guidance C1)",
            start=start,
            end=end,
            location="bulletin",
        )
    ]


__all__ = [
    "Issue",
    "_check_c1_multi_report",
    "_check_metar_speci_field_order",
    "_check_r8_pack",
    "_emit_nsc_layer_exclusivity",
    "_emit_token_info",
    "_forecast_or_obs_segments",
    "_report_segment_count",
]
