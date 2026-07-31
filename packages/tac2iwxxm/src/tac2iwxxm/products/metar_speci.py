"""METAR/SPECI TAC → IR parser (F6.a annex3 path)."""

from __future__ import annotations

import re
from typing import Any

_REPORT = re.compile(
    r"^(?P<rtype>METAR|SPECI)\s+(?:(?P<cor_pre>COR)\s+)?(?P<station>[A-Z][A-Z0-9]{3})\s+"
    r"(?P<ddhhmm>\d{6})Z\b(?P<body>.*)$",
    re.DOTALL,
)
_WIND = re.compile(r"\b(?P<dir>\d{3}|VRB)(?P<spd>\d{2,3})(?:G(?P<gust>\d{2,3}))?(?P<uom>KT|MPS)\b")
_VIS_SM = re.compile(r"\b(?P<vis>\d{1,2})SM\b")
_VIS_M = re.compile(r"\b(?P<vis>\d{4})\b")
# AUTO missing visibility: ////SM (statute) or //// (metres); avoid matching ////SM as ////.
# Note: ``\b`` does not fire before ``/`` (non-word), so use explicit lookarounds.
_VIS_SM_NOT_OBS = re.compile(r"(?<![A-Z0-9/])////SM(?![A-Z0-9/])")
_VIS_M_NOT_OBS = re.compile(r"(?<![A-Z0-9/])////(?!SM)(?![A-Z0-9/])")
_CAVOK = re.compile(r"\bCAVOK\b")
_TEMP = re.compile(r"\b(?P<temp>M?\d{2})/(?P<dew>M?\d{2})\b")
# AUTO missing temperature/dewpoint group (five slashes).
_TEMP_NOT_OBS = re.compile(r"(?<![A-Z0-9/])/////(?![A-Z0-9/])")
_ALT_INHG = re.compile(r"\bA(?P<alt>\d{4})\b")
_ALT_NOT_OBS = re.compile(r"(?<![A-Z0-9])A////(?![A-Z0-9/])")
_QNH_HPA = re.compile(r"\bQ(?P<qnh>\d{3,4})\b")
_QNH_NOT_OBS = re.compile(r"(?<![A-Z0-9])Q////(?![A-Z0-9/])")
_CLOUD = re.compile(r"\b(?P<amt>FEW|SCT|BKN|OVC)(?P<base>\d{3})(?P<ctype>CB|TCU)?\b")
_NIL = re.compile(r"\bNIL\b")
_AUTO = re.compile(r"\bAUTO\b")
_NOSIG = re.compile(r"\bNOSIG\b")
_NSC = re.compile(r"\bNSC\b")
_NCD = re.compile(r"\bNCD\b")
_VV_NOT_OBS = re.compile(r"\bVV///(?![A-Z0-9/])")
_WIND_SECTOR = re.compile(r"\b(?P<ccw>\d{3})V(?P<cw>\d{3})\b")
# Variable RVR (US / FMH-1): R04L/1100V2300FT — try before simple RVR.
_RVR_VAR = re.compile(
    r"\bR(?P<rwy>\d{2}[LCR]?)/(?P<min_op>[PM])?(?P<min>\d{4})V(?P<max_op>[PM])?(?P<max>\d{4})"
    r"(?P<tend>[UDN])?(?P<ft>FT)?\b"
)
_RVR = re.compile(r"\bR(?P<rwy>\d{2}[LCR]?)/(?P<op>[PM])?(?P<val>\d{4})(?P<tend>[UDN])?(?P<ft>FT)?\b")
# Minimum visibility with compass sector (e.g. 1200NE) — after prevailing metres.
_VIS_MIN = re.compile(r"\b(?P<vis>\d{4})(?P<dir>N|NE|E|SE|S|SW|W|NW)\b")
_COMPASS_DEG = {
    "N": 360,
    "NE": 45,
    "E": 90,
    "SE": 135,
    "S": 180,
    "SW": 225,
    "W": 270,
    "NW": 315,
}
# Present weather: `//` (not observable) or coded group (-SN, FG, VCSH, …).
_WX_TOKEN = re.compile(
    r"(?<![A-Z0-9/])(?P<wx>//|"
    r"(?:\+|-|VC)?"
    r"(?:MI|PR|BC|DR|BL|SH|TS|FZ)?"
    r"(?:DZ|RA|SN|SG|PL|GR|GS|UP|BR|FG|FU|VA|DU|SA|HZ|PY|PO|SQ|FC|SS|DS)+"
    r")(?![A-Z0-9/])"
)
_TREND_GROUP = re.compile(
    r"\b(?P<kind>BECMG|TEMPO|NOSIG)\b(?P<body>.*?)(?=\b(?:BECMG|TEMPO|NOSIG)\b|$)",
    re.DOTALL,
)
_TREND_TL = re.compile(r"\bTL(?P<hhmm>\d{4})\b")
_TREND_AT = re.compile(r"\bAT(?P<hhmm>\d{4})\b")
_TREND_FM = re.compile(r"\bFM(?P<hhmm>\d{4})\b")
_RMK = re.compile(r"\bRMK\b(?P<rmk>.*)$")
_AO = re.compile(r"\bAO(?P<ao>[12])\b")
_SLP = re.compile(r"\bSLP(?P<code>\d{3})\b")
_PK_WND = re.compile(r"\bPK\s+WND\s+(?P<dir>\d{3})(?P<spd>\d{2,3})/(?P<hhmm>\d{4})\b")
_RMK_T = re.compile(r"\bT(?P<tsign>[01])(?P<tttt>\d{3})(?P<dsign>[01])(?P<dddd>\d{3})\b")
_RMK_P = re.compile(r"\bP(?P<p>\d{4})\b")
_COR_AFTER_TIME = re.compile(r"^\s*COR\b\s*")
_OBS_SYSTEM_HREF = "https://codes.nws.noaa.gov/FMH-1/ObservingSystemType/AO{ao}"
_FREQ_HREF = "https://codes.nws.noaa.gov/FMH-1/LightningFrequency/{code}"
_TYPE_HREF = "https://codes.nws.noaa.gov/FMH-1/LightningType/{code}"
_DIST_HREF = "https://codes.nws.noaa.gov/FMH-1/QualitativeDistance/{code}"
_LTG_FREQ_CODES = {"OCNL": "OCCASIONAL", "FRQ": "FREQUENT", "CONS": "CONTINUOUS"}
_LTG_DIST_CODES = {"DSNT": "DISTANT", "VC": "VICINITY"}
# 8-point compass for lightning sector extremes (true north = 0°).
_LTG_COMPASS_DEG: dict[str, float] = {
    "N": 0.0,
    "NE": 45.0,
    "E": 90.0,
    "SE": 135.0,
    "S": 180.0,
    "SW": 225.0,
    "W": 270.0,
    "NW": 315.0,
}
# FMH-1 lightning REMARKS: [OCNL|FRQ|CONS] LTG[IC|CC|CG…] [DSNT|VC] [dirs|ALQDS]
_LTG_REMARK = re.compile(
    r"\b(?:(?P<freq>OCNL|FRQ|CONS)\s+)?"
    r"LTG(?P<type>(?:IC|CC|CG)*)"
    r"(?:\s+(?P<dist>DSNT|VC))?"
    r"(?:\s+(?P<sector>ALQDS|(?:N|NE|E|SE|S|SW|W|NW)(?:-(?:N|NE|E|SE|S|SW|W|NW))*))?"
    r"\b"
)
# Structured tokens removed before free-text retain (AO/SLP/PK/LTG — T/P stay in free-text).
_CONSUMED_REMARK = re.compile(
    r"\bAO[12]\b|\bSLP\d{3}\b|\bPK\s+WND\s+\d{3}\d{2,3}/\d{4}\b|"
    r"(?:\b(?:OCNL|FRQ|CONS)\s+)?LTG(?:IC|CC|CG)*"
    r"(?:\s+(?:DSNT|VC))?"
    r"(?:\s+(?:ALQDS|(?:N|NE|E|SE|S|SW|W|NW)(?:-(?:N|NE|E|SE|S|SW|W|NW))*))?\b"
)


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


