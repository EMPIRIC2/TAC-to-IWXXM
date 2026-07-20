"""Product-specific TAC checklist and template-gate rules (F12 / E10-21).

Cite paraphrase tables in ``docs/domain/TAC_VALIDATION.md`` only — no Annex prose.
"""

from __future__ import annotations

import re

from tac_validate.issue_registry import issue_from
from tac_validate.models import Issue

_ICAO = re.compile(r"\b[A-Z]{4}\b")
_OBS_TIME = re.compile(r"\b\d{6}Z\b")
_WIND = re.compile(r"\b(?:(?:VRB|\d{3})\d{2,3}(?:G\d{2,3})?(?:KT|MPS)|CALM)\b")
# R2: CAVOK | statute miles (incl. fractions / M|P prefix) | 4-digit meters (9999).
_VIS_OK = re.compile(r"\b(?:CAVOK|P?\d{1,2}SM|[MP]?\d{1,2}/\d{1,2}SM|\d{1,2}\s+[MP]?\d{1,2}/\d{1,2}SM|\d{4})\b")
_VIS_BAD = re.compile(
    r"\b(\d+KM|\d+MILES|\d{5,})\b",
    re.IGNORECASE,
)
# R3: WMO 306 Table 4678 subset — intensity / descriptor / phenomenon grammar.
_WX_PHENOMENA = frozenset(
    {
        "DZ",
        "RA",
        "SN",
        "SG",
        "IC",
        "PL",
        "GR",
        "GS",
        "UP",
        "BR",
        "FG",
        "FU",
        "VA",
        "DU",
        "SA",
        "HZ",
        "PY",
        "PO",
        "SQ",
        "FC",
        "SS",
        "DS",
    }
)
_WX_DESCRIPTORS = ("VC", "MI", "BC", "PR", "DR", "BL", "SH", "TS", "FZ")
_WX_STANDALONE = frozenset({"TS", "SS", "DS", "SQ", "FC", "PO", "BR", "FG", "FU", "HZ", "VA", "DU", "SA", "PY"})
_WX_SPECIAL = frozenset({"UP", "//"})
_RVR = re.compile(r"^R\d{2}")
# R8: RVR runway visual range (simplified ICAO/US shapes).
_RVR_OK = re.compile(r"^R\d{2}[LCR]?/(?:[MP]?\d{4}(?:V[MP]?\d{4})?|////)(?:FT|N)?$")
_WIND_TOKEN = re.compile(r"(?:KT|MPS)$|^CALM$")
_CLOUD_START = re.compile(r"^(?:FEW|SCT|BKN|OVC|VV|NSC|NCD|SKC|CLR)")
# R4: FEW|SCT|BKN|OVC + 3-digit height + optional CB|TCU; VV###|VV///; NSC|NCD|SKC|CLR.
_CLOUD_OK = re.compile(r"^(?:(?:FEW|SCT|BKN|OVC)\d{3}(?:CB|TCU)?|VV(?:\d{3}|///)|NSC|NCD|SKC|CLR)$")
_CLOUD_LIKE = re.compile(r"^(?:FEW|SCT|BKN|OVC|VV|NSC|NCD|SKC|CLR|[A-Z]{3}\d{3})")
# R5: US METAR remarks (iwxxm_us) — AO1/AO2, SLP###, P####, T########, PK WND dddss/tt.
_RMK_AO = frozenset({"AO1", "AO2"})
_RMK_SLP_OK = re.compile(r"^SLP\d{3}$")
_RMK_P_OK = re.compile(r"^P\d{4}$")
_RMK_T_OK = re.compile(r"^T\d{8}$")
_RMK_PK_VAL = re.compile(r"^\d{5}/\d{2,4}$")
_WX_TOKEN_SHAPE = re.compile(r"^(?://|[+-]{1,2}[A-Z]{2,8}|[A-Z]{2,8}[+-]|[+-]?[A-Z]{2,8})$")
_TEMP = re.compile(r"\bM?\d{2}/M?\d{2}\b")
_QNH = re.compile(r"\b[QA]\d{4}\b")
_TAF_VALIDITY = re.compile(r"\b\d{4}/\d{4}\b")
_VALID_PERIOD = re.compile(r"\bVALID\s+\d{6}/\d{6}\b", re.IGNORECASE)
_DTG_LINE = re.compile(r"(?m)^\s*DTG\s*:", re.IGNORECASE)
_VAAC_LINE = re.compile(r"(?m)^\s*VAAC\s*:", re.IGNORECASE)
_MAX_WIND_LINE = re.compile(r"(?m)^\s*MAX\s+WIND\s*:", re.IGNORECASE)

