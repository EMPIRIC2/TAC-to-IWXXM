"""SIGMET / AIRMET TAC → IR parsers (F6.d annex3 path)."""

from __future__ import annotations

import re
from typing import Any, cast

from tac2iwxxm.geometry.reference_point import parse_vor_reference_geometry

_SIGMET = re.compile(
    r"^(?P<fir>[A-Z]{4})\s+SIGMET\s+(?P<seq>\d+)\s+VALID\s+"
    r"(?P<from>\d{6})/(?P<to>\d{6})\s+(?P<mwo>[A-Z]{4})\s*-\s*(?P<body>.*)$",
    re.DOTALL | re.IGNORECASE,
)
_AIRMET = re.compile(
    r"^(?P<fir>[A-Z]{4})\s+AIRMET\s+(?P<seq>\d+)\s+VALID\s+"
    r"(?P<from>\d{6})/(?P<to>\d{6})\s+(?P<mwo>[A-Z]{4})\s*-\s*(?P<body>.*)$",
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
_AREA_TS_MOV = re.compile(
    r"\bAREA\s+TS\s+MOV\s+FROM\s+(?P<dir>\d{3})(?P<spd>\d{2,3})KT\b",
    re.IGNORECASE,
)
_CONVECTIVE_SIGMET = re.compile(
    r"^(?:(?P<unit>[A-Z]{4})\s+)?CONVECTIVE\s+SIGMET\s+(?P<tag>\S+)\s+VALID\s+UNTIL\s+"
    r"(?P<until>\d{4,6})Z\s+(?P<states>(?:[A-Z]{2}\s*)+?)\s+FROM\s+(?P<body>.*)$",
    re.DOTALL | re.IGNORECASE,
)
_NWS_HAZARD_IFR = "http://nws.weather.gov/codes/NWSI10-811/HazardTypes/IFR"
_NWS_SIGMET_AREA_TS = "https://codes.nws.noaa.gov/NWSI-10-811/SIGMETWeatherPhenomena/AreaTS"
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
    ("ISOL TSGR", "ISOL_TSGR"),
    ("OCNL TSGR", "OCNL_TSGR"),
    ("FRQ TSGR", "FRQ_TSGR"),
    ("ISOL TS", "ISOL_TS"),
    ("OCNL TS", "OCNL_TS"),
    ("FRQ TS", "FRQ_TS"),
    ("MOD ICE", "MOD_ICE"),
    ("MOD TURB", "MOD_TURB"),
    ("MOD MTW", "MOD_MTW"),
    ("MT OBSC", "MT_OBSC"),
    ("MTN OBSC", "MT_OBSC"),
    ("IFR", "SFC_VIS"),
    ("MTW", "MTW"),
    ("TS", "TS"),
)
# MANAIR GFA compound phenomena → MSC code-ca vocabulary (EV-064 M5).
_CA_GFA_PHENOMENA = (
    ("FRQ TCU ISOL TSGR", "FRQ_TCU_ISOL_TSGR"),
    ("FRQ TCU ISOL TS", "FRQ_TCU_ISOL_TS"),
    ("OCNL TCU ISOL TSGR", "OCNL_TCU_ISOL_TSGR"),
    ("OCNL TCU ISOL TS", "OCNL_TCU_ISOL_TS"),
    ("SFC VIS AND OVC CLD", "SFC_VIS_and_OVC_CLD"),
    ("SFC VIS AND BKN CLD", "SFC_VIS_and_BKN_CLD"),
)
_GFA_CHART = re.compile(r"\bRMK\s+(GFACN\d+)\b", re.IGNORECASE)
_GFA_SFC_VIS_SM = re.compile(r"\b(?P<vis>\d{1,2})SM\b")
_GFA_SFC_VIS_M = re.compile(r"\b(?P<vis>\d{4})M\b")
_GFA_CLOUD_BASE = re.compile(r"\b(?:BKN|OVC)(?P<base>\d{3})\b")

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
_OTLK_VALID = re.compile(
    r"\bOTLK\s+VALID\s+(?P<from>\d{4})[-/](?P<to>\d{4})Z?",
    re.IGNORECASE,
)
_AIR_AREA_BOUNDARY = re.compile(
    r"\s+AND\s+(?=(?:MOD|ISOL|OCNL|FRQ|MT|MTN|IFR)\s+)",
    re.IGNORECASE,
)
# CONUS/Hawaii bulletin product line (NWSI 10-811 Appendix A2.1).
_CONUS_AIRMET = re.compile(
    r"^(?:W[A-Z]{3}\d{2}\s+(?P<wmo_cccc>[A-Z]{4})\s+(?P<wmo_time>\d{6})\s+)?"
    r"(?:(?P<faa_zone>[A-Z]{4})\s+WA\s+(?P<issue>\d{6})\s+)?"
    r"AIRMET\s+(?P<series>[A-Z]+)\s+(?:UPDT|UPDATE)\s+(?P<upd>\d+)\s+"
    r"FOR\s+(?P<for_text>.+?)\s+VALID\s+UNTIL\s+(?P<until>\d{4,6})\s+(?P<body>.*)$",
    re.IGNORECASE | re.DOTALL,
)
_FRZLVL_SECTION = re.compile(r"\bFRZLVL\.\.\.", re.IGNORECASE)
_FRZLVL_RANGING = re.compile(
    r"FRZLVL\.\.\.RANGING FROM (?P<from>SFC|\d{3})-(?P<to>\d{3})\s+ACRS AREA",
    re.IGNORECASE,
)
_MULT_FRZLVL = re.compile(r"MULT FRZLVL (?P<lo>\d{3})-(?P<hi>\d{3})", re.IGNORECASE)
_FRZLVL_ALG = re.compile(
    r"(?P<alt>SFC|\d{3})\s+ALG\s+(?P<boundary>[A-Z0-9][A-Z0-9\s\-]*?)"
    r"(?=\s+(?:\d{3}|SFC)\s+ALG|\s*\.|\s*=|$)",
    re.IGNORECASE,
)
_FRZLVL_BAND = re.compile(r"\bBTN\s+FRZLVL\s+AND\s+FL(?P<fl>\d{2,3})\b", re.IGNORECASE)
_INLINE_FRZLVL = re.compile(r"\bFRZLVL\s+(?P<lo>\d{3})-(?P<hi>\d{3})\b", re.IGNORECASE)
_CONUS_AIR_LEAD = re.compile(r"^AIRMET\s+[A-Z]+\.\.\.", re.IGNORECASE)


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


