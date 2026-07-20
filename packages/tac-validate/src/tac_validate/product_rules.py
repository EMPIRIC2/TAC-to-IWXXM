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
_TEMP = re.compile(r"\bM?\d{2}/M?\d{2}\b")
_QNH = re.compile(r"\b[QA]\d{4}\b")
_CLOUD_OK = re.compile(r"\b(?:FEW|SCT|BKN|OVC|VV|NSC|NCD|SKC|CLR)\d{0,3}(?:CB|TCU)?\b")
_CLOUD_BAD = re.compile(r"\b([A-Z]{3}\d{3})\b")
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

    if not _WIND.search(core):
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

    bad_vis = list(_VIS_BAD.finditer(core))
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
    elif not _VIS_OK.search(core):
        issues.append(
            _issue(
                "MISSING_VISIBILITY",
                f"{product} missing visibility or CAVOK — A3-2 #6",
                start=start,
                end=end,
                location="visibility",
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

    # Flag unknown XXX### cloud-like tokens that are not valid cloud groups.
    for match in _CLOUD_BAD.finditer(core):
        token = match.group(1)
        if _CLOUD_OK.fullmatch(token):
            continue
        # Wind already matched as \d{3}\d{2}KT — not XXX###.
        if token[:3] in {"FEW", "SCT", "BKN", "OVC"}:
            continue
        abs_start = start + match.start(1)
        abs_end = start + match.end(1)
        issues.append(
            _issue(
                "INVALID_CLOUD_TOKEN",
                f"{product} invalid cloud/VV token {token!r} — A3-2 #9",
                start=abs_start,
                end=abs_end,
                location="cloud",
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