# Phenomenon family markers (template+gate — not exhaustive Annex vocab).
_SIGMET_FAMILIES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("TS", re.compile(r"\b(?:OBSC|EMBD|FRQ|SQL)?\s*TS(?:GR)?\b")),
    ("TURB", re.compile(r"\b(?:SEV|MOD)?\s*TURB\b")),
    ("ICE", re.compile(r"\b(?:SEV|MOD)?\s*ICE\b")),
    ("MTW", re.compile(r"\b(?:SEV|MOD)?\s*MTW\b")),
    ("DS_SS", re.compile(r"\b(?:HVY\s+)?(?:DS|SS)\b")),
    ("VA", re.compile(r"\bVA\b")),
    ("TC", re.compile(r"\bTC\b")),
    ("RDOACT", re.compile(r"\bRDOACT\s+CLD\b")),
)
_AIRMET_FAMILIES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("TS", re.compile(r"\b(?:ISOL|OCNL|FRQ)\s+TS\b")),
    ("ICE", re.compile(r"\b(?:MOD|SEV)?\s*ICE\b")),
    ("TURB", re.compile(r"\b(?:MOD|SEV)?\s*TURB\b")),
    ("MTW", re.compile(r"\b(?:MOD|SEV)?\s*MTW\b")),
    ("MT_OBSC", re.compile(r"\bMT\s+OBSC\b")),
    ("CLD", re.compile(r"\b(?:BKN|OVC)\s+CLD\b")),
    ("CB_TCU", re.compile(r"\b(?:ISOL|OCNL|FRQ)\s+(?:CB|TCU)\b")),
    ("SFC", re.compile(r"\bSFC\s+(?:WIND|VIS)\b")),
)

_METAR_SPECI_SKIP = frozenset({"METAR", "SPECI", "COR", "AUTO", "NIL", "CAVOK", "NOSIG"})
_TAF_SKIP = frozenset({"TAF", "AMD", "COR", "NIL", "CNL", "CAVOK"})


def _issue(
    code: str,
    message: str,
    *,
    start: int,
    end: int,
    location: str = "body",
) -> Issue:
    """Build an Issue via the registry (severity from IssueSpec; message preserved)."""
    return issue_from(
        code,
        message=message,
        location=location,
        start=start,
        end=end,
    )


def _body_span(tac: str) -> tuple[int, int, str]:
    stripped = tac.strip()
    if not stripped:
        return 0, len(tac), ""
    leading = len(tac) - len(tac.lstrip())
    return leading, leading + len(stripped), stripped


def _first_icao(tokens: list[str], skip: frozenset[str]) -> str | None:
    for tok in tokens:
        if tok in skip:
            continue
        if _ICAO.fullmatch(tok) and tok not in {"KT", "MPS", "SM"}:
            return tok
    return None


def _token_index(tokens: list[str], matcher: re.Pattern[str]) -> int | None:
    for i, tok in enumerate(tokens):
        if matcher.fullmatch(tok):
            return i
    return None


def _first_icao_index(tokens: list[str], skip: frozenset[str]) -> int | None:
    for i, tok in enumerate(tokens):
        if tok in skip:
            continue
        if _ICAO.fullmatch(tok) and tok not in {"KT", "MPS", "SM"}:
            return i
    return None


def _consume_wx_descriptors(rest: str) -> str:
    while len(rest) >= 2:
        matched = False
        for desc in _WX_DESCRIPTORS:
            if rest.startswith(desc):
                rest = rest[len(desc) :]
                matched = True
                break
        if not matched:
            break
    return rest


def _is_valid_weather_token(token: str) -> bool:
    """Return True when ``token`` is a valid A3-2 present weather group (4678 subset)."""
    if token in _WX_SPECIAL:
        return True
    if not _WX_TOKEN_SHAPE.fullmatch(token):
        return False
    if token.endswith(("+", "-")):
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
    """Return (index, token) pairs for optional present-weather groups after visibility."""
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
    match = re.search(r"\b" + re.escape(token) + r"\b", core)
    if not match:
        return None
    return body_start + match.start(), body_start + match.end()


def _is_valid_cloud_token(token: str) -> bool:
    """Return True when ``token`` is a valid A3-2 cloud / VV / NSC-class group."""
    return bool(_CLOUD_OK.fullmatch(token))


def _cloud_candidate_tokens(tokens: list[str]) -> list[tuple[int, str]]:
    """Return (index, token) pairs for cloud-like groups after wind / visibility / wx."""
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
    span = _token_span_in_core(core, token, body_start)
    if span is None:
        start, end = body_start, body_end
    else:
        start, end = span
    issues.append(_issue(code, message, start=start, end=end, location="remark"))


