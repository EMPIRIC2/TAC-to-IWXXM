"""Shared emit helpers for WMO-782 extended METAR/SPECI checks."""

from __future__ import annotations

import re

from tac_validate.models import Issue
from tac_validate.product_rules_pkg._common import _issue, _token_span_in_core

CLOUD_LAYER = re.compile(r"^(?:FEW|SCT|BKN|OVC)(\d{3})(CB|TCU)?$")
CLOUD_SOLIDUS = re.compile(r"^(?:FEW|SCT|BKN|OVC|VV)/{3}")
CLOUD_BAD_SUFFIX = re.compile(r"^(?:FEW|SCT|BKN|OVC)\d{3}([A-Z]{2,3})$")
RVR_TOKEN = re.compile(
    r"^R(?P<rwy>\d{2}[LCR]?)/(?P<body>[MP]?\d{4}|/////)(?P<var>V[MP]?\d{4})?(?:FT)?(?P<tend>/?[UDNX])?$"
)
RECENT = re.compile(r"^RE(?P<body>.+)$")
SEA_W = re.compile(r"^W\d{2}/(?:S\d|H\d{3})$")
TEMP_PAIR = re.compile(r"^(M?\d{2}|/{2,3})/(M?\d{2}|/{2,3})$")
QNH = re.compile(r"^(?P<pre>[QA])(?P<digits>\d{4}|/{4})$")
FM6 = re.compile(r"^FM\d{6}$")
WX_TRAILING_INTENSITY = re.compile(r"^[A-Z]{2,}[+-]$")


def emit(
    issues: list[Issue],
    code: str,
    message: str,
    *,
    core: str,
    tok: str,
    body_start: int,
    body_end: int,
    location: str,
) -> None:
    """Append a registry-backed issue with a token span when available."""
    span = _token_span_in_core(core, tok, body_start)
    start, end = span if span is not None else (body_start, body_end)
    issues.append(_issue(code, message, start=start, end=end, location=location))


def parse_temp_c(token: str) -> int | None:
    """Parse a METAR temperature token into Celsius, or None if missing."""
    if token in {"//", "///"} or set(token) <= {"/"}:
        return None
    if token.startswith("M"):
        return -int(token[1:])
    return int(token)


def rvr_value_on_scale(raw: str) -> bool:
    """Return True when an RVR numeric body follows handbook reporting steps."""
    if raw in {"/////", "////"}:
        return True
    body = raw.lstrip("MP")
    if not body.isdigit():
        return False
    value = int(body)
    if raw.startswith("P"):
        return value >= 2000
    if value < 400:
        return value % 25 == 0
    if value < 800:
        return value % 50 == 0
    if value <= 2000:
        return value % 100 == 0
    return False


def split_obs_trend(body: list[str]) -> tuple[list[str], list[str]]:
    """Split observation tokens from TREND change groups at the earliest marker."""
    markers = ("BECMG", "TEMPO", "NOSIG")
    idxs = [body.index(m) for m in markers if m in body]
    if not idxs:
        return body, []
    i = min(idxs)
    return body[:i], body[i:]


def dedupe(issues: list[Issue]) -> list[Issue]:
    """Keep first issue per (code, start, message)."""
    seen: set[tuple[str, int, str]] = set()
    out: list[Issue] = []
    for issue in issues:
        key = (issue.code, issue.start or 0, issue.message)
        if key in seen:
            continue
        seen.add(key)
        out.append(issue)
    return out
