"""Shared helpers for product rule checks."""

# ruff: noqa: F403, F405
# pyright: reportWildcardImportFromLibrary=false, reportConstantRedefinition=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportInvalidTypeForm=false, reportUnusedImport=false, reportPrivateUsage=false, reportGeneralTypeIssues=false
from __future__ import annotations

import re

from tac_validate import membership
from tac_validate.issue_registry import issue_from
from tac_validate.models import Issue
from tac_validate.product_rules_pkg._common.patterns import *


def _strip_research_refs(message: str) -> str:
    """
    Strip research milestone and planning vocabulary from operator lint messages.

    Parameters
    ----------
    message : str
        Raw issue message (may include research or ticket suffixes).

    Returns
    -------
    str
        Operator-safe message; returns ``message`` unchanged when scrubbing would
        empty the string.
    """
    cleaned = _RESEARCH_REF_RE.sub("", message)
    cleaned = _FN_THEME_RE.sub("", cleaned)
    cleaned = _THEME_CRUMB_RE.sub("", cleaned)
    cleaned = _PLANNING_REF_RE.sub("", cleaned)
    cleaned = _VAGUE_FILLER_RE.sub("", cleaned)
    cleaned = _EMPTY_PARENS_RE.sub("", cleaned)
    cleaned = re.sub(r"\s*/\s*/+", " ", cleaned)
    # Collapse `` - / `` left after removing a middle planning crumb.
    cleaned = re.sub(r"\s+/\s+", " ", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    cleaned = _DANGLING_SEP_RE.sub("", cleaned)
    cleaned = _TRAILING_SEP_RE.sub("", cleaned).strip()
    return cleaned if cleaned else message


def _issue(
    code: str,
    message: str,
    *,
    start: int,
    end: int,
    location: str = "body",
) -> Issue:
    """
    Internal helper ``_issue``.

    Parameters
    ----------
    code : object
        Argument ``code``.
    message : object
        Argument ``message``.
    start : object
        Argument ``start``.
    end : object
        Argument ``end``.
    location : object
        Argument ``location``.

    Returns
    -------
    object
        Return value.
    """
    return issue_from(
        code,
        message=_strip_research_refs(message),
        location=location,
        start=start,
        end=end,
    )


def _body_span(tac: str) -> tuple[int, int, str]:
    """
    Internal helper ``_body_span``.

    Parameters
    ----------
    tac : object
        Argument ``tac``.

    Returns
    -------
    object
        Return value.
    """
    stripped = tac.strip()
    if not stripped:
        return 0, len(tac), ""
    leading = len(tac) - len(tac.lstrip())
    return leading, leading + len(stripped), stripped


def _first_icao(tokens: list[str], skip: frozenset[str]) -> str | None:
    """
    Internal helper ``_first_icao``.

    Parameters
    ----------
    tokens : object
        Argument ``tokens``.
    skip : object
        Argument ``skip``.

    Returns
    -------
    object
        Return value.
    """
    for tok in tokens:
        if tok in skip:
            continue
        if _ICAO.fullmatch(tok) and tok not in {"KT", "MPS", "SM"}:
            return tok
    return None


def _token_index(tokens: list[str], matcher: re.Pattern[str]) -> int | None:
    """
    Internal helper ``_token_index``.

    Parameters
    ----------
    tokens : object
        Argument ``tokens``.
    matcher : object
        Argument ``matcher``.

    Returns
    -------
    object
        Return value.
    """
    for i, tok in enumerate(tokens):
        if matcher.fullmatch(tok):
            return i
    return None


def _first_icao_index(tokens: list[str], skip: frozenset[str]) -> int | None:
    """
    Internal helper ``_first_icao_index``.

    Parameters
    ----------
    tokens : object
        Argument ``tokens``.
    skip : object
        Argument ``skip``.

    Returns
    -------
    object
        Return value.
    """
    for i, tok in enumerate(tokens):
        if tok in skip:
            continue
        if _ICAO.fullmatch(tok) and tok not in {"KT", "MPS", "SM"}:
            return i
    return None


def _consume_wx_descriptors(rest: str) -> str:
    """
    Internal helper ``_consume_wx_descriptors``.

    Parameters
    ----------
    rest : object
        Argument ``rest``.

    Returns
    -------
    object
        Return value.
    """
    while len(rest) >= 2:
        matched = False
        for desc in _WX_DESCRIPTORS:
            if rest.startswith(desc) and len(rest) > len(desc):
                rest = rest[len(desc) :]
                matched = True
                break
        if not matched:
            break
    return rest


def _is_valid_weather_token(token: str) -> bool:
    """
    Internal helper ``_is_valid_weather_token``.

    Parameters
    ----------
    token : object
        Argument ``token``.

    Returns
    -------
    object
        Return value.
    """
    if token in _WX_SPECIAL:
        return True
    if not _WX_TOKEN_SHAPE.fullmatch(token):
        return False
    rest = token
    if rest and rest[0] in "-+":
        if len(rest) > 1 and rest[1] in "-+":
            return False
        if "VC" in rest:
            return False
        rest = rest[1:]
    if not rest:
        return False
    if rest == "VCSH":
        return True
    if rest.endswith(("+", "-")):
        return False
    rest = _consume_wx_descriptors(rest)
    if not rest:
        return False
    if rest in _WX_STANDALONE or rest in _WX_PHENOMENA:
        return True
    while rest:
        matched = False
        for phen in sorted(_WX_PHENOMENA, key=len, reverse=True):
            if rest.startswith(phen):
                rest = rest[len(phen) :]
                matched = True
                break
        if not matched:
            return False
    return True


def _weather_candidate_tokens(tokens: list[str]) -> list[tuple[int, str]]:
    """
    Internal helper ``_weather_candidate_tokens``.

    Parameters
    ----------
    tokens : object
        Argument ``tokens``.

    Returns
    -------
    object
        Return value.
    """
    wind_i = _token_index(tokens, _WIND)
    if wind_i is None:
        return []
    candidates: list[tuple[int, str]] = []
    for i, tok in enumerate(tokens[wind_i + 1 :], start=wind_i + 1):
        if _CLOUD_START.match(tok) or _TEMP.fullmatch(tok) or _QNH.fullmatch(tok):
            break
        if tok in _METAR_SPECI_SKIP or _RVR.match(tok):
            continue
        if _WIND.fullmatch(tok) or _VIS_OK.fullmatch(tok) or _VIS_BAD.fullmatch(tok):
            continue
        if _WX_TOKEN_SHAPE.fullmatch(tok):
            candidates.append((i, tok))
    return candidates


def _token_span_in_core(core: str, token: str, body_start: int) -> tuple[int, int] | None:
    """
    Internal helper ``_token_span_in_core``.

    Parameters
    ----------
    core : object
        Argument ``core``.
    token : object
        Argument ``token``.
    body_start : object
        Argument ``body_start``.

    Returns
    -------
    object
        Return value.
    """
    match = re.search(r"\b" + re.escape(token) + r"\b", core)
    if not match:
        return None
    return body_start + match.start(), body_start + match.end()


def _is_valid_cloud_token(token: str) -> bool:
    """
    Internal helper ``_is_valid_cloud_token``.

    Parameters
    ----------
    token : object
        Argument ``token``.

    Returns
    -------
    object
        Return value.
    """
    return bool(_CLOUD_OK.fullmatch(token))


def _membership_issue(
    *,
    product: str,
    token: str,
    family: str,
    start: int,
    end: int,
    location: str,
) -> Issue:
    """
    Internal helper ``_membership_issue``.

    Parameters
    ----------
    product : object
        Argument ``product``.
    token : object
        Argument ``token``.
    family : object
        Argument ``family``.
    start : object
        Argument ``start``.
    end : object
        Argument ``end``.
    location : object
        Argument ``location``.

    Returns
    -------
    object
        Return value.
    """
    return _issue(
        "UNKNOWN_WMO_MEMBERSHIP",
        f"{product} token {token!r} not in WMO register ({family})",
        start=start,
        end=end,
        location=location,
    )


def _weather_in_register(token: str) -> bool:
    """
    Internal helper ``_weather_in_register``.

    Parameters
    ----------
    token : object
        Argument ``token``.

    Returns
    -------
    object
        Return value.
    """
    if token in {"//"}:
        return True
    return membership.is_member("present_or_forecast_weather", token) or membership.is_member("weather_306_4678", token)


__all__ = [
    "_body_span",
    "_consume_wx_descriptors",
    "_first_icao",
    "_first_icao_index",
    "_is_valid_cloud_token",
    "_is_valid_weather_token",
    "_issue",
    "_membership_issue",
    "_strip_research_refs",
    "_token_index",
    "_token_span_in_core",
    "_weather_candidate_tokens",
    "_weather_in_register",
]