def _check_us_remarks(
    tokens: list[str],
    *,
    product: str,
    core: str,
    body_start: int,
    body_end: int,
) -> list[Issue]:
    """Lint US REMARKS after ``RMK`` (research R5 / iwxxm_us awareness)."""
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
                message=f"{product} malformed remark {tok!r} (SLP needs 3 digits) — research R5 / iwxxm_us",
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
                message=f"{product} malformed remark {tok!r} (P precip needs 4 digits) — research R5 / iwxxm_us",
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
                message=f"{product} malformed remark {tok!r} (T tenths needs 8 digits) — research R5 / iwxxm_us",
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
                message=f"{product} malformed remark PK WND (need dddss/tt) — research R5 / iwxxm_us",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token=span_tok,
            )
            i += 2 if has_wnd else 1
            continue
        i += 1

    if saw_us:
        _append_remark_issue(
            issues,
            code="REMARK_US_EXTENSION",
            message=(
                f"{product} US remarks present (AO1/AO2/SLP/P/T/PK WND) — iwxxm_us profile awareness; research R5"
            ),
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="RMK",
        )
    return issues


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
    span = _token_span_in_core(core, token, body_start)
    if span is None:
        start, end = body_start, body_end
    else:
        start, end = span
    issues.append(_issue(code, message, start=start, end=end, location="modifier"))


def _check_r8_pack(
    tokens: list[str],
    *,
    product: str,
    core: str,
    body_start: int,
    body_end: int,
) -> list[Issue]:
    """AUTO/COR/NOSIG/TEMPO/RVR/VRB·gust info + INVALID_RVR/WIND (research R8)."""
    issues: list[Issue] = []
    if "AUTO" in tokens:
        _emit_token_info(
            issues,
            code="AUTO_PRESENT",
            message=f"{product} AUTO modifier present — research R8",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="AUTO",
        )
    if "COR" in tokens:
        _emit_token_info(
            issues,
            code="COR_PRESENT",
            message=f"{product} COR modifier present — research R8",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="COR",
        )
    if "NOSIG" in tokens:
        _emit_token_info(
            issues,
            code="NOSIG_PRESENT",
            message=f"{product} NOSIG trend present — research R8",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="NOSIG",
        )
    if "TEMPO" in tokens:
        _emit_token_info(
            issues,
            code="TEMPO_PRESENT",
            message=f"{product} TEMPO trend present — research R8",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="TEMPO",
        )

    for tok in tokens:
        if not _RVR.match(tok):
            continue
        if _RVR_OK.fullmatch(tok):
            _emit_token_info(
                issues,
                code="RVR_PRESENT",
                message=f"{product} RVR group {tok!r} present — research R8",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token=tok,
            )
        else:
            _emit_token_info(
                issues,
                code="INVALID_RVR",
                message=f"{product} invalid RVR token {tok!r} — research R8",
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
            message=f"{product} invalid wind token {tok!r} — research R8",
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
                message=f"{product} wind {tok!r} uses VRB and/or gust — research R8",
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
    """Warn when CCCC / ddhhmmZ / wind are present but not in A3-2 body order."""
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
        f"{product} groups out of A3-2 order (CCCC → ddhhmmZ → wind) — research R1",
        start=start,
        end=end,
        location="order",
    )


