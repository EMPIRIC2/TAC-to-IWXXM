"""Lookup tables for TAC decode patterns.

[Corpus: product §F9]
"""

from __future__ import annotations

import re

_US_STATE = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "IA": "Iowa",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "MA": "Massachusetts",
    "MD": "Maryland",
    "ME": "Maine",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MO": "Missouri",
    "MS": "Mississippi",
    "MT": "Montana",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "NE": "Nebraska",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NV": "Nevada",
    "NY": "New York",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VA": "Virginia",
    "VT": "Vermont",
    "WA": "Washington",
    "WI": "Wisconsin",
    "WV": "West Virginia",
    "WY": "Wyoming",
    "DC": "District of Columbia",
}
_US_LAKE = {
    "LS": "Superior",
    "LM": "Michigan",
    "LH": "Huron",
    "LE": "Erie",
    "LO": "Ontario",
}
_SIG_DIR_NAME = {
    "N": "North",
    "NNE": "North-northeast",
    "NE": "Northeast",
    "ENE": "East-northeast",
    "E": "East",
    "ESE": "East-southeast",
    "SE": "Southeast",
    "SSE": "South-southeast",
    "S": "South",
    "SSW": "South-southwest",
    "SW": "Southwest",
    "WSW": "West-southwest",
    "W": "West",
    "WNW": "West-northwest",
    "NW": "Northwest",
    "NNW": "North-northwest",
}
_CLOUD_TYPE = {"CB": "cumulonimbus", "TCU": "towering cumulus"}
_TREND_TIME_LABEL = {
    "TL": "until",
    "AT": "at",
    "FM": "from",
}
_WX = re.compile(
    r"^(?P<int>\+|-|VC)?"
    r"(?P<desc>MI|PR|BC|DR|BL|SH|TS|FZ)?"
    r"(?P<phen>(?:DZ|RA|SN|SG|IC|PL|GR|GS|UP|BR|FG|FU|VA|DU|SA|HZ|PY|PO|SQ|FC|SS|DS)+)$"
)
# Runway visual range — R{rw}/{vis}[FT][/{U|D|N}] (e.g. R12/1000U, R11/1800FT/N).
_RVR = re.compile(r"^R(?P<rw>\d{2}[LCR]?)/(?P<vis>[MP]?\d{4})(?P<unit>FT)?(?:/(?P<trend>[UDN]))?(?P<trend2>[UDN])?$")
# Legacy runway state group: runway, deposit, extent, depth, friction (e.g. R19/290052).
_RUNWAY_STATE = re.compile(
    r"^R(?P<rw>\d{2}[LCR]?)/(?P<dep>[0-9/])(?P<ext>[1259/])(?P<depth>\d{2}|//)(?P<fric>\d{2}|//)$"
)
_RUNWAY_CLEARED = re.compile(r"^R(?P<rw>\d{2}[LCR]?)/CLRD(?P<fric>\d{2}|//)$")
_QFE = re.compile(r"^QFE(?P<mm>\d{3})(?:/(?P<hpa>\d{4}))?$")
_RUNWAY_DEPOSIT = {
    "0": "clear and dry",
    "1": "damp",
    "2": "wet or water patches",
    "3": "rime or frost",
    "4": "dry snow",
    "5": "wet snow",
    "6": "slush",
    "7": "ice",
    "8": "compacted or rolled snow",
    "9": "frozen ruts or ridges",
    "/": "deposit not reported",
}
_RUNWAY_EXTENT = {
    "1": "less than 10 percent covered",
    "2": "11 to 25 percent covered",
    "5": "26 to 50 percent covered",
    "9": "51 to 100 percent covered",
    "/": "coverage not reported",
}
_RUNWAY_DEPTH_CM = {92: 10, 93: 15, 94: 20, 95: 25, 96: 30, 97: 35, 98: 40}
_RUNWAY_BRAKING = {
    "91": "poor",
    "92": "medium to poor",
    "93": "medium",
    "94": "medium to good",
    "95": "good",
}

_WX_INTENSITY = {"+": "heavy", "-": "light", "VC": "in the vicinity"}
_WX_DESCRIPTOR = {
    "MI": "shallow",
    "PR": "partial",
    "BC": "patches of",
    "DR": "low drifting",
    "BL": "blowing",
    "SH": "showers of",
    "TS": "thunderstorm with",
    "FZ": "freezing",
}
_WX_PHENOMENON = {
    "DZ": "drizzle",
    "RA": "rain",
    "SN": "snow",
    "SG": "snow grains",
    "IC": "ice crystals",
    "PL": "ice pellets",
    "GR": "hail",
    "GS": "small hail",
    "UP": "unknown precipitation",
    "BR": "mist",
    "FG": "fog",
    "FU": "smoke",
    "VA": "volcanic ash",
    "DU": "widespread dust",
    "SA": "sand",
    "HZ": "haze",
    "PY": "spray",
    "PO": "dust whirls",
    "SQ": "squalls",
    "FC": "funnel cloud",
    "SS": "sandstorm",
    "DS": "duststorm",
}
_CLOUD_AMOUNT = {
    "FEW": "Few clouds",
    "SCT": "Scattered clouds",
    "BKN": "Broken clouds",
    "OVC": "Overcast",
    "SKC": "Sky clear",
    "CLR": "Sky clear",
    "NSC": "No significant cloud",
    "NCD": "No cloud detected",
}