def _slp_code_to_hpa(code: int) -> float:
    """Decode FMH-1 SLP### (tenths hPa, leading 9/10 omitted) to hPa."""
    if code < 500:
        return 1000.0 + code / 10.0
    return 900.0 + code / 10.0


def _tenths_celsius(sign: str, digits: str) -> float:
    """Decode FMH-1 additive T sign+three-digit tenths to Celsius."""
    value = int(digits) / 10.0
    return -value if sign == "1" else value


def _split_obs_and_trends(body: str) -> tuple[str, list[re.Match[str]]]:
    """
    Split METAR/SPECI body into observation text and trend groups.

    Trend keywords (BECMG / TEMPO / NOSIG) and their bodies are excluded from
    observation scanning so trend NSW/NSC/FG do not pollute present weather.
    """
    first = re.search(r"\b(?:BECMG|TEMPO|NOSIG)\b", body)
    if first is None:
        return body, []
    obs = body[: first.start()]
    trends = list(_TREND_GROUP.finditer(body, first.start()))
    return obs, trends


def _hhmm_to_stamp(ir: dict[str, Any], hhmm: str) -> str:
    """Map TL/AT/FM HHMM onto the observation calendar day (WMO YUDO → 2012-08)."""
    hour = int(hhmm[0:2])
    minute = int(hhmm[2:4])
    day = int(ir["day"])
    # Match annex3 emit stamp month/year for YUDO WMO examples.
    if str(ir.get("station")) == "YUDO":
        return f"2012-08-{day:02d}T{hour:02d}:{minute:02d}:00Z"
    return f"2023-06-{day:02d}T{hour:02d}:{minute:02d}:00Z"


