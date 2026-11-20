"""Phenomenon, cloud-candidate, and remark helper checks."""

# ruff: noqa: F403, F405
# pyright: reportWildcardImportFromLibrary=false, reportConstantRedefinition=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportInvalidTypeForm=false, reportUnusedImport=false, reportPrivateUsage=false, reportGeneralTypeIssues=false
from __future__ import annotations

from tac_validate import membership
from tac_validate.models import Issue
from tac_validate.product_rules_pkg._common.helpers import (
    _is_valid_weather_token,
    _issue,
    _membership_issue,
    _token_index,
    _token_span_in_core,
)
from tac_validate.product_rules_pkg._common.patterns import *


def _check_phenomenon_membership(
    upper: str,
    *,
    product: str,
    start: int,
    end: int,
) -> list[Issue]:
    """
    Emit membership issues for SIGMET/AIRMET phenomenon candidates in ``upper``.

    Parameters
    ----------
    upper : str
        Uppercased TAC body slice.
    product : str
        ``SIGMET`` or ``AIRMET``.
    start : int
        Absolute start offset of ``upper`` in the source TAC.
    end : int
        Absolute end offset of ``upper`` in the source TAC.

    Returns
    -------
    list[Issue]
        Membership findings for unknown phenomenon tokens.
    """
    family = "airwx_phenomena" if product == "AIRMET" else "sigwx_phenomena"
    pattern = _AIRMET_PHENOM_CANDIDATE if product == "AIRMET" else _SIGMET_PHENOM_CANDIDATE
    issues: list[Issue] = []
    seen: set[str] = set()
    for match in pattern.finditer(upper):
        raw = match.group(1)
        key = membership.normalize_register_notation(raw)
        if key in seen:
            continue
        seen.add(key)
        if membership.is_member_normalized(family, raw):
            continue
        issues.append(
            _membership_issue(
                product=product,
                token=raw,
                family=family,
                start=start + match.start(1),
                end=start + match.end(1),
                location="phenomenon",
            )
        )
    return issues


def _cloud_candidate_tokens(tokens: list[str]) -> list[tuple[int, str]]:
    """
    Return (index, token) pairs that look like cloud groups after wind.

    Parameters
    ----------
    tokens : list[str]
        TAC body tokens.

    Returns
    -------
    list[tuple[int, str]]
        Candidate cloud token indexes and values.
    """
    wind_i = _token_index(tokens, _WIND)
    if wind_i is None:
        return []
    candidates: list[tuple[int, str]] = []
    for i, tok in enumerate(tokens[wind_i + 1 :], start=wind_i + 1):
        if _TEMP.fullmatch(tok) or _QNH.fullmatch(tok) or tok == "RMK":
            break
        if tok in _METAR_SPECI_SKIP or _RVR.match(tok):
            continue
        if _WIND.fullmatch(tok) or _VIS_OK.fullmatch(tok) or _VIS_BAD.fullmatch(tok):
            continue
        if _WX_TOKEN_SHAPE.fullmatch(tok) and _is_valid_weather_token(tok):
            continue
        if _CLOUD_LIKE.match(tok) or _CLOUD_START.match(tok):
            candidates.append((i, tok))
    return candidates


def _append_remark_issue(
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
    Append a remark-scoped issue, spanning ``token`` when found in ``core``.

    Parameters
    ----------
    issues : list[Issue]
        Mutable finding list.
    code : str
        Registry issue code.
    message : str
        Operator message text.
    core : str
        TAC body core text used for span lookup.
    body_start : int
        Absolute start of the body core.
    body_end : int
        Absolute end of the body core.
    token : str
        Remark token to highlight when present.
    """
    span = _token_span_in_core(core, token, body_start)
    if span is None:
        start, end = body_start, body_end
    else:
        start, end = span
    issues.append(_issue(code, message, start=start, end=end, location="remark"))


__all__ = [
    "_append_remark_issue",
    "_check_phenomenon_membership",
    "_cloud_candidate_tokens",
]