def _detect_ca_gfa_phenomenon(body: str) -> str | None:
    """Return MSC code-ca id when body encodes a MANAIR GFA compound phenomenon."""
    upper = body.upper()
    for needle, code in _CA_GFA_PHENOMENA:
        if needle in upper:
            return code
    return None


def _parse_ca_gfa_structured(body: str, gfa_code: str) -> dict[str, Any] | None:
    """Extract GFA structured ranges for SFC VIS compound phenomena."""
    if gfa_code not in {"SFC_VIS_and_BKN_CLD", "SFC_VIS_and_OVC_CLD"}:
        return None
    structured: dict[str, Any] = {}
    sm = _GFA_SFC_VIS_SM.search(body)
    if sm is not None:
        metres = int(sm.group("vis")) * 1609
        structured["surface_visibility_m"] = {"lower": metres, "higher": metres}
    else:
        vis_m = _GFA_SFC_VIS_M.search(body)
        if vis_m is not None:
            metres = int(vis_m.group("vis"))
            structured["surface_visibility_m"] = {"lower": metres, "higher": metres}
    cloud = _GFA_CLOUD_BASE.search(body)
    if cloud is not None:
        base_ft = int(cloud.group("base")) * 100
        structured["cloud_base_ft"] = {"lower": base_ft, "higher": base_ft}
    spd = re.search(r"\bMOV\s+[NSEW]{1,2}\s+(?P<spd>\d{2,3})KT\b", body.upper())
    if spd is not None:
        kt = int(spd.group("spd"))
        structured["surface_wind_kt"] = {"lower": kt, "higher": kt}
    return structured or None


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

    # Multi-location VA (AND-joined OBS/FCST) or single OBS(+FCST) VA cloud (#809 / #856).
    locations = _parse_va_locations(body)
    if locations:
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
        frzlvl_band = _FRZLVL_BAND.search(body)
        if frzlvl_band is not None:
            ir["lower_surface"] = "FRZLVL"
            ir["upper_fl"] = int(frzlvl_band.group("fl"))
        inline_frz = _INLINE_FRZLVL.search(body)
        if inline_frz is not None:
            ir["inline_frzlvl_lo"] = int(inline_frz.group("lo"))
            ir["inline_frzlvl_hi"] = int(inline_frz.group("hi"))
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

    vor_geometry = parse_vor_reference_geometry(body)
    if vor_geometry is not None:
        ir["geometry"] = vor_geometry
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


