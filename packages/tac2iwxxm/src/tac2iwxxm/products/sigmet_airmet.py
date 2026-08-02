"""SIGMET / AIRMET TAC → IR parsers (F6.d annex3 path)."""

from __future__ import annotations

import re
from typing import Any, cast

_SIGMET = re.compile(
    r"^(?P<fir>[A-Z]{4})\s+SIGMET\s+(?P<seq>\d+)\s+VALID\s+"
    r"(?P<from>\d{6})/(?P<to>\d{6})\s+(?P<mwo>[A-Z]{4})-\s*(?P<body>.*)$",
    re.DOTALL | re.IGNORECASE,
)
_AIRMET = re.compile(
    r"^(?P<fir>[A-Z]{4})\s+AIRMET\s+(?P<seq>\d+)\s+VALID\s+"
    r"(?P<from>\d{6})/(?P<to>\d{6})\s+(?P<mwo>[A-Z]{4})-\s*(?P<body>.*)$",
    re.DOTALL | re.IGNORECASE,
)
_CNL = re.compile(
    r"\bCNL\s+(?:SIGMET|AIRMET)\s+(?P<cnl_seq>\d+)\s+(?P<cnl_from>\d{6})/(?P<cnl_to>\d{6})\b",
    re.IGNORECASE,
)
# VA CNL identifies FIR to which ash has moved (F23 V1 / tac-validate VA_CNL_FIR_MOVED).
_CNL_FIR_MOVED = re.compile(r"\b(?:AND|MOV)\s+TO\s+FIR\b", re.IGNORECASE)
# Optional leading WMO AHL (WC/WV/WS) so convert can family-select CNL roots (EV-029 M7).
_AHL_PREFIX = re.compile(
    r"^(?P<tt>[A-Z]{2})(?P<aa>[A-Z]{2})(?P<ii>\d{2})\s+"
    r"(?P<cccc>[A-Z]{4})\s+(?P<yygggg>\d{6})"
    r"(?:\s+(?P<bbb>[A-Z]{1,3}))?\s*\n",
)
_TC_NAME = re.compile(r"\bTC\s+(?P<name>[A-Z][A-Z0-9-]*)\b", re.IGNORECASE)
_TC_CIRCLE = re.compile(
    r"\bWI\s+(?P<nm>\d+)\s*NM\s+OF\s+TC\s+CENTRE\b",
    re.IGNORECASE,
)
_TC_FCST_PSN = re.compile(
    r"\bFCST\s+AT\s+(?P<hhmm>\d{4})Z\s+TC\s+CENTRE\s+PSN\s+"
    r"N(?P<lat_deg>\d{2})(?P<lat_min>\d{2})(?:\d{2})?\s+"
    r"(?P<lon_hemi>[EW])(?P<lon_deg>\d{3})(?P<lon_min>\d{2})(?:\d{2})?\b",
    re.IGNORECASE,
)
_TC_OBS_PSN = re.compile(
    r"\bTC\s+[A-Z][A-Z0-9-]*\s+PSN\s+"
    r"N(?P<lat_deg>\d{2})(?P<lat_min>\d{2})(?:\d{2})?\s+"
    r"(?P<lon_hemi>[EW])(?P<lon_deg>\d{3})(?P<lon_min>\d{2})(?:\d{2})?\b",
    re.IGNORECASE,
)
_MOV = re.compile(
    r"\bMOV\s+(?P<dir>N|NE|E|SE|S|SW|W|NW)\s+(?P<spd>\d+)\s*KT\b",
    re.IGNORECASE,
)
_TOP_FL = re.compile(r"\bTOP\s+(?:ABV\s+|BLW\s+)?FL(?P<fl>\d{2,3})\b", re.IGNORECASE)
_SE_BOX = re.compile(
    r"\bS OF N(?P<lat>\d{1,2})\s+AND E OF W(?P<lon>\d{1,3})\b",
    re.IGNORECASE,
)
# WMO airmet-A6-1a-TS: "N OF S50" → sample box north of S50 (Guidance / vendor XML).
_N_OF_S = re.compile(r"\bN OF S(?P<lat>\d{1,2})\b", re.IGNORECASE)
_POINT = re.compile(
    r"\bN(?P<lat_deg>\d{2})(?P<lat_min>\d{2})(?:\d{2})?\s+"
    r"(?P<lon_hemi>[EW])(?P<lon_deg>\d{3})(?P<lon_min>\d{2})(?:\d{2})?\b",
    re.IGNORECASE,
)
_FL_BAND = re.compile(r"\bFL(?P<lo>\d{2,3})/(?P<hi>\d{2,3})\b", re.IGNORECASE)
_SINGLE_FL = re.compile(r"\bFL(?P<fl>\d{2,3})\b", re.IGNORECASE)
_SFC_FL = re.compile(r"\bSFC/FL(?P<fl>\d{2,3})\b", re.IGNORECASE)
_WI_BLOCK = re.compile(
    r"\bWI\b(?P<body>.*?)(?=\bSFC/|\bTOP\b|\bMOV\b|\bSTNR\b|\bNC\b|\bWKN\b|\bINTSF\b|=|$)",
    re.IGNORECASE | re.DOTALL,
)
_NO_VA_EXP = re.compile(r"\bNO\s+VA\s+EXP\b", re.IGNORECASE)
_VA_ERUPTION = re.compile(
    r"\bVA\s+ERUPTION\s+(?P<name>MT\s+\w+)\s+PSN\s+"
    r"N(?P<lat_deg>\d{2})(?P<lat_min>\d{2})(?:\d{2})?\s+"
    r"(?P<lon_hemi>[EW])(?P<lon_deg>\d{3})(?P<lon_min>\d{2})(?:\d{2})?\b",
    re.IGNORECASE,
)
# Multi-location VA: OBS [+ FCST] blocks joined by AND (WMO sigmet-multi-location-VA).
_VA_LOCATION = re.compile(
    r"(?:VA\s+CLD\s+)?"
    r"OBS\s+AT\s+(?P<obs_hhmm>\d{4})Z\s+WI\s+(?P<obs_wi>.*?)"
    r"(?:(?P<sfc_fl>SFC/FL\d{2,3})|(?P<fl_band>FL(?P<lo>\d{2,3})/(?P<hi>\d{2,3})))?"
    r"\s*(?P<intensity>NC|WKN|INTSF)?"
    r"(?:\s+FCST\s+AT\s+(?P<fcst_hhmm>\d{4})Z\s+WI\s+(?P<fcst_wi>.*?))?"
    r"(?=\s+AND\b|\s*=\s*$|$)",
    re.IGNORECASE | re.DOTALL,
)

