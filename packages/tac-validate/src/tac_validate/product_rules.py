"""Product-specific TAC checklist and template-gate rules (F12 / E10-21).

Cite paraphrase tables in ``docs/domain/TAC_VALIDATION.md`` only — no Annex prose.
"""

from __future__ import annotations

import re

from tac_validate import membership
from tac_validate.issue_registry import issue_from
from tac_validate.models import Issue

_ICAO = re.compile(r"\b[A-Z]{4}\b")
_OBS_TIME = re.compile(r"\b\d{6}Z\b")
_WIND = re.compile(r"\b(?:(?:VRB|\d{3})\d{2,3}(?:G\d{2,3})?(?:KT|MPS)|CALM)\b")
# Extreme direction variation group (Guidance: counter-clockwise then clockwise).
_WIND_DIR_VAR = re.compile(r"^\d{3}V\d{3}$")
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
# ICAO tendency U|D|N may follow the value (and optional FT for US). EV-040: R12/1000U
# from WMO A3-1 is valid — prior pattern only allowed bare N/FT, not U/D.
_RVR_OK = re.compile(r"^R\d{2}[LCR]?/(?:[MP]?\d{4}(?:V[MP]?\d{4})?|////)(?:FT)?[UDN]?$")
# WMO AHL heading: T1T2A1A2ii CCCC YYGGgg [BBB] — YYGGgg must not be treated as visibility.
_AHL_HEADING_LINE = re.compile(r"^[A-Z]{2}[A-Z]{2}\d{2}\s+[A-Z]{4}\s+\d{6}(?:\s+[A-Z]{3})?\s*$")
_WIND_TOKEN = re.compile(r"(?:KT|MPS)$|^CALM$")
_CLOUD_START = re.compile(r"^(?:FEW|SCT|BKN|OVC|VV|NSC|NCD|SKC|CLR)")
# R4: FEW|SCT|BKN|OVC + 3-digit height + optional CB|TCU; VV###|VV///; NSC|NCD|SKC|CLR.
_CLOUD_OK = re.compile(r"^(?:(?:FEW|SCT|BKN|OVC)\d{3}(?:CB|TCU)?|VV(?:\d{3}|///)|NSC|NCD|SKC|CLR)$")
_CLOUD_LIKE = re.compile(r"^(?:FEW|SCT|BKN|OVC|VV|NSC|NCD|SKC|CLR|[A-Z]{3}\d{3})")
# Layered amounts only (NSC exclusivity / TC-EV023-001) — not VV/NSC/NCD/SKC/CLR.
_LAYER_CLOUD_TOKEN = re.compile(r"^(?:FEW|SCT|BKN|OVC)\d{3}(?:CB|TCU)?$")
# R5: US METAR remarks (iwxxm_us) — AO1/AO2, SLP###, P####, T########, PK WND dddss/tt.
_RMK_AO = frozenset({"AO1", "AO2"})
_RMK_SLP_OK = re.compile(r"^SLP\d{3}$")
_RMK_P_OK = re.compile(r"^P\d{4}$")
_RMK_T_OK = re.compile(r"^T\d{8}$")
_RMK_PK_VAL = re.compile(r"^\d{5}/\d{2,4}$")
_RMK_PRES_CA = re.compile(r"^PRES(?:FR|RR)$")
_RMK_NOSPECI = re.compile(r"^NOSPECI$")
_RMK_SECTOR_VIS_IN_TEXT = re.compile(r"\bVIS\s+M?(?:(?:\d+\s+)?\d/\d|\d+)(?!V)(?!\s+RWY)\s*(?:N|NE|E|SE|S|SW|W|NW)\b")
_NCLWS_TAC = re.compile(r"^WS\d{3}/\d{3}\d{2,3}KT$")
_CA_GFA_PHENOM = re.compile(
    r"\b(?:FRQ|OCNL)\s+TCU\s+ISOL\s+TS(?:GR)?\b|\bSFC\s+VIS\s+AND\s+(?:BKN|OVC)\s+CLD\b",
    re.IGNORECASE,
)
_GFA_CHART = re.compile(r"\bRMK\s+GFACN\d+\b", re.IGNORECASE)
_TAF_VIS_SM = re.compile(r"^P?\d{1,2}SM$")
_ALT_INHG_BODY = re.compile(r"\bA\d{4}\b")
_ALT_NOT_OBS_BODY = re.compile(r"\bA////(?=\s|$)")
_WX_TOKEN_SHAPE = re.compile(r"^(?://|[+-]{1,2}[A-Z]{2,8}|[A-Z]{2,8}[+-]|[+-]?[A-Z]{2,8})$")
_TEMP = re.compile(r"\bM?\d{2}/M?\d{2}\b")
_QNH = re.compile(r"\b[QA]\d{4}\b")
_QNH_NOT_OBS = re.compile(r"\b[QA]////(?=\s|$)")
_TAF_VALIDITY = re.compile(r"\b\d{4}/\d{4}\b")
_TAF_FM = re.compile(r"^FM(?:\d{6})?$")
_TAF_PROB = re.compile(r"^PROB(\d{2})$")
_TAF_TL = re.compile(r"^TL(?:\d{4})?$")
_TAF_AT = re.compile(r"^AT(?:\d{4})?$")
_TAF_TX_TN = re.compile(r"^T[XN]-?\d{2}/\d{4}Z$")
_VALID_PERIOD = re.compile(r"\bVALID\s+\d{6}/\d{6}\b", re.IGNORECASE)
_DTG_LINE = re.compile(r"(?m)^\s*DTG\s*:", re.IGNORECASE)
_VAAC_LINE = re.compile(r"(?m)^\s*VAAC\s*:", re.IGNORECASE)
_VOLCANO_LINE = re.compile(r"(?m)^\s*VOLCANO\s*:\s*(.*)$", re.IGNORECASE)
_RMK_LINE = re.compile(r"(?m)^\s*RMK\s*:\s*(.*)$", re.IGNORECASE)
_NXT_ADVISORY_LINE = re.compile(r"(?m)^\s*NXT\s+ADVISORY\s*:\s*(.*)$", re.IGNORECASE)
_NO_VA_EXP = re.compile(r"\bNO\s+VA\s+EXP\b", re.IGNORECASE)
_SWXC_LINE = re.compile(r"(?m)^\s*SWXC\s*:", re.IGNORECASE)
_SWX_EFFECT_LINE = re.compile(r"(?m)^\s*SWX\s+EFFECT\s*:\s*(.+?)\s*$", re.IGNORECASE)
_OBS_SWX_LINE = re.compile(r"(?m)^\s*OBS\s+SWX\s*:\s*(.+)$", re.IGNORECASE)
_NO_SWX_EXP = re.compile(r"\bNO\s+SWX\s+EXP\b", re.IGNORECASE)
# SpaceWxPhenomena register prefixes (vendor CSV) — TAC EFFECT uses spaces.
_SWX_EFFECT_PREFIX: dict[str, str] = {
    "HF COM": "HF_COM",
    "GNSS": "GNSS",
    "RADIATION": "RADIATION",
    "SATCOM": "SATCOM",
}
_MAX_WIND_LINE = re.compile(r"(?m)^\s*MAX\s+WIND\s*:", re.IGNORECASE)
_SVO_LINE = re.compile(r"(?m)^\s*SVO\s*:", re.IGNORECASE)
_ONSET_LINE = re.compile(r"(?m)^\s*ONSET\s*:\s*(.*)$", re.IGNORECASE)
_DUR_LINE = re.compile(r"(?m)^\s*DUR\s*:\s*(.*)$", re.IGNORECASE)
_TC_LINE = re.compile(r"(?m)^\s*TC\s*:\s*(.*)$", re.IGNORECASE)
_CB_LINE = re.compile(r"(?m)^\s*CB\s*:\s*(.*)$", re.IGNORECASE)
_NXT_MSG_LINE = re.compile(r"(?m)^\s*NXT\s+MSG\s*:\s*(.*)$", re.IGNORECASE)
# F23 theme G1 — general SIGMET exceptional TAC shapes (#733).
_SIGMET_POINT_COORD = re.compile(r"\b[NS]\d{4,5}\s+[EW]\d{5,7}\b")
_SIGMET_LEVEL_RANGE = re.compile(
    r"\b(?:FL\d{3}/\d{3}|SFC/FL\d{3}|\d{4}/\d{4}FT)\b",
)
_SIGMET_SINGLE_LEVEL = re.compile(r"\b(?:FL\d{3}|\d{4}(?:FT|M))\b")
_SIGMET_TOP_ABV_BLW = re.compile(r"\bTOP\s+(?:ABV|BLW)\b")
_SIGMET_WI = re.compile(r"\bWI\b")
_SIGMET_STNR = re.compile(r"\bSTNR\b")
_SIGMET_MOV = re.compile(r"\bMOV\b")
_SIGMET_CNL = re.compile(r"\bCNL\b")
_SIGMET_COR = re.compile(r"\bCOR\b")
_SIGMET_SEQ = re.compile(r"\bSIGMET\s+(\d{1,3})\b")
_SIGMET_NO_SEQ = re.compile(r"\bSIGMET\s+VALID\b")
_AIRMET_SEQ = re.compile(r"\bAIRMET\s+(\d{1,3})\b")
_AIRMET_NO_SEQ = re.compile(r"\bAIRMET\s+VALID\b")
_SIGMET_VALID_PAIR = re.compile(r"\bVALID\s+(\d{6})/(\d{6})\b")
_SIGMET_FIR_CTA = re.compile(r"\b(?:FIR(?:/UIR)?|CTA|UIR)\b")
_SIGMET_OBS_FCST = re.compile(r"\b(?:OBS|FCST)\b")
_SIGMET_INTENSITY = re.compile(r"\b(?:INTSF|WKN|NC)\b")
_SIGMET_VA_TOKEN = re.compile(r"\bVA\b")
_SIGMET_TC_TOKEN = re.compile(r"\bTC\b")
_SIGMET_VA_VOLCANO = re.compile(r"\bMT\b.+\bPSN\b|\bPSN\b.+\bMT\b")
_SIGMET_VA_CLD = re.compile(r"\bVA\s+CLD\b")
_SIGMET_NO_VA_EXP = re.compile(r"\bNO\s+VA\s+EXP\b")
_SIGMET_CNL_FIR_MOVED = re.compile(r"\b(?:AND|MOV)\s+TO\s+FIR\b")
# TC SIGMET — name/PSN identity vs OF TC CENTRE geometry (#829).
_SIGMET_TC_IDENTITY = re.compile(r"\bTC\s+(?!CENTRE\b)([A-Z][A-Z0-9-]*)\s+PSN\b")
_SIGMET_OF_TC_CENTRE = re.compile(r"\bOF\s+TC\s+CENTRE\b")
_SIGMET_TC_NAME = re.compile(r"\bTC\s+(?!CENTRE\b)([A-Z][A-Z0-9-]*)\b")
_WS_MAX_VALIDITY_HOURS = 4.0
_WV_MAX_VALIDITY_HOURS = 6.0
_WC_MAX_VALIDITY_HOURS = 6.0

