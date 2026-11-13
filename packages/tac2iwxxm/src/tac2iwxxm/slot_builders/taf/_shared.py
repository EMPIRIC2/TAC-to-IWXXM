"""TAF TAC → IR parser (F6.c annex3 path / F25 W3)."""

from __future__ import annotations

# Imports/constants consumed by exec'd part bodies.

import re

from typing import Any

from tac2iwxxm.bulletin import BulletinSplitError, parse_ahl

from tac2iwxxm.slot_builders.metar_speci import parse_statute_mile_fraction

from tac2iwxxm.taf_prob import is_unqualified_probability, probability_tempo_parts

from tac2iwxxm.time_anchor import iso_stamp

from tac2iwxxm.visibility_measure import (
    TAF_STATUTE_MILE_GROUP,
    prevailing_from_metre_group,
    prevailing_from_statute_miles,
)

_TAF = re.compile(
    r"^(?:TAF\s+)?(?:AMD\s+|COR\s+)?(?P<station>[A-Z][A-Z0-9]{3})\s+"
    r"(?P<issue>\d{6})Z\s+"
    r"(?:(?P<valid_from>\d{4})/(?P<valid_to>\d{4})\s+)?(?P<body>.*)$",
    re.DOTALL,
)

_TAF_NIL_ONLY = re.compile(
    r"^(?:TAF\s+)?(?:AMD\s+|COR\s+)?(?P<station>[A-Z][A-Z0-9]{3})\s+"
    r"(?P<issue>\d{6})Z\s+NIL\b(?P<body>.*)$",
    re.DOTALL,
)

_WIND = re.compile(r"\b(?P<dir>\d{3}|VRB)(?P<spd>\d{2,3})(?:G(?P<gust>\d{2,3}))?(?P<uom>KT|MPS)\b")

_VIS_M = re.compile(r"\b(?P<vis>\d{4})\b")

_VIS_SM = TAF_STATUTE_MILE_GROUP

_NCLWS = re.compile(r"\bWS(?P<height>\d{3})/(?P<dir>\d{3})(?P<spd>\d{2,3})KT\b")

_CLOUD = re.compile(r"\b(?P<amt>FEW|SCT|BKN|OVC)(?P<base>\d{3}|///)(?P<ctype>CB|TCU)?\b")

_NSC = re.compile(r"\bNSC\b")

_NCD = re.compile(r"\bNCD\b")

_SKC_CLR = re.compile(r"\b(?:SKC|CLR)\b")

_VV = re.compile(r"\bVV(?P<vv>\d{3}|///)(?![A-Z0-9/])")

_ALT_INHG = re.compile(r"\bA(?P<alt>\d{4})\b")

_NIL = re.compile(r"\bNIL\b")

_CNL = re.compile(r"\bCNL\b")

_CAVOK = re.compile(r"\bC(?:AVOK|\s+A\s+V\s+O\s+K)\b")

_BECMG = re.compile(
    r"\bBECMG\s+(?P<from>\d{4})/(?P<to>\d{4})\s+(?P<body>.*)$",
    re.DOTALL,
)

_TEMPO = re.compile(
    r"\b(?:TEMPO|EMPO)\s+(?P<from>\d{4})/(?P<to>\d{4})\s+(?P<body>.*)$",
    re.DOTALL,
)

_INTER = re.compile(
    r"\bINTER\s+(?P<from>\d{4})/(?P<to>\d{4})\s+(?P<body>.*)$",
    re.DOTALL,
)

_FM = re.compile(
    r"\bFM(?P<stamp>\d{6})\s+(?P<body>.*)$",
    re.DOTALL,
)

_WX_TOKEN = re.compile(
    r"(?<![A-Z0-9/])(?P<wx>"
    r"(?:\+|-|VC)?"
    r"(?:MI|PR|BC|DR|BL|SH|TS|FZ)?"
    r"(?:DZ|RA|SN|SG|PL|GR|GS|UP|BR|FG|FU|VA|DU|SA|HZ|PY|PO|SQ|FC|SS|DS|IC|TS)+"
    r"|VCSH"
    r")(?![A-Z0-9/])"
)

_CHANGE_TOKEN = (
    r"(?:"
    r"(?:PROB(?:30|40)\s+)?(?:TEMPO|EMPO)\s+\d{4}/\d{4}"
    r"|BECMG\s+\d{4}/\d{4}"
    r"|INTER\s+\d{4}/\d{4}"
    r"|FM\d{6}"
    r"|PROB(?:30|40)(?:\s+\d{4}/\d{4})?"
    r")"
)

_CHANGE_GROUP = re.compile(
    rf"\b{_CHANGE_TOKEN}\b.*?(?=\b{_CHANGE_TOKEN}\b|$)",
    re.DOTALL,
)

_VIS_KM = re.compile(r"\b(?P<vis>\d{1,3})KM\b")

_TAF3_MARKER = re.compile(r"\bTAF3(?:\s+VALID\s+TL\s+\d{6})?\b")

_RMK_T_SERIES = re.compile(r"\bT\s+((?:M?\d{2}\s+)+M?\d{2})\b")

_RMK_Q_SERIES = re.compile(r"\bQ\s+((?:\d{4}\s+)+\d{4})\b")

_NZ_2000FT_WIND = re.compile(r"\b2000FT\s+WIND\s+(?P<dir>\d{3}|VRB)(?P<spd>\d{2,3})(?:G(?P<gust>\d{2,3}))?KT\b")

_NZ_QNH_MNM_MAX = re.compile(r"\bQNH\s+MNM\s+(?P<mnm>\d{4})\s+MAX\s+(?P<max>\d{4})\b")

_CODE_CA_PRESENT_FORECAST_WEATHER = "https://dd.weather.gc.ca/today/aviation/iwxxm/code-ca/present_and_forecast_weather"
