"""SIGMET / AIRMET TAC → IR parsers (F6.d annex3 path)."""

from __future__ import annotations

# Imports/constants consumed by exec'd part bodies.
import math
import re
from typing import Any, cast

from tac2iwxxm.geometry.reference_point import parse_vor_reference_geometry
from tac2iwxxm.slot_builders.sigmet_body import (
    compound_movement_degrees,
    flight_information_region_name,
    unwrap_wrapped_coordinates,
    use_volcanic_ash_locations,
    without_cancellation_remark,
)

_SIGMET = re.compile(
    r"^(?:(?P<fir>[A-Z]{4})(?:\s+(?P<fir_extra>(?:[A-Z]{4}\s+)+))?\s*)?"
    r"SIGMET\s+"
    r"(?P<seq>(?:[A-Z]+\s+\d+|[A-Z]?\d+))\s+VALID\s+"
    r"(?P<from>\d{6})/(?P<to>\d{6})\s+(?P<mwo>[A-Z]{4})\s*-\s*(?P<body>.*)$",
    re.DOTALL | re.IGNORECASE,
)

_BODY_FIR = re.compile(r"\b(?P<fir>[A-Z]{4})\b(?=\s+\S+\s+FIR\b)", re.IGNORECASE)

_AIRMET = re.compile(
    r"^(?P<fir>[A-Z]{4})\s+AIRMET\s+"
    r"(?P<seq>(?:[A-Z]+\s+\d+|[A-Z]?\d+))\s+VALID\s+"
    r"(?P<from>\d{6})/(?P<to>\d{6})\s+(?P<mwo>[A-Z]{4})\s*-\s*(?P<body>.*)$",
    re.DOTALL | re.IGNORECASE,
)

_CNL = re.compile(
    r"\bCNL\s+(?:SIGMET|AIRMET)\s+(?P<cnl_seq>(?:[A-Z]+\s+\d+|[A-Z]?\d+))\s+"
    r"(?:VALID\s+)?"
    r"(?P<cnl_from>\d{6})/(?P<cnl_to>\d{6})\b",
    re.IGNORECASE | re.DOTALL,
)

_CNL_INCOMPLETE = re.compile(
    r"\bCNL\s+(?:SIGMET|AIRMET)\s+(?:[A-Z]+\s+\d+|[A-Z]?\d+)\b",
    re.IGNORECASE,
)

_SIGA0_LINE = re.compile(r"^SIGA0[A-Z0-9]*\s*$", re.IGNORECASE)

_CNL_FIR_MOVED = re.compile(r"\b(?:AND|MOV)\s+TO\s+FIR\b", re.IGNORECASE)

_AHL_PREFIX = re.compile(
    r"^(?P<tt>[A-Z]{2})(?P<aa>[A-Z]{2})(?P<ii>(?=[A-Z0-9]*\d)[A-Z0-9]{2})\s+"
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
    r"(?P<lat_hemi>[NS])(?P<lat_deg>\d{2})(?P<lat_min>\d{2})(?:\d{2})?\s+"
    r"(?P<lon_hemi>[EW])(?P<lon_deg>\d{3})(?P<lon_min>\d{2})(?:\d{2})?\b",
    re.IGNORECASE,
)

_TC_OBS_PSN = re.compile(
    r"\bTC\s+[A-Z][A-Z0-9-]*\s+PSN\s+"
    r"(?P<lat_hemi>[NS])(?P<lat_deg>\d{2})(?P<lat_min>\d{2})(?:\d{2})?\s+"
    r"(?P<lon_hemi>[EW])(?P<lon_deg>\d{3})(?P<lon_min>\d{2})(?:\d{2})?\b",
    re.IGNORECASE,
)

_MOV = re.compile(
    r"\bMOV\s+(?P<dir>NNE|ENE|ESE|SSE|SSW|WSW|WNW|NNW|NE|SE|SW|NW|N|E|S|W)"
    r"(?:\s+(?P<spd>\d+)\s*(?P<unit>KT|KM/?H|MPS))?(?=\s|\Z|=)",
    re.IGNORECASE,
)

_LINE_SIDE_OFFSET_DEG = 0.05

_LINE_SIDE = re.compile(
    r"\b(?P<side>NNE|ENE|ESE|SSE|SSW|WSW|WNW|NNW|NE|SE|SW|NW|N|E|S|W)\s+OF\s+LINE\b",
    re.IGNORECASE,
)

_LINE_WIDTH = re.compile(r"\b(?P<width>\d+)\s*(?P<unit>NM|KM)\s+WID\s+LINE\b", re.IGNORECASE)

_LINE_SPAN = re.compile(
    r"\bLINE\b(?P<body>.*?)(?=\bSFC/|\bFL\d|\bTOP\b|\bMOV\b|\bSTNR\b|\bNC\b|\bWKN\b|\bINTSF\b|=|$)",
    re.IGNORECASE | re.DOTALL,
)

_AREA_TS_MOV = re.compile(
    r"\bAREA\s+TS\s+MOV\s+FROM\s+(?P<dir>\d{3})(?P<spd>\d{2,3})KT\b",
    re.IGNORECASE,
)

_CONVECTIVE_SIGMET = re.compile(
    r"^(?:SIG(?!MET)[A-Z0-9]*\s+)?"
    r"(?:(?P<unit>(?!SIG)[A-Z]{4})\s+(?:WST\s+\d{6}\s+)?)?"
    r"CONVECTIVE\s+SIGMET\s+(?P<tag>\S+)\s+"
    r"VALID\s+UNTIL\s+(?P<until>\d{4,6})Z\s+(?P<states>.+?)\s+FROM\s+(?P<body>.*)$",
    re.DOTALL | re.IGNORECASE,
)