# Phenomenon family markers (template+gate — not exhaustive Annex vocab).
# Underscore forms match vendor AirWx/SigWx notations (EV-050 / #959).
_SIGMET_FAMILIES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("TS", re.compile(r"\b(?:OBSC|EMBD|FRQ|SQL)?(?:\s+|_)?TS(?:GR)?\b")),
    ("TURB", re.compile(r"\b(?:SEV|MOD)?(?:\s+|_)?TURB\b")),
    ("ICE", re.compile(r"\b(?:SEV|MOD)?(?:\s+|_)?ICE(?:(?:\s+|_)FZRA)?\b")),
    ("MTW", re.compile(r"\b(?:SEV|MOD)?(?:\s+|_)?MTW\b")),
    ("DS_SS", re.compile(r"\b(?:HVY(?:\s+|_))?(?:DS|SS)\b")),
    ("VA", re.compile(r"\bVA\b")),
    ("TC", re.compile(r"\bTC\b")),
    ("RDOACT", re.compile(r"\bRDOACT(?:\s+|_)CLD\b")),
)
_AIRMET_FAMILIES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("TS", re.compile(r"\b(?:ISOL|OCNL|FRQ)(?:\s+|_)TS(?:GR)?\b")),
    ("ICE", re.compile(r"\b(?:MOD|SEV)?(?:\s+|_)?ICE\b")),
    ("TURB", re.compile(r"\b(?:MOD|SEV)?(?:\s+|_)?TURB\b")),
    ("MTW", re.compile(r"\b(?:MOD|SEV)?(?:\s+|_)?MTW\b")),
    ("MT_OBSC", re.compile(r"\bMT(?:\s+|_)OBSC\b")),
    ("CLD", re.compile(r"\b(?:BKN|OVC)(?:\s+|_)CLD\b")),
    ("CB_TCU", re.compile(r"\b(?:ISOL|OCNL|FRQ)(?:\s+|_)(?:CB|TCU)\b")),
    ("SFC", re.compile(r"\bSFC(?:\s+|_)(?:WIND|VIS)\b")),
)
# Candidate phrases for WMO membership (includes unknown/sad forms).
_AIRMET_PHENOM_CANDIDATE = re.compile(
    r"\b("
    r"(?:ISOL|OCNL|FRQ)(?:\s+|_)[A-Z]{2,}|"
    r"(?:MOD|SEV)(?:\s+|_)(?:ICE|TURB|MTW)|"
    r"MT(?:\s+|_)OBSC|"
    r"(?:BKN|OVC)(?:\s+|_)CLD|"
    r"SFC(?:\s+|_)(?:WIND|VIS)"
    r")\b"
)
_SIGMET_PHENOM_CANDIDATE = re.compile(
    r"\b("
    r"(?:OBSC|EMBD|FRQ|SQL)(?:\s+|_)TS(?:GR)?|"
    r"(?:SEV|MOD)(?:\s+|_)(?:ICE(?:(?:\s+|_)FZRA)?|TURB|MTW)|"
    r"HVY(?:\s+|_)(?:DS|SS)|"
    r"RDOACT(?:\s+|_)CLD|"
    r"VA|TC"
    r")\b"
)
_RECENT_WX = re.compile(r"^RE[A-Z]{2,}$")
_LAYER_CLOUD_PARTS = re.compile(r"^(FEW|SCT|BKN|OVC)\d{3}(CB|TCU)?$")

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


