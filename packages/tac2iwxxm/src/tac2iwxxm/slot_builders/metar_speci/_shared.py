"""METAR/SPECI TAC → IR parser (F6.a annex3 path)."""

from __future__ import annotations

# Imports/constants consumed by exec'd part bodies.

import re

from typing import Any

from tac2iwxxm.recent_weather import accept_recent_code

from tac2iwxxm.visibility_measure import (
    METAR_STATUTE_MILE_GROUP,
    prevailing_from_metre_group,
    prevailing_from_statute_miles,
)

_CA_SURFACE_TYPES = frozenset({"METAR", "SPECI", "LWIS", "SAWR"})

_OBS_KEYWORD = re.compile(r"(?<![A-Za-z])(?:LWIS|SAWR|METAR|SPECI)\b", re.IGNORECASE)

_OTHER_PRODUCT = re.compile(
    r"(?im)^[ \t]*(?:TAF\b|(?:[A-Za-z]{4}[ \t]+)?(?:SIGMET|AIRMET)\b|VONA\b|"
    r"VA[ \t]+ADVISORY\b|TC[ \t]+ADVISORY\b|SWX[ \t]+ADVISORY\b)"
)

_REPORT = re.compile(
    r"^(?P<rtype>LWIS|SAWR|METAR|SPECI)\s+(?:(?P<cor_pre>COR)\s+)?(?P<station>[A-Z][A-Z0-9]{3})\s+"
    r"(?P<ddhhmm>\d{6})Z\b(?P<body>.*)$",
    re.DOTALL,
)

_CA_DENSITY_ALT = re.compile(r"\bDENSITY\s+ALT(?:ITUDE)?\s+(?P<ft>\d{3,5})FT\b", re.I)

_CA_DENSITY_ALT_MISG = re.compile(r"\bDENSITY\s+ALT(?:ITUDE)?\s+MISG\b", re.I)

_CA_ICE_REMARK = re.compile(r"\bICE\s+(?P<intensity>TRC|LGT|MOD|SEV|HVY)\b", re.I)

_WIND = re.compile(r"\b(?P<dir>\d{3}|VRB)(?P<spd>\d{2,3})(?:G(?P<gust>\d{2,3}))?(?P<uom>KT|MPS)\b")

_VIS_SM = METAR_STATUTE_MILE_GROUP

_VIS_M = re.compile(r"\b(?P<vis>\d{4})\b")

_VIS_SM_NOT_OBS = re.compile(r"(?<![A-Z0-9/])////SM(?![A-Z0-9/])")

_VIS_M_NOT_OBS = re.compile(r"(?<![A-Z0-9/])////(?!SM)(?![A-Z0-9/])")

_CAVOK = re.compile(r"\bCAVOK\b")

_TEMP = re.compile(r"\b(?P<temp>M?\d{2})/(?P<dew>M?\d{2})\b")

_TEMP_NOT_OBS = re.compile(r"(?<![A-Z0-9/])/////(?![A-Z0-9/])")

_ALT_INHG = re.compile(r"\bA(?P<alt>\d{4})\b")

_ALT_NOT_OBS = re.compile(r"(?<![A-Z0-9])A////(?![A-Z0-9/])")

_QNH_HPA = re.compile(r"\bQ(?P<qnh>\d{3,4})\b")

_QNH_NOT_OBS = re.compile(r"(?<![A-Z0-9])Q////(?![A-Z0-9/])")

_CLOUD = re.compile(r"\b(?P<amt>FEW|SCT|BKN|OVC)(?P<base>\d{3}|///)(?P<ctype>CB|TCU)?\b")

_NIL = re.compile(r"\bNIL\b")

_AUTO = re.compile(r"\bAUTO\b")

_NOSIG = re.compile(r"\b(?:NOSIG|NOISG)\b")

_BARE_OBS = re.compile(
    r"^((?:COR\s+)?[A-Z][A-Z0-9]{3}\s+\d{6}Z(?:\s+COR)?\b.*?)(?:=\s*)?$",
    re.DOTALL | re.IGNORECASE,
)

_NSC = re.compile(r"\bNSC\b")

_NCD = re.compile(r"\bNCD\b")

_VV_NOT_OBS = re.compile(r"\bVV///(?![A-Z0-9/])")

_WIND_SECTOR = re.compile(r"\b(?P<ccw>\d{3})V(?P<cw>\d{3})\b")