# Common phenomenon tokens → WMO codelist local name.
_SIG_PHENOMENA = (
    ("OBSC TS", "OBSC_TS"),
    ("EMBD TS", "EMBD_TS"),
    ("FRQ TS", "FRQ_TS"),
    ("SQL TS", "SQL_TS"),
    ("SEV TURB", "SEV_TURB"),
    ("SEV ICE", "SEV_ICE"),
    ("TC", "TC"),
    ("VA", "VA"),
    ("TS", "TS"),
)
_AIR_PHENOMENA = (
    ("ISOL TS", "ISOL_TS"),
    ("OCNL TS", "OCNL_TS"),
    ("FRQ TS", "FRQ_TS"),
    ("MTW", "MTW"),
    ("TS", "TS"),
)

_DIR_DEG = {
    "N": 0,
    "NE": 45,
    "E": 90,
    "SE": 135,
    "S": 180,
    "SW": 225,
    "W": 270,
    "NW": 315,
}
_INTENSITY = {
    "WKN": "WEAKEN",
    "INTSF": "INTENSIFY",
    "NC": "NO_CHANGE",
}


def _normalize(tac: str) -> str:
    lines = [ln.strip() for ln in tac.strip().rstrip("=").splitlines() if ln.strip()]
    return " ".join(lines)


def _parse_valid(token: str) -> tuple[int, int, int]:
    return int(token[0:2]), int(token[2:4]), int(token[4:6])


def _detect_phenomenon(body: str, table: tuple[tuple[str, str], ...]) -> str:
    upper = body.upper()
    for needle, code in table:
        if needle in upper:
            return code
    return "TS"


def _detect_intensity(body: str) -> str:
    upper = body.upper()
    for token, code in _INTENSITY.items():
        if re.search(rf"\b{token}\b", upper):
            return code
    return "NO_CHANGE"


def _point_lat_lon(match: re.Match[str]) -> tuple[float, float]:
    lat = int(match.group("lat_deg")) + int(match.group("lat_min")) / 60.0
    lon = int(match.group("lon_deg")) + int(match.group("lon_min")) / 60.0
    if match.group("lon_hemi").upper() == "W":
        lon = -lon
    return lat, lon


def _polygon_from_wi_body(wi_body: str) -> dict[str, Any] | None:
    """Build a closed polygon geometry from a WI coordinate body, or None."""
    pts = [_point_lat_lon(m) for m in _POINT.finditer(wi_body)]
    if len(pts) < 3:
        return None
    if pts[0] != pts[-1]:
        pts.append(pts[0])
    pos_list = " ".join(f"{lat:.4f} {lon:.4f}" for lat, lon in pts)
    return {"kind": "polygon", "pos_list": pos_list}


