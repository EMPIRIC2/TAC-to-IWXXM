"""WMO AHL bulletin helpers and splitter (F6.bulletin / TC-EV029-003).

Shared parse / format / ``T1T2`` map / BBB→``reportStatus`` / IWXXM filename
helpers live here so ``packages/dissemination`` can import them without
duplicating AHL rules (EV-029 / E29-T2).
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Literal

from tac2iwxxm.models import AhlParts, BulletinMeta, BulletinSplit

ReportStatus = Literal["NORMAL", "AMENDMENT", "CORRECTION"]

# TAC → IWXXM T1T2 (docs/domain/IWXXM_CONVERSION.md §AHL / bulletin EV-029)
_TAC_TO_IWXXM: dict[str, str] = {
    "SA": "LA",
    "SP": "LP",
    "FC": "LC",
    "FT": "LT",
    "FK": "LK",
    "FN": "LN",
    "FV": "LU",
    "WA": "LW",
    "WS": "LS",
    "WC": "LY",
    "WV": "LV",
}

_AHL_LINE = re.compile(
    r"^(?P<tt>[A-Z]{2})(?P<aa>[A-Z]{2})(?P<ii>\d{2})\s+"
    r"(?P<cccc>[A-Z]{4})\s+(?P<yygggg>\d{6})"
    r"(?:\s+(?P<bbb>[A-Z]{1,3}))?\s*$"
)

# AHL page v1.0.1 prefix families: RRx / AAx / CCx with x ∈ A…X (not Y/Z).
_BBB_VALID = re.compile(r"^(?:AA|CC|RR)[A-X]$")

# gifts METAR.re_TAC — report starts at METAR|SPECI and ends at '='
_TAC_METAR_SPECI = re.compile(
    r"^(?:METAR|SPECI)\s+(?:COR\s+)?[A-Z][A-Z0-9]{3}\s.+?=",
    re.MULTILINE | re.DOTALL,
)

# TAF body — optional AMD/COR after TAF; ends at '=' (design-note §3.2)
_TAC_TAF = re.compile(
    r"^TAF\s+(?:(?:AMD|COR)\s+)?[A-Z][A-Z0-9]{3}\s.+?=",
    re.MULTILINE | re.DOTALL,
)

# SIGMET body — FIR SIGMET seq VALID … MWO- … = (design-note §3.2; WS gen / WV VA)
_TAC_SIGMET = re.compile(
    r"^[A-Z]{4}\s+SIGMET\s+\d+\s+VALID\s+\d{6}/\d{6}\s+[A-Z]{4}-\s*.+?=",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)

# AIRMET body — FIR AIRMET seq VALID … MWO- … = (design-note §3.2; WA → LW / EV-029 M8)
_TAC_AIRMET = re.compile(
    r"^[A-Z]{4}\s+AIRMET\s+\d+\s+VALID\s+\d{6}/\d{6}\s+[A-Z]{4}-\s*.+?=",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)

# VAA body — VA ADVISORY … = (``=`` preferred for multi; single block may omit — §3.2 / M9)
_TAC_VAA = re.compile(
    r"^VA\s+ADVISORY\b.+?(?:=\s*$|\Z)",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)

# TCA body — TC ADVISORY … = (``=`` preferred for multi; single block may omit — §3.2 / M10)
_TAC_TCA = re.compile(
    r"^TC\s+ADVISORY\b.+?(?:=\s*$|\Z)",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)

_PRODUCT_TT: dict[str, frozenset[str]] = {
    "METAR": frozenset({"SA"}),
    "SPECI": frozenset({"SP"}),
    "TAF": frozenset({"FC", "FT"}),
    # WS general + WV volcanic ash + WC tropical cyclone (content-selected root;
    # E19-13 / EV-029 M5–M7).
    "SIGMET": frozenset({"WS", "WV", "WC"}),
    "AIRMET": frozenset({"WA"}),
    "VAA": frozenset({"FV"}),
    "TCA": frozenset({"FK"}),
}

_PRODUCT_BODY_RE: dict[str, re.Pattern[str]] = {
    "METAR": _TAC_METAR_SPECI,
    "SPECI": _TAC_METAR_SPECI,
    "TAF": _TAC_TAF,
    "SIGMET": _TAC_SIGMET,
    "AIRMET": _TAC_AIRMET,
    "VAA": _TAC_VAA,
    "TCA": _TAC_TCA,
}


class BulletinSplitError(ValueError):
    """
    Bulletin or AHL could not be parsed.

    Parameters
    ----------
    code :
        Machine-readable error (``bulletin_split_failed``, ``empty_bulletin``,
        or ``invalid_bbb``).
    message :
        Human-readable description.
    """

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


def map_t1t2(tac_tt: str) -> str:
    """
    Map a TAC ``T1T2`` designator to the IWXXM (L*) designator.

    Parameters
    ----------
    tac_tt :
        Two-letter TAC data type designator (e.g. ``SA``, ``FN``).

    Returns
    -------
    str
        IWXXM ``T1T2`` (e.g. ``LA``, ``LN``).

    Raises
    ------
    ValueError
        When ``tac_tt`` is not in the EV-029 aviation map.
    """
    key = tac_tt.strip().upper()
    try:
        return _TAC_TO_IWXXM[key]
    except KeyError as exc:
        raise ValueError(f"unsupported TAC T1T2 for IWXXM map: {tac_tt!r}") from exc


def bbb_to_report_status(bbb: str | None) -> ReportStatus:
    """
    Map optional BBB to IWXXM ``reportStatus``.

    Parameters
    ----------
    bbb :
        BBB indicator (``AAx`` / ``CCx`` / ``RRx`` with x ∈ A…X), or ``None``.

    Returns
    -------
    ReportStatus
        ``NORMAL``, ``AMENDMENT``, or ``CORRECTION``.

    Raises
    ------
    BulletinSplitError
        When ``bbb`` is present but not an accepted prefix family.
    """
    if bbb is None or bbb == "":
        return "NORMAL"
    token = bbb.strip().upper()
    if not _BBB_VALID.match(token):
        raise BulletinSplitError(
            "invalid_bbb",
            f"invalid WMO AHL BBB (expected AA/CC/RR + A…X): {bbb!r}",
        )
    if token.startswith("AA"):
        return "AMENDMENT"
    if token.startswith("CC"):
        return "CORRECTION"
    return "NORMAL"


def parse_ahl(line_or_text: str) -> AhlParts:
    """
    Parse a WMO abbreviated heading line (first matching line).

    Parameters
    ----------
    line_or_text :
        A single AHL line, or text whose first non-empty line is the AHL.

    Returns
    -------
    AhlParts
        Parsed fields plus derived ``iwxxm_tt`` and ``report_status``.

    Raises
    ------
    BulletinSplitError
        When the heading cannot be parsed, ``T1T2`` is unknown, or BBB is invalid.
    """
    raw = line_or_text.strip()
    if not raw:
        raise BulletinSplitError("bulletin_split_failed", "Empty AHL input")
    first = raw.splitlines()[0].strip()
    match = _AHL_LINE.match(first)
    if match is None:
        raise BulletinSplitError(
            "bulletin_split_failed",
            f"Cannot parse WMO AHL header: {first!r}",
        )
    groups = match.groupdict()
    tt = groups["tt"]
    if tt not in _TAC_TO_IWXXM:
        raise BulletinSplitError(
            "bulletin_split_failed",
            f"Unsupported TAC T1T2 in AHL: {tt!r}",
        )
    bbb_raw = groups.get("bbb")
    bbb: str | None
    if bbb_raw:
        bbb = bbb_raw.upper()
        # Validate via reportStatus map (rejects Y/Z third letter and non-families)
        status = bbb_to_report_status(bbb)
    else:
        bbb = None
        status = "NORMAL"
    iwxxm_tt = _TAC_TO_IWXXM[tt]
    return AhlParts(
        ahl=first,
        tt=tt,
        aa=groups["aa"],
        ii=groups["ii"],
        cccc=groups["cccc"],
        yygggg=groups["yygggg"],
        bbb=bbb,
        iwxxm_tt=iwxxm_tt,
        report_status=status,
    )


def format_ahl(parts: AhlParts) -> str:
    """
    Format ``AhlParts`` as a single WMO AHL line (TAC ``T1T2``).

    Parameters
    ----------
    parts :
        Parsed or constructed AHL parts.

    Returns
    -------
    str
        ``T1T2A1A2ii CCCC YYGGgg [BBB]``.

    Raises
    ------
    BulletinSplitError
        When BBB is present but invalid.
    """
    tt = parts.tt.strip().upper()
    aa = parts.aa.strip().upper()
    ii = parts.ii.strip()
    cccc = parts.cccc.strip().upper()
    yygggg = parts.yygggg.strip()
    if not re.fullmatch(r"[A-Z]{2}", tt):
        raise BulletinSplitError("bulletin_split_failed", f"invalid AHL tt: {parts.tt!r}")
    if not re.fullmatch(r"[A-Z]{2}", aa):
        raise BulletinSplitError("bulletin_split_failed", f"invalid AHL aa: {parts.aa!r}")
    if not re.fullmatch(r"\d{2}", ii):
        raise BulletinSplitError("bulletin_split_failed", f"invalid AHL ii: {parts.ii!r}")
    if not re.fullmatch(r"[A-Z]{4}", cccc):
        raise BulletinSplitError("bulletin_split_failed", f"invalid AHL cccc: {parts.cccc!r}")
    if not re.fullmatch(r"\d{6}", yygggg):
        raise BulletinSplitError("bulletin_split_failed", f"invalid AHL yygggg: {parts.yygggg!r}")
    line = f"{tt}{aa}{ii} {cccc} {yygggg}"
    if parts.bbb:
        bbb_u = parts.bbb.strip().upper()
        bbb_to_report_status(bbb_u)  # validate
        line = f"{line} {bbb_u}"
    return line


def iwxxm_filename(
    parts: AhlParts,
    *,
    issued_at: datetime,
    gzip: bool = False,
    fractional: str | None = None,
) -> str:
    """
    Build an IWXXM AMHS / FTBP filename using the **IWXXM** ``T1T2``.

    Parameters
    ----------
    parts :
        AHL parts (must include ``iwxxm_tt``).
    issued_at :
        UTC (or aware) issue timestamp for the ``_C_CCCC_yyyyMMddhhmmss`` segment.
    gzip :
        When ``True``, append ``.gz``.
    fractional :
        Optional fractional-second / sequence suffix ``ffffff``.

    Returns
    -------
    str
        ``A_…xml`` or ``A_…xml.gz``.
    """
    ts = issued_at.astimezone(UTC).strftime("%Y%m%d%H%M%S")
    bbb = (parts.bbb or "").strip().upper()
    head = f"A_{parts.iwxxm_tt}{parts.aa}{parts.ii}{parts.cccc}{parts.yygggg}{bbb}"
    mid = f"_C_{parts.cccc}_{ts}"
    if fractional:
        mid = f"{mid}_{fractional}"
    suffix = ".xml.gz" if gzip else ".xml"
    return f"{head}{mid}{suffix}"


def split_bulletin(text: str, *, product: str = "METAR") -> BulletinSplit:
    """
    Parse a WMO AHL bulletin and return ordered TAC report strings.

    Parameters
    ----------
    text :
        Full bulletin text including the AHL line and one or more TAC reports.
    product :
        Product hint selecting the AHL dialect (``METAR``, ``SPECI``, ``TAF``,
        ``SIGMET`` for WS/WV/WC, ``AIRMET`` for WA, ``VAA`` for FV, or ``TCA``
        for FK; other products raise until their splitters land).

    Returns
    -------
    BulletinSplit
        AHL metadata plus the list of TAC reports.

    Raises
    ------
    BulletinSplitError
        When the AHL cannot be parsed (``bulletin_split_failed`` / ``invalid_bbb``)
        or no reports are found after a valid AHL (``empty_bulletin``).
    """
    product_key = product.strip().upper()
    allowed_tt = _PRODUCT_TT.get(product_key)
    body_re = _PRODUCT_BODY_RE.get(product_key)
    if allowed_tt is None or body_re is None:
        raise BulletinSplitError(
            "bulletin_split_failed",
            f"Unsupported product for bulletin split: {product!r}",
        )

    # Locate first AHL-shaped line, then validate via parse_ahl (strict BBB)
    ahl_match = None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if _AHL_LINE.match(stripped):
            ahl_match = stripped
            break
    if ahl_match is None:
        raise BulletinSplitError(
            "bulletin_split_failed",
            "Cannot parse WMO AHL header for bulletin split",
        )

    parts = parse_ahl(ahl_match)
    if parts.tt not in allowed_tt:
        raise BulletinSplitError(
            "bulletin_split_failed",
            f"AHL T1T2 {parts.tt!r} does not match product {product_key!r}",
        )

    # Only scan TAC reports after the AHL so pre-header noise cannot inflate the bulletin
    ahl_pos = text.find(ahl_match)
    body_text = text[ahl_pos + len(ahl_match) :]
    reports = [m.group(0).strip() for m in body_re.finditer(body_text)]
    if not reports:
        raise BulletinSplitError(
            "empty_bulletin",
            "No TAC reports found after AHL header",
        )

    if product_key == "SPECI":
        reports = [r for r in reports if r.startswith("SPECI")]
    elif product_key == "METAR":
        reports = [r for r in reports if r.startswith("METAR")]
    elif product_key == "TAF":
        reports = [r for r in reports if r.startswith("TAF")]
    elif product_key == "SIGMET":
        # Keep FIR SIGMET…= only (reject VAA/TCA advisory blocks misrouted under WS/WV/WC).
        reports = [r for r in reports if re.match(r"^[A-Z]{4}\s+SIGMET\s+", r, re.IGNORECASE)]
    elif product_key == "AIRMET":
        reports = [r for r in reports if re.match(r"^[A-Z]{4}\s+AIRMET\s+", r, re.IGNORECASE)]
    elif product_key == "VAA":
        reports = [r for r in reports if re.match(r"^VA\s+ADVISORY\b", r, re.IGNORECASE)]
    elif product_key == "TCA":
        reports = [r for r in reports if re.match(r"^TC\s+ADVISORY\b", r, re.IGNORECASE)]

    if not reports:
        raise BulletinSplitError(
            "empty_bulletin",
            f"No {product_key} TAC reports found after AHL header",
        )

    meta = BulletinMeta(
        ahl=parts.ahl,
        report_count=len(reports),
        tt=parts.tt,
        aa=parts.aa,
        cccc=parts.cccc,
        yygggg=parts.yygggg,
        bbb=parts.bbb,
        ii=parts.ii,
        report_status=parts.report_status,
    )
    return BulletinSplit(meta=meta, reports=reports)


__all__ = [
    "BulletinSplitError",
    "bbb_to_report_status",
    "format_ahl",
    "iwxxm_filename",
    "map_t1t2",
    "parse_ahl",
    "split_bulletin",
]