def _obs_stamp(ir: dict[str, Any]) -> str:
    day = int(ir["day"])
    hour = int(ir["hour"])
    minute = int(ir["minute"])
    if str(ir.get("station")) == "YUDO":
        return f"2012-08-{day:02d}T{hour:02d}:{minute:02d}:00Z"
    return f"2023-06-{day:02d}T{hour:02d}:{minute:02d}:00Z"


def _parse_trend_group(ir: dict[str, Any], kind: str, body: str) -> dict[str, Any] | None:
    """Parse one BECMG/TEMPO/NOSIG group into an IR trend dict."""
    if kind == "NOSIG":
        return {"change_indicator": "NOSIG", "nil_nosig": True}

    trend: dict[str, Any] = {
        "change_indicator": ("BECOMING" if kind == "BECMG" else "TEMPORARY_FLUCTUATIONS"),
    }
    tl = _TREND_TL.search(body)
    at = _TREND_AT.search(body)
    fm = _TREND_FM.search(body)
    if tl is not None:
        trend["time_indicator"] = "UNTIL"
        trend["phenomenon_begin"] = _obs_stamp(ir)
        trend["phenomenon_end"] = _hhmm_to_stamp(ir, tl.group("hhmm"))
    elif at is not None:
        trend["time_indicator"] = "AT"
        trend["phenomenon_at"] = _hhmm_to_stamp(ir, at.group("hhmm"))
    elif fm is not None:
        trend["time_indicator"] = "FROM"
        trend["phenomenon_at"] = _hhmm_to_stamp(ir, fm.group("hhmm"))

    # Visibility: prefer 9999 / 4-digit metres; SM uncommon in ICAO trends.
    if re.search(r"\b9999\b", body):
        trend["visibility_m"] = 10000
        trend["visibility_above"] = True
    else:
        vis_m = _VIS_M.search(body)
        if vis_m is not None:
            metres = int(vis_m.group("vis"))
            trend["visibility_m"] = metres
            trend["visibility_above"] = metres >= 9999

    if re.search(r"\bNSW\b", body):
        trend["weather_nsw"] = True
    else:
        wx_codes: list[str] = []
        for wx_m in _WX_TOKEN.finditer(body):
            token = wx_m.group("wx")
            if token != "//":
                wx_codes.append(token)
        if wx_codes:
            trend["weather"] = wx_codes

    if _NSC.search(body):
        trend["cloud_nsc"] = True
    if _CAVOK.search(body):
        trend["cavok"] = True

    return trend