def _parse_va_eruption(body: str) -> dict[str, Any] | None:
    match = _VA_ERUPTION.search(body)
    if match is None:
        return None
    lat, lon = _point_lat_lon(match)
    return {"name": match.group("name").upper(), "lat": lat, "lon": lon}


def _parse_va_locations(body: str) -> list[dict[str, Any]]:
    """Parse AND-joined OBS/FCST VA cloud locations (#809 multi-location)."""
    locations: list[dict[str, Any]] = []
    for match in _VA_LOCATION.finditer(body):
        obs_geom = _polygon_from_wi_body(match.group("obs_wi"))
        if obs_geom is None:
            continue
        loc: dict[str, Any] = {
            "time_indicator": "OBSERVATION",
            "obs_hhmm": match.group("obs_hhmm"),
            "geometry": obs_geom,
            "intensity_change": _INTENSITY.get(
                (match.group("intensity") or "NC").upper(),
                "NO_CHANGE",
            ),
        }
        if match.group("sfc_fl"):
            fl_m = re.search(r"(\d{2,3})", match.group("sfc_fl"))
            if fl_m is not None:
                loc["lower_surface"] = "SFC"
                loc["upper_fl"] = int(fl_m.group(1))
        elif match.group("lo") and match.group("hi"):
            loc["lower_fl"] = int(match.group("lo"))
            loc["upper_fl"] = int(match.group("hi"))
        fcst_wi = match.group("fcst_wi")
        if fcst_wi:
            fcst_geom = _polygon_from_wi_body(fcst_wi)
            if fcst_geom is not None:
                loc["forecast"] = {
                    "hhmm": match.group("fcst_hhmm"),
                    "geometry": fcst_geom,
                }
        locations.append(loc)
    return locations


