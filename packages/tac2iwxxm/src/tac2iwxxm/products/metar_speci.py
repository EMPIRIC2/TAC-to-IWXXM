"""METAR/SPECI TAC → IR parser (F6.a annex3 path)."""

from __future__ import annotations

import re
from typing import Any

_REPORT = re.compile(
    r"^(?P<rtype>METAR|SPECI)\s+(?:COR\s+)?(?P<station>[A-Z][A-Z0-9]{3})\s+"
    r"(?P<ddhhmm>\d{6})Z\b(?P<body>.*)$",
    re.DOTALL,
)
_WIND = re.compile(r"\b(?P<dir>\d{3}|VRB)(?P<spd>\d{2,3})(?:G(?P<gust>\d{2,3}))?(?P<uom>KT|MPS)\b")
_VIS_SM = re.compile(r"\b(?P<vis>\d{1,2})SM\b")
_TEMP = re.compile(r"\b(?P<temp>M?\d{2})/(?P<dew>M?\d{2})\b")
_ALT_INHG = re.compile(r"\bA(?P<alt>\d{4})\b")
_CLOUD = re.compile(r"\b(?P<amt>FEW|SCT|BKN|OVC)(?P<base>\d{3})\b")
_NIL = re.compile(r"\bNIL\b")


def _celsius(token: str) -> int:
    if token.startswith("M"):
        return -int(token[1:])
    return int(token)


def _inhg_to_hpa(alt_token: str) -> float:
    """Convert Axxxx (hundredths inHg) to hPa rounded to 1 decimal."""
    inhg = int(alt_token) / 100.0
    return round(inhg * 33.8639, 1)


def _sm_to_m(sm: int) -> tuple[int, bool]:
    """
    Statute miles → metres.

    Returns
    -------
    metres, above
        ``above`` is True when SM ≥ 10 (IWXXM ABOVE operator for 10SM+).
    """
    metres = int(round(sm * 1609.344))
    if sm >= 10:
        return 10000, True
    return metres, False


def parse_metar_speci(tac: str, *, product: str) -> dict[str, Any]:
    """
    Parse a single METAR/SPECI TAC report into a versioned IR dict.

    Parameters
    ----------
    tac :
        TAC text (optional AHL line ignored; first METAR/SPECI…= used).
    product :
        Expected ``METAR`` or ``SPECI``.

    Returns
    -------
    dict[str, Any]
        Intermediate representation for annex3 XML emission and M-field.

    Raises
    ------
    ValueError
        When the TAC cannot be decoded.
    """
    text = tac.strip()
    report_match = re.search(
        r"((?:METAR|SPECI)\s+(?:COR\s+)?[A-Z][A-Z0-9]{3}\s+\d{6}Z\b.*?)=",
        text,
        re.DOTALL,
    )
    if report_match is None:
        report_match = re.search(
            r"((?:METAR|SPECI)\s+(?:COR\s+)?[A-Z][A-Z0-9]{3}\s+\d{6}Z\b.*)",
            text,
            re.DOTALL,
        )
    if report_match is None:
        raise ValueError("no METAR/SPECI report found in TAC")

    report = " ".join(report_match.group(1).split())
    m = _REPORT.match(report)
    if m is None:
        raise ValueError(f"unable to parse METAR/SPECI report: {report!r}")

    rtype = m.group("rtype")
    if rtype.upper() != product.upper():
        raise ValueError(f"product mismatch: expected {product}, found {rtype}")

    station = m.group("station")
    ddhhmm = m.group("ddhhmm")
    day = int(ddhhmm[0:2])
    hour = int(ddhhmm[2:4])
    minute = int(ddhhmm[4:6])
    rest = m.group("body")

    ir: dict[str, Any] = {
        "station": station,
        "report_type": rtype,
        "day": day,
        "hour": hour,
        "minute": minute,
        "nil": bool(_NIL.search(rest)),
    }

    if ir["nil"]:
        return ir

    wind = _WIND.search(rest)
    if wind is None:
        raise ValueError("missing wind group")
    if wind.group("dir") == "VRB":
        ir["wind_dir_deg"] = None
        ir["wind_variable"] = True
    else:
        ir["wind_dir_deg"] = int(wind.group("dir"))
        ir["wind_variable"] = False
    ir["wind_speed_kt"] = int(wind.group("spd"))
    if wind.group("uom") == "MPS":
        ir["wind_speed_mps"] = int(wind.group("spd"))
        ir["wind_speed_kt"] = int(round(int(wind.group("spd")) * 1.94384))
    if wind.group("gust"):
        gust_raw = int(wind.group("gust"))
        if wind.group("uom") == "MPS":
            ir["wind_gust_mps"] = gust_raw
            ir["wind_gust_kt"] = int(round(gust_raw * 1.94384))
        else:
            ir["wind_gust_kt"] = gust_raw

    vis = _VIS_SM.search(rest)
    if vis is None:
        raise ValueError("missing visibility (SM) group")
    sm = int(vis.group("vis"))
    ir["visibility_sm"] = sm
    metres, above = _sm_to_m(sm)
    ir["visibility_m"] = metres
    ir["visibility_above"] = above

    temp = _TEMP.search(rest)
    if temp is None:
        raise ValueError("missing temperature/dewpoint group")
    ir["temp_c"] = _celsius(temp.group("temp"))
    ir["dewpoint_c"] = _celsius(temp.group("dew"))

    alt = _ALT_INHG.search(rest)
    if alt is None:
        raise ValueError("missing altimeter (Axxxx) group")
    ir["altimeter_inhg"] = int(alt.group("alt")) / 100.0
    ir["qnh_hpa"] = _inhg_to_hpa(alt.group("alt"))

    clouds = [(c.group("amt"), int(c.group("base")) * 100) for c in _CLOUD.finditer(rest)]
    ir["clouds"] = [{"amount": amt, "base_ft": base} for amt, base in clouds]
    if clouds:
        ir["cloud_amount"] = clouds[0][0]
        ir["cloud_base_ft"] = clouds[0][1]

    return ir