def _parse_until_token(until: str) -> tuple[int, int, int]:
    """Parse ``VALID UNTIL`` token (``hhmm`` or ``ddhhmm``) into day/hour/minute."""
    if len(until) >= 6:
        return int(until[0:2]), int(until[2:4]), int(until[4:6])
    hour = int(until[0:2])
    minute = int(until[2:4])
    return 9, hour, minute


def _attach_us_airmet_hazard(ir: dict[str, Any]) -> None:
    """Map parsed AIRMET phenomenon to iwxxm-us ``AIRMETWeatherHazards`` when required."""
    phen = ir.get("phenomenon")
    if phen == "SFC_VIS":
        ir["us_airmet_hazard"] = {
            "href": _NWS_HAZARD_IFR,
            "causing_ifr_conditions": True,
        }


def _split_airmet_main_and_outlook(body: str) -> tuple[str, str | None]:
    """Split AIRMET body into active and optional ``OTLK VALID`` outlook subsection."""
    match = re.search(r"\bOTLK\b", body, flags=re.IGNORECASE)
    if match is None:
        return body, None
    return body[: match.start()].strip(), body[match.start() :].strip()


def _split_frzlvl_section(body: str) -> tuple[str, str | None]:
    """Split optional standalone ``FRZLVL...`` subsection from the hazard body."""
    match = _FRZLVL_SECTION.search(body)
    if match is None:
        return body, None
    return body[: match.start()].strip(), body[match.start() :].strip()


def _strip_conus_airmet_lead(body: str) -> str:
    """Remove ``AIRMET ICE...`` phenomenon lead from a CONUS product body."""
    if not _CONUS_AIR_LEAD.match(body):
        return body
    from_match = re.search(r"\bFROM\b", body, flags=re.IGNORECASE)
    if from_match is not None:
        return body[from_match.start() :].strip()
    bounded = re.search(r"\bBOUNDED BY\b", body, flags=re.IGNORECASE)
    if bounded is not None:
        return body[bounded.start() :].strip()
    mod_match = re.search(r"\bMOD\s+", body, flags=re.IGNORECASE)
    if mod_match is not None:
        return body[mod_match.start() :].strip()
    return body


def _phenomenon_from_conus_for_text(for_text: str) -> str:
    """Map CONUS ``FOR …`` clause tokens to IWXXM phenomenon codes."""
    upper = for_text.upper()
    if "ICE" in upper:
        return "MOD_ICE"
    if "TURB" in upper:
        return "MOD_TURB"
    if "IFR" in upper or "VIS" in upper:
        return "SFC_VIS"
    if "MTN" in upper and "OBSC" in upper:
        return "MT_OBSC"
    return _detect_phenomenon(for_text, _AIR_PHENOMENA)


def _parse_frzlvl_section(text: str) -> dict[str, Any]:
    """Parse standalone ``FRZLVL...`` subsection into structured IR."""
    section: dict[str, Any] = {"isopleths": []}
    ranging = _FRZLVL_RANGING.search(text)
    if ranging is not None:
        section["ranging_from"] = ranging.group("from").upper()
        section["ranging_to"] = int(ranging.group("to"))
    multi = _MULT_FRZLVL.search(text)
    if multi is not None:
        section["multiple_levels"] = True
        section["multi_lo"] = int(multi.group("lo"))
        section["multi_hi"] = int(multi.group("hi"))
    else:
        section["multiple_levels"] = False
    for match in _FRZLVL_ALG.finditer(text):
        section["isopleths"].append(
            {
                "alt": match.group("alt").upper(),
                "boundary": match.group("boundary").strip(),
            }
        )
    return section