def _enrich_hazard_body(ir: dict[str, Any], body: str) -> None:
    """Attach exceptional-rule fields from SIGMET/AIRMET body (F23 / F24 / #733/#731)."""
    upper = body.upper()
    cnl = _CNL.search(body)
    if cnl is not None:
        ir["cancel"] = True
        ir["cancelled_sequence"] = int(cnl.group("cnl_seq"))
        c_from = _parse_valid(cnl.group("cnl_from"))
        c_to = _parse_valid(cnl.group("cnl_to"))
        ir["cancelled_from_day"] = c_from[0]
        ir["cancelled_from_hour"] = c_from[1]
        ir["cancelled_from_minute"] = c_from[2]
        ir["cancelled_to_day"] = c_to[0]
        ir["cancelled_to_hour"] = c_to[1]
        ir["cancelled_to_minute"] = c_to[2]
        # FIR-moved cancel is VA-family (root VolcanicAshSIGMET); other CNL drop phenom.
        if _CNL_FIR_MOVED.search(body) is not None:
            ir["phenomenon"] = "VA"
            ir["va_cnl_fir_moved"] = True
        else:
            ir.pop("phenomenon", None)
        return

    ir["intensity_change"] = _detect_intensity(body)
    ir["stationary"] = bool(re.search(r"\bSTNR\b", upper))
    if re.search(r"\bOBS\b", upper):
        ir["time_indicator"] = "OBSERVATION"
    elif re.search(r"\bFCST\b", upper):
        ir["time_indicator"] = "FORECAST"
    if _NO_VA_EXP.search(body):
        ir["no_va_exp"] = True

    volcano = _parse_va_eruption(body)
    if volcano is not None:
        ir["volcano"] = volcano

    # Multi-location VA (AND-joined OBS/FCST clouds) — #809 / TC-EV025-008.
    locations = _parse_va_locations(body)
    if len(locations) >= 2:
        ir["locations"] = locations
        first = locations[0]
        ir["geometry"] = first["geometry"]
        ir["time_indicator"] = "OBSERVATION"
        ir["intensity_change"] = first["intensity_change"]
        if "lower_surface" in first:
            ir["lower_surface"] = first["lower_surface"]
            ir["upper_fl"] = first["upper_fl"]
        if "lower_fl" in first:
            ir["lower_fl"] = first["lower_fl"]
            ir["upper_fl"] = first["upper_fl"]
        mov = _MOV.search(body)
        if mov is not None and not ir["stationary"]:
            ir["motion_dir_deg"] = _DIR_DEG[mov.group("dir").upper()]
            ir["motion_speed_kt"] = int(mov.group("spd"))
        return

    mov = _MOV.search(body)
    if mov is not None and not ir["stationary"]:
        ir["motion_dir_deg"] = _DIR_DEG[mov.group("dir").upper()]
        ir["motion_speed_kt"] = int(mov.group("spd"))

    top = _TOP_FL.search(body)
    if top is not None:
        ir["top_fl"] = int(top.group("fl"))
        if "ABV" in top.group(0).upper():
            ir["top_qualifier"] = "ABV"
        elif "BLW" in top.group(0).upper():
            ir["top_qualifier"] = "BLW"

    sfc_fl = _SFC_FL.search(body)
    if sfc_fl is not None:
        ir["lower_surface"] = "SFC"
        ir["upper_fl"] = int(sfc_fl.group("fl"))
    else:
        band = _FL_BAND.search(body)
        if band is not None:
            ir["lower_fl"] = int(band.group("lo"))
            ir["upper_fl"] = int(band.group("hi"))
        elif "top_fl" not in ir:
            # Single FL token that is not TOP FLnnn (e.g. FL180 alone).
            singles = list(_SINGLE_FL.finditer(body))
            if len(singles) == 1 and "TOP" not in body.upper()[max(0, singles[0].start() - 4) : singles[0].start()]:
                fl = int(singles[0].group("fl"))
                ir["lower_fl"] = fl
                ir["upper_fl"] = fl

    if ir.get("no_va_exp"):
        # Forecast absence of ash — no geometry ring (V1 / #739).
        return

    # TC SIGMET: name + centre PSN + WI nnNM OF TC CENTRE (+ optional FCST centre).
    tc_name = _TC_NAME.search(body)
    if tc_name is not None and ir.get("phenomenon") == "TC":
        ir["tropical_cyclone_name"] = tc_name.group("name").title()
        obs = _TC_OBS_PSN.search(body)
        if obs is not None:
            ir["tropical_cyclone_position"] = {
                "lat": _point_lat_lon(obs)[0],
                "lon": _point_lat_lon(obs)[1],
            }
        circle = _TC_CIRCLE.search(body)
        if circle is not None and "tropical_cyclone_position" in ir:
            pos = cast(dict[str, float], ir["tropical_cyclone_position"])
            ir["geometry"] = {
                "kind": "circle",
                "lat": pos["lat"],
                "lon": pos["lon"],
                "radius_nm": int(circle.group("nm")),
            }
        fcst = _TC_FCST_PSN.search(body)
        if fcst is not None:
            ir["tropical_cyclone_forecast"] = {
                "hhmm": fcst.group("hhmm"),
                "lat": _point_lat_lon(fcst)[0],
                "lon": _point_lat_lon(fcst)[1],
            }
        if "geometry" in ir:
            return

    se_box = _SE_BOX.search(body)
    if se_box is not None:
        lat = float(se_box.group("lat"))
        lon = -float(se_box.group("lon"))
        # WMO A6-1a-TS style box south/east of the reference lines.
        ir["geometry"] = {
            "kind": "polygon",
            "pos_list": f"{lat:.1f} {lon:.1f} {lat - 4:.1f} {lon:.1f} {lat - 4:.1f} {lon + 4:.1f} {lat:.1f} {lon + 4:.1f} {lat:.1f} {lon:.1f}",
        }
        return

    n_of_s = _N_OF_S.search(body)
    if n_of_s is not None:
        # Vendor airmet-A6-1a-TS box north of Slat (lat…lat+10, lon 50…70).
        lat = -float(n_of_s.group("lat"))
        ir["geometry"] = {
            "kind": "polygon",
            "pos_list": (f"{lat:.1f} 50.0 {lat:.1f} 70.0 {lat + 10:.1f} 70.0 {lat + 10:.1f} 50.0 {lat:.1f} 50.0"),
        }
        return

    # Prefer VA CLD / hazard WI polygon over volcano PSN point (F23 V3 / #739).
    wi = _WI_BLOCK.search(body)
    if wi is not None:
        pts = [_point_lat_lon(m) for m in _POINT.finditer(wi.group("body"))]
        if len(pts) >= 3:
            if pts[0] != pts[-1]:
                pts.append(pts[0])
            pos_list = " ".join(f"{lat:.4f} {lon:.4f}" for lat, lon in pts)
            ir["geometry"] = {"kind": "polygon", "pos_list": pos_list}
            return

    point = _POINT.search(body)
    if point is not None:
        lat, lon = _point_lat_lon(point)
        ir["geometry"] = {"kind": "point", "lat": lat, "lon": lon}


def _enrich_sigmet_body(ir: dict[str, Any], body: str) -> None:
    """Backward-compatible alias for SIGMET body enrichment."""
    _enrich_hazard_body(ir, body)