def _membership_issue(
    *,
    product: str,
    token: str,
    family: str,
    start: int,
    end: int,
    location: str,
) -> Issue:
    """Build ``UNKNOWN_WMO_MEMBERSHIP`` for a token missing from a harvested family."""
    return _issue(
        "UNKNOWN_WMO_MEMBERSHIP",
        f"{product} token {token!r} not in WMO register ({family})",
        start=start,
        end=end,
        location=location,
    )


def _weather_in_register(token: str) -> bool:
    """Return True when present-weather ``token`` is in harvested WMO sets."""
    if token in {"//"}:
        return True
    return membership.is_member("present_or_forecast_weather", token) or membership.is_member("weather_306_4678", token)


def _check_phenomenon_membership(
    upper: str,
    *,
    product: str,
    start: int,
    end: int,
) -> list[Issue]:
    """Emit membership errors for SIGMET/AIRMET phenomenon candidates (EV-050)."""
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
    profile: str = "annex3",
) -> list[Issue]:
    """Lint US REMARKS after ``RMK`` (research R5 / iwxxm_us L5 overlay).

    Malformed remark tokens are errors under both profiles. ``REMARK_US_EXTENSION``
    info is emitted only under ``profile=iwxxm_us`` (EV-050 / AC8 true-error fix).
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

    if saw_us and profile == "iwxxm_us":
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


def _check_ca_manobs(
    tokens: list[str],
    *,
    product: str,
    core: str,
    body_start: int,
    body_end: int,
    profile: str = "annex3",
) -> list[Issue]:
    """MANOBS overlay hints for ``profile=ca_eccc`` (EV-064 M3)."""
    if profile != "ca_eccc":
        return []
    issues: list[Issue] = []
    lead = tokens[0].upper() if tokens else ""
    if lead == "LWIS":
        _emit_token_info(
            issues,
            code="CA_METAR_LWIS",
            message=f"{product} Limited Weather Information System (LWIS) report — MANOBS CA overlay",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="LWIS",
        )
    elif lead == "SAWR":
        _emit_token_info(
            issues,
            code="CA_METAR_SAWR",
            message=f"{product} Surface Aviation Weather Report (SAWR) — MANOBS CA overlay",
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
                    message=f"{product} statute-mile visibility ({tok}) — MANOBS CA overlay",
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
            message=f"{product} inch-of-mercury altimeter ({alt.group(0)}) — MANOBS CA overlay",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token=alt.group(0),
        )
    elif _ALT_NOT_OBS_BODY.search(core):
        _emit_token_info(
            issues,
            code="CA_ALTIMETER_NOT_OBS",
            message=f"{product} altimeter not observable (A////) — MANOBS CA overlay",
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
                message=f"{product} Canadian REMARKS (SLP/PRESFR/PRESRR) — ca_eccc profile awareness",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token="RMK",
            )
        if saw_presrr:
            _append_remark_issue(
                issues,
                code="CA_REMARK_PRESRR",
                message=f"{product} MANOBS pressure rising rapidly (PRESRR) — ca_eccc profile awareness",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token="PRESRR",
            )
        if saw_presfr:
            _append_remark_issue(
                issues,
                code="CA_REMARK_PRESFR",
                message=f"{product} MANOBS pressure falling rapidly (PRESFR) — ca_eccc profile awareness",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token="PRESFR",
            )
        if saw_nospeci:
            _append_remark_issue(
                issues,
                code="CA_REMARK_NOSPECI",
                message=f"{product} MANOBS no-specials remark (NOSPECI) — ca_eccc profile awareness",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token="NOSPECI",
            )
        if sector_vis is not None:
            _append_remark_issue(
                issues,
                code="CA_REMARK_SECTOR_VIS",
                message=f"{product} MANOBS sector visibility ({sector_vis.group(0)}) — ca_eccc profile awareness",
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
    """MANAIR overlay hints for ``profile=ca_eccc`` (EV-064 M4)."""
    if profile != "ca_eccc" or product != "TAF":
        return []
    issues: list[Issue] = []
    for tok in tokens:
        if _NCLWS_TAC.fullmatch(tok):
            _emit_token_info(
                issues,
                code="CA_TAF_NCLWS",
                message=f"{product} MANAIR low-level wind shear ({tok}) — ca_eccc profile awareness",
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
                message=f"{product} statute-mile visibility ({tok}) — MANAIR CA overlay",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token=tok,
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
    """MANAIR GFA overlay hints for ``profile=ca_eccc`` AIRMET (EV-064 M5)."""
    if profile != "ca_eccc" or product != "AIRMET":
        return []
    issues: list[Issue] = []
    phenom = _CA_GFA_PHENOM.search(core)
    if phenom is not None:
        _emit_token_info(
            issues,
            code="CA_AIRMET_GFA",
            message=f"{product} MANAIR GFA compound phenomenon ({phenom.group(0).strip()}) — ca_eccc profile awareness",
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
            message=f"{product} GFA chart remark ({chart.group(0).strip()}) — ca_eccc profile awareness",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token=chart.group(0).strip(),
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


def _forecast_or_obs_segments(tokens: list[str]) -> list[list[str]]:
    """Split tokens on TEMPO/BECMG/NOSIG/FM*/PROB* so exclusivity is per group."""
    segments: list[list[str]] = []
    current: list[str] = []
    for tok in tokens:
        if tok in {"TEMPO", "BECMG", "NOSIG"} or _TAF_FM.fullmatch(tok) or _TAF_PROB.fullmatch(tok):
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
    """Warn when NSC co-occurs with FEW/SCT/BKN/OVC in the same obs/change group."""
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
                f"{product} NSC with FEW/SCT/BKN/OVC in same group — FAQ §14.3 exclusivity (TC-EV023-001)",
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


def _report_segment_count(body: str) -> int:
    """Count '='-delimited TAC report segments in a bulletin body."""
    return sum(1 for part in body.split("=") if part.strip())


def _check_c1_multi_report(tac: str, product: str) -> list[Issue]:
    """
    Emit MULTI_REPORT_BULLETIN when the input packs multiple TAC reports.

    Guidance common / C1: one IWXXM report object per TAC report. CRS,
    translationFailedTAC, and COLLECT packing remain convert-only (lint N/A).
    """
    start, end, body = _body_span(tac)
    if _report_segment_count(body) < 2:
        return []
    return [
        _issue(
            "MULTI_REPORT_BULLETIN",
            f"{product} bulletin has multiple TAC reports — one IWXXM report per TAC (Guidance C1)",
            start=start,
            end=end,
            location="bulletin",
        )
    ]


def _check_metar_speci(tac: str, product: str, *, profile: str = "annex3") -> list[Issue]:
    start, end, body = _body_span(tac)
    upper = body.upper()
    # Drop trailing '=' for token scans.
    core = upper[:-1] if upper.endswith("=") else upper
    tokens = core.replace("=", " ").split()
    issues: list[Issue] = []
    issues.extend(_check_c1_multi_report(tac, product))

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
    # Strip WMO AHL heading lines so YYGGgg (e.g. 121200) is not INVALID_VISIBILITY (EV-040).
    rmk_at = core.find("RMK")
    vis_core = core[:rmk_at] if rmk_at >= 0 else core
    vis_core = "\n".join(line for line in vis_core.splitlines() if not _AHL_HEADING_LINE.match(line.strip()))
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
        span = _token_span_in_core(core, wx_tok, start)
        if span is None:
            wx_start, wx_end = start, end
        else:
            wx_start, wx_end = span
        # Recent weather (RE*) — AerodromeRecentWeather membership (EV-050).
        if _RECENT_WX.fullmatch(wx_tok):
            if membership.is_member("recent_weather", wx_tok):
                continue
            issues.append(
                _membership_issue(
                    product=product,
                    token=wx_tok,
                    family="recent_weather",
                    start=wx_start,
                    end=wx_end,
                    location="weather",
                )
            )
            continue
        if _is_valid_weather_token(wx_tok):
            if _weather_in_register(wx_tok):
                continue
            issues.append(
                _membership_issue(
                    product=product,
                    token=wx_tok,
                    family="present_or_forecast_weather",
                    start=wx_start,
                    end=wx_end,
                    location="weather",
                )
            )
            continue
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

    if not _QNH.search(core) and not _QNH_NOT_OBS.search(core):
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
        parts = _LAYER_CLOUD_PARTS.fullmatch(cloud_tok)
        if parts is not None:
            amount, ctype = parts.group(1), parts.group(2)
            if not membership.is_member("cloud_amount", amount):
                issues.append(
                    _membership_issue(
                        product=product,
                        token=amount,
                        family="cloud_amount",
                        start=cloud_start,
                        end=cloud_end,
                        location="cloud",
                    )
                )
            if ctype is not None and not membership.is_member("cloud_type", ctype):
                issues.append(
                    _membership_issue(
                        product=product,
                        token=ctype,
                        family="cloud_type",
                        start=cloud_start,
                        end=cloud_end,
                        location="cloud",
                    )
                )
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
            profile=profile,
        )
    )
    issues.extend(
        _check_ca_manobs(
            tokens,
            product=product,
            core=core,
            body_start=start,
            body_end=end,
            profile=profile,
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
    issues.extend(
        _check_s1_exceptional(
            tokens,
            product=product,
            core=core,
            body_start=start,
            body_end=end,
        )
    )

    return issues


def _check_s1_exceptional(
    tokens: list[str],
    *,
    product: str,
    core: str,
    body_start: int,
    body_end: int,
) -> list[Issue]:
    """S1 exceptional METAR/SPECI tokens (Guidance + #734) — info diagnostics."""
    issues: list[Issue] = []
    if "CAVOK" in tokens:
        _emit_token_info(
            issues,
            code="CAVOK_PRESENT",
            message=f"{product} CAVOK present — research T3 / S1",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="CAVOK",
        )
    if "NSC" in tokens:
        _emit_token_info(
            issues,
            code="NSC_PRESENT",
            message=f"{product} NSC present — research T3 / S1",
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
    if "NCD" in tokens:
        _emit_token_info(
            issues,
            code="NCD_PRESENT",
            message=f"{product} NCD present — research S1",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="NCD",
        )
    if "NSW" in tokens:
        _emit_token_info(
            issues,
            code="NSW_PRESENT",
            message=f"{product} NSW present — research T3 / S1",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="NSW",
        )
    if "VV///" in tokens:
        _emit_token_info(
            issues,
            code="VV_NOT_OBSERVABLE",
            message=f"{product} VV/// — verticalVisibility nil notObservable — research S1",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="VV///",
        )
    if "//" in tokens:
        _emit_token_info(
            issues,
            code="WX_NOT_OBSERVABLE",
            message=f"{product} present weather // — nil notObservable — research S1",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="//",
        )
    for tok in tokens:
        if _WIND_DIR_VAR.fullmatch(tok):
            _emit_token_info(
                issues,
                code="WIND_DIR_VARIATION",
                message=f"{product} wind direction variation {tok!r} — research S1",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token=tok,
            )
            break
    return issues


def _check_taf(tac: str, *, profile: str = "annex3") -> list[Issue]:
    """TAF checklist — A5-1 template gates + F20 T1 NIL/CNL/AMD/COR."""
    start, end, body = _body_span(tac)
    upper = body.upper()
    core = upper[:-1] if upper.endswith("=") else upper
    tokens = core.replace("=", " ").split()
    issues: list[Issue] = []
    product = "TAF"
    issues.extend(_check_c1_multi_report(tac, product))

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

    # T1 NIL: missing forecast ends the message (A5-1 #4) — skip validity body gates.
    if "NIL" in tokens:
        if "AMD" in tokens:
            _emit_token_info(
                issues,
                code="AMD_PRESENT",
                message=f"{product} AMD modifier present — research T1",
                core=core,
                body_start=start,
                body_end=end,
                token="AMD",
            )
        if "COR" in tokens:
            _emit_token_info(
                issues,
                code="COR_PRESENT",
                message=f"{product} COR modifier present — research T1",
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
                message=f"{product} NIL must not include body groups — research T1",
                core=core,
                body_start=start,
                body_end=end,
                token="NIL",
            )
        else:
            _emit_token_info(
                issues,
                code="NIL_REPORT",
                message=f"{product} NIL report — research T1",
                core=core,
                body_start=start,
                body_end=end,
                token="NIL",
            )
        return issues

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

    if "AMD" in tokens:
        _emit_token_info(
            issues,
            code="AMD_PRESENT",
            message=f"{product} AMD modifier present — research T1",
            core=core,
            body_start=start,
            body_end=end,
            token="AMD",
        )
    if "COR" in tokens:
        _emit_token_info(
            issues,
            code="COR_PRESENT",
            message=f"{product} COR modifier present — research T1",
            core=core,
            body_start=start,
            body_end=end,
            token="COR",
        )

    if "CNL" in tokens:
        # CNL must terminate the forecast content (A5-1 #6 paraphrase).
        cnl_idx = tokens.index("CNL")
        trailing = [t for t in tokens[cnl_idx + 1 :] if t not in {"="}]
        if trailing:
            _emit_token_info(
                issues,
                code="INVALID_CNL_SHAPE",
                message="TAF CNL must end the message — A5-1 #6",
                core=core,
                body_start=start,
                body_end=end,
                token="CNL",
            )
        else:
            _emit_token_info(
                issues,
                code="CNL_REPORT",
                message=f"{product} CNL cancel report — research T1",
                core=core,
                body_start=start,
                body_end=end,
                token="CNL",
            )
        return issues

    # T2 change groups — FM / BECMG / TEMPO / PROB + TL / AT (App 5 §1.4 / A5-2).
    _check_taf_change_groups(
        issues,
        tokens=tokens,
        product=product,
        core=core,
        body_start=start,
        body_end=end,
    )
    # T3 — TX/TN base-only; CAVOK / NSC / NSW / VV/// (Guidance exceptional).
    _check_taf_t3_elements(
        issues,
        tokens=tokens,
        product=product,
        core=core,
        body_start=start,
        body_end=end,
    )
    issues.extend(
        _check_ca_manair(
            tokens,
            product=product,
            core=core,
            body_start=start,
            body_end=end,
            profile=profile,
        )
    )

    return issues


def _taf_first_change_index(tokens: list[str]) -> int | None:
    """Index of first FM/BECMG/TEMPO/PROB change indicator, if any."""
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
) -> None:
    """Emit T3 info/error codes for TX/TN and CAVOK/NSC/NSW/VV///."""
    change_i = _taf_first_change_index(tokens)
    tx_tn_toks = [(i, t) for i, t in enumerate(tokens) if _TAF_TX_TN.fullmatch(t)]
    if tx_tn_toks:
        on_change = any(change_i is not None and i >= change_i for i, _t in tx_tn_toks)
        first_tok = tx_tn_toks[0][1]
        if on_change:
            _emit_token_info(
                issues,
                code="INVALID_TX_TN",
                message=f"{product} TX/TN allowed on base forecast only — research T3",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token=first_tok,
            )
        else:
            _emit_token_info(
                issues,
                code="TX_TN_PRESENT",
                message=f"{product} TX/TN temperature forecasts on base — research T3",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token=first_tok,
            )

    if "CAVOK" in tokens:
        _emit_token_info(
            issues,
            code="CAVOK_PRESENT",
            message=f"{product} CAVOK present — research T3 / S1",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="CAVOK",
        )
    if "NSC" in tokens:
        _emit_token_info(
            issues,
            code="NSC_PRESENT",
            message=f"{product} NSC present — research T3 / S1",
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
            message=f"{product} NSW present — research T3 / S1",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="NSW",
        )
    if "VV///" in tokens:
        _emit_token_info(
            issues,
            code="VV_OMIT",
            message=f"{product} VV/// — omit verticalVisibility without nilReason — research T3",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="VV///",
        )


def _check_taf_change_groups(
    issues: list[Issue],
    *,
    tokens: list[str],
    product: str,
    core: str,
    body_start: int,
    body_end: int,
) -> None:
    """Emit T2 info/error codes for TAF change indicators."""
    fm_tok = next((t for t in tokens if _TAF_FM.fullmatch(t)), None)
    if fm_tok is not None:
        _emit_token_info(
            issues,
            code="FM_PRESENT",
            message=f"{product} FM change group present — research T2",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token=fm_tok,
        )
    if "BECMG" in tokens:
        _emit_token_info(
            issues,
            code="BECMG_PRESENT",
            message=f"{product} BECMG change group present — research T2",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="BECMG",
        )
    if "TEMPO" in tokens:
        _emit_token_info(
            issues,
            code="TEMPO_PRESENT",
            message=f"{product} TEMPO change group present — research T2",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token="TEMPO",
        )

    tl_tok = next((t for t in tokens if _TAF_TL.fullmatch(t)), None)
    if tl_tok is not None:
        _emit_token_info(
            issues,
            code="TL_PRESENT",
            message=f"{product} TL time group present — research T2",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token=tl_tok,
        )
    at_tok = next((t for t in tokens if _TAF_AT.fullmatch(t)), None)
    if at_tok is not None:
        _emit_token_info(
            issues,
            code="AT_PRESENT",
            message=f"{product} AT time group present — research T2",
            core=core,
            body_start=body_start,
            body_end=body_end,
            token=at_tok,
        )

    for i, tok in enumerate(tokens):
        m = _TAF_PROB.fullmatch(tok)
        if m is None:
            continue
        pct = m.group(1)
        nxt = tokens[i + 1] if i + 1 < len(tokens) else ""
        qualifies_forbidden = nxt == "BECMG" or bool(_TAF_FM.fullmatch(nxt))
        if pct not in {"30", "40"} or qualifies_forbidden:
            _emit_token_info(
                issues,
                code="INVALID_PROB",
                message=(f"{product} invalid PROB (only 30|40; must not qualify BECMG/FM) — App 5 §1.4 / research T2"),
                core=core,
                body_start=body_start,
                body_end=body_end,
                token=tok,
            )
        else:
            _emit_token_info(
                issues,
                code="PROB_PRESENT",
                message=f"{product} PROB30/40 change group present — research T2",
                core=core,
                body_start=body_start,
                body_end=body_end,
                token=tok,
            )


def _count_families(text: str, families: tuple[tuple[str, re.Pattern[str]], ...]) -> list[str]:
    found: list[str] = []
    for name, pattern in families:
        if pattern.search(text):
            found.append(name)
    return found


def _check_sigmet_g1(*, start: int, end: int, upper: str) -> list[Issue]:
    """F23 theme G1 — CNL / COR / STNR / geometry / single-alt / TOP ABV|BLW."""
    issues: list[Issue] = []
    core = upper[:-1] if upper.endswith("=") else upper

    if _SIGMET_COR.search(core):
        _emit_token_info(
            issues,
            code="INVALID_SIGMET_COR",
            message="SIGMET must not use COR (cancel + re-issue) — research G1",
            core=core,
            body_start=start,
            body_end=end,
            token="COR",
        )

    if _SIGMET_CNL.search(core):
        # Cancel reports omit phenomenon/analysis (Guidance AIRMET/SIGMET CNL).
        hit = _count_families(core, _SIGMET_FAMILIES)
        if hit:
            _emit_token_info(
                issues,
                code="INVALID_SIGMET_CNL",
                message="SIGMET CNL must omit phenomenon/analysis body — research G1",
                core=core,
                body_start=start,
                body_end=end,
                token="CNL",
            )
        else:
            _emit_token_info(
                issues,
                code="SIGMET_CNL",
                message="SIGMET CNL cancel report — research G1",
                core=core,
                body_start=start,
                body_end=end,
                token="CNL",
            )
            if _SIGMET_CNL_FIR_MOVED.search(core):
                _emit_token_info(
                    issues,
                    code="VA_CNL_FIR_MOVED",
                    message="VA SIGMET CNL identifies FIR to which ash has moved — research V1",
                    core=core,
                    body_start=start,
                    body_end=end,
                    token="FIR",
                )
        return issues

    if _SIGMET_STNR.search(core):
        if _SIGMET_MOV.search(core):
            _emit_token_info(
                issues,
                code="INVALID_STNR_MOVEMENT",
                message="SIGMET STNR conflicts with MOV — research G1",
                core=core,
                body_start=start,
                body_end=end,
                token="STNR",
            )
        else:
            _emit_token_info(
                issues,
                code="STNR_MOVEMENT",
                message="SIGMET STNR stationary movement — research G1",
                core=core,
                body_start=start,
                body_end=end,
                token="STNR",
            )

    if _SIGMET_WI.search(core):
        _emit_token_info(
            issues,
            code="POLYGON_LOCATION",
            message="SIGMET polygon/line WI geometry — research G1",
            core=core,
            body_start=start,
            body_end=end,
            token="WI",
        )
    elif _SIGMET_POINT_COORD.search(core):
        m = _SIGMET_POINT_COORD.search(core)
        assert m is not None
        _emit_token_info(
            issues,
            code="POINT_LOCATION",
            message=("SIGMET single-point location (encode CircleByCenterPoint r=0) — research G1"),
            core=core,
            body_start=start,
            body_end=end,
            token=m.group(0).split()[0],
        )

    if _SIGMET_TOP_ABV_BLW.search(core):
        _emit_token_info(
            issues,
            code="TOP_ABV_OR_BLW",
            message="SIGMET TOP ABV/BLW level grammar — research G1",
            core=core,
            body_start=start,
            body_end=end,
            token="TOP",
        )
    elif not _SIGMET_LEVEL_RANGE.search(core) and _SIGMET_SINGLE_LEVEL.search(core):
        m = _SIGMET_SINGLE_LEVEL.search(core)
        assert m is not None
        _emit_token_info(
            issues,
            code="SINGLE_ALTITUDE",
            message="SIGMET single altitude (same lower/upper) — research G1",
            core=core,
            body_start=start,
            body_end=end,
            token=m.group(0),
        )

    return issues


def _sigmet_validity_hours(start: str, end: str) -> float | None:
    """Return VALID period length in hours (coarse midnight/month wrap)."""
    if len(start) != 6 or len(end) != 6 or not start.isdigit() or not end.isdigit():
        return None
    sd, sh, sm = int(start[:2]), int(start[2:4]), int(start[4:6])
    ed, eh, em = int(end[:2]), int(end[2:4]), int(end[4:6])
    if not (1 <= sd <= 31 and 1 <= ed <= 31 and sh < 24 and eh < 24 and sm < 60 and em < 60):
        return None
    start_m = sd * 24 * 60 + sh * 60 + sm
    end_m = ed * 24 * 60 + eh * 60 + em
    if end_m < start_m:
        # Day/month wrap (e.g. 312200/010200) — add one 31-day month bucket.
        end_m += 31 * 24 * 60
    return (end_m - start_m) / 60.0


def _check_sigmet_g2(
    *,
    start: int,
    end: int,
    upper: str,
    is_va: bool = False,
    is_tc: bool = False,
) -> list[Issue]:
    """F23 theme G2 — sequence / validity duration / FIR / OBS·FCST / intensity."""
    issues: list[Issue] = []
    core = upper[:-1] if upper.endswith("=") else upper

    seq = _SIGMET_SEQ.search(core)
    if seq is not None:
        _emit_token_info(
            issues,
            code="SIGMET_SEQUENCE",
            message="SIGMET sequence number present — research G2",
            core=core,
            body_start=start,
            body_end=end,
            token=seq.group(1),
        )
    elif _SIGMET_NO_SEQ.search(core):
        _emit_token_info(
            issues,
            code="MISSING_SEQUENCE",
            message="SIGMET missing sequence number after SIGMET — research G2",
            core=core,
            body_start=start,
            body_end=end,
            token="SIGMET",
        )

    valid = _SIGMET_VALID_PAIR.search(core)
    if valid is not None:
        hours = _sigmet_validity_hours(valid.group(1), valid.group(2))
        if is_va:
            max_hours = _WV_MAX_VALIDITY_HOURS
            label = "6 hours (WV)"
        elif is_tc:
            max_hours = _WC_MAX_VALIDITY_HOURS
            label = "6 hours (WC)"
        else:
            max_hours = _WS_MAX_VALIDITY_HOURS
            label = "4 hours (WS)"
        if hours is not None and hours > max_hours:
            _emit_token_info(
                issues,
                code="INVALID_VALIDITY_DURATION",
                message=f"SIGMET VALID period exceeds {label} — research G2",
                core=core,
                body_start=start,
                body_end=end,
                token="VALID",
            )

    fir = _SIGMET_FIR_CTA.search(core)
    if fir is not None:
        _emit_token_info(
            issues,
            code="FIR_OR_CTA",
            message="SIGMET FIR/CTA/UIR airspace identity — research G2",
            core=core,
            body_start=start,
            body_end=end,
            token=fir.group(0).split("/")[0],
        )
    else:
        _emit_token_info(
            issues,
            code="MISSING_FIR_OR_CTA",
            message="SIGMET missing FIR/CTA/UIR airspace identity — research G2",
            core=core,
            body_start=start,
            body_end=end,
            token="SIGMET",
        )

    obs = _SIGMET_OBS_FCST.search(core)
    if obs is not None:
        _emit_token_info(
            issues,
            code="OBS_OR_FCST",
            message="SIGMET OBS or FCST analysis — research G2",
            core=core,
            body_start=start,
            body_end=end,
            token=obs.group(0),
        )
    elif not _SIGMET_NO_VA_EXP.search(core):
        _emit_token_info(
            issues,
            code="MISSING_OBS_OR_FCST",
            message="SIGMET missing OBS or FCST — research G2",
            core=core,
            body_start=start,
            body_end=end,
            token="SIGMET",
        )

    intensity = _SIGMET_INTENSITY.search(core)
    if intensity is not None:
        _emit_token_info(
            issues,
            code="INTENSITY_CHANGE",
            message="SIGMET intensity change INTSF/WKN/NC — research G2",
            core=core,
            body_start=start,
            body_end=end,
            token=intensity.group(0),
        )

    return issues


def _check_airmet_a1(*, start: int, end: int, upper: str) -> list[Issue]:
    """F24 theme A1 — AIRMET sequence number + FIR/CTA identity."""
    issues: list[Issue] = []
    core = upper[:-1] if upper.endswith("=") else upper

    seq = _AIRMET_SEQ.search(core)
    if seq is not None:
        _emit_token_info(
            issues,
            code="SIGMET_SEQUENCE",
            message="AIRMET sequence number present — F24 theme A1",
            core=core,
            body_start=start,
            body_end=end,
            token=seq.group(1),
        )
    elif _AIRMET_NO_SEQ.search(core):
        _emit_token_info(
            issues,
            code="MISSING_SEQUENCE",
            message="AIRMET missing sequence number after AIRMET — F24 theme A1",
            core=core,
            body_start=start,
            body_end=end,
            token="AIRMET",
        )

    fir = _SIGMET_FIR_CTA.search(core)
    if fir is not None:
        _emit_token_info(
            issues,
            code="FIR_OR_CTA",
            message="AIRMET FIR/CTA/UIR airspace identity — F24 theme A1",
            core=core,
            body_start=start,
            body_end=end,
            token=fir.group(0).split("/")[0],
        )
    else:
        _emit_token_info(
            issues,
            code="MISSING_FIR_OR_CTA",
            message="AIRMET missing FIR/CTA/UIR airspace identity — F24 theme A1",
            core=core,
            body_start=start,
            body_end=end,
            token="AIRMET",
        )

    return issues


def _check_airmet_a2(*, start: int, end: int, upper: str) -> list[Issue]:
    """F24 theme A2 — AIRMET phenomenon modifiers (OBS/STNR/WKN/TOP ABV)."""
    issues: list[Issue] = []
    core = upper[:-1] if upper.endswith("=") else upper

    if _SIGMET_STNR.search(core):
        if _SIGMET_MOV.search(core):
            _emit_token_info(
                issues,
                code="INVALID_STNR_MOVEMENT",
                message="AIRMET STNR conflicts with MOV — F24 theme A2",
                core=core,
                body_start=start,
                body_end=end,
                token="STNR",
            )
        else:
            _emit_token_info(
                issues,
                code="STNR_MOVEMENT",
                message="AIRMET STNR stationary movement — F24 theme A2",
                core=core,
                body_start=start,
                body_end=end,
                token="STNR",
            )

    if _SIGMET_TOP_ABV_BLW.search(core):
        _emit_token_info(
            issues,
            code="TOP_ABV_OR_BLW",
            message="AIRMET TOP ABV/BLW level grammar — F24 theme A2",
            core=core,
            body_start=start,
            body_end=end,
            token="TOP",
        )

    obs = _SIGMET_OBS_FCST.search(core)
    if obs is not None:
        _emit_token_info(
            issues,
            code="OBS_OR_FCST",
            message="AIRMET OBS or FCST analysis — F24 theme A2",
            core=core,
            body_start=start,
            body_end=end,
            token=obs.group(0),
        )
    else:
        _emit_token_info(
            issues,
            code="MISSING_OBS_OR_FCST",
            message="AIRMET missing OBS or FCST — F24 theme A2",
            core=core,
            body_start=start,
            body_end=end,
            token="AIRMET",
        )

    intensity = _SIGMET_INTENSITY.search(core)
    if intensity is not None:
        _emit_token_info(
            issues,
            code="INTENSITY_CHANGE",
            message="AIRMET intensity change INTSF/WKN/NC — F24 theme A2",
            core=core,
            body_start=start,
            body_end=end,
            token=intensity.group(0),
        )

    return issues


def _check_sigmet_v1(*, start: int, end: int, upper: str) -> list[Issue]:
    """F23 theme V1 — VA volcano identity / ash geometry / NO VA EXP / CNL FIR-moved."""
    issues: list[Issue] = []
    core = upper[:-1] if upper.endswith("=") else upper

    if _SIGMET_NO_VA_EXP.search(core):
        if _SIGMET_VA_CLD.search(core):
            _emit_token_info(
                issues,
                code="INVALID_NO_VA_EXP",
                message="VA SIGMET NO VA EXP must not include VA CLD body — research V1",
                core=core,
                body_start=start,
                body_end=end,
                token="NO",
            )
        else:
            _emit_token_info(
                issues,
                code="NO_VA_EXP",
                message="VA SIGMET NO VA EXP absence token — research V1",
                core=core,
                body_start=start,
                body_end=end,
                token="NO",
            )

    if not _SIGMET_VA_TOKEN.search(core):
        return issues

    # Volcano identity required for active VA (including NO VA EXP with volcano named).
    if _SIGMET_VA_VOLCANO.search(core):
        _emit_token_info(
            issues,
            code="VA_VOLCANO_IDENTITY",
            message="VA SIGMET erupting volcano identity (MT/PSN) — research V1",
            core=core,
            body_start=start,
            body_end=end,
            token="MT",
        )
    elif not _SIGMET_CNL.search(core):
        _emit_token_info(
            issues,
            code="MISSING_VA_VOLCANO",
            message="VA SIGMET missing volcano identity (MT … PSN) — research V1",
            core=core,
            body_start=start,
            body_end=end,
            token="VA",
        )

    if _SIGMET_VA_CLD.search(core) and (_SIGMET_WI.search(core) or _SIGMET_POINT_COORD.search(core)):
        _emit_token_info(
            issues,
            code="VA_ASH_GEOMETRY",
            message="VA SIGMET ash cloud geometry / forecast position — research V1",
            core=core,
            body_start=start,
            body_end=end,
            token="VA",
        )

    return issues


def _check_sigmet_tc(*, start: int, end: int, upper: str) -> list[Issue]:
    """EV-030 theme TC — cyclone identity / OF TC CENTRE geometry (#829)."""
    issues: list[Issue] = []
    core = upper[:-1] if upper.endswith("=") else upper

    has_identity = _SIGMET_TC_IDENTITY.search(core) is not None
    has_of_centre = _SIGMET_OF_TC_CENTRE.search(core) is not None
    has_tc_name = _SIGMET_TC_NAME.search(core) is not None
    # TC family cue: named TC, OF TC CENTRE, or bare TC token (shared with G2 is_tc).
    if not (has_identity or has_of_centre or has_tc_name or _SIGMET_TC_TOKEN.search(core)):
        return issues

    if has_identity:
        _emit_token_info(
            issues,
            code="TC_CYCLONE_IDENTITY",
            message="TC SIGMET tropical cyclone identity (TC … PSN) — #829 / TC-EV030-004",
            core=core,
            body_start=start,
            body_end=end,
            token="TC",
        )
    elif has_of_centre or has_tc_name:
        _emit_token_info(
            issues,
            code="MISSING_TC_IDENTITY",
            message="TC SIGMET missing cyclone identity (TC … PSN) — #829 / TC-EV030-004",
            core=core,
            body_start=start,
            body_end=end,
            token="TC",
        )

    if has_of_centre and _SIGMET_WI.search(core):
        _emit_token_info(
            issues,
            code="TC_CB_GEOMETRY",
            message="TC SIGMET CB geometry WI … OF TC CENTRE — #829 / TC-EV030-004",
            core=core,
            body_start=start,
            body_end=end,
            token="TC",
        )

    return issues


def _check_sigmet_airmet(tac: str, product: str, *, profile: str = "annex3") -> list[Issue]:
    start, end, body = _body_span(tac)
    upper = body.upper()
    core = upper[:-1] if upper.endswith("=") else upper
    issues: list[Issue] = []
    # F23 theme C1 — one IWXXM report per TAC report (shared with METAR/SPECI/TAF).
    issues.extend(_check_c1_multi_report(tac, product))

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

    if product == "SIGMET":
        issues.extend(_check_sigmet_g1(start=start, end=end, upper=upper))
        # CNL reports intentionally omit phenomenon — skip multi-family + G2 body gates.
        if _SIGMET_CNL.search(upper[:-1] if upper.endswith("=") else upper):
            return issues
        is_va = bool(_SIGMET_VA_TOKEN.search(upper))
        is_tc = bool(_SIGMET_TC_TOKEN.search(upper))
        issues.extend(_check_sigmet_g2(start=start, end=end, upper=upper, is_va=is_va, is_tc=is_tc))
        if is_va:
            issues.extend(_check_sigmet_v1(start=start, end=end, upper=upper))
        if is_tc and not is_va:
            issues.extend(_check_sigmet_tc(start=start, end=end, upper=upper))
    elif product == "AIRMET":
        # F24 theme A1 — sequence + FIR (CNL still needs identity; skip multi-family below).
        issues.extend(_check_airmet_a1(start=start, end=end, upper=upper))
        if _SIGMET_CNL.search(upper[:-1] if upper.endswith("=") else upper):
            return issues
        # F24 theme A2 — OBS/STNR/intensity/TOP ABV (phenomenon families below).
        issues.extend(_check_airmet_a2(start=start, end=end, upper=upper))
        issues.extend(
            _check_ca_gfa_airmet(
                product=product,
                core=core,
                body_start=start,
                body_end=end,
                profile=profile,
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

    # EV-050 — AirWx/SigWx register membership (underscore↔space normalize).
    issues.extend(_check_phenomenon_membership(upper, product=product, start=start, end=end))

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
    # F26 theme V1 — exceptional volcano / remarks / forecast / next-advisory cues (#736).
    volcano_m = _VOLCANO_LINE.search(body)
    if not volcano_m:
        issues.append(
            _issue(
                "MISSING_VOLCANO",
                "VAA missing VOLCANO: template field — F26 theme V1 / A2-1",
                start=start,
                end=end,
                location="volcano",
            )
        )
    else:
        volcano_val = volcano_m.group(1).strip().upper()
        v_start, v_end = volcano_m.start(1), volcano_m.end(1)
        if not volcano_val:
            issues.append(
                _issue(
                    "MISSING_VOLCANO",
                    "VAA missing VOLCANO: template field — F26 theme V1 / A2-1",
                    start=volcano_m.start(),
                    end=volcano_m.end(),
                    location="volcano",
                )
            )
        elif volcano_val.split()[0] == "UNKNOWN":
            issues.append(
                _issue(
                    "VAA_VOLCANO_UNKNOWN",
                    "VAA VOLCANO UNKNOWN — exceptional name allowed (F26 theme V1)",
                    start=v_start,
                    end=v_end,
                    location="volcano",
                )
            )
        elif volcano_val.split()[0] == "UNNAMED":
            issues.append(
                _issue(
                    "VAA_VOLCANO_UNNAMED",
                    "VAA VOLCANO UNNAMED — exceptional name allowed (F26 theme V1)",
                    start=v_start,
                    end=v_end,
                    location="volcano",
                )
            )
    rmk_m = _RMK_LINE.search(body)
    if rmk_m:
        rmk_val = rmk_m.group(1).strip().rstrip("=").upper()
        if rmk_val == "NIL":
            issues.append(
                _issue(
                    "VAA_RMK_NIL",
                    "VAA RMK NIL — remarks inapplicable (F26 theme V1)",
                    start=rmk_m.start(1),
                    end=rmk_m.end(1),
                    location="remarks",
                )
            )
    no_va = _NO_VA_EXP.search(body)
    if no_va is not None:
        issues.append(
            _issue(
                "VAA_FCST_NO_VA_EXP",
                "VAA forecast NO VA EXP — status NO_VOLCANIC_ASH_EXPECTED (F26 theme V1)",
                start=no_va.start(),
                end=no_va.end(),
                location="forecast",
            )
        )
    nxt_m = _NXT_ADVISORY_LINE.search(body)
    if nxt_m and "NO FURTHER" in nxt_m.group(1).upper():
        issues.append(
            _issue(
                "VAA_NO_FURTHER_ADVISORIES",
                "VAA NXT ADVISORY NO FURTHER ADVISORIES — next time inapplicable (F26 theme V1)",
                start=nxt_m.start(1),
                end=nxt_m.end(1),
                location="next_advisory",
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
    # F27 theme T1 — exceptional cyclone / CB / remarks / next-msg cues (#737).
    tc_m = _TC_LINE.search(body)
    if not tc_m:
        issues.append(
            _issue(
                "MISSING_TC",
                "TCA missing TC: template field — F27 theme T1 / A2-2",
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
                    "TCA missing TC: template field — F27 theme T1 / A2-2",
                    start=tc_m.start(),
                    end=tc_m.end(),
                    location="tropical_cyclone",
                )
            )
        elif tc_val.split()[0] == "UNNAMED":
            issues.append(
                _issue(
                    "TCA_CYCLONE_UNNAMED",
                    "TCA TC UNNAMED — exceptional name allowed (F27 theme T1)",
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
                    "TCA CB NIL — CB missing (F27 theme T1)",
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
                    "TCA RMK NIL — remarks inapplicable (F27 theme T1)",
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
                "TCA NXT MSG NO MSG EXP — next time inapplicable (F27 theme T1)",
                start=nxt_m.start(1),
                end=nxt_m.end(1),
                location="next_advisory",
            )
        )
    return issues


def _check_swxa_spacewx_membership(body: str, *, start: int) -> list[Issue]:
    """Map SWX EFFECT + OBS severity to SpaceWxPhenomena membership (EV-050)."""
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


def _check_swxa(tac: str) -> list[Issue]:
    start, end, body = _body_span(tac)
    issues: list[Issue] = []
    if not _DTG_LINE.search(body):
        issues.append(
            _issue(
                "MISSING_DTG",
                "SWXA missing DTG: template field — A2-3",
                start=start,
                end=end,
                location="dtg",
            )
        )
    if not _SWXC_LINE.search(body):
        issues.append(
            _issue(
                "MISSING_SWXC",
                "SWXA missing SWXC: template field — F28 theme SX1 / A2-3",
                start=start,
                end=end,
                location="swxc",
            )
        )
    issues.extend(_check_swxa_spacewx_membership(body, start=start))
    # F28 theme SX1 — exceptional remarks / forecast / next-advisory cues (#740).
    rmk_m = _RMK_LINE.search(body)
    if rmk_m:
        rmk_val = rmk_m.group(1).strip().rstrip("=").upper()
        if rmk_val == "NIL":
            issues.append(
                _issue(
                    "SWXA_RMK_NIL",
                    "SWXA RMK NIL — remarks inapplicable (F28 theme SX1)",
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
                "SWXA forecast NO SWX EXP — no space weather expected (F28 theme SX1)",
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
                "SWXA NXT ADVISORY NO FURTHER ADVISORIES — next time inapplicable (F28 theme SX1)",
                start=nxt_m.start(1),
                end=nxt_m.end(1),
                location="next_advisory",
            )
        )
    return issues


def _check_vona(tac: str) -> list[Issue]:
    """F32 theme V1 — VONA template gates + ONSET/DUR NIL info (#741)."""
    start, end, body = _body_span(tac)
    issues: list[Issue] = []
    if not _DTG_LINE.search(body):
        issues.append(
            _issue(
                "MISSING_DTG",
                "VONA missing DTG: template field — A7-1",
                start=start,
                end=end,
                location="dtg",
            )
        )
    if not _SVO_LINE.search(body):
        issues.append(
            _issue(
                "MISSING_SVO",
                "VONA missing SVO: template field — F32 theme V1 / A7-1",
                start=start,
                end=end,
                location="svo",
            )
        )
    volcano_m = _VOLCANO_LINE.search(body)
    if not volcano_m:
        issues.append(
            _issue(
                "MISSING_VONA_VOLCANO",
                "VONA missing VOLCANO: template field — F32 theme V1 / A7-1",
                start=start,
                end=end,
                location="volcano",
            )
        )
    onset_m = _ONSET_LINE.search(body)
    if onset_m and onset_m.group(1).strip().rstrip("=").upper() == "NIL":
        issues.append(
            _issue(
                "VONA_ONSET_NIL",
                "VONA ONSET NIL — onsetTime omitted (F32 theme V1)",
                start=onset_m.start(1),
                end=onset_m.end(1),
                location="onset",
            )
        )
    dur_m = _DUR_LINE.search(body)
    if dur_m and dur_m.group(1).strip().rstrip("=").upper() == "NIL":
        issues.append(
            _issue(
                "VONA_DUR_NIL",
                "VONA DUR NIL — duration omitted (F32 theme V1)",
                start=dur_m.start(1),
                end=dur_m.end(1),
                location="duration",
            )
        )
    return issues


def check_product_rules(
    tac_text: str,
    product: str,
    *,
    profile: str = "annex3",
) -> list[Issue]:
    """
    Run product checklist / template-gate rules after parse-gate success.

    Parameters
    ----------
    tac_text :
        Raw TAC text.
    product :
        F6 product id.
    profile :
        ``annex3`` or ``iwxxm_us``. Reserved for L5 overlay gating (EV-050 T3.3);
        WMO L3 membership checks are shared across profiles today.

    Returns
    -------
    list[Issue]
        Error-severity findings with spans when possible.
    """
    if product in {"METAR", "SPECI"}:
        return _check_metar_speci(tac_text, product, profile=profile)
    if product == "TAF":
        return _check_taf(tac_text, profile=profile)
    if product in {"SIGMET", "AIRMET"}:
        return _check_sigmet_airmet(tac_text, product, profile=profile)
    if product == "VAA":
        return _check_vaa(tac_text)
    if product == "TCA":
        return _check_tca(tac_text)
    if product == "SWXA":
        return _check_swxa(tac_text)
    if product == "VONA":
        return _check_vona(tac_text)
    return []


__all__ = ["check_product_rules"]