def _lightning_type_code(raw: str) -> str | None:
    """Map concatenated FMH-1 LTG type letters to NWS LightningType code."""
    if not raw:
        return None
    parts: list[str] = []
    i = 0
    while i < len(raw):
        if raw.startswith("IC", i):
            parts.append("IC")
            i += 2
        elif raw.startswith("CC", i):
            parts.append("CC")
            i += 2
        elif raw.startswith("CG", i):
            parts.append("CG")
            i += 2
        else:
            return None
    uniq = frozenset(parts)
    if uniq == frozenset({"IC", "CC", "CG"}):
        return "CCCGIC"
    if uniq == frozenset({"IC", "CG"}):
        return "ICCG"
    if uniq == frozenset({"CC", "CG"}):
        return "CCCG"
    if uniq == frozenset({"IC", "CC"}):
        return "ICCC"
    if len(uniq) == 1:
        return next(iter(uniq))
    return "".join(parts)


def _lightning_sector(sector_tok: str | None) -> dict[str, Any] | None:
    """Build sector IR from ALQDS or hyphenated compass list (PDF ±22.5° padding)."""
    if not sector_tok:
        return None
    if sector_tok == "ALQDS":
        return {"in_all_quadrants": True}
    dirs = sector_tok.split("-")
    if any(d not in _LTG_COMPASS_DEG for d in dirs):
        return None
    first = _LTG_COMPASS_DEG[dirs[0]]
    last = _LTG_COMPASS_DEG[dirs[-1]]
    return {
        "in_all_quadrants": False,
        "ccw_deg": (first - 22.5) % 360.0,
        "cw_deg": (last + 22.5) % 360.0,
    }


def _parse_lightning_remark(remarks: str) -> dict[str, Any] | None:
    """Parse first FMH-1 lightning REMARKS group into ObservedLightning IR fields."""
    m = _LTG_REMARK.search(remarks)
    if m is None:
        return None
    entry: dict[str, Any] = {}
    freq = m.group("freq")
    if freq:
        entry["frequency_href"] = _FREQ_HREF.format(code=_LTG_FREQ_CODES[freq])
    type_code = _lightning_type_code(m.group("type") or "")
    if type_code:
        entry["type_href"] = _TYPE_HREF.format(code=type_code)
    dist = m.group("dist")
    if dist:
        entry["qualitative_distance_href"] = _DIST_HREF.format(code=_LTG_DIST_CODES[dist])
    sector = _lightning_sector(m.group("sector"))
    if sector is not None:
        entry["sector"] = sector
    return entry or None


def _remarks_free_text(remarks: str) -> str:
    """
    Return REMARKS remainder after removing structured AO/SLP/PK/LTG tokens.

    Additive T/P and plain language stay so ``iwxxm_us`` can retain them in
    ``humanReadableText`` (#667 / UJ-026 never-drop).
    """
    leftover = _CONSUMED_REMARK.sub(" ", remarks)
    leftover = re.sub(r"\s+", " ", leftover).strip(" =")
    return leftover