def _check_metar_speci(tac: str, product: str) -> list[Issue]:
    start, end, body = _body_span(tac)
    upper = body.upper()
    # Drop trailing '=' for token scans.
    core = upper[:-1] if upper.endswith("=") else upper
    tokens = core.replace("=", " ").split()
    issues: list[Issue] = []

    cccc = _first_icao(tokens, _METAR_SPECI_SKIP)
    if cccc is None:
        issues.append(
            _issue(
                "MISSING_CCCC",
                f"{product} missing ICAO location (CCCC) — A3-2 #2",
                start=start,
                end=end,
                location="station",
            )
        )

    if not _OBS_TIME.search(core):
        issues.append(
            _issue(
                "MISSING_OBS_TIME",
                f"{product} missing observation time ddhhmmZ — A3-2 #3",
                start=start,
                end=end,
                location="time",
            )
        )

    # R8 NIL: short-circuit body checklist when NIL is the report content.
    if "NIL" in tokens:
        if "AUTO" in tokens:
            _emit_token_info(
                issues,
                code="AUTO_PRESENT",
                message=f"{product} AUTO modifier present — research R8",
                core=core,
                body_start=start,
                body_end=end,
                token="AUTO",
            )
        if "COR" in tokens:
            _emit_token_info(
                issues,
                code="COR_PRESENT",
                message=f"{product} COR modifier present — research R8",
                core=core,
                body_start=start,
                body_end=end,
                token="COR",
            )
        trailing = tokens[tokens.index("NIL") + 1 :]
        if trailing:
            _emit_token_info(
                issues,
                code="INVALID_NIL",
                message=f"{product} NIL must not include body groups — research R8",
                core=core,
                body_start=start,
                body_end=end,
                token="NIL",
            )
        else:
            _emit_token_info(
                issues,
                code="NIL_REPORT",
                message=f"{product} NIL report — research R8",
                core=core,
                body_start=start,
                body_end=end,
                token="NIL",
            )
        return issues

    wind_tokens = [t for t in tokens if t == "CALM" or t.endswith(("KT", "MPS"))]
    has_good_wind = any(_WIND.fullmatch(t) for t in wind_tokens)
    if not has_good_wind and not wind_tokens:
        issues.append(
            _issue(
                "MISSING_WIND",
                f"{product} missing surface wind group — A3-2 #5",
                start=start,
                end=end,
                location="wind",
            )
        )

    order_issue = _check_metar_speci_field_order(tokens, product=product, start=start, end=end)
    if order_issue is not None:
        issues.append(order_issue)

    # Visibility lives before RMK — do not treat PK WND dddss/tt digits as vis (R2/R5).
    rmk_at = core.find("RMK")
    vis_core = core[:rmk_at] if rmk_at >= 0 else core
    bad_vis = list(_VIS_BAD.finditer(vis_core))
    if bad_vis:
        for match in bad_vis:
            issues.append(
                _issue(
                    "INVALID_VISIBILITY",
                    f"{product} invalid visibility token {match.group(1)!r} — research R2",
                    start=start + match.start(1),
                    end=start + match.end(1),
                    location="visibility",
                )
            )
    elif not _VIS_OK.search(vis_core):
        issues.append(
            _issue(
                "MISSING_VISIBILITY",
                f"{product} missing visibility or CAVOK — A3-2 #6",
                start=start,
                end=end,
                location="visibility",
            )
        )

    for _i, wx_tok in _weather_candidate_tokens(tokens):
        if _is_valid_weather_token(wx_tok):
            continue
        span = _token_span_in_core(core, wx_tok, start)
        if span is None:
            issues.append(
                _issue(
                    "INVALID_WEATHER",
                    f"{product} invalid present weather token {wx_tok!r} — A3-2 #8 / research R3",
                    start=start,
                    end=end,
                    location="weather",
                )
            )
        else:
            wx_start, wx_end = span
            issues.append(
                _issue(
                    "INVALID_WEATHER",
                    f"{product} invalid present weather token {wx_tok!r} — A3-2 #8 / research R3",
                    start=wx_start,
                    end=wx_end,
                    location="weather",
                )
            )

    if not _TEMP.search(core):
        issues.append(
            _issue(
                "MISSING_TEMP_DEWPOINT",
                f"{product} missing temperature/dewpoint tt/td — A3-2 #10",
                start=start,
                end=end,
                location="temperature",
            )
        )

    if not _QNH.search(core):
        issues.append(
            _issue(
                "MISSING_QNH",
                f"{product} missing QNH/altimeter (Qnnnn/Annnn) — A3-2 #11",
                start=start,
                end=end,
                location="pressure",
            )
        )

    for _i, cloud_tok in _cloud_candidate_tokens(tokens):
        span = _token_span_in_core(core, cloud_tok, start)
        if span is None:
            cloud_start, cloud_end = start, end
        else:
            cloud_start, cloud_end = span
        if not _is_valid_cloud_token(cloud_tok):
            issues.append(
                _issue(
                    "INVALID_CLOUD_TOKEN",
                    f"{product} invalid cloud/VV token {cloud_tok!r} — A3-2 #9 / research R4",
                    start=cloud_start,
                    end=cloud_end,
                    location="cloud",
                )
            )
            continue
        if cloud_tok.endswith(("CB", "TCU")):
            issues.append(
                _issue(
                    "CLOUD_CB_OR_TCU",
                    f"{product} cloud group {cloud_tok!r} includes convective type — research R4",
                    start=cloud_start,
                    end=cloud_end,
                    location="cloud",
                )
            )

    issues.extend(
        _check_us_remarks(
            tokens,
            product=product,
            core=core,
            body_start=start,
            body_end=end,
        )
    )
    issues.extend(
        _check_r8_pack(
            tokens,
            product=product,
            core=core,
            body_start=start,
            body_end=end,
        )
    )

    return issues


