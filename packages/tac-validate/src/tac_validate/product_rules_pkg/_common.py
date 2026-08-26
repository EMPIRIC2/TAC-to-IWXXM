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


__all__ = [
    "_ICAO",
    "_OBS_TIME",
    "_WIND",
    "_WIND_DIR_VAR",
    "_VIS_OK",
    "_VIS_BAD",
    "_WX_PHENOMENA",
    "_WX_DESCRIPTORS",
    "_WX_STANDALONE",
    "_WX_SPECIAL",
    "_RVR",
    "_RVR_OK",
    "_AHL_HEADING_LINE",
    "_WIND_TOKEN",
    "_CLOUD_START",
    "_CLOUD_OK",
    "_CLOUD_LIKE",
    "_LAYER_CLOUD_TOKEN",
    "_RMK_AO",
    "_RMK_SLP_OK",
    "_RMK_P_OK",
    "_RMK_T_OK",
    "_RMK_PK_VAL",
    "_RMK_PRES_CA",
    "_RMK_NOSPECI",
    "_RMK_SECTOR_VIS_IN_TEXT",
    "_NCLWS_TAC",
    "_CA_GFA_PHENOM",
    "_GFA_CHART",
    "_TAF_VIS_SM",
    "_ALT_INHG_BODY",
    "_ALT_NOT_OBS_BODY",
    "_WX_TOKEN_SHAPE",
    "_TEMP",
    "_QNH",
    "_QNH_NOT_OBS",
    "_TAF_VALIDITY",
    "_TAF_FM",
    "_TAF_PROB",
    "_TAF_TL",
    "_TAF_AT",
    "_TAF_TX_TN",
    "_VALID_PERIOD",
    "_DTG_LINE",
    "_VAAC_LINE",
    "_VOLCANO_LINE",
    "_RMK_LINE",
    "_NXT_ADVISORY_LINE",
    "_NO_VA_EXP",
    "_SWXC_LINE",
    "_SWX_EFFECT_LINE",
    "_OBS_SWX_LINE",
    "_NO_SWX_EXP",
    "_SWX_EFFECT_PREFIX",
    "_MAX_WIND_LINE",
    "_SVO_LINE",
    "_ONSET_LINE",
    "_DUR_LINE",
    "_TC_LINE",
    "_CB_LINE",
    "_NXT_MSG_LINE",
    "_SIGMET_POINT_COORD",
    "_SIGMET_LEVEL_RANGE",
    "_SIGMET_SINGLE_LEVEL",
    "_SIGMET_TOP_ABV_BLW",
    "_SIGMET_WI",
    "_SIGMET_STNR",
    "_SIGMET_MOV",
    "_SIGMET_CNL",
    "_SIGMET_COR",
    "_SIGMET_SEQ",
    "_SIGMET_NO_SEQ",
    "_AIRMET_SEQ",
    "_AIRMET_NO_SEQ",
    "_SIGMET_VALID_PAIR",
    "_SIGMET_FIR_CTA",
    "_SIGMET_OBS_FCST",
    "_SIGMET_INTENSITY",
    "_SIGMET_VA_TOKEN",
    "_SIGMET_TC_TOKEN",
    "_SIGMET_VA_VOLCANO",
    "_SIGMET_VA_CLD",
    "_SIGMET_NO_VA_EXP",
    "_SIGMET_CNL_FIR_MOVED",
    "_SIGMET_TC_IDENTITY",
    "_SIGMET_OF_TC_CENTRE",
    "_SIGMET_TC_NAME",
    "_WS_MAX_VALIDITY_HOURS",
    "_WV_MAX_VALIDITY_HOURS",
    "_WC_MAX_VALIDITY_HOURS",
    "_SIGMET_FAMILIES",
    "_AIRMET_FAMILIES",
    "_AIRMET_PHENOM_CANDIDATE",
    "_SIGMET_PHENOM_CANDIDATE",
    "_RECENT_WX",
    "_LAYER_CLOUD_PARTS",
    "_METAR_SPECI_SKIP",
    "_TAF_SKIP",
    "_issue",
    "_body_span",
    "_first_icao",
    "_token_index",
    "_first_icao_index",
    "_consume_wx_descriptors",
    "_is_valid_weather_token",
    "_weather_candidate_tokens",
    "_token_span_in_core",
    "_is_valid_cloud_token",
    "_membership_issue",
    "_weather_in_register",
    "_check_phenomenon_membership",
    "_cloud_candidate_tokens",
    "_append_remark_issue",
    "_check_us_remarks",
    "_check_ca_manobs",
    "_check_ca_manair",
    "_check_ca_gfa_airmet",
    "_emit_token_info",
    "_forecast_or_obs_segments",
    "_emit_nsc_layer_exclusivity",
    "_check_r8_pack",
    "_check_metar_speci_field_order",
    "_report_segment_count",
    "_check_c1_multi_report",
]