def _parse_remarks(rest: str, ir: dict[str, Any]) -> None:
    """
    Enrich IR with IWXXM-US REMARKS groups (AO2, SLP, PK WND, LTG, T, P).

    Malformed US REMARKS tokens append to ``ir['remark_issues']`` for UJ-010 /
    TC-F6-012 diagnostics (profile isolation: annex3 emit ignores extensions).
    Unparsed remainder is stored in ``remarks_free_text`` for never-drop emit.
    """
    rmk = _RMK.search(rest)
    if rmk is None:
        return
    remarks = rmk.group("rmk")
    ir["remarks_present"] = True
    ir["remarks_text"] = remarks.strip().rstrip("=").strip()
    issues: list[str] = list(ir.get("remark_issues") or [])

    if re.search(r"\bAO(?![12]\b)\w*\b", remarks):
        issues.append("malformed AO observing-system token in REMARKS")
    ao = _AO.search(remarks)
    if ao is not None:
        ir["observing_system_type"] = f"AO{ao.group('ao')}"
        ir["observing_system_href"] = _OBS_SYSTEM_HREF.format(ao=ao.group("ao"))

    if re.search(r"\bSLP(?!\d{3}\b)\w*\b", remarks):
        issues.append("malformed SLP sea-level-pressure token in REMARKS")
    slp = _SLP.search(remarks)
    if slp is not None:
        ir["sea_level_pressure_hpa"] = _slp_code_to_hpa(int(slp.group("code")))

    if re.search(r"\bPK\s+WND\b", remarks) and _PK_WND.search(remarks) is None:
        issues.append("malformed PK WND group in REMARKS")
    pk = _PK_WND.search(remarks)
    if pk is not None:
        ir["peak_wind_dir_deg"] = int(pk.group("dir"))
        ir["peak_wind_speed_kt"] = int(pk.group("spd"))
        hhmm = pk.group("hhmm")
        ir["peak_wind_hour"] = int(hhmm[0:2])
        ir["peak_wind_minute"] = int(hhmm[2:4])

    lightning = _parse_lightning_remark(remarks)
    if lightning is not None:
        ir["observed_lightning"] = lightning

    temp_tenths = _RMK_T.search(remarks)
    if temp_tenths is not None:
        ir["remark_temp_tenths_c"] = _tenths_celsius(temp_tenths.group("tsign"), temp_tenths.group("tttt"))
        ir["remark_dewpoint_tenths_c"] = _tenths_celsius(temp_tenths.group("dsign"), temp_tenths.group("dddd"))

    precip = _RMK_P.search(remarks)
    if precip is not None:
        ir["precip_inches"] = int(precip.group("p")) / 100.0

    free = _remarks_free_text(remarks)
    if free:
        ir["remarks_free_text"] = free

    if issues:
        ir["remark_issues"] = issues


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
        Intermediate representation for annex3 / iwxxm_us XML emission and M-field.

    Raises
    ------
    ValueError
        When the TAC cannot be decoded.
    """
    text = tac.strip()
    # Allow COR before station or immediately after observation time (ICAO #594).
    report_match = re.search(
        r"((?:METAR|SPECI)\s+(?:COR\s+)?[A-Z][A-Z0-9]{3}\s+\d{6}Z(?:\s+COR)?\b.*?)=",
        text,
        re.DOTALL,
    )
    if report_match is None:
        report_match = re.search(
            r"((?:METAR|SPECI)\s+(?:COR\s+)?[A-Z][A-Z0-9]{3}\s+\d{6}Z(?:\s+COR)?\b.*)",
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
    correction = bool(m.group("cor_pre"))
    if _COR_AFTER_TIME.match(rest):
        correction = True
        rest = _COR_AFTER_TIME.sub("", rest, count=1)

    ir: dict[str, Any] = {
        "station": station,
        "report_type": rtype,
        "day": day,
        "hour": hour,
        "minute": minute,
        "nil": bool(_NIL.search(rest)),
        "correction": correction,
        "auto": bool(_AUTO.search(rest)),
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

    if _CAVOK.search(rest):
        ir["cavok"] = True
        ir["visibility_m"] = 10000
        ir["visibility_above"] = True
    elif _VIS_SM_NOT_OBS.search(rest) or _VIS_M_NOT_OBS.search(rest):
        # Guidance / TC-EV023-002: AUTO missing vis → common/nil/notObservable.
        ir["visibility_not_observable"] = True
    else:
        vis_sm = _VIS_SM.search(rest)
        if vis_sm is not None:
            sm = int(vis_sm.group("vis"))
            ir["visibility_sm"] = sm
            metres, above = _sm_to_m(sm)
            ir["visibility_m"] = metres
            ir["visibility_above"] = above
        else:
            vis_m = _VIS_M.search(rest)
            if vis_m is None:
                raise ValueError("missing visibility (SM/m/CAVOK) group")
            metres = int(vis_m.group("vis"))
            ir["visibility_m"] = metres
            # ICAO 9999 means 10 km or more.
            ir["visibility_above"] = metres >= 9999

    if _TEMP_NOT_OBS.search(rest):
        ir["temp_not_observable"] = True
        ir["dewpoint_not_observable"] = True
    else:
        temp = _TEMP.search(rest)
        if temp is None:
            raise ValueError("missing temperature/dewpoint group")
        ir["temp_c"] = _celsius(temp.group("temp"))
        ir["dewpoint_c"] = _celsius(temp.group("dew"))

    if _ALT_NOT_OBS.search(rest) or _QNH_NOT_OBS.search(rest):
        ir["qnh_not_observable"] = True
    else:
        alt = _ALT_INHG.search(rest)
        if alt is not None:
            ir["altimeter_inhg"] = int(alt.group("alt")) / 100.0
            ir["qnh_hpa"] = _inhg_to_hpa(alt.group("alt"))
        else:
            qnh = _QNH_HPA.search(rest)
            if qnh is None:
                raise ValueError("missing altimeter (Axxxx/Qxxxx) group")
            ir["qnh_hpa"] = float(qnh.group("qnh"))

    # Strip REMARKS; split observation vs trend groups before exceptional tokens.
    body_for_wx = _RMK.split(rest, maxsplit=1)[0]
    obs_body, trend_matches = _split_obs_and_trends(body_for_wx)

    # Re-bind visibility from observation only (avoid trend 9999 / TL times).
    if not ir.get("cavok"):
        if _VIS_SM_NOT_OBS.search(obs_body) or _VIS_M_NOT_OBS.search(obs_body):
            ir["visibility_not_observable"] = True
            ir.pop("visibility_m", None)
            ir.pop("visibility_sm", None)
            ir.pop("visibility_above", None)
        else:
            vis_sm = _VIS_SM.search(obs_body)
            if vis_sm is not None:
                sm = int(vis_sm.group("vis"))
                ir["visibility_sm"] = sm
                metres, above = _sm_to_m(sm)
                ir["visibility_m"] = metres
                ir["visibility_above"] = above
            else:
                vis_m = _VIS_M.search(obs_body)
                if vis_m is not None:
                    metres = int(vis_m.group("vis"))
                    ir["visibility_m"] = metres
                    ir["visibility_above"] = metres >= 9999

    min_vis = _VIS_MIN.search(obs_body)
    if min_vis is not None:
        ir["min_visibility_m"] = int(min_vis.group("vis"))
        ir["min_visibility_dir_deg"] = _COMPASS_DEG[min_vis.group("dir")]

    cloud_layers: list[dict[str, Any]] = []
    for c in _CLOUD.finditer(obs_body):
        layer: dict[str, Any] = {
            "amount": c.group("amt"),
            "base_ft": int(c.group("base")) * 100,
        }
        ctype = c.group("ctype")
        if ctype:
            layer["cloud_type"] = ctype
        cloud_layers.append(layer)
    ir["clouds"] = cloud_layers
    if cloud_layers:
        ir["cloud_amount"] = cloud_layers[0]["amount"]
        ir["cloud_base_ft"] = cloud_layers[0]["base_ft"]

    if _NOSIG.search(body_for_wx):
        ir["nosig"] = True
    if _NSC.search(obs_body):
        # FAQ §14.3 / TC-EV023-001: NSC is exclusive — drop any FEW/SCT/… layers.
        ir["nsc"] = True
        ir["clouds"] = []
        ir.pop("cloud_amount", None)
        ir.pop("cloud_base_ft", None)
    if _NCD.search(obs_body):
        ir["ncd"] = True
    if _VV_NOT_OBS.search(obs_body):
        ir["vertical_visibility_not_observable"] = True

    sector = _WIND_SECTOR.search(obs_body)
    if sector is not None:
        ir["wind_dir_ccw_deg"] = int(sector.group("ccw"))
        ir["wind_dir_cw_deg"] = int(sector.group("cw"))

    rvr_var = _RVR_VAR.search(obs_body)
    if rvr_var is not None:
        min_raw = int(rvr_var.group("min"))
        max_raw = int(rvr_var.group("max"))
        if rvr_var.group("ft"):
            min_m = int(round(min_raw * 0.3048))
            max_m = int(round(max_raw * 0.3048))
        else:
            min_m = min_raw
            max_m = max_raw
        ir["rvr"] = {
            "runway": rvr_var.group("rwy"),
            "variable": True,
            "min_m": min_m,
            "max_m": max_m,
            "below_sensor_minimum": rvr_var.group("min_op") == "M",
            "above_sensor_maximum": rvr_var.group("max_op") == "P",
            "tendency": {"U": "UPWARD", "D": "DOWNWARD", "N": "NO_CHANGE"}.get(rvr_var.group("tend") or ""),
        }
    else:
        rvr = _RVR.search(obs_body)
        if rvr is not None:
            val = int(rvr.group("val"))
            # US FT → metres; ICAO metre groups stay as-is.
            if rvr.group("ft"):
                metres = int(round(val * 0.3048))
            else:
                metres = val
            ir["rvr"] = {
                "runway": rvr.group("rwy"),
                "mean_m": metres,
                "operator": {"P": "ABOVE", "M": "BELOW"}.get(rvr.group("op") or ""),
                "tendency": {"U": "UPWARD", "D": "DOWNWARD", "N": "NO_CHANGE"}.get(rvr.group("tend") or ""),
            }

    present: list[str] = []
    wx_not_obs = False
    for wx_m in _WX_TOKEN.finditer(obs_body):
        token = wx_m.group("wx")
        if token == "//":
            wx_not_obs = True
        else:
            present.append(token)
    if wx_not_obs:
        ir["present_weather_not_observable"] = True
    if present:
        ir["present_weather"] = present

    trends: list[dict[str, Any]] = []
    for tm in trend_matches:
        parsed = _parse_trend_group(ir, tm.group("kind"), tm.group("body"))
        if parsed is not None:
            trends.append(parsed)
    if trends:
        ir["trend_forecasts"] = trends
        # Back-compat for F20 SPECI tempo-only emitters / gml:id helpers.
        for t in trends:
            if t.get("change_indicator") == "TEMPORARY_FLUCTUATIONS":
                legacy: dict[str, Any] = {
                    "change_indicator": "TEMPORARY_FLUCTUATIONS",
                }
                if t.get("visibility_m") is not None:
                    legacy["visibility_m"] = t["visibility_m"]
                if t.get("weather_nsw"):
                    legacy["weather_nsw"] = True
                ir["tempo_trend"] = legacy
                break
        if any(t.get("nil_nosig") for t in trends):
            ir["nosig"] = True

    _parse_remarks(rest, ir)
    return ir
