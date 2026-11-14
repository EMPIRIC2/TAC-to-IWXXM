"""VAA / TCA TAC → IR parsers (F6.f annex3 path)."""

from __future__ import annotations

# Imports/constants consumed by exec'd part bodies.
import re
from typing import Any

_FIELD_LINE = re.compile(r"^(?P<key>[A-Z0-9 /+]+?):\s*(?P<val>.*)$")

_DTG_SHORT = re.compile(r"(?P<yyyy>\d{4})(?P<mm>\d{2})(?P<dd>\d{2})/(?P<hh>\d{2})(?P<mi>\d{2})Z")

_PSN = re.compile(r"(?P<ns>[NS])(?P<lat>\d{4,5})\s+(?P<ew>[EW])(?P<lon>\d{5,6})")

_POINT = re.compile(r"(?P<ns>[NS])(?P<lat>\d{4})\s+(?P<ew>[EW])(?P<lon>\d{5})")

_ERUPTION_AT = re.compile(
    r"ERUPTION\s+AT\s+(?P<dtg>\d{8}/\d{4}Z)\s*(?P<rest>.*)$",
    re.IGNORECASE,
)

_DAY_HHMM = re.compile(r"(?P<dd>\d{2})/(?P<hh>\d{2})(?P<mi>\d{2})Z")

_MOV = re.compile(
    r"\bMOV\s+(?P<dir>NNE|ENE|ESE|SSE|SSW|WSW|WNW|NNW|NE|SE|SW|NW|N|E|S|W)"
    r"\s+(?P<spd>\d+)\s*(?P<unit>KT|KM/?H|MPS)\b",
    re.IGNORECASE,
)

_FL_BAND = re.compile(r"\bFL(?P<lo>\d{2,3})/(?P<hi>\d{2,3})\b", re.IGNORECASE)

_SFC_FL = re.compile(r"\bSFC/FL(?P<hi>\d{2,3})\b", re.IGNORECASE)

_CLOUD_CHUNK = re.compile(
    r"(?P<level>(?:FL\d{2,3}/\d{2,3}|SFC/FL\d{2,3}))\s+"
    r"(?P<body>.*?)(?=(?:FL\d{2,3}/\d{2,3}|SFC/FL\d{2,3}|NO\s+VA\s+EXP|$))",
    re.IGNORECASE | re.DOTALL,
)

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

_MOV_TCA = re.compile(
    r"(?P<dir>NNE|ENE|ESE|SSE|SSW|WSW|WNW|NNW|NE|SE|SW|NW|N|E|S|W)\s+"
    r"(?P<spd>\d+)\s*(?P<uom>KMH|KM/?H|KT|MPS)?",
    re.IGNORECASE,
)

_CB_WI = re.compile(
    r"WI\s+(?P<rad>\d+)\s*NM\s+OF\s+TC\s+CENTRE(?:\s+TOP\s+FL(?P<fl>\d+))?",
    re.IGNORECASE,
)

_INTST_MAP = {
    "INTSF": "INTENSIFY",
    "WKN": "WEAKEN",
    "NC": "NO_CHANGE",
}
