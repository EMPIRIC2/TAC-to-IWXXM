"""Regex and constant tables for TAC decode.

[Corpus: product §F9]
"""

from __future__ import annotations

import re

from tac_decoding.decode_patterns_tables import (
    _CLOUD_AMOUNT,
    _CLOUD_TYPE,
    _QFE,
    _RUNWAY_BRAKING,
    _RUNWAY_CLEARED,
    _RUNWAY_DEPOSIT,
    _RUNWAY_DEPTH_CM,
    _RUNWAY_EXTENT,
    _RUNWAY_STATE,
    _RVR,
    _SIG_DIR_NAME,
    _TREND_TIME_LABEL,
    _US_LAKE,
    _US_STATE,
    _WX,
    _WX_DESCRIPTOR,
    _WX_INTENSITY,
    _WX_PHENOMENON,
)

_SUPPORTED = frozenset({"AIRMET", "METAR", "SIGMET", "SPECI", "TAF", "VAA", "TCA", "SWXA", "VONA"})
_ADVISORY_STRUCTURED = frozenset({"VAA", "TCA", "SWXA", "VONA"})

_WIND = re.compile(r"^(?P<dir>\d{3}|VRB)(?P<spd>\d{2,3})(?:G(?P<gust>\d{2,3}))?(?P<unit>KT|MPS)$")
_VIS_SM = re.compile(r"^(?P<mod>[PM])?(?P<val>\d{1,2})SM$")
_VIS_M = re.compile(r"^\d{4}$")
# Minimum visibility with compass sector (e.g. 1200NE) - after prevailing metres.
_VIS_MIN = re.compile(r"^(?P<vis>\d{4})(?P<dir>N|NE|E|SE|S|SW|W|NW)$")
_CLOUD = re.compile(r"^(?P<amt>FEW|SCT|BKN|OVC|SKC|CLR|NSC|NCD)(?P<hgt>\d{3})?(?P<ctype>CB|TCU)?(?P<unk>///)?$")
_WIND_VAR = re.compile(r"^(?P<a>\d{3})V(?P<b>\d{3})$")
_VIS_FRAC = re.compile(r"^(?P<num>\d)/(?P<den>\d)SM$")
_T_GROUP = re.compile(r"^T(?P<t>[01]\d{3})(?P<td>[01]\d{3})$")
_T_TEMP_ONLY = re.compile(r"^T(?P<body>[01]\d{3})$")
_SIX_HOUR_MAX = re.compile(r"^1(?P<body>[01]\d{3})$")
_SIX_HOUR_MIN = re.compile(r"^2(?P<body>[01]\d{3})$")
_DAY_MAX_MIN = re.compile(r"^4(?P<max>[01]\d{3})(?P<min>[01]\d{3})$")
_PRECIP_3_6H = re.compile(r"^6(?P<amt>\d{4}|/{4})$")
_PRECIP_24H = re.compile(r"^7(?P<amt>\d{4}|/{4})$")
_PRESSURE_TENDENCY = re.compile(r"^5(?P<char>[0-8])(?P<amt>\d{3})$")
_PRECIP_AMOUNT = re.compile(r"^P(?P<amt>\d{4})$")
_PEAK_WIND = re.compile(r"^(?P<dir>\d{3})(?P<spd>\d{2,3})/(?P<hh>\d{2})(?P<mm>\d{2})$")
_DENSITY_FT = re.compile(r"^(?P<n>-?\d+)FT$")
_WIND_ALOFT_FT = re.compile(r"^(?P<ft>\d{3,5})FT$")
_SEA_STATE = re.compile(r"^W(?P<wave>\d{1,2}|/{2,3})/S(?P<swell>\d)$")
_ICE_ACCRETION = re.compile(r"^I(?P<amt>\d{4})$")
_MISSING_TEMP_DEW = re.compile(r"^(?P<body>\d{2})///$")
_TEMP_MISSING_DEW = re.compile(r"^(?P<body>M?\d{2})/$")
_SHORT_PRECIP = re.compile(r"^P(?P<amt>\d{3})$")
_PP_PRECIP_MM = re.compile(r"^PP(?P<amt>\d{3})$")
_TX_DECIMAL = re.compile(r"^TX(?P<val>\d+(?:\.\d+)?)$")
_RWY_DESIGNATOR = re.compile(r"^RWY(?P<rw>\d{2}[LCR]?)$")
_LTG_TYPES = re.compile(r"^LTG(?P<types>[A-Z]+)$")
_PAST_HOUR = re.compile(r"^(?P<n>\d+)PAST$")
_FRAC_MILE = re.compile(r"^(?P<num>\d)/(?P<den>\d)$")
_BBB_CORRECTION = re.compile(r"^CC[A-Z]$")
_BBB_DELAYED = re.compile(r"^RR[A-Z]$")
_BBB_AMENDMENT = re.compile(r"^AA[A-Z]$")
_ELLIPSIS_HAZARD = re.compile(r"^(?P<head>TORNADOES|HAIL|WIND|GUSTS)\.\.\.(?P<tail>HAIL|WIND|GUSTS|TORNADOES)?$")
_IN_WIND_ELLIPSIS = re.compile(r"^IN\.\.\.WIND$|^\d+IN\.\.\.WIND$")
_CA_CLOUD_TYPE = "(?:TCU|CI|CS|CC|AC|AS|NS|SC|ST|SF|CU|CF|CB|FG)"
_CA_CLOUD_AMOUNTS = re.compile(rf"^(?:{_CA_CLOUD_TYPE}\d)+$")
_CA_CLOUD_ONE = re.compile(rf"^{_CA_CLOUD_TYPE}$")
_SIG_SFC_LAYER = re.compile(r"^SFC/(?P<alt>\d{3,5})(?P<unit>FT|M)$")
_SIG_NM = re.compile(r"^(?P<n>\d{1,3})NM$")
_RVR_MISSING = re.compile(r"^R(?P<rw>\d{2}[LCR]?)/+$")
_RVR_VARY = re.compile(r"^R(?P<rw>\d{2}[LCR]?)/(?P<a>[MP]?\d{4})V(?P<b>[MP]?\d{4})(?P<unit>FT)?(?:/(?P<trend>[UDN]))?$")
# Bare runway designator after WS (Annex 3 wind shear), e.g. R36R.
_WS_RUNWAY = re.compile(r"^R(?P<rw>\d{2}[LCR]?)$")
# CA / national TAF RMK trailer crumbs (known-ignored; not partial decode).
_TAF_RMK_TRAILER_WORD = frozenset(
    {
        "NXT",
        "NEXT",
        "FCST",
        "BY",
        "BASED",
        "ON",
        "AUTO",
        "OBS",
        "OBS.",
        "MIL",
    }
)
_TAF_RMK_NATIONAL = re.compile(r"^P[A-Z]{2,3}$|^PH[A-Z]{0,2}$")
_TAF_RMK_NEXT_TIME = re.compile(r"^\d{2}Z$|^\d{6}Z$|^\d{2}$")
_CLOUD_TYPE_8 = re.compile(r"^8/(?P<body>[0-9/]{3})$")
_MISSING_WIND_KT = re.compile(r"^/{5}KT$")
_MISSING_QNH_SLASH = re.compile(r"^Q/{4}$")
_MISSING_PRESS_TEND = re.compile(r"^5/{4}$")
_SOG_DEPTH = re.compile(r"^SOG$")
_SOG_VALUE = re.compile(r"^(?P<cm>\d{2})$")
_VIS_VARIABLE = re.compile(r"^(?P<lo>M?(?:\d+\s+)?\d+/\d+|\d+|M?\d+/\d+)V(?P<hi>\d+(?:/\d+)?)$")
# VIS VRB ranges: 1-2, 0-1/4, 1/4-3/4, 3/8-1 (CA remark form).
_VIS_VRB_RANGE = re.compile(r"^(?P<a>M?\d+(?:/\d+)?)-(?P<b>M?\d+(?:/\d+)?)$")
_WSHFT_MIN = re.compile(r"^(?P<mm>\d{2})$")
_CB_LOC = re.compile(r"^(?P<head>CB|TCU|TCUE)(?P<sep>[-/])(?P<dir>[A-Z;/-]+)$")
_OHD_CHAIN = re.compile(r"^(?:[A-Z]{1,3}-)*OHD(?:-[A-Z]{1,3})+$|^(?:[A-Z]{1,3}-){2,}[A-Z]{1,3}$")
_LAST_STFD = re.compile(
    r"^LAST(?:STFD)?OBS/(?:NXT|NEXT)(?P<rest>.*)$",
    re.IGNORECASE,
)
_NAVY_FS_FN = re.compile(r"^F[SN]\d{5}$")
_AU_TEMP_DIGIT = re.compile(r"^\d{2}$")
_AU_QNH_DIGIT = re.compile(r"^\d{4}$")
_TAF_AFT_HH = re.compile(r"^(?P<dd>\d{2})(?P<hh>\d{2})(?P<mm>\d{2})?$")
_MX_PRESS_9 = re.compile(r"^9(?P<body>\d{2})$")
_CIG_HUNDREDS = re.compile(r"^(?P<h>\d{3})$")
_VV = re.compile(r"^VV(?P<h>\d{3}|///)$")
_MISSING_CLOUD = re.compile(r"^(?P<slashes>/{4,}|(?:/+)(?P<ctype>CB|TCU))$")
_MM_AMOUNT = re.compile(r"^(?P<n>\d+(?:\.\d+)?)MM$")
_WX_TIME_NAME = {
    "RA": "Rain",
    "SN": "Snow",
    "DZ": "Drizzle",
    "SG": "Snow grains",
    "PL": "Ice pellets",
    "GR": "Hail",
    "GS": "Small hail",
    "UP": "Unknown precipitation",
    "TS": "Thunderstorm",
}
# Unhyphenated names need ≥3 letters; hyphenated runs may start at 2 (e.g. IN-FA).
_CYCLONE_NAME = re.compile(r"^(?:[A-Z]{3,}|[A-Z]{2,}(?:-[A-Z]{2,})+)$")
_CYCLONE_NAME_RESERVED = frozenset({"CENTRE", "CENTER"})
_TEMP = re.compile(r"^(?P<t>M?\d{2})/(?P<td>M?\d{2})$")
_ALT = re.compile(r"^A(?P<val>\d{4})$")
_QNH = re.compile(r"^Q(?P<val>\d{3,4})$")
_QNH_MEANING = "the altimeter setting reduced to mean sea level"
_TIME_Z = re.compile(r"^(?P<dd>\d{2})(?P<hh>\d{2})(?P<mm>\d{2})Z$")
_STATION = re.compile(r"^[A-Z][A-Z0-9]{3}$")
_TAF_VALID = re.compile(r"^(?P<d1>\d{2})(?P<h1>\d{2})/(?P<d2>\d{2})(?P<h2>\d{2})$")
_TAF_FM = re.compile(r"^FM(?P<dd>\d{2})(?P<hh>\d{2})(?P<mm>\d{2})$")
_TAF_PROB = re.compile(r"^PROB(?P<pct>\d{2})$")
_TAF_TX_TN = re.compile(r"^T(?P<which>[XN])(?P<sign>M)?(?P<tt>\d{2})/(?P<dd>\d{2})(?P<hh>\d{2})Z$")
_TAF_QNH_INS = re.compile(r"^QNH(?P<raw>\d{4})INS$")
_TAF_WS = re.compile(r"^WS(?P<hhh>\d{3})/(?P<dir>\d{3})(?P<spd>\d{2,3})KT$")
_TAF_TURB = re.compile(r"^5(?P<intensity>\d)(?P<base>\d{3}|/{3})(?P<thick>\d|/)$")
_TAF_ICING = re.compile(r"^6(?P<intensity>\d)(?P<base>\d{3}|/{3})(?P<thick>\d|/)$")
# METAR/SPECI trend time indicators (TL/AT/FM + HHMM) - distinct from TAF FMDDHHMM.
_TREND_TIME = re.compile(r"^(?P<kind>TL|AT|FM)(?P<hh>\d{2})(?P<mm>\d{2})$")
_SIG_VALID = re.compile(r"^(?P<d1>\d{2})(?P<h1>\d{2})(?P<m1>\d{2})/(?P<d2>\d{2})(?P<h2>\d{2})(?P<m2>\d{2})$")
_SIG_FL = re.compile(r"^FL(?P<fl>\d{2,3})$")
_SIG_WIND_RANGE = re.compile(r"^(?P<a>\d{2,3})-(?P<b>\d{2,3})(?P<unit>KT|KMH|MPS)$")
_SIG_TRAIL_DOTS = re.compile(r"^\.{3,}$")
# Vertical layer - ``SFC/FL550``, ``FL250/370``, or ``9000FT/FL290``.
_SIG_FL_LAYER = re.compile(r"^(?:SFC/FL(?P<sfc>\d{2,3})|FL(?P<a>\d{2,3})/(?:FL)?(?P<b>\d{2,3}))$")
_SIG_FT_LAYER = re.compile(r"^(?P<alt>\d{3,4})(?P<unit>FT|M)/FL(?P<fl>\d{2,3})$")
_LOOSE_AHL = re.compile(r"^(?P<ahl>[A-Z]{4}(?=[A-Z0-9]*\d)[A-Z0-9]{2})\s+(?P<cccc>[A-Z]{4})\s+(?P<yygggg>\d{6})\b")
_SIG_SPEED = re.compile(r"^(?P<spd>\d{1,3})(?P<unit>KT|KM/H|KMH|MPS)$")
_SIG_SPEED_UNIT = {
    "KT": "kt",
    "KMH": "kilometres per hour",
    "KM/H": "kilometres per hour",
    "MPS": "metres per second",
}
_SIG_LAT = re.compile(r"^(?P<hemi>[NS])(?P<deg>\d{1,2})(?P<min>\d{2})?$")
_SIG_LON = re.compile(r"^(?P<hemi>[EW])(?P<deg>\d{1,3})(?P<min>\d{2})?$")
_SIG_LATLON = re.compile(r"^(?P<lat>[NS]\d{4})(?P<lon>[EW]\d{5})$")
_SIG_SEQ = re.compile(r"^(?:(?P<letter_first>[A-Z])(?P<num_a>\d{1,2})|(?P<num_b>\d{1,3})(?P<letter_last>[A-Z])?)$")
_MOV_FROM = re.compile(r"^(?P<deg>\d{3})(?P<spd>\d{2,3})KT$")
_BEARING = "NNE|ENE|ESE|SSE|SSW|WSW|WNW|NNW|NE|NW|SE|SW|N|E|S|W"
_BOUNDARY_PART = re.compile(rf"^(?:(?P<dist>\d{{1,3}})(?P<dir>{_BEARING}))?(?P<fix>[A-Z]{{2,5}})?$")
_SIGMET_SERIES = frozenset(
    {
        "ALFA",
        "BRAVO",
        "CHARLIE",
        "DELTA",
        "ECHO",
        "FOXTROT",
        "GOLF",
        "HOTEL",
        "INDIA",
        "JULIET",
        "KILO",
        "LIMA",
        "MIKE",
        "NOVEMBER",
        "OSCAR",
        "PAPA",
        "QUEBEC",
        "ROMEO",
        "SIERRA",
        "TANGO",
        "UNIFORM",
        "VICTOR",
        "WHISKEY",
        "XRAY",
        "YANKEE",
        "ZULU",
    }
)
# Observation/forecast clock ``1600Z`` (hhmmZ) - distinct from METAR ``ddhhmmZ``.
_SIG_HHMMZ = re.compile(r"^(?P<hh>\d{2})(?P<mm>\d{2})Z$")
_SIG_DIR = frozenset(
    {
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    }
)
_TENDENCY_CHAR = {
    "0": "increasing, then decreasing",
    "1": "increasing, then steady",
    "2": "increasing",
    "3": "decreasing or steady, then increasing",
    "4": "steady",
    "5": "decreasing, then increasing",
    "6": "decreasing, then steady",
    "7": "decreasing",
    "8": "steady or increasing, then decreasing",
}
_CA_CLOUD_NAME = {
    "CI": "cirrus",
    "CS": "cirrostratus",
    "CC": "cirrocumulus",
    "AC": "altocumulus",
    "AS": "altostratus",
    "NS": "nimbostratus",
    "SC": "stratocumulus",
    "ST": "stratus",
    "SF": "stratus fractus",
    "CU": "cumulus",
    "CF": "cumulus fractus",
    "CB": "cumulonimbus",
    "TCU": "towering cumulus",
    "FG": "fog",
}
_RMK_WORD = {
    "TR": "Trace",
    "DSNT": "Distant",
    "DIST": "Distant",
    "PCPN": "Precipitation",
    "VRY": "Very",
    "LGT": "Light",
    "ALQDS": "All quadrants",
    "SH": "Showers",
    "CVCTV": "Convective",
    "EMBD": "Embedded",
    "CLD": "Cloud",
    "VIS": "Visibility",
    "FG": "Fog",
    "BANK": "Bank",
    "QUAD": "Quadrant",
    "DNWND": "Downwind",
    "LO": "Low",
    "TOPS": "Tops",
    "HR": "Hour",
    "LWR": "Lower",
    "ACSL": "Altocumulus standing lenticular",
    "SM": "Statute miles",
    "PAST": "Past",
    "ASOCTD": "Associated",
    "CONTRAILS": "Contrails",
    "VIRGA": "Virga",
    "LTNG": "Lightning",
    "MOD": "Moderate",
    "MOV": "Moving",
    "ICE": "Ice",
    "PRESRR": "Pressure rising rapidly",
    "PRESFR": "Pressure falling rapidly",
    "PWINO": "Present weather not available",
    "LTG": "Lightning",
    "AND": "And",
    "SFC": "Surface",
    "TWR": "Tower",
    "OHD": "Overhead",
    "BINOVC": "Breaks in overcast",
    "OCNL": "Occasional",
    "FRQ": "Frequent",
    "CONS": "Continuous",
    "APCH": "Approach",
    "IN": "In",
    "BIRD": "Bird",
    "HAZARD": "Hazard",
    "WIND": "Wind",
    "RWY": "Runway",
    "EST": "Estimated",
    "RAG": "Ragged",
    "INTMT": "Intermittent",
    "HYR": "Higher",
    "VRB": "Variable",
    "FOG": "Fog",
    "HZY": "Hazy",
    "ISOL": "Isolated",
    "RTD": "Delayed routine report",
    "RTS": "Remark text (unverified)",
    "MOVD": "Moved",
    "OBST": "Obstacles",
    "OBSC": "Obscured",
    "SKEID": "Skeid sensor",
    "LAST": "Last",
    "STFD": "Staffed",
    "OBS": "Observation",
    "NXT": "Next",
    "NEXT": "Next",
    "SOG": "Snow on ground",
}