_RVR_VAR = re.compile(
    r"\bR(?P<rwy>\d{2}[LCR]?)/(?P<min_op>[PM])?(?P<min>\d{4})V(?P<max_op>[PM])?(?P<max>\d{4})"
    r"(?:(?P<tend>[UDN])(?P<ft>FT)?|(?P<ft_ca>FT)(?:/(?P<tend_ca>[UDN]))?)?\b"
)

_RVR = re.compile(
    r"\bR(?P<rwy>\d{2}[LCR]?)/(?P<op>[PM])?(?P<val>\d{4})"
    r"(?:(?P<tend>[UDN])(?P<ft>FT)?|(?P<ft_ca>FT)(?:/(?P<tend_ca>[UDN]))?)?\b"
)

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

_WX_TOKEN = re.compile(
    r"(?<![A-Z0-9/])(?P<wx>//|"
    r"(?:\+|-|VC)?"
    r"(?:MI|PR|BC|DR|BL|SH|TS|FZ)?"
    r"(?:DZ|RA|SN|SG|PL|GR|GS|UP|BR|FG|FU|VA|DU|SA|HZ|PY|PO|SQ|FC|SS|DS|TS)+"
    r"|VCSH"
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

_WSHFT = re.compile(r"\bWSHFT\s+(?P<hhmm>\d{4})(?P<fropa>\s+FROPA)?\b")

_RMK_T = re.compile(r"\bT(?P<tsign>[01])(?P<tttt>\d{3})(?P<dsign>[01])(?P<dddd>\d{3})\b")

_RMK_P = re.compile(r"\bP(?P<p>\d{4})\b")

_RMK_MAX_6H = re.compile(r"\b1(?P<sign>[01])(?P<ttt>\d{3})\b")

_RMK_MIN_6H = re.compile(r"\b2(?P<sign>[01])(?P<ttt>\d{3})\b")

_RMK_MAXMIN_24H = re.compile(r"\b4(?P<msign>[01])(?P<mttt>\d{3})(?P<nsign>[01])(?P<nttt>\d{3})\b")

_RMK_PRECIP_6 = re.compile(r"\b6(?P<p>\d{4})\b")

_RMK_PRECIP_7 = re.compile(r"\b7(?P<p>\d{4})\b")

_COR_AFTER_TIME = re.compile(r"^\s*COR\b\s*")

_OBS_SYSTEM_HREF = "https://codes.nws.noaa.gov/FMH-1/ObservingSystemType/AO{ao}"

_FREQ_HREF = "https://codes.nws.noaa.gov/FMH-1/LightningFrequency/{code}"

_TYPE_HREF = "https://codes.nws.noaa.gov/FMH-1/LightningType/{code}"

_DIST_HREF = "https://codes.nws.noaa.gov/FMH-1/QualitativeDistance/{code}"

_PRECIP_ELEMENT_HREF = "https://codes.nws.noaa.gov/FMH-1/StatisticallyProcessedWeatherElement/PRECIPITATION"

_PRES_CHANGE_HREF = "https://codes.nws.noaa.gov/FMH-1/PressureChangingRapidly/{code}"

_PRES_CHANGE = re.compile(r"\bPRES(?P<dir>FR|RR)\b")

_CONTRAILS = re.compile(r"\bCONTRAILS?\b")

_AURORA = re.compile(r"\bAURORA\b")

_NOSPECI = re.compile(r"\bNOSPECI\b")

_MAINTENANCE = re.compile(r"(?:^|\s)\$(?=\s|$)")

_RECENT_WX = re.compile(
    r"\b(?P<wx>FZRA|FZDZ|SHRA|SHSN|SHGR|SHGS|TS|DZ|RA|SN|SG|IC|PL|GR|GS|UP)"
    r"(?:B(?P<b>\d{2,4})(?:E(?P<e>\d{2,4}))?|E(?P<e_only>\d{2,4}))\b"
)

_RECENT_BODY = re.compile(r"(?<![A-Z0-9])(?P<wx>RE[A-Z]{2,8})(?![A-Z0-9])")

_LTG_FREQ_CODES = {"OCNL": "OCCASIONAL", "FRQ": "FREQUENT", "CONS": "CONTINUOUS"}

_LTG_DIST_CODES = {"DSNT": "DISTANT", "VC": "VICINITY"}

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

_LTG_REMARK = re.compile(
    r"\b(?:(?P<freq>OCNL|FRQ|CONS)\s+)?"
    r"LTG(?P<type>(?:IC|CC|CG)*)"
    r"(?:\s+(?P<dist>DSNT|VC))?"
    r"(?:\s+(?P<sector>ALQDS|(?:N|NE|E|SE|S|SW|W|NW)(?:-(?:N|NE|E|SE|S|SW|W|NW))*))?"
    r"\b"
)

_SNINCR = re.compile(r"\bSNINCR\s+(?P<incr>\d{1,2})/(?P<depth>\d{1,2})\b")

_SKY_TYPES = re.compile(r"\b8/(?P<cl>[0-9/])(?P<cm>[0-9/])(?P<ch>[0-9/])(?![0-9A-Za-z/])")

_CONVECTIVE = re.compile(
    r"\b(?P<ctype>CBMAM|CB|TCU|TS)"
    r"(?:\s+(?P<dist>DSNT|VC|OHD|OVHD))?"
    r"(?:\s+(?P<sector>ALQDS|(?:N|NE|E|SE|S|SW|W|NW)(?:-(?:N|NE|E|SE|S|SW|W|NW))*))?"
    r"(?:\s+MOV\s+(?P<mov>N|NE|E|SE|S|SW|W|NW))?"
    r"\b"
)

_HAIL_SIZE = re.compile(
    r"\bGR\s+(?:"
    r"(?P<below>LT|LESS(?:\s+THAN)?)\s+(?P<bfrac>\d/\d)"
    r"|(?P<whole>\d+)\s+(?P<frac>\d/\d)"
    r"|(?P<onlyfrac>\d/\d)"
    r"|(?P<onlywhole>\d+)"
    r")\b"
)

_SM_FRAC = r"(?:(?:\d+\s+)?\d/\d|\d+)"

_SECOND_LOC = re.compile(
    r"\b(?:CIG\s+(?P<cig>\d{3})\s+)?"
    r"(?:VIS\s+(?P<vis_lt>M)?(?P<vis>" + _SM_FRAC + r")\s+)?"
    r"(?P<loc>RWY\d{2}[LCR]?(?:\s+TDZ)?)\b"
)

_TWR_VIS = re.compile(r"\bTWR\s+VIS\s+(?P<lt>M)?(?P<vis>" + _SM_FRAC + r")\b")

_SECTOR_VIS = re.compile(
    r"\bVIS\s+(?P<lt>M)?(?P<vis>" + _SM_FRAC + r")(?!V)(?!\s+RWY)"
    r"\s*(?P<dir>N|NE|E|SE|S|SW|W|NW)\b"
)

_OBSCURATION = re.compile(r"\b(?P<wx>FU|HZ|BR|FG|VA|DU|SA|PY)\s+(?P<amt>FEW|SCT|BKN|OVC)(?P<base>\d{3})\b")

_CIG_VAR = re.compile(r"\bCIG\s+(?P<min>\d{3})V(?P<max>\d{3})\b")

_SKY_VAR = re.compile(r"\b(?P<a>FEW|SCT|BKN|OVC)(?:\d{3})?\s+V\s+(?P<b>FEW|SCT|BKN|OVC)\b")

_VIS_VAR = re.compile(r"\bVIS\s+(?P<lt>M)?(?P<min>" + _SM_FRAC + r")V(?P<max>" + _SM_FRAC + r")\b")

_CLOUD_AMOUNT_HREF = "http://codes.wmo.int/49-2/CloudAmountReportedAtAerodrome/{amt}"

_WX_4678_HREF = "http://codes.wmo.int/306/4678/{code}"

_SENSOR_NO_HREF = "https://codes.nws.noaa.gov/FMH-1/Sensor/{code}"

_SENSOR_NO_CODES = {
    "CHINO": "CEILING",
    "RVRNO": "RUNWAY_VISUAL_RANGE",
    "VISNO": "VISIBILITY",
    "FZRANO": "FREEZING_PRECIPITATION",
    "PNO": "PRECIPITATION",
    "PWINO": "PRESENT_WEATHER",
    "TSNO": "THUNDERSTORM",
}

_SENSOR_NO = re.compile(r"\b(?P<tok>" + "|".join(_SENSOR_NO_CODES) + r")\b")

_SNOW_ELEMENT_HREF = "https://codes.nws.noaa.gov/FMH-1/StatisticallyProcessedWeatherElement/SNOW"

_STAT_ACCUM_HREF = "http://codes.wmo.int/grib2/codeflag/4.10/1"

_BUFR_CLOUD_HREF = "http://codes.wmo.int/bufr4/codeflag/0-20-012/{code}"

_NIL_NOT_OBSERVABLE = "http://codes.wmo.int/common/nil/notObservable"

_CONVECTIVE_TYPE_HREF = "https://codes.nws.noaa.gov/FMH-1/ConvectiveCloudType/{code}"

_CONVECTIVE_TYPE_CODES = {
    "CB": "CUMULONIMBUS",
    "CBMAM": "CUMULONIMBUS_MAMMATUS",
    "TCU": "TOWERING_CUMULUS",
    "TS": "THUNDERSTORM",
}

_CONVECTIVE_DIST_CODES = {
    "DSNT": "DISTANT",
    "VC": "VICINITY",
    "OHD": "OVERHEAD",
    "OVHD": "OVERHEAD",
}

_CONSUMED_REMARK = re.compile(
    r"\bAO[12]\b|\bSLP\d{3}\b|\bPK\s+WND\s+\d{3}\d{2,3}/\d{4}\b|"
    r"\bWSHFT\s+\d{4}(?:\s+FROPA)?\b|"
    r"(?:\b(?:OCNL|FRQ|CONS)\s+)?LTG(?:IC|CC|CG)*"
    r"(?:\s+(?:DSNT|VC))?"
    r"(?:\s+(?:ALQDS|(?:N|NE|E|SE|S|SW|W|NW)(?:-(?:N|NE|E|SE|S|SW|W|NW))*))?\b|"
    r"\bSNINCR\s+\d{1,2}/\d{1,2}\b|"
    r"\b8/[0-9/]{3}(?![0-9A-Za-z/])|"
    r"\b(?:CBMAM|CB|TCU|TS)"
    r"(?:\s+(?:DSNT|VC|OHD|OVHD))?"
    r"(?:\s+(?:ALQDS|(?:N|NE|E|SE|S|SW|W|NW)(?:-(?:N|NE|E|SE|S|SW|W|NW))*))?"
    r"(?:\s+MOV\s+(?:N|NE|E|SE|S|SW|W|NW))?\b|"
    r"\bGR\s+(?:(?:LT|LESS(?:\s+THAN)?)\s+)?(?:\d+\s+)?\d/\d\b|"
    r"\bGR\s+\d+\b|"
    r"\b(?:CIG\s+\d{3}\s+)?(?:VIS\s+M?(?:(?:\d+\s+)?\d/\d|\d+)\s+)?RWY\d{2}[LCR]?(?:\s+TDZ)?\b|"
    r"\bTWR\s+VIS\s+M?(?:(?:\d+\s+)?\d/\d|\d+)\b|"
    r"\bVIS\s+M?(?:(?:\d+\s+)?\d/\d|\d+)(?!V)(?!\s+RWY)\s*(?:N|NE|E|SE|S|SW|W|NW)\b|"
    r"\bCIG\s+\d{3}V\d{3}\b|"
    r"\b(?:FEW|SCT|BKN|OVC)(?:\d{3})?\s+V\s+(?:FEW|SCT|BKN|OVC)\b|"
    r"\bVIS\s+M?(?:(?:\d+\s+)?\d/\d|\d+)V(?:(?:\d+\s+)?\d/\d|\d+)\b|"
    r"\b(?:FU|HZ|BR|FG|VA|DU|SA|PY)\s+(?:FEW|SCT|BKN|OVC)\d{3}\b|"
    r"\b(?:" + "|".join(_SENSOR_NO_CODES) + r")\b|"
    r"\b4[01]\d{3}[01]\d{3}\b|\b[12][01]\d{3}\b|"
    r"\bP\d{4}\b|\b[67]\d{4}\b|"
    r"\bPRES(?:FR|RR)\b|\bCONTRAILS?\b|\bAURORA\b|\bNOSPECI\b|"
    r"(?:^|\s)\$(?=\s|$)|"
    r"\b(?:FZRA|FZDZ|SHRA|SHSN|SHGR|SHGS|TS|DZ|RA|SN|SG|IC|PL|GR|GS|UP)"
    r"(?:B\d{2,4}(?:E\d{2,4})?|E\d{2,4})\b"
)