def _check_taf(tac: str) -> list[Issue]:
    start, end, body = _body_span(tac)
    upper = body.upper()
    core = upper[:-1] if upper.endswith("=") else upper
    tokens = core.replace("=", " ").split()
    issues: list[Issue] = []

    if _first_icao(tokens, _TAF_SKIP) is None:
        issues.append(
            _issue(
                "MISSING_CCCC",
                "TAF missing ICAO location (CCCC) — A5-1 #2",
                start=start,
                end=end,
                location="station",
            )
        )

    if not _OBS_TIME.search(core):
        issues.append(
            _issue(
                "MISSING_ISSUE_TIME",
                "TAF missing issue time ddhhmmZ — A5-1 #3",
                start=start,
                end=end,
                location="time",
            )
        )

    if not _TAF_VALIDITY.search(core):
        issues.append(
            _issue(
                "MISSING_VALIDITY",
                "TAF missing validity period ddhh/ddhh — A5-1 #5",
                start=start,
                end=end,
                location="validity",
            )
        )

    if "CNL" in tokens:
        # CNL must terminate the forecast content (A5-1 #6 paraphrase).
        cnl_idx = tokens.index("CNL")
        trailing = [t for t in tokens[cnl_idx + 1 :] if t not in {"="}]
        if trailing:
            issues.append(
                _issue(
                    "INVALID_CNL_SHAPE",
                    "TAF CNL must end the message — A5-1 #6",
                    start=start,
                    end=end,
                    location="cnl",
                )
            )

    return issues


def _count_families(text: str, families: tuple[tuple[str, re.Pattern[str]], ...]) -> list[str]:
    found: list[str] = []
    for name, pattern in families:
        if pattern.search(text):
            found.append(name)
    return found


def _check_sigmet_airmet(tac: str, product: str) -> list[Issue]:
    start, end, body = _body_span(tac)
    upper = body.upper()
    issues: list[Issue] = []

    if not _VALID_PERIOD.search(upper):
        issues.append(
            _issue(
                "MISSING_VALID",
                f"{product} missing VALID ddhhmm/ddhhmm period — A6 identity",
                start=start,
                end=end,
                location="valid",
            )
        )

    families = _SIGMET_FAMILIES if product == "SIGMET" else _AIRMET_FAMILIES
    hit = _count_families(upper, families)
    if len(hit) > 1:
        issues.append(
            _issue(
                "MULTIPLE_PHENOMENA",
                f"{product} encodes multiple phenomenon families {hit} — A6 one-phenomenon gate",
                start=start,
                end=end,
                location="phenomenon",
            )
        )

    return issues


def _check_vaa(tac: str) -> list[Issue]:
    start, end, body = _body_span(tac)
    issues: list[Issue] = []
    if not _DTG_LINE.search(body):
        issues.append(
            _issue(
                "MISSING_DTG",
                "VAA missing DTG: template field — A2-1",
                start=start,
                end=end,
                location="dtg",
            )
        )
    if not _VAAC_LINE.search(body):
        issues.append(
            _issue(
                "MISSING_VAAC",
                "VAA missing VAAC: template field — A2-1",
                start=start,
                end=end,
                location="vaac",
            )
        )
    return issues


def _check_tca(tac: str) -> list[Issue]:
    start, end, body = _body_span(tac)
    issues: list[Issue] = []
    if not _DTG_LINE.search(body):
        issues.append(
            _issue(
                "MISSING_DTG",
                "TCA missing DTG: template field — A2-2",
                start=start,
                end=end,
                location="dtg",
            )
        )
    if not _MAX_WIND_LINE.search(body):
        issues.append(
            _issue(
                "MISSING_MAX_WIND",
                "TCA missing MAX WIND: template field — A2-2",
                start=start,
                end=end,
                location="max_wind",
            )
        )
    return issues


def check_product_rules(tac_text: str, product: str) -> list[Issue]:
    """
    Run product checklist / template-gate rules after parse-gate success.

    Parameters
    ----------
    tac_text :
        Raw TAC text.
    product :
        F6 product id.

    Returns
    -------
    list[Issue]
        Error-severity findings with spans when possible.
    """
    if product in {"METAR", "SPECI"}:
        return _check_metar_speci(tac_text, product)
    if product == "TAF":
        return _check_taf(tac_text)
    if product in {"SIGMET", "AIRMET"}:
        return _check_sigmet_airmet(tac_text, product)
    if product == "VAA":
        return _check_vaa(tac_text)
    if product == "TCA":
        return _check_tca(tac_text)
    return []


__all__ = ["check_product_rules"]
