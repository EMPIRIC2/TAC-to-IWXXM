"""WMO AHL bulletin splitter (F6.bulletin).

Splits a Traditional Alphanumeric Code bulletin with an abbreviated header
into per-report TAC strings. Product-specific AHL / TAC patterns follow the
gifts METAR/SPECI dialect for v1 (TC-F6-030).
"""

from __future__ import annotations

import re

from tac2iwxxm.models import BulletinMeta, BulletinSplit

# WMO AHL: T1T2 A1A2 ii CCCC YYGGgg [BBB] — METAR=SA*, SPECI=SP*
_AHL_METAR = re.compile(
    r"^(?P<tt>SA)(?P<aa>[A-Z]{2})(?P<ii>\d{2})\s+(?P<cccc>[A-Z]{4})\s+"
    r"(?P<yygggg>\d{6})(?:\s+(?P<bbb>[ACR]{2}[A-Z]))?",
    re.MULTILINE,
)
_AHL_SPECI = re.compile(
    r"^(?P<tt>SP)(?P<aa>[A-Z]{2})(?P<ii>\d{2})\s+(?P<cccc>[A-Z]{4})\s+"
    r"(?P<yygggg>\d{6})(?:\s+(?P<bbb>[ACR]{2}[A-Z]))?",
    re.MULTILINE,
)

# gifts METAR.re_TAC — report starts at METAR|SPECI and ends at '='
_TAC_METAR_SPECI = re.compile(
    r"^(?:METAR|SPECI)\s+(?:COR\s+)?[A-Z][A-Z0-9]{3}\s.+?=",
    re.MULTILINE | re.DOTALL,
)

_PRODUCT_AHL: dict[str, re.Pattern[str]] = {
    "METAR": _AHL_METAR,
    "SPECI": _AHL_SPECI,
}


class BulletinSplitError(ValueError):
    """
    Bulletin could not be split into reports.

    Parameters
    ----------
    code :
        Machine-readable error matching api-contract
        (``bulletin_split_failed`` or ``empty_bulletin``).
    message :
        Human-readable description.
    """

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


def split_bulletin(text: str, *, product: str = "METAR") -> BulletinSplit:
    """
    Parse a WMO AHL bulletin and return ordered TAC report strings.

    Parameters
    ----------
    text :
        Full bulletin text including the AHL line and one or more TAC reports.
    product :
        Product hint selecting the AHL dialect (``METAR`` or ``SPECI`` for v1).

    Returns
    -------
    BulletinSplit
        AHL metadata plus the list of TAC reports.

    Raises
    ------
    BulletinSplitError
        When the AHL cannot be parsed (``bulletin_split_failed``) or no reports
        are found after a valid AHL (``empty_bulletin``).
    """
    product_key = product.strip().upper()
    ahl_re = _PRODUCT_AHL.get(product_key)
    if ahl_re is None:
        raise BulletinSplitError(
            "bulletin_split_failed",
            f"Unsupported product for bulletin split: {product!r}",
        )

    ahl_match = ahl_re.search(text)
    if ahl_match is None:
        raise BulletinSplitError(
            "bulletin_split_failed",
            "Cannot parse WMO AHL header for bulletin split",
        )

    groups = ahl_match.groupdict()
    bbb = groups.get("bbb") or None
    ahl_line = ahl_match.group(0).strip()

    reports = [m.group(0).strip() for m in _TAC_METAR_SPECI.finditer(text)]
    if not reports:
        raise BulletinSplitError(
            "empty_bulletin",
            "No TAC reports found after AHL header",
        )

    # SPECI product should prefer SPECI reports; METAR prefers METAR (still allow mixed fixtures)
    if product_key == "SPECI":
        speci_only = [r for r in reports if r.startswith("SPECI")]
        if speci_only:
            reports = speci_only
    elif product_key == "METAR":
        metar_only = [r for r in reports if r.startswith("METAR")]
        if metar_only:
            reports = metar_only

    if not reports:
        raise BulletinSplitError(
            "empty_bulletin",
            f"No {product_key} TAC reports found after AHL header",
        )

    meta = BulletinMeta(
        ahl=ahl_line,
        report_count=len(reports),
        tt=groups["tt"],
        aa=groups["aa"],
        cccc=groups["cccc"],
        yygggg=groups["yygggg"],
        bbb=bbb,
    )
    return BulletinSplit(meta=meta, reports=reports)


__all__ = ["BulletinSplitError", "split_bulletin"]