__all__ = [
    "_ADVISORY_STRUCTURED",
    "_ALT",
    "_AU_QNH_DIGIT",
    "_AU_TEMP_DIGIT",
    "_BBB_AMENDMENT",
    "_BBB_CORRECTION",
    "_BBB_DELAYED",
    "_BEARING",
    "_BOUNDARY_PART",
    "_CA_CLOUD_AMOUNTS",
    "_CA_CLOUD_NAME",
    "_CA_CLOUD_ONE",
    "_CA_CLOUD_TYPE",
    "_CB_LOC",
    "_CIG_HUNDREDS",
    "_CLOUD",
    "_CLOUD_AMOUNT",
    "_CLOUD_TYPE",
    "_CLOUD_TYPE_8",
    "_CYCLONE_NAME",
    "_CYCLONE_NAME_RESERVED",
    "_DAY_MAX_MIN",
    "_DENSITY_FT",
    "_ELLIPSIS_HAZARD",
    "_FRAC_MILE",
    "_ICE_ACCRETION",
    "_IN_WIND_ELLIPSIS",
    "_LAST_STFD",
    "_LOOSE_AHL",
    "_LTG_TYPES",
    "_MISSING_CLOUD",
    "_MISSING_PRESS_TEND",
    "_MISSING_QNH_SLASH",
    "_MISSING_TEMP_DEW",
    "_MISSING_WIND_KT",
    "_MM_AMOUNT",
    "_MOV_FROM",
    "_MX_PRESS_9",
    "_NAVY_FS_FN",
    "_OHD_CHAIN",
    "_PAST_HOUR",
    "_PEAK_WIND",
    "_PP_PRECIP_MM",
    "_PRECIP_3_6H",
    "_PRECIP_24H",
    "_PRECIP_AMOUNT",
    "_PRESSURE_TENDENCY",
    "_QFE",
    "_QNH",
    "_QNH_MEANING",
    "_RMK_WORD",
    "_RUNWAY_BRAKING",
    "_RUNWAY_CLEARED",
    "_RUNWAY_DEPOSIT",
    "_RUNWAY_DEPTH_CM",
    "_RUNWAY_EXTENT",
    "_RUNWAY_STATE",
    "_RVR",
    "_RVR_MISSING",
    "_RVR_VARY",
    "_RWY_DESIGNATOR",
    "_SEA_STATE",
    "_SHORT_PRECIP",
    "_SIGMET_SERIES",
    "_SIG_DIR",
    "_SIG_DIR_NAME",
    "_SIG_FL",
    "_SIG_FL_LAYER",
    "_SIG_FT_LAYER",
    "_SIG_HHMMZ",
    "_SIG_LAT",
    "_SIG_LATLON",
    "_SIG_LON",
    "_SIG_NM",
    "_SIG_SEQ",
    "_SIG_SFC_LAYER",
    "_SIG_SPEED",
    "_SIG_SPEED_UNIT",
    "_SIG_TRAIL_DOTS",
    "_SIG_VALID",
    "_SIG_WIND_RANGE",
    "_SIX_HOUR_MAX",
    "_SIX_HOUR_MIN",
    "_SOG_DEPTH",
    "_SOG_VALUE",
    "_STATION",
    "_SUPPORTED",
    "_TAF_AFT_HH",
    "_TAF_FM",
    "_TAF_ICING",
    "_TAF_PROB",
    "_TAF_QNH_INS",
    "_TAF_RMK_NATIONAL",
    "_TAF_RMK_NEXT_TIME",
    "_TAF_RMK_TRAILER_WORD",
    "_TAF_TURB",
    "_TAF_TX_TN",
    "_TAF_VALID",
    "_TAF_WS",
    "_TEMP",
    "_TEMP_MISSING_DEW",
    "_TENDENCY_CHAR",
    "_TIME_Z",
    "_TREND_TIME",
    "_TREND_TIME_LABEL",
    "_TX_DECIMAL",
    "_T_GROUP",
    "_T_TEMP_ONLY",
    "_US_LAKE",
    "_US_STATE",
    "_VIS_FRAC",
    "_VIS_M",
    "_VIS_MIN",
    "_VIS_SM",
    "_VIS_VARIABLE",
    "_VIS_VRB_RANGE",
    "_VV",
    "_WIND",
    "_WIND_ALOFT_FT",
    "_WIND_VAR",
    "_WSHFT_MIN",
    "_WS_RUNWAY",
    "_WX",
    "_WX_DESCRIPTOR",
    "_WX_INTENSITY",
    "_WX_PHENOMENON",
    "_WX_TIME_NAME",
]