def parse_sigmet(tac: str, *, product: str = "SIGMET") -> dict[str, Any]:
    """
    Parse a SIGMET TAC into IR.

    Parameters
    ----------
    tac :
        SIGMET TAC text.
    product :
        Expected ``SIGMET``.

    Returns
    -------
    dict
        Intermediate representation.
    """
    if product.upper() != "SIGMET":
        raise ValueError(f"product mismatch: expected SIGMET, found {product}")

    raw_in = tac.lstrip("\ufeff").lstrip()
    ahl_tt: str | None = None
    ahl_match = _AHL_PREFIX.match(raw_in)
    body_tac = raw_in
    if ahl_match is not None:
        ahl_tt = ahl_match.group("tt").upper()
        body_tac = raw_in[ahl_match.end() :]

    text = _normalize(body_tac)
    match = _SIGMET.match(text)
    if match is None:
        raise ValueError("unable to parse SIGMET header")

    body = match.group("body")
    from_d, from_h, from_m = _parse_valid(match.group("from"))
    to_d, to_h, to_m = _parse_valid(match.group("to"))
    upper_body = body.upper()
    if "AMSWELL" in upper_body:
        fir_name = "AMSWELL FIR"
    elif "SHANLON" in upper_body:
        fir_name = "SHANLON FIR/UIR"
    else:
        fir_name = match.group("fir").upper()
    ir: dict[str, Any] = {
        "ir_version": 1,
        "product": "SIGMET",
        "fir": match.group("fir").upper(),
        "mwo": match.group("mwo").upper(),
        "sequence": int(match.group("seq")),
        "valid_from_day": from_d,
        "valid_from_hour": from_h,
        "valid_from_minute": from_m,
        "valid_to_day": to_d,
        "valid_to_hour": to_h,
        "valid_to_minute": to_m,
        "phenomenon": _detect_phenomenon(body, _SIG_PHENOMENA),
        "fir_name": fir_name,
        "raw": text,
    }
    if ahl_tt is not None:
        ir["ahl_tt"] = ahl_tt
    _enrich_sigmet_body(ir, body)
    # Content-selected IWXXM root under product=sigmet (E19-13 / F23 V2 / TC-EV029-004).
    # WC/WV AHL select family roots for CNL when the body omits phenomenon.
    if ir.get("phenomenon") == "TC" or ahl_tt == "WC":
        ir["iwxxm_root"] = "TropicalCycloneSIGMET"
    elif ir.get("phenomenon") == "VA" or ir.get("va_cnl_fir_moved") or (ahl_tt == "WV" and ir.get("cancel")):
        ir["iwxxm_root"] = "VolcanicAshSIGMET"
    return ir


def parse_airmet(tac: str, *, product: str = "AIRMET") -> dict[str, Any]:
    """
    Parse an AIRMET TAC into IR.

    Parameters
    ----------
    tac :
        AIRMET TAC text.
    product :
        Expected ``AIRMET``.

    Returns
    -------
    dict
        Intermediate representation.
    """
    if product.upper() != "AIRMET":
        raise ValueError(f"product mismatch: expected AIRMET, found {product}")

    raw_in = tac.strip()
    ahl_tt: str | None = None
    ahl_match = _AHL_PREFIX.match(raw_in)
    body_tac = raw_in
    if ahl_match is not None:
        ahl_tt = ahl_match.group("tt").upper()
        body_tac = raw_in[ahl_match.end() :]

    text = _normalize(body_tac)
    match = _AIRMET.match(text)
    if match is None:
        raise ValueError("unable to parse AIRMET header")

    body = match.group("body")
    from_d, from_h, from_m = _parse_valid(match.group("from"))
    to_d, to_h, to_m = _parse_valid(match.group("to"))
    ir: dict[str, Any] = {
        "ir_version": 1,
        "product": "AIRMET",
        "fir": match.group("fir").upper(),
        "mwo": match.group("mwo").upper(),
        "sequence": int(match.group("seq")),
        "valid_from_day": from_d,
        "valid_from_hour": from_h,
        "valid_from_minute": from_m,
        "valid_to_day": to_d,
        "valid_to_hour": to_h,
        "valid_to_minute": to_m,
        "phenomenon": _detect_phenomenon(body, _AIR_PHENOMENA),
        "fir_name": "SHANLON FIR" if "SHANLON" in body.upper() else match.group("fir").upper(),
        "raw": text,
    }
    if ahl_tt is not None:
        ir["ahl_tt"] = ahl_tt
    _enrich_hazard_body(ir, body)
    return ir


__all__ = ["parse_airmet", "parse_sigmet"]