def _try_parse_conus_airmet(text: str) -> dict[str, Any] | None:
    """Parse CONUS/Hawaii ``AIRMET <series> UPDT`` bulletin when ICAO header absent."""
    match = _CONUS_AIRMET.match(text)
    if match is None:
        return None
    until_day, until_hour, until_minute = _parse_until_token(match.group("until"))
    issue_day, issue_hour, issue_minute = until_day, until_hour, until_minute
    if match.group("issue"):
        issue_day, issue_hour, issue_minute = _parse_valid(match.group("issue"))
    elif match.group("wmo_time"):
        issue_day, issue_hour, issue_minute = _parse_valid(match.group("wmo_time"))
    fir = (match.group("faa_zone") or match.group("wmo_cccc") or "KKCI").upper()
    mwo = (match.group("wmo_cccc") or "KKCI").upper()
    body = _strip_conus_airmet_lead(match.group("body").strip())
    return {
        "fir": fir,
        "mwo": mwo,
        "sequence": int(match.group("upd")),
        "valid_from_day": issue_day,
        "valid_from_hour": issue_hour,
        "valid_from_minute": issue_minute,
        "valid_to_day": until_day,
        "valid_to_hour": until_hour,
        "valid_to_minute": until_minute,
        "phenomenon": _phenomenon_from_conus_for_text(match.group("for_text")),
        "fir_name": fir,
        "conus_series": match.group("series").upper(),
        "conus_update": int(match.group("upd")),
        "conus_for_text": match.group("for_text").strip(),
        "header_style": "conus_updt",
        "body": body,
    }


def _split_airmet_areas(body: str) -> list[str]:
    """Split AND-joined multi-area AIRMET bodies (NWSI 10-811 §7.3)."""
    segments = [segment.strip() for segment in _AIR_AREA_BOUNDARY.split(body) if segment.strip()]
    return segments if len(segments) > 1 else [body]


def _airmet_area_ir(segment: str, *, default_phenomenon: str | None = None) -> dict[str, Any]:
    """Parse one geographic AIRMET subsection into a minimal IR fragment."""
    area: dict[str, Any] = {
        "phenomenon": default_phenomenon or _detect_phenomenon(segment, _AIR_PHENOMENA),
    }
    _enrich_hazard_body(area, segment)
    return area


def _parse_airmet_outlook(outlook_text: str, *, default_phenomenon: str) -> dict[str, Any]:
    """Parse ``OTLK VALID`` outlook block (CONUS/Hawaii AIRMET bulletin §7.3 item 10)."""
    match = _OTLK_VALID.search(outlook_text)
    if match is None:
        raise ValueError("unable to parse AIRMET outlook valid period")
    from_hhmm = match.group("from")
    to_hhmm = match.group("to")
    tail = outlook_text[match.end() :].strip()
    if tail.startswith("..."):
        tail = tail[3:].strip()
    outlook = _airmet_area_ir(tail, default_phenomenon=default_phenomenon)
    outlook["valid_from_hour"] = int(from_hhmm[0:2])
    outlook["valid_from_minute"] = int(from_hhmm[2:4])
    outlook["valid_to_hour"] = int(to_hhmm[0:2])
    outlook["valid_to_minute"] = int(to_hhmm[2:4])
    return outlook


def _apply_airmet_area_to_ir(ir: dict[str, Any], area: dict[str, Any]) -> None:
    """Merge parsed area fields onto the root AIRMET IR."""
    for key, value in area.items():
        ir[key] = value


