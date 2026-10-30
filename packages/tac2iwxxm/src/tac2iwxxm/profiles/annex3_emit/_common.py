"""Shared constants and helpers for annex3 product emitters."""

from __future__ import annotations

_NS = {
    "2025-2": "http://icao.int/iwxxm/2025-2",
    "2023-1": "http://icao.int/iwxxm/2023-1",
    "3.0.0": "http://icao.int/iwxxm/3.0",
}

_CLOUD_HREF = "http://codes.wmo.int/49-2/CloudAmountReportedAtAerodrome/{amt}"
_CLOUD_TYPE_HREF = "http://codes.wmo.int/49-2/SigConvectiveCloudType/{ctype}"
_WX_HREF = "http://codes.wmo.int/306/4678/{code}"
_SIG_PHENOM_HREF = "http://codes.wmo.int/49-2/SigWxPhenomena/{code}"
_AIR_PHENOM_HREF = "http://codes.wmo.int/49-2/AirWxPhenomena/{code}"

# WMO 49-2 SigWxPhenomena local names (IWXXM 2025-2 / 2023-1 rule RDF).
_SIG_WX_PHENOMENA_CODES = frozenset(
    {
        "EMBD_TS",
        "EMBD_TSGR",
        "FRQ_TS",
        "FRQ_TSGR",
        "HVY_DS",
        "HVY_SS",
        "OBSC_TS",
        "OBSC_TSGR",
        "RDOACT_CLD",
        "SEV_ICE",
        "SEV_ICE_FZRA",
        "SEV_MTW",
        "SEV_TURB",
        "SQL_TS",
        "SQL_TSGR",
        "TC",
        "VA",
    }
)

_YUDO_NAME = "DONLON/INTERNATIONAL"
_YUDO_POS = "12.34 -12.34"
_YUDO_ELEV_M = "12"

# Stable TimeInstant ids for WMO sigmet-multi-location-VA (second collection xlink reuse).
_WMO_MULTI_VA_OBS_TIME_ID = "uuid.5299e948-f719-4fd2-85fc-20ad96644250"
_WMO_MULTI_VA_FCST_TIME_ID = "uuid.cce9b23a-d604-4194-8f73-2b7357ee4a9c"


def _ns(iwxxm_version: str) -> str:
    """
    Internal helper ``_ns``.

    Parameters
    ----------
    iwxxm_version : str
        Argument ``iwxxm_version``.

    Returns
    -------
    str
        Return value.
    """
    ns = _NS.get(iwxxm_version)
    if ns is None:
        raise ValueError(f"unsupported iwxxm_version for annex3 emit: {iwxxm_version}")
    return ns


def _fmt_coord(value: float) -> str:
    """
    Internal helper ``_fmt_coord``.

    Parameters
    ----------
    value : float
        Argument ``value``.

    Returns
    -------
    str
        Return value.
    """
    text = f"{value:.2f}"
    if text.endswith(".00"):
        return text[:-3]
    return text


def _sigmet_phenomenon_href(code: str) -> str:
    """
    Build the IWXXM phenomenon ``xlink:href`` for a SIGMET IR code.

    Prefers SigWxPhenomena when the code is in that list. Otherwise uses
    AirWxPhenomena so national SIGMET TAC that carries AIRMET vocabulary
    (for example ``OCNL TS``) still emits a resolvable WMO codelist value.

    Parameters
    ----------
    code : str
        IR phenomenon local name (for example ``SEV_MTW`` or ``OCNL_TS``).

    Returns
    -------
    str
        Absolute ``codes.wmo.int`` href for the phenomenon.
    """
    token = str(code or "").strip()
    if token in _SIG_WX_PHENOMENA_CODES:
        return _SIG_PHENOM_HREF.format(code=token)
    return _AIR_PHENOM_HREF.format(code=token)


__all__ = [
    "_AIR_PHENOM_HREF",
    "_CLOUD_HREF",
    "_CLOUD_TYPE_HREF",
    "_NS",
    "_SIG_PHENOM_HREF",
    "_SIG_WX_PHENOMENA_CODES",
    "_WMO_MULTI_VA_FCST_TIME_ID",
    "_WMO_MULTI_VA_OBS_TIME_ID",
    "_WX_HREF",
    "_YUDO_ELEV_M",
    "_YUDO_NAME",
    "_YUDO_POS",
    "_fmt_coord",
    "_ns",
    "_sigmet_phenomenon_href",
]