_NWS_HAZARD_IFR = "http://nws.weather.gov/codes/NWSI10-811/HazardTypes/IFR"

_NWS_SIGMET_AREA_TS = "https://codes.nws.noaa.gov/NWSI-10-811/SIGMETWeatherPhenomena/AreaTS"

_TOP_FL = re.compile(r"\bTOP\s+(?:ABV\s+|BLW\s+)?FL(?P<fl>\d{2,3})\b", re.IGNORECASE)

_SE_BOX = re.compile(
    r"\bS OF N(?P<lat>\d{1,2})\s+AND E OF W(?P<lon>\d{1,3})\b",
    re.IGNORECASE,
)

_N_OF_S = re.compile(r"\bN OF S(?P<lat>\d{1,2})\b", re.IGNORECASE)

_POINT = re.compile(
    r"\b(?P<lat_hemi>[NS])(?P<lat_deg>\d{2})(?P<lat_min>\d{2})(?:\d{2})?\s+"
    r"(?P<lon_hemi>[EW])(?P<lon_deg>\d{3})(?P<lon_min>\d{2})(?:\d{2})?\b",
    re.IGNORECASE,
)

_FL_BAND = re.compile(r"\bFL(?P<lo>\d{2,3})/(?P<hi>\d{2,3})\b", re.IGNORECASE)

_FT_FL_LAYER = re.compile(
    r"\b(?P<ft>\d{3,4})(?P<unit>FT|M)/FL(?P<fl>\d{2,3})\b",
    re.IGNORECASE,
)

_SINGLE_FL = re.compile(r"\bFL(?P<fl>\d{2,3})\b", re.IGNORECASE)

_SFC_FL = re.compile(r"\bSFC/FL(?P<fl>\d{2,3})\b", re.IGNORECASE)

_WI_BLOCK = re.compile(
    r"\bWI\b(?P<body>.*?)(?=\bSFC/|\bTOP\b|\bMOV\b|\bSTNR\b|\bNC\b|\bWKN\b|\bINTSF\b|=|$)",
    re.IGNORECASE | re.DOTALL,
)

_NO_VA_EXP = re.compile(r"\bNO\s+VA\s+EXP\b", re.IGNORECASE)

_VA_ERUPTION = re.compile(
    r"\bVA\s+ERUPTION\s+(?P<name>MT\s+\w+)\s+PSN\s+"
    r"(?P<lat_hemi>[NS])(?P<lat_deg>\d{2})(?P<lat_min>\d{2})(?:\d{2})?\s+"
    r"(?P<lon_hemi>[EW])(?P<lon_deg>\d{3})(?P<lon_min>\d{2})(?:\d{2})?\b",
    re.IGNORECASE,
)

_VA_LOCATION = re.compile(
    r"(?:VA\s+CLD\s+)?"
    r"OBS\s+AT\s+(?P<obs_hhmm>\d{4})Z\s+WI\s+(?P<obs_wi>.*?)"
    r"(?:(?P<sfc_fl>SFC/FL\d{2,3})|(?P<fl_band>FL(?P<lo>\d{2,3})/(?P<hi>\d{2,3})))?"
    r"\s*(?P<intensity>NC|WKN|INTSF)?"
    r"(?:\s+FCST\s+AT\s+(?P<fcst_hhmm>\d{4})Z\s+WI\s+(?P<fcst_wi>.*?))?"
    r"(?=\s+AND\b|\s*=\s*$|$)",
    re.IGNORECASE | re.DOTALL,
)

_SIG_PHENOMENA = (
    ("OBSC TSGR", "OBSC_TSGR"),
    ("EMBD TSGR", "EMBD_TSGR"),
    ("FRQ TSGR", "FRQ_TSGR"),
    ("SQL TSGR", "SQL_TSGR"),
    ("OBSC TS", "OBSC_TS"),
    ("EMBD TS", "EMBD_TS"),
    ("FRQ TS", "FRQ_TS"),
    ("SQL TS", "SQL_TS"),
    ("OCNL TSGR", "OCNL_TSGR"),
    ("ISOL TSGR", "ISOL_TSGR"),
    ("OCNL TS", "OCNL_TS"),
    ("ISOL TS", "ISOL_TS"),
    ("SEV TURB", "SEV_TURB"),
    ("SEV ICE (FZRA)", "SEV_ICE_FZRA"),
    ("SEV ICE", "SEV_ICE"),
    ("SEV MTW", "SEV_MTW"),
    ("HVY DS", "HVY_DS"),
    ("HVY SS", "HVY_SS"),
    ("RDOACT CLD", "RDOACT_CLD"),
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
    ("SFC WSPD", "SFC_WIND"),
    ("SFC WIND", "SFC_WIND"),
    ("IFR", "SFC_VIS"),
    ("MTW", "MTW"),
    ("TS", "TS"),
)

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
    "NNE": 22.5,
    "NE": 45,
    "ENE": 67.5,
    "E": 90,
    "ESE": 112.5,
    "SE": 135,
    "SSE": 157.5,
    "S": 180,
    "SSW": 202.5,
    "SW": 225,
    "WSW": 247.5,
    "W": 270,
    "WNW": 292.5,
    "NW": 315,
    "NNW": 337.5,
}

_INTENSITY = {
    "WKN": "WEAKEN",
    "DECR": "WEAKEN",
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