def _parse_convective_sigmet(text: str) -> dict[str, Any] | None:
    """Parse US ``CONVECTIVE SIGMET`` body (WST / #919 M11)."""
    match = _CONVECTIVE_SIGMET.match(text)
    if match is None:
        return None
    body = match.group("body")
    tag = match.group("tag").upper()
    unit = (match.group("unit") or "MKCC").upper()
    to_d, to_h, to_m = _parse_until_token(match.group("until"))
    # Active period ends at UNTIL; issue ~2h earlier (NWS convective convention).
    from_h = to_h - 2
    from_d = to_d
    from_m = to_m
    if from_h < 0:
        from_h += 24
        from_d = max(1, from_d - 1)
    states = " ".join(match.group("states").upper().split())
    ir: dict[str, Any] = {
        "ir_version": 1,
        "product": "SIGMET",
        "fir": unit,
        "mwo": "KKCI",
        "sequence": 0,
        "valid_from_day": from_d,
        "valid_from_hour": from_h,
        "valid_from_minute": from_m,
        "valid_to_day": to_d,
        "valid_to_hour": to_h,
        "valid_to_minute": to_m,
        "convective": True,
        "convective_tag": tag,
        "affected_states": states,
        "fir_name": f"{unit} FIC",
        "raw": text,
        "us_sigmet_hazard": {
            "href": _NWS_SIGMET_AREA_TS,
            "tag": tag,
        },
    }
    area_mov = _AREA_TS_MOV.search(body)
    if area_mov is not None:
        ir["motion_dir_deg"] = int(area_mov.group("dir"))
        ir["motion_speed_kt"] = int(area_mov.group("spd"))
    top = _TOP_FL.search(body)
    if top is not None:
        ir["top_fl"] = int(top.group("fl"))
        if "ABV" in top.group(0).upper():
            ir["top_qualifier"] = "ABV"
        elif "BLW" in top.group(0).upper():
            ir["top_qualifier"] = "BLW"
    elif re.search(r"\bTOPS\s+TO\s+FL(?P<fl>\d{2,3})\b", body, re.I):
        fl_m = re.search(r"\bTOPS\s+TO\s+FL(?P<fl>\d{2,3})\b", body, re.I)
        if fl_m is not None:
            ir["top_fl"] = int(fl_m.group("fl"))
            ir["top_qualifier"] = "TO"
    vor_geometry = parse_vor_reference_geometry(f"FROM {body.split('AREA', 1)[0]}")
    if vor_geometry is not None:
        ir["geometry"] = vor_geometry
    return ir


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
    conv = _parse_convective_sigmet(text)
    if conv is not None:
        if ahl_tt is not None:
            conv["ahl_tt"] = ahl_tt
        return conv
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
    elif "SHANWICK OCEANIC FIR" in upper_body:
        fir_name = "SHANWICK OCEANIC FIR"
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
    conus = _try_parse_conus_airmet(text)
    if conus is not None:
        body = conus.pop("body")
        ir: dict[str, Any] = {
            "ir_version": 1,
            "product": "AIRMET",
            "raw": text,
            **conus,
        }
    else:
        match = _AIRMET.match(text)
        if match is None:
            raise ValueError("unable to parse AIRMET header")

        body = match.group("body")
        from_d, from_h, from_m = _parse_valid(match.group("from"))
        to_d, to_h, to_m = _parse_valid(match.group("to"))
        ir = {
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
    main_body, outlook_body = _split_airmet_main_and_outlook(body)
    hazard_body, frzlvl_body = _split_frzlvl_section(main_body)
    if ahl_tt is not None:
        ir["ahl_tt"] = ahl_tt
    gfa_code = _detect_ca_gfa_phenomenon(hazard_body)
    if gfa_code is not None:
        ir["ca_gfa_phenomenon"] = gfa_code
        structured = _parse_ca_gfa_structured(hazard_body, gfa_code)
        if structured is not None:
            ir["ca_gfa_structured"] = structured
    chart = _GFA_CHART.search(hazard_body)
    if chart is not None:
        ir["gfa_chart_id"] = chart.group(1).upper()
    area_segments = _split_airmet_areas(hazard_body)
    if len(area_segments) > 1:
        areas = [_airmet_area_ir(segment, default_phenomenon=str(ir["phenomenon"])) for segment in area_segments]
        ir["areas"] = areas
        _apply_airmet_area_to_ir(ir, areas[0])
    else:
        _enrich_hazard_body(ir, hazard_body)
    if frzlvl_body is not None:
        ir["frzlvl_section"] = _parse_frzlvl_section(frzlvl_body)
    if outlook_body is not None:
        outlook = _parse_airmet_outlook(outlook_body, default_phenomenon=str(ir["phenomenon"]))
        outlook["valid_from_day"] = ir["valid_from_day"]
        if outlook["valid_to_hour"] < outlook["valid_from_hour"] or (
            outlook["valid_to_hour"] == outlook["valid_from_hour"]
            and outlook["valid_to_minute"] < outlook["valid_from_minute"]
        ):
            outlook["valid_to_day"] = ir["valid_to_day"] + 1
        else:
            outlook["valid_to_day"] = ir["valid_to_day"]
        ir["outlook"] = outlook
    _attach_us_airmet_hazard(ir)
    return ir


__all__ = ["parse_airmet", "parse_sigmet"]
