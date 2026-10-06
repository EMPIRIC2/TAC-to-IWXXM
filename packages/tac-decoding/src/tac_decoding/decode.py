"""TAC decode/annotate segments for the operator decode panel (F7 / #702).

Produces ordered ``code`` | explanation segments with character offsets, plus
explicit residuals for undecoded spans. VAA/TCA/SWXA/VONA use structured
``LABEL:`` fields (EV-030 / EV-099); leftover tokens stay explicit (G4).
"""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from typing import Protocol, cast

import msgspec

from tac_decoding.glossary import (
    explain_glossary_token,
    meaning_for,
    resolve_location_name,
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
_PRESSURE_TENDENCY = re.compile(r"^5(?P<char>[0-8])(?P<amt>\d{3})$")
_PRECIP_AMOUNT = re.compile(r"^P(?P<amt>\d{4})$")
_PEAK_WIND = re.compile(r"^(?P<dir>\d{3})(?P<spd>\d{2,3})/(?P<hh>\d{2})(?P<mm>\d{2})$")
_DENSITY_FT = re.compile(r"^(?P<n>-?\d+)FT$")
_PAST_HOUR = re.compile(r"^(?P<n>\d+)PAST$")
_FRAC_MILE = re.compile(r"^(?P<num>\d)/(?P<den>\d)$")
_BBB_CORRECTION = re.compile(r"^CC[A-Z]$")
_BBB_DELAYED = re.compile(r"^RR[A-Z]$")
_CA_CLOUD_TYPE = "(?:TCU|CI|CS|CC|AC|AS|NS|SC|ST|SF|CU|CF|CB)"
_CA_CLOUD_AMOUNTS = re.compile(rf"^(?:{_CA_CLOUD_TYPE}\d)+$")
_CA_CLOUD_ONE = re.compile(rf"^{_CA_CLOUD_TYPE}$")
_SIG_SFC_LAYER = re.compile(r"^SFC/(?P<alt>\d{3,5})(?P<unit>FT|M)$")
_SIG_NM = re.compile(r"^(?P<n>\d{1,3})NM$")
_RVR_MISSING = re.compile(r"^R(?P<rw>\d{2}[LCR]?)/+$")
_RVR_VARY = re.compile(r"^R(?P<rw>\d{2}[LCR]?)/(?P<a>[MP]?\d{4})V(?P<b>[MP]?\d{4})(?P<unit>FT)?$")
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
_CYCLONE_NAME = re.compile(r"^[A-Z]{3,}(?:-[A-Z]{2,})*$")
_TEMP = re.compile(r"^(?P<t>M?\d{2})/(?P<td>M?\d{2})$")
_ALT = re.compile(r"^A(?P<val>\d{4})$")
_QNH = re.compile(r"^Q(?P<val>\d{3,4})$")
_QNH_MEANING = "the altimeter setting reduced to mean sea level"
_TIME_Z = re.compile(r"^(?P<dd>\d{2})(?P<hh>\d{2})(?P<mm>\d{2})Z$")
_STATION = re.compile(r"^[A-Z][A-Z0-9]{3}$")
_TAF_VALID = re.compile(r"^(?P<d1>\d{2})(?P<h1>\d{2})/(?P<d2>\d{2})(?P<h2>\d{2})$")
_TAF_FM = re.compile(r"^FM(?P<dd>\d{2})(?P<hh>\d{2})(?P<mm>\d{2})$")
_TAF_PROB = re.compile(r"^PROB(?P<pct>\d{2})$")
# METAR/SPECI trend time indicators (TL/AT/FM + HHMM) - distinct from TAF FMDDHHMM.
_TREND_TIME = re.compile(r"^(?P<kind>TL|AT|FM)(?P<hh>\d{2})(?P<mm>\d{2})$")
_SIG_VALID = re.compile(r"^(?P<d1>\d{2})(?P<h1>\d{2})(?P<m1>\d{2})/(?P<d2>\d{2})(?P<h2>\d{2})(?P<m2>\d{2})$")
_SIG_FL = re.compile(r"^FL(?P<fl>\d{2,3})$")
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
}
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
# Runway visual range - R{rw}/{vis}{U|D|N}? (e.g. R12/1000U).
_RVR = re.compile(r"^R(?P<rw>\d{2}[LCR]?)/(?P<vis>[MP]?\d{4})(?P<trend>[UDN])?$")

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


def _signed_temp(raw: str) -> int:
    """
    Internal helper ``_signed_temp``.

    Parameters
    ----------
    raw : object
        Argument ``raw``.

    Returns
    -------
    object
        Return value.
    """
    return -int(raw[1:]) if raw.startswith("M") else int(raw)


def _fmt_qnh(raw: str) -> str:
    """
    Explain a QNH group and keep the pressure in hectopascals.

    Parameters
    ----------
    raw : str
        Digits from the ``Q`` group.

    Returns
    -------
    str
        Operator sentence for that group.
    """
    return f"QNH {int(raw)} hPa, {_QNH_MEANING}"


def _fmt_wind(m: re.Match[str], *, label: str) -> str:
    """
    Internal helper ``_fmt_wind``.

    Parameters
    ----------
    m : object
        Argument ``m``.
    label : object
        Argument ``label``.

    Returns
    -------
    object
        Return value.
    """
    direction = m.group("dir")
    speed = int(m.group("spd"))
    unit = "kt" if m.group("unit") == "KT" else "m/s"
    origin = "variable in direction" if direction == "VRB" else f"from {int(direction)}°"
    text = f"{label} {origin} at {speed} {unit}"
    gust = m.group("gust")
    if gust:
        text += f", gusting {int(gust)} {unit}"
    return text


def _fmt_time(m: re.Match[str], *, label: str) -> str:
    """
    Internal helper ``_fmt_time``.

    Parameters
    ----------
    m : object
        Argument ``m``.
    label : object
        Argument ``label``.

    Returns
    -------
    object
        Return value.
    """
    return f"{label} on day {int(m.group('dd'))} at {m.group('hh')}:{m.group('mm')} UTC"


def _fmt_vis_sm(m: re.Match[str], *, label: str) -> str:
    """
    Internal helper ``_fmt_vis_sm``.

    Parameters
    ----------
    m : object
        Argument ``m``.
    label : object
        Argument ``label``.

    Returns
    -------
    object
        Return value.
    """
    value = int(m.group("val"))
    prefix = {"P": "more than ", "M": "less than "}.get(m.group("mod") or "", "")
    plural = "s" if value != 1 else ""
    return f"{label} {prefix}{value} statute mile{plural}"


def _fmt_cloud(m: re.Match[str], *, forecast: bool) -> str:
    """
    Internal helper ``_fmt_cloud``.

    Parameters
    ----------
    m : object
        Argument ``m``.
    forecast : object
        Argument ``forecast``.

    Returns
    -------
    object
        Return value.
    """
    amount = _CLOUD_AMOUNT[m.group("amt")]
    if forecast:
        amount = f"Forecast {amount[0].lower()}{amount[1:]}"
    height = m.group("hgt")
    ctype = m.group("ctype")
    type_note = f" ({_CLOUD_TYPE[ctype]})" if ctype else ""
    if m.group("unk"):
        type_note = f"{type_note}, type not reported"
    if height:
        return f"{amount} at {int(height) * 100:,} ft{type_note}"
    return f"{amount}{type_note}"


def _fmt_wx(m: re.Match[str], *, forecast: bool) -> str:
    """
    Internal helper ``_fmt_wx``.

    Parameters
    ----------
    m : object
        Argument ``m``.
    forecast : object
        Argument ``forecast``.

    Returns
    -------
    object
        Return value.
    """
    parts: list[str] = []
    intensity = m.group("int")
    if intensity:
        parts.append(_WX_INTENSITY[intensity])
    descriptor = m.group("desc")
    if descriptor:
        parts.append(_WX_DESCRIPTOR[descriptor])
    phen = m.group("phen")
    parts.extend(_WX_PHENOMENON[phen[i : i + 2]] for i in range(0, len(phen), 2))
    phrase = " ".join(parts)
    label = "Forecast weather" if forecast else "Weather"
    if not phrase:
        return f"{label} group"
    return f"{label}: {phrase[0].upper()}{phrase[1:]}"


class DecodeSegment(msgspec.Struct, frozen=True):
    """
    One annotated TAC span for the Code | Explanation panel.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    start: int
    end: int
    code: str
    explanation: str


class DecodeResidual(msgspec.Struct, frozen=True):
    """
    Undecoded character span (explicit residuals - G4).

    Attributes
    ----------
    _ : object
        See implementation.
    """

    start: int
    end: int
    text: str


class DecodeResult(msgspec.Struct, frozen=True):
    """
    Result of :func:`decode_tac`.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    product: str
    segments: list[DecodeSegment] = msgspec.field(default_factory=list)
    residuals: list[DecodeResidual] = msgspec.field(default_factory=list)
    summary: str = ""


def _iter_tokens(tac: str) -> list[tuple[int, int, str]]:
    """
    Internal helper ``_iter_tokens``.

    Parameters
    ----------
    tac : object
        Argument ``tac``.

    Returns
    -------
    object
        Return value.
    """
    return [(m.start(), m.end(), m.group(0)) for m in re.finditer(r"=|[^\s=]+", tac)]


def _tenths_c(raw: str) -> str:
    """FMH-1 temperature in tenths, with a leading sign digit.

    Parameters
    ----------
    raw : str
        Four digits. ``0`` is positive and ``1`` is negative.

    Returns
    -------
    str
        Degrees Celsius with one decimal place.
    """
    sign = -1 if raw[0] == "1" else 1
    return f"{sign * int(raw[1:]) / 10:.1f}"


def _pressure_tendency(token: str) -> str | None:
    """FMH-1 group ``5appp``: characteristic and 3-hour change in tenths of hPa.

    Parameters
    ----------
    token : str
        One remarks group.

    Returns
    -------
    str | None
        The tendency in plain language, or None when the group is not ``5appp``.
    """
    match = _PRESSURE_TENDENCY.match(token)
    if match is None:
        return None
    amount = int(match.group("amt")) / 10
    return f"Pressure tendency: {_TENDENCY_CHAR[match.group('char')]}, change {amount:.1f} hPa in 3 hours"


def _precip_amount(token: str) -> str | None:
    """Hourly precipitation ``P####`` in hundredths of an inch. ``P0000`` is a trace.

    Parameters
    ----------
    token : str
        One remarks group.

    Returns
    -------
    str | None
        The amount in plain language, or None when the group is not ``P####``.
    """
    match = _PRECIP_AMOUNT.match(token)
    if match is None:
        return None
    hundredths = int(match.group("amt"))
    if hundredths == 0:
        return "Precipitation trace in the past hour"
    return f"Precipitation {hundredths / 100:.2f} inches in the past hour"


def _okta_phrase(kind: str, amount: str) -> str:
    """One Canadian remark cloud type and its coverage in oktas.

    Parameters
    ----------
    kind : str
        A two-letter cloud type, or ``TCU``.
    amount : str
        Coverage as a single digit of oktas.

    Returns
    -------
    str
        The type name and coverage.
    """
    count = int(amount)
    unit = "okta" if count == 1 else "oktas"
    return f"{_CA_CLOUD_NAME[kind]} {count} {unit}"


def _canadian_clouds(token: str) -> str | None:
    """Canadian remark clouds, either ``SF8`` or a run such as ``ST3CU1CI1``.

    Parameters
    ----------
    token : str
        One remarks group.

    Returns
    -------
    str | None
        The clouds in plain language, or None when the group is not a cloud run.
    """
    if _CA_CLOUD_AMOUNTS.match(token):
        parts = re.findall(rf"({_CA_CLOUD_TYPE})(\d)", token)
        return "Clouds: " + ", ".join(_okta_phrase(kind, amount) for kind, amount in parts)
    if _CA_CLOUD_ONE.match(token):
        return f"Cloud type ({_CA_CLOUD_NAME[token]})"
    return None


def _whole_miles(token: str, following: str) -> str | None:
    """The whole miles that sit in front of a fractional statute-mile group.

    Parameters
    ----------
    token : str
        A single digit from 1 to 9.
    following : str
        The next group, which must be a fractional mile.

    Returns
    -------
    str | None
        The whole-mile phrase, or None when the pair is not whole miles plus a fraction.
    """
    if not re.fullmatch(r"[1-9]", token):
        return None
    following_upper = following.upper()
    if not _VIS_FRAC.match(following_upper) and not _FRAC_MILE.match(following_upper):
        return None
    return f"Visibility {token} statute mile, plus the following fraction"


def _rvr_bound(raw: str) -> str:
    """A runway visual range limit, including a greater-than or less-than mark.

    Parameters
    ----------
    raw : str
        Digits, or the same digits with a leading ``P`` or ``M``.

    Returns
    -------
    str
        The limit, with ``more than`` or ``less than`` when marked.
    """
    if raw.startswith("P"):
        return f"more than {int(raw[1:])}"
    if raw.startswith("M"):
        return f"less than {int(raw[1:])}"
    return str(int(raw))


def _varying_rvr(token: str) -> str | None:
    """Runway visual range that varies, in metres or feet.

    Parameters
    ----------
    token : str
        One runway visual range group.

    Returns
    -------
    str | None
        The varying or unreported range, or None when the group is a single value.
    """
    missing = _RVR_MISSING.match(token)
    if missing:
        return f"Runway visual range runway {missing.group('rw')}: not reported"
    varying = _RVR_VARY.match(token)
    if varying is None:
        return None
    unit = "ft" if varying.group("unit") == "FT" else "m"
    return (
        f"Runway visual range runway {varying.group('rw')}: "
        f"varying from {_rvr_bound(varying.group('a'))} {unit} to {_rvr_bound(varying.group('b'))} {unit}"
    )


def _wx_clock(raw: str) -> str:
    """Minutes past the hour, or an hour and minute when four digits are present.

    Parameters
    ----------
    raw : str
        Two digits of minutes, or four digits of hour and minute.

    Returns
    -------
    str
        A clock phrase for that time.
    """
    if len(raw) == 4:
        return f"at {raw[:2]}:{raw[2:]}"
    return f"at {raw} minutes past the hour"


def _wx_began_or_ended(token: str) -> str | None:
    """One weather type, or several glued together, with began and ended times.

    Parameters
    ----------
    token : str
        A remarks group such as ``RAB19`` or ``RAE2055DZB08E10``.

    Returns
    -------
    str | None
        The begin and end times, or None when the group is not a weather-time chain.
    """
    pos = 0
    clauses: list[str] = []
    while pos < len(token):
        kind = next((name for name in _WX_TIME_NAME if token.startswith(name, pos)), None)
        if kind is None:
            return None
        pos += len(kind)
        edges: list[str] = []
        while pos < len(token) and token[pos] in "BE":
            word = "began" if token[pos] == "B" else "ended"
            pos += 1
            four = token[pos : pos + 4]
            two = token[pos : pos + 2]
            if len(four) == 4 and four.isdigit() and _wx_four_digits(token, pos):
                edges.append(f"{word} {_wx_clock(four)}")
                pos += 4
            elif len(two) == 2 and two.isdigit():
                edges.append(f"{word} {_wx_clock(two)}")
                pos += 2
            else:
                return None
        if not edges:
            return None
        sentence = f"{_WX_TIME_NAME[kind]} {edges[0]}"
        if len(edges) > 1:
            sentence += "".join(f" and {edge}" for edge in edges[1:])
        clauses.append(sentence)
    return ". ".join(clauses)


def _wx_four_digits(token: str, pos: int) -> bool:
    """True when four digits end the token, or a new edge or weather type follows.

    Parameters
    ----------
    token : str
        The full weather-time group.
    pos : int
        Index of the first of the four digits.

    Returns
    -------
    bool
        Whether those four digits are an hour and minute.
    """
    nxt = token[pos + 4 : pos + 6]
    if not nxt:
        return True
    if nxt[0] in "BE":
        return True
    return any(nxt.startswith(name) for name in _WX_TIME_NAME)


def _navaid_chain(token: str) -> str | None:
    """A hyphenated run of navaids with no distance, such as ``TRV-PBI``.

    Parameters
    ----------
    token : str
        One group from a convective ``FROM`` line.

    Returns
    -------
    str | None
        The navaids in order, or None when a part is not a navaid name.
    """
    parts = token.split("-")
    if len(parts) < 2 or any(part == "" for part in parts):
        return None
    if not all(re.fullmatch(r"[A-Z]{2,5}", part) for part in parts):
        return None
    return "Navaids " + " to ".join(parts)


def _in_convective_area(seen: dict[str, int]) -> bool:
    """True on the convective area line, after validity and before ``FROM``.

    Parameters
    ----------
    seen : dict[str, int]
        Tokens already accepted while decoding this report.

    Returns
    -------
    bool
        Whether a state or lake abbreviation is part of the area line.
    """
    return bool(
        seen.get("convective")
        and seen.get("until")
        and not seen.get("from_line")
        and not seen.get("area")
        and not seen.get("tops")
    )


def _coord_token(token: str) -> str:
    """Drop a polygon hyphen glued to a latitude or longitude.

    Parameters
    ----------
    token : str
        One coordinate group, with or without a trailing hyphen.

    Returns
    -------
    str
        The coordinate without a glued hyphen.
    """
    if len(token) > 1 and token.endswith("-"):
        bare = token[:-1]
        if _SIG_LAT.match(bare) or _SIG_LON.match(bare) or _SIG_LATLON.match(bare):
            return bare
    return token


def _boundary_points(token: str) -> str | None:
    """Explain a navaid boundary such as ``50WSW`` or ``MSS-30S``.

    Parameters
    ----------
    token : str
        One whitespace-delimited group.

    Returns
    -------
    str | None
        A plain-language boundary, or None when the group is not one.
    """
    parts = token.split("-")
    rendered: list[str] = []
    saw_distance = False
    for part in parts:
        match = _BOUNDARY_PART.match(part)
        if match is None:
            return None
        dist = match.group("dist")
        direction = match.group("dir")
        fix = match.group("fix")
        if dist and direction:
            saw_distance = True
            place = f" of {fix}" if fix else ""
            rendered.append(f"{int(dist)} nm {_SIG_DIR_NAME[direction]}{place}")
        elif fix and not dist:
            rendered.append(fix)
        else:
            return None
    if not saw_distance:
        return None
    return "Boundary " + " to ".join(rendered)


def _lat_lon_phrase(lat: str, lon: str) -> str | None:
    """Plain language for one glued latitude and longitude.

    Parameters
    ----------
    lat : str
        Latitude token such as ``N1346``.
    lon : str
        Longitude token such as ``W09652``.

    Returns
    -------
    str | None
        Both coordinates, or None when either half does not match.
    """
    lat_match = _SIG_LAT.match(lat)
    lon_match = _SIG_LON.match(lon)
    if lat_match is None or lon_match is None:
        return None
    lat_hemi = "North" if lat_match.group("hemi") == "N" else "South"
    lon_hemi = "East" if lon_match.group("hemi") == "E" else "West"
    lat_min = lat_match.group("min") or "00"
    lon_min = lon_match.group("min") or "00"
    return (
        f"Latitude {int(lat_match.group('deg'))}°{lat_min}' {lat_hemi[0]}, "
        f"longitude {int(lon_match.group('deg'))}°{lon_min}' {lon_hemi[0]}"
    )


def _explain_metar_speci(token: str, *, product: str, seen: dict[str, int]) -> str | None:
    """
    Internal helper ``_explain_metar_speci``.

    Parameters
    ----------
    token : object
        Argument ``token``.
    product : object
        Argument ``product``.
    seen : object
        Argument ``seen``.

    Returns
    -------
    object
        Return value.
    """
    upper = token.upper()
    if seen.get("density_alt"):
        seen["density_alt"] = 0
        if m := _DENSITY_FT.match(upper):
            return f"Density altitude {m.group('n')} ft"
    if seen.get("cig"):
        seen["cig"] = 0
        if m := _WIND_VAR.match(upper):
            return f"Ceiling varying from {int(m.group('a')) * 100} ft to {int(m.group('b')) * 100} ft"
    if upper in {"METAR", "SPECI"} and seen.get("rtype", 0) == 0:
        seen["rtype"] = 1
        label = "routine" if upper == "METAR" else "special"
        return f"Report type ({label} meteorological aerodrome report)"
    if upper == "COR":
        return "Correction indicator"
    if _BBB_CORRECTION.match(upper):
        return f"Correction ({upper})"
    if _BBB_DELAYED.match(upper):
        return f"Delayed report ({upper})"
    if upper == "NIL":
        return "Nil report (no observation)"
    if upper == "CAVOK":
        return "Ceiling and visibility OK"
    if upper == "NOSIG":
        seen["in_trend"] = 1
        return "No significant change expected"
    if upper == "TEMPO":
        seen["in_trend"] = 1
        return "Temporary fluctuations expected during the following period"
    if upper == "BECMG":
        seen["in_trend"] = 1
        return "Becoming, a gradual change during the following period"
    if upper == "NSW":
        return "No significant weather"
    if upper == "RMK":
        seen["rmk"] = 1
        return "Remarks section"
    if upper == "AO1":
        return "Automated station without precipitation discriminator"
    if upper == "AO2":
        return "Automated station with precipitation discriminator"
    if upper.startswith("SLP") and len(upper) == 6 and upper[3:].isdigit():
        return "Sea-level pressure (FMH-1 SLP code)"
    if upper == "=" or token == "=":
        return "Report terminator"
    if _STATION.match(upper) and seen.get("station", 0) == 0 and seen.get("rtype", 0):
        seen["station"] = 1
        place = resolve_location_name(upper)
        if place:
            return f"Station {place} ({upper})"
        return f"Station {upper}"
    if m := _TIME_Z.match(upper):
        return _fmt_time(m, label="Observation time")
    if m := _WIND.match(upper):
        return _fmt_wind(m, label="Surface wind")
    if m := _VIS_SM.match(upper):
        label = "Trend visibility" if seen.get("in_trend") else "Prevailing visibility"
        return _fmt_vis_sm(m, label=label)
    if m := _VIS_MIN.match(upper):
        compass = _SIG_DIR_NAME[m.group("dir")]
        return f"Minimum visibility {int(m.group('vis'))} m toward {compass} ({m.group('dir')})"
    if _VIS_M.match(upper):
        label = "Trend visibility" if seen.get("in_trend") else "Prevailing visibility"
        return f"{label} {int(upper)} m"
    if m := _TREND_TIME.match(upper):
        kind = m.group("kind")
        return f"Trend {_TREND_TIME_LABEL[kind]} {m.group('hh')}:{m.group('mm')} UTC"
    if m := _CLOUD.match(upper):
        return _fmt_cloud(m, forecast=bool(seen.get("in_trend")))
    if m := _TEMP.match(upper):
        return f"Temperature {_signed_temp(m.group('t'))} °C, dewpoint {_signed_temp(m.group('td'))} °C"
    if m := _ALT.match(upper):
        return f"Altimeter {int(m.group('val')) / 100:.2f} inHg"
    if m := _QNH.match(upper):
        return _fmt_qnh(m.group("val"))
    if m := _WX.match(upper):
        return _fmt_wx(m, forecast=bool(seen.get("in_trend")))
    if m := _RVR.match(upper):
        trend = m.group("trend")
        trend_txt = {
            "U": ", upward trend",
            "D": ", downward trend",
            "N": ", no distinct trend",
        }.get(trend or "", "")
        return f"Runway visual range runway {m.group('rw')}: {m.group('vis')} m{trend_txt}"
    if phrase := _varying_rvr(upper):
        return phrase
    if m := _VV.match(upper):
        if m.group("h") == "///":
            return "Vertical visibility not reported"
        return f"Vertical visibility {int(m.group('h')) * 100} ft"
    if m := _MISSING_CLOUD.match(upper):
        kind = _CA_CLOUD_NAME.get(m.group("ctype") or "")
        if kind:
            return f"Cloud amount not reported, {kind}"
        return "Cloud amount not reported"
    if phrase := _wx_began_or_ended(upper):
        return phrase
    if upper.startswith("PK") or upper == "WND":
        return "Peak wind remarks token"
    if upper == "AUTO":
        return "Automated report"
    if upper == "$":
        return "Station needs maintenance"
    if upper == "WSHFT":
        return "Wind shift"
    if upper in {"//", "///"}:
        return "Missing data"
    if upper == "TS":
        return "Thunderstorm"
    if m := _WIND_VAR.match(upper):
        return f"Wind direction varying from {int(m.group('a'))}° to {int(m.group('b'))}°"
    if m := _VIS_FRAC.match(upper):
        return f"Prevailing visibility {m.group('num')}/{m.group('den')} statute mile"
    if m := _T_GROUP.match(upper):
        return f"Temperature {_tenths_c(m.group('t'))} °C, dewpoint {_tenths_c(m.group('td'))} °C in tenths"
    if seen.get("rmk"):
        remark = _explain_metar_remark(upper, seen)
        if remark:
            return remark
    _ = product
    return None


def _explain_metar_remark(upper: str, seen: dict[str, int]) -> str | None:
    """Groups that show up in the remarks, after ``RMK``.

    Parameters
    ----------
    upper : str
        One remarks group, already uppercased.
    seen : dict[str, int]
        Tokens already accepted while decoding this report.

    Returns
    -------
    str | None
        The remark in plain language, or None when the group stays unexplained.
    """
    if upper == "SLPNO":
        return "Sea-level pressure not available"
    if upper == "PNO":
        return "Precipitation amount not available"
    if phrase := _pressure_tendency(upper):
        return phrase
    if phrase := _precip_amount(upper):
        return phrase
    if phrase := _canadian_clouds(upper):
        return phrase
    if m := _MM_AMOUNT.match(upper):
        return f"Precipitation {m.group('n')} mm"
    if upper == "CIG":
        seen["cig"] = 1
        return "Ceiling"
    if upper == "DENSITY":
        seen["density"] = 1
        return "Density"
    if upper == "ALT" and seen.get("density"):
        seen["density"] = 0
        seen["density_alt"] = 1
        return "Altitude"
    if m := _PEAK_WIND.match(upper):
        return f"Peak wind {int(m.group('dir'))}° at {int(m.group('spd'))} kt at {m.group('hh')}:{m.group('mm')} UTC"
    if m := _PAST_HOUR.match(upper):
        unit = "hour" if m.group("n") == "1" else "hours"
        return f"In the past {m.group('n')} {unit}"
    if m := _FRAC_MILE.match(upper):
        return f"Visibility {m.group('num')}/{m.group('den')} statute mile"
    if upper in _RMK_WORD:
        return _RMK_WORD[upper]
    if upper in _SIG_DIR:
        return _SIG_DIR_NAME[upper]
    sector = re.fullmatch(rf"({_BEARING})-({_BEARING})", upper)
    if sector:
        return f"From {_SIG_DIR_NAME[sector.group(1)]} to {_SIG_DIR_NAME[sector.group(2)]}"
    return None


def _explain_taf(token: str, *, seen: dict[str, int]) -> str | None:
    """
    Internal helper ``_explain_taf``.

    Parameters
    ----------
    token : object
        Argument ``token``.
    seen : object
        Argument ``seen``.

    Returns
    -------
    object
        Return value.
    """
    upper = token.upper()
    if upper == "TAF" and seen.get("rtype", 0) == 0:
        seen["rtype"] = 1
        return "Report type (terminal aerodrome forecast)"
    if upper in {"AMD", "COR"}:
        return "Amendment / correction indicator"
    if upper == "CNL":
        return "Cancelled forecast"
    if upper == "NIL":
        return "Nil forecast"
    if upper == "=":
        return "Report terminator"
    if _STATION.match(upper) and seen.get("station", 0) == 0:
        seen["station"] = 1
        place = resolve_location_name(upper)
        if place:
            return f"Station {place} ({upper})"
        return f"Station {upper}"
    if m := _TIME_Z.match(upper):
        return _fmt_time(m, label="Issue time")
    if m := _TAF_VALID.match(upper):
        return (
            f"Valid from day {int(m.group('d1'))} {m.group('h1')}:00 UTC"
            f" to day {int(m.group('d2'))} {m.group('h2')}:00 UTC"
        )
    if m := _WIND.match(upper):
        return _fmt_wind(m, label="Forecast wind")
    if _VIS_M.match(upper):
        return f"Forecast visibility {int(upper)} m"
    if m := _VIS_SM.match(upper):
        return _fmt_vis_sm(m, label="Forecast visibility")
    if m := _CLOUD.match(upper):
        return _fmt_cloud(m, forecast=True)
    if m := _ALT.match(upper):
        return f"Altimeter {int(m.group('val')) / 100:.2f} inHg"
    if m := _QNH.match(upper):
        return _fmt_qnh(m.group("val"))
    if m := _TAF_FM.match(upper):
        return (
            f"From day {int(m.group('dd'))} at {m.group('hh')}:{m.group('mm')} UTC, then the conditions change quickly"
        )
    if upper == "TEMPO":
        return "Temporary fluctuations expected during the following period"
    if upper == "BECMG":
        return "Becoming, a gradual change during the following period"
    if m := _TAF_PROB.match(upper):
        return f"{int(m.group('pct'))}% probability of the following conditions"
    if upper.startswith(("FM", "TEMPO", "BECMG", "PROB")):
        return "Change / probability group"
    if m := _WX.match(upper):
        return _fmt_wx(m, forecast=True)
    return None


def _explain_sigmet_airmet(token: str, *, product: str, seen: dict[str, int]) -> str | None:
    """
    Internal helper ``_explain_sigmet_airmet``.

    Parameters
    ----------
    token : object
        Argument ``token``.
    product : object
        Argument ``product``.
    seen : object
        Argument ``seen``.

    Returns
    -------
    object
        Return value.
    """
    upper = token.upper().rstrip(".")
    if upper in {"SIGMET", "AIRMET"} and seen.get("rtype", 0) == 0:
        seen["rtype"] = 1
        return f"Report type ({upper})"
    if upper in {"SIGMET", "AIRMET"} and seen.get("cnl"):
        # Cancelled bulletin references the product again (``CNL SIGMET 2 …``).
        return f"Cancelled {upper} reference"
    if upper in {"SIGMET", "AIRMET"} and seen.get("ref"):
        return f"Referenced report ({upper})"
    if upper in {"SIGMET", "AIRMET"} and seen.get("rtype"):
        return f"Report type ({upper})"
    if _BBB_CORRECTION.match(upper):
        return f"Correction ({upper})"
    if _BBB_DELAYED.match(upper):
        return f"Delayed report ({upper})"
    if upper == "=":
        return "Report terminator"
    if upper == "CNL":
        seen["cnl"] = 1
        return explain_glossary_token(upper, fallback="Cancellation")
    if upper == "CONVECTIVE" and not seen.get("rtype"):
        seen["convective"] = 1
        return "Convective"
    if upper == "VALID":
        return "Validity period marker"
    if upper == "UNTIL":
        if seen.get("convective"):
            seen["until"] = 1
        return "Until"
    if upper == "WST":
        return "Convective SIGMET bulletin"
    if upper in _SIGMET_SERIES and seen.get("rtype") and not seen.get("seq") and not seen.get("valid_period"):
        return f"SIGMET series ({upper.capitalize()})"
    if seen.get("rtype") and not seen.get("seq") and not seen.get("valid_period") and (m := _SIG_SEQ.match(upper)):
        seen["seq"] = 1
        if m.group("letter_first"):
            label = f"{m.group('letter_first')}{int(m.group('num_a'))}"
        elif m.group("letter_last"):
            label = f"{int(m.group('num_b'))}{m.group('letter_last')}"
        else:
            label = str(int(m.group("num_b")))
        return f"Sequence number ({label})"
    if re.fullmatch(r"\d{6}", upper) and not seen.get("valid_period"):
        return f"Issue time day {int(upper[:2])} {upper[2:4]}:{upper[4:]} UTC"
    if upper.isdigit() and seen.get("cnl"):
        return f"Cancelled sequence number ({int(upper)})"
    if m := _SIG_VALID.match(upper):
        seen["valid_period"] = 1
        return (
            f"Valid day {int(m.group('d1'))} {m.group('h1')}:{m.group('m1')} UTC"
            f" to day {int(m.group('d2'))} {m.group('h2')}:{m.group('m2')} UTC"
        )

    if upper == "FROM" and seen.get("rtype"):
        seen["from_line"] = 1
        return "From"
    if upper == "AREA":
        seen["from_line"] = 0
        seen["area"] = 1
        return "Area"
    if upper == "TOPS":
        seen["tops"] = 1
        return "Cloud tops"
    if upper == "CSTL":
        return "Coastal"
    if upper == "WTRS":
        return "Waters"
    if _in_convective_area(seen) and upper in _US_STATE:
        return f"State ({_US_STATE[upper]})"
    if _in_convective_area(seen) and upper in _US_LAKE:
        return f"Lake ({_US_LAKE[upper]})"
    if seen.get("tc_next"):
        seen["tc_next"] = 0
        if _CYCLONE_NAME.match(upper) and not meaning_for(upper.split("-")[0]):
            return f"Tropical cyclone ({upper})"
    if upper == "REF":
        seen["ref"] = 1
        return "Reference"
    if upper == "INTL":
        return "International"
    if upper == "SERIES":
        return "Series"
    if upper in _SIGMET_SERIES and seen.get("ref"):
        return f"Referenced SIGMET series ({upper.capitalize()})"

    # MWO designator often carries a trailing hyphen (``YUSO-``).
    icao = upper.rstrip("-")
    if _STATION.match(icao):
        if seen.get("station", 0) == 0:
            seen["station"] = 1
            place = resolve_location_name(icao)
            if place:
                return f"Originating FIR / location indicator {icao} ({place})"
            return f"Originating FIR / location indicator ({icao})"
        if seen.get("valid_period") and not seen.get("mwo"):
            seen["mwo"] = 1
            place = resolve_location_name(icao)
            if place:
                return f"Originating meteorological watch office {icao} ({place})"
            return f"Originating meteorological watch office ({icao})"
        if not seen.get("fir_icao") and not (seen.get("name_open") and icao.isalpha()):
            seen["fir_icao"] = 1
            return f"Affected FIR / ATS region ({icao})"

    if upper in {"FIR/UIR", "FIR", "UIR"}:
        seen["name_open"] = 0
        seen["after_fir"] = 1
        return explain_glossary_token(upper, fallback="Flight information region")
    if upper == "OCEANIC":
        seen["name_open"] = 0
        seen["after_fir"] = 1
        return "Oceanic FIR qualifier"
    if upper == "ERUPTION":
        seen["eruption"] = 1
        return "Volcanic eruption"
    if upper == "MT":
        return "Mount"
    if upper == "AT":
        return "At (observation / forecast time)"
    if upper == "TO" and seen.get("tops"):
        return "To"
    if upper == "LTL":
        return "Little"
    if upper == "WI":
        return "Within (area polygon)"
    if upper in {"-", "\u2013", "\u2014"}:
        if seen.get("line"):
            return "Line vertex separator"
        return "Polygon vertex separator"
    if upper == "LINE":
        seen["line"] = 1
        return "Line of coordinates"
    if upper == "OBS/FCST":
        return "Observed and forecast"
    if m := _SIG_SFC_LAYER.match(upper):
        unit = "ft" if m.group("unit") == "FT" else "m"
        return f"Surface to {int(m.group('alt'))} {unit}"
    if m := _SIG_NM.match(upper):
        return f"Within {int(m.group('n'))} nautical miles"
    if m := _SIG_FT_LAYER.match(upper):
        unit = "ft" if m.group("unit") == "FT" else "m"
        return f"Altitude {int(m.group('alt'))} {unit} to flight level {int(m.group('fl'))}"
    if m := _SIG_FL_LAYER.match(upper):
        if m.group("sfc"):
            return f"Surface to flight level {int(m.group('sfc'))}"
        return f"Flight levels {int(m.group('a'))} to {int(m.group('b'))}"
    if m := _SIG_FL.match(upper):
        return f"Flight level {int(m.group('fl'))}"
    if m := _SIG_HHMMZ.match(upper):
        return f"Time {m.group('hh')}:{m.group('mm')} UTC"
    if upper == "MOV":
        seen["mov"] = 1
        return explain_glossary_token(upper, fallback="Moving")
    if upper in _SIG_DIR:
        if seen.get("mov") and not seen.get("mov_dir"):
            seen["mov_dir"] = 1
            return f"Movement direction ({_SIG_DIR_NAME[upper]})"
        return _SIG_DIR_NAME[upper]
    if m := _SIG_SPEED.match(upper):
        unit = _SIG_SPEED_UNIT[m.group("unit")]
        return f"Speed {int(m.group('spd'))} {unit}"
    if m := _MOV_FROM.match(upper):
        return f"Moving from {int(m.group('deg'))}° at {int(m.group('spd'))} kt"
    if upper.isdigit() and seen.get("mov_dir") and not seen.get("mov_spd") and len(upper) <= 3:
        seen["mov_spd"] = 1
        return f"Speed {int(upper)}"
    if upper in _SIG_SPEED_UNIT and seen.get("mov_spd") and not seen.get("mov_unit"):
        seen["mov_unit"] = 1
        return _SIG_SPEED_UNIT[upper]
    coord = _coord_token(upper)
    if m := _SIG_LAT.match(coord):
        hemi = "North" if m.group("hemi") == "N" else "South"
        mins = m.group("min")
        if mins:
            return f"Latitude {int(m.group('deg'))}°{mins}' {hemi[0]}"
        return f"Latitude {int(m.group('deg'))}° {hemi}"
    if m := _SIG_LATLON.match(coord):
        return _lat_lon_phrase(m.group("lat"), m.group("lon"))
    if m := _SIG_LON.match(coord):
        hemi = "East" if m.group("hemi") == "E" else "West"
        mins = m.group("min")
        if mins:
            return f"Longitude {int(m.group('deg'))}°{mins}' {hemi[0]}"
        return f"Longitude {int(m.group('deg'))}° {hemi}"
    if upper in {"OF", "AND"}:
        return explain_glossary_token(upper, fallback=upper.capitalize())
    if upper == "CENTER":
        return "Center"
    if seen.get("from_line"):
        boundary = _boundary_points(upper)
        if boundary:
            return boundary
        chain = _navaid_chain(upper)
        if chain:
            return chain
        if re.fullmatch(r"[A-Z]{3}", upper):
            return f"Navaid {upper}"

    if upper == "TC":
        seen["tc_next"] = 1
        return explain_glossary_token(upper, fallback="Tropical cyclone")

    # Volcano name after ``ERUPTION MT …`` (e.g. HEKLA, ASHVAL).
    if (
        seen.get("eruption")
        and icao.isalpha()
        and len(icao) >= 3
        and not meaning_for(icao)
        and icao not in {"FIR", "UIR", "VA", "CLD"}
    ):
        return f"Volcano name ({icao})"

    # FIR proper name (e.g. SHANLON) when not a known glossary hazard token.
    if (
        icao.isalpha()
        and len(icao) >= 2
        and seen.get("station")
        and not meaning_for(icao)
        and (not seen.get("fir_name") or seen.get("name_open") or seen.get("after_fir"))
    ):
        seen["fir_name"] = 1
        seen["name_open"] = 1
        seen["after_fir"] = 0
        return f"FIR name ({icao})"

    # Glossary-backed intensity / hazard / movement tokens (F9 deepen).
    gloss = explain_glossary_token(upper)
    if gloss:
        return gloss
    bare = upper.strip("()")
    if bare and bare != upper:
        return explain_glossary_token(bare)
    return None


def _explain_advisory(token: str, *, product: str, seen: dict[str, int]) -> str | None:
    """
    Internal helper ``_explain_advisory``.

    Parameters
    ----------
    token : object
        Argument ``token``.
    product : object
        Argument ``product``.
    seen : object
        Argument ``seen``.

    Returns
    -------
    object
        Return value.
    """
    upper = token.upper().rstrip(":")
    if product == "VAA":
        if upper == "VA" and seen.get("va", 0) == 0:
            seen["va"] = 1
            return explain_glossary_token(upper, fallback="Volcanic ash advisory marker")
        if upper == "ADVISORY" and seen.get("adv", 0) == 0:
            seen["adv"] = 1
            return explain_glossary_token(upper, fallback="Advisory product header")
        if upper == "VAA":
            return explain_glossary_token(upper, fallback="Volcanic ash advisory abbreviation")
    if product == "TCA":
        if upper == "TC" and seen.get("tc", 0) == 0:
            seen["tc"] = 1
            return explain_glossary_token(upper, fallback="Tropical cyclone advisory marker")
        if upper == "ADVISORY" and seen.get("adv", 0) == 0:
            seen["adv"] = 1
            return explain_glossary_token(upper, fallback="Advisory product header")
        if upper == "TCA":
            return explain_glossary_token(upper, fallback="Tropical cyclone advisory abbreviation")
    if product == "SWXA":
        if upper == "SWX" and seen.get("swx", 0) == 0:
            seen["swx"] = 1
            return explain_glossary_token(upper, fallback="Space weather advisory marker")
        if upper == "ADVISORY" and seen.get("adv", 0) == 0:
            seen["adv"] = 1
            return explain_glossary_token(upper, fallback="Advisory product header")
        if upper == "SWXA":
            return explain_glossary_token(upper, fallback="Space weather advisory abbreviation")
    if product == "VONA" and upper == "VONA":
        return explain_glossary_token(upper, fallback="Volcano Observatory Notice for Aviation")
    return explain_glossary_token(upper, fallback="Unrecognized group")


# Longest-first advisory field labels (WMO VAA/TCA/SWXA/VONA TAC layout). Title templates use
# ``{hours}`` when the label includes ``+N HR``.
_VAA_FIELD_SPECS: tuple[tuple[str, str], ...] = (
    (r"FCST\s+VA\s+CLD\s+\+(?P<hours>\d+)\s+HR", "Forecast volcanic ash cloud at +{hours} hours"),
    (r"OBS\s+VA\s+CLD", "Observed volcanic ash cloud"),
    (r"OBS\s+VA\s+DTG", "Observed volcanic ash date-time"),
    (r"ERUPTION\s+DETAILS", "Eruption details"),
    (r"INFO\s+SOURCE", "Information source"),
    (r"SOURCE\s+ELEV", "Source elevation"),
    (r"ADVISORY\s+NR", "Advisory number"),
    (r"NXT\s+ADVISORY", "Next advisory time"),
    (r"VAAC", "Volcanic ash advisory centre"),
    (r"VOLCANO", "Volcano"),
    (r"AREA", "Area"),
    (r"PSN", "Position"),
    (r"DTG", "Date-time group"),
    (r"RMK", "Remarks"),
)

_TCA_FIELD_SPECS: tuple[tuple[str, str], ...] = (
    (r"FCST\s+MAX\s+WIND\s+\+(?P<hours>\d+)\s+HR", "Forecast maximum wind at +{hours} hours"),
    (r"FCST\s+PSN\s+\+(?P<hours>\d+)\s+HR", "Forecast position at +{hours} hours"),
    (r"ADVISORY\s+NR", "Advisory number"),
    (r"OBS\s+PSN", "Observed position"),
    (r"INTST\s+CHANGE", "Intensity change"),
    (r"MAX\s+WIND", "Maximum wind"),
    (r"NXT\s+MSG", "Next message time"),
    (r"TCAC", "Tropical cyclone advisory centre"),
    (r"DTG", "Date-time group"),
    (r"MOV", "Movement"),
    (r"CB", "Cumulonimbus extent"),
    (r"TC", "Tropical cyclone name"),
    (r"RMK", "Remarks"),
    (r"C", "Central pressure"),
)

_SWXA_FIELD_SPECS: tuple[tuple[str, str], ...] = (
    (r"FCST\s+SWX\s+\+(?P<hours>\d+)\s+HR", "Forecast space weather at +{hours} hours"),
    (r"NXT\s+ADVISORY", "Next advisory time"),
    (r"ADVISORY\s+NR", "Advisory number"),
    (r"SWX\s+EFFECT", "Space weather effect"),
    (r"OBS\s+SWX", "Observed space weather"),
    (r"NR\s+RPLC", "Replaced advisory number(s)"),
    (r"SWXC", "Space weather centre"),
    (r"DTG", "Date-time group"),
    (r"RMK", "Remarks"),
)

_VONA_FIELD_SPECS: tuple[tuple[str, str], ...] = (
    (r"CURRENT\s+COLOUR\s+CODE", "Current aviation colour code"),
    (r"PREVIOUS\s+COLOUR\s+CODE", "Previous aviation colour code"),
    (r"SOURCE\s+ELEV", "Source elevation"),
    (r"VA\s+CLD\s+HGT", "Volcanic ash cloud height"),
    (r"HGT\s+SOURCE", "Height information source"),
    (r"NOTICE\s+NR", "Notice number"),
    (r"NXT\s+NOTICE", "Next notice"),
    (r"ACT\s+STS", "Activity status"),
    (r"VOLCANO", "Volcano"),
    (r"AREA", "Area / state or region"),
    (r"ONSET", "Onset time"),
    (r"DUR", "Duration"),
    (r"MOV", "Ash cloud movement"),
    (r"CTC", "Contacts"),
    (r"SVO", "State volcano observatory"),
    (r"PSN", "Position"),
    (r"DTG", "Date-time group"),
    (r"RMK", "Remarks"),
)

_FIELD_SPECS_BY_PRODUCT: dict[str, tuple[tuple[str, str], ...]] = {
    "VAA": _VAA_FIELD_SPECS,
    "TCA": _TCA_FIELD_SPECS,
    "SWXA": _SWXA_FIELD_SPECS,
    "VONA": _VONA_FIELD_SPECS,
}


def _advisory_field_finder(product: str) -> list[tuple[re.Pattern[str], str]]:
    """
    Internal helper ``_advisory_field_finder``.

    Parameters
    ----------
    product : object
        Argument ``product``.

    Returns
    -------
    object
        Return value.
    """
    specs = _FIELD_SPECS_BY_PRODUCT.get(product)
    if not specs:
        return []
    return [(re.compile(rf"(?P<label>{pat})\s*:", re.IGNORECASE), title) for pat, title in specs]


def _advisory_field_title(label: str, title_template: str, match: re.Match[str]) -> str:
    """
    Internal helper ``_advisory_field_title``.

    Parameters
    ----------
    label : object
        Argument ``label``.
    title_template : object
        Argument ``title_template``.
    match : object
        Argument ``match``.

    Returns
    -------
    object
        Return value.
    """
    hours = match.groupdict().get("hours")
    if hours is not None and "{hours}" in title_template:
        return title_template.format(hours=hours)
    return title_template


_AHL_LINE = re.compile(
    r"^(?P<ahl>[A-Z]{4}\d{2})\s+(?P<cccc>[A-Z]{4})\s+(?P<yygggg>\d{6})\b",
    re.MULTILINE,
)


def _iter_ahl_heading(tac: str) -> list[tuple[int, int, str, str]]:
    """
    Internal helper ``_iter_ahl_heading``.

    Parameters
    ----------
    tac : object
        Argument ``tac``.

    Returns
    -------
    object
        Return value.
    """
    m = _AHL_LINE.match(tac.lstrip("\ufeff"))
    if m is None:
        stripped = tac.lstrip()
        offset = len(tac) - len(stripped)
        m = _AHL_LINE.match(stripped)
        if m is None:
            return []
        start = offset + m.start()
        end = offset + m.end()
    else:
        start, end = m.start(), m.end()
    code = tac[start:end]
    explanation = f"Abbreviated heading {m.group('ahl')} from {m.group('cccc')} at {m.group('yygggg')}"
    return [(start, end, code, explanation)]


def _iter_advisory_ahl(tac: str, *, product: str) -> list[tuple[int, int, str, str]]:
    """
    Internal helper ``_iter_advisory_ahl``.

    Parameters
    ----------
    tac : object
        Argument ``tac``.
    product : object
        Argument ``product``.

    Returns
    -------
    object
        Return value.
    """
    if product not in _ADVISORY_STRUCTURED:
        return []
    return _iter_ahl_heading(tac)


_MONTHS = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)

_COMPASS = {
    "N": "north",
    "NNE": "north-northeast",
    "NE": "northeast",
    "ENE": "east-northeast",
    "E": "east",
    "ESE": "east-southeast",
    "SE": "southeast",
    "SSE": "south-southeast",
    "S": "south",
    "SSW": "south-southwest",
    "SW": "southwest",
    "WSW": "west-southwest",
    "W": "west",
    "WNW": "west-northwest",
    "NW": "northwest",
    "NNW": "north-northwest",
}

_SPEED_UNIT = {
    "KMH": "kilometres per hour",
    "KM/H": "kilometres per hour",
    "KT": "knots",
    "MPS": "metres per second",
}

_COMPASS_RE = "|".join(sorted(_COMPASS, key=len, reverse=True))

_ADVISORY_PHRASES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bNO\s+VA\s+EXP\b"), "no volcanic ash expected"),
    (re.compile(r"\bNO\s+MSG\s+EXP\b"), "no message expected"),
    (re.compile(r"\bOF\s+TC\s+CENTRE\b"), "of the tropical cyclone centre,"),
    (re.compile(r"\bAMSL\b"), "above mean sea level"),
    (re.compile(r"\bINTSF\b"), "intensifying"),
    (re.compile(r"\bINTST\b"), "intensifying"),
    (re.compile(r"\bWKN\b"), "weakening"),
    (re.compile(r"\bSTNR\b"), "stationary"),
    (re.compile(r"\bNIL\b"), "none"),
    (re.compile(r"\bNC\b"), "no change"),
    (re.compile(r"\bWI\b"), "within"),
    (re.compile(r"\bTOP\b"), "top"),
)


def _ordinal_day(day: int) -> str:
    """Day of month with an ordinal, such as ``the 1st``.

    Parameters
    ----------
    day : int
        Day of the month.

    Returns
    -------
    str
        ``the`` plus the day and its suffix.
    """
    suffix = "th" if 10 <= day % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return f"the {day}{suffix}"


def _plain_advisory_value(value: str) -> str:
    """Read coded advisory values as plain language.

    Dates, positions, speeds, distances, and a few fixed phrases are expanded.
    Surrounding words stay as written. [Corpus: product §F9]

    Parameters
    ----------
    value : str
        Text after an advisory field label.

    Returns
    -------
    str
        The same text with coded pieces expanded.
    """
    text = " ".join(value.split())
    if not text:
        return ""

    def _dtg(match: re.Match[str]) -> str:
        """Expand ``YYYYMMDD/HHMMZ`` to a clock time and calendar date.

        Parameters
        ----------
        match : re.Match[str]
            Date and time groups.

        Returns
        -------
        str
            Plain time, or the original text when the date is impossible.
        """
        raw, hhmm = match.group(1), match.group(2)
        month, day = int(raw[4:6]), int(raw[6:8])
        if not 1 <= month <= 12 or not 1 <= day <= 31:
            return match.group(0)
        return f"{hhmm[:2]}:{hhmm[2:]} UTC on {day} {_MONTHS[month - 1]} {raw[:4]}"

    def _daytime(match: re.Match[str]) -> str:
        """Expand ``DD/HHMMZ`` to a clock time on that day.

        Parameters
        ----------
        match : re.Match[str]
            Day and time groups.

        Returns
        -------
        str
            Plain time, or the original text when the day is impossible.
        """
        day = int(match.group(1))
        hhmm = match.group(2)
        if not 1 <= day <= 31:
            return match.group(0)
        return f"{hhmm[:2]}:{hhmm[2:]} UTC on {_ordinal_day(day)}"

    def _lat(match: re.Match[str]) -> str:
        """Expand a coded latitude.

        Parameters
        ----------
        match : re.Match[str]
            Hemisphere, degrees, and minutes.

        Returns
        -------
        str
            Degrees and minutes north or south.
        """
        hemi = "north" if match.group(1) == "N" else "south"
        return f"{int(match.group(2))} degrees {match.group(3)} minutes {hemi}"

    def _lon(match: re.Match[str]) -> str:
        """Expand a coded longitude.

        Parameters
        ----------
        match : re.Match[str]
            Hemisphere, degrees, and minutes.

        Returns
        -------
        str
            Degrees and minutes east or west.
        """
        hemi = "east" if match.group(1) == "E" else "west"
        return f"{int(match.group(2))} degrees {match.group(3)} minutes {hemi}"

    def _move(match: re.Match[str]) -> str:
        """Expand a compass direction and speed.

        Parameters
        ----------
        match : re.Match[str]
            Direction, speed, and unit.

        Returns
        -------
        str
            Direction, speed, and unit in words.
        """
        unit = match.group(3).upper()
        return f"{_COMPASS[match.group(1)]} at {int(match.group(2))} {_SPEED_UNIT[unit]}"

    def _speed(match: re.Match[str]) -> str:
        """Expand a bare speed.

        Parameters
        ----------
        match : re.Match[str]
            Speed and unit.

        Returns
        -------
        str
            Speed and unit in words.
        """
        unit = match.group(2).upper()
        return f"{int(match.group(1))} {_SPEED_UNIT[unit]}"

    text = re.sub(r"\b(\d{8})/(\d{4})Z\b", _dtg, text)
    text = re.sub(r"\b(\d{2})/(\d{4})Z\b", _daytime, text)
    text = re.sub(r"\b([NS])(\d{2})(\d{2})\b", _lat, text)
    text = re.sub(r"\b([EW])(\d{2,3})(\d{2})\b", _lon, text)
    text = re.sub(rf"\b({_COMPASS_RE})\s*(\d{{1,3}})\s*(KM/H|KMH|KT|MPS)\b", _move, text)
    text = re.sub(r"\bSFC/FL(\d+)\b", lambda m: f"surface to flight level {int(m.group(1))}", text)
    text = re.sub(
        r"\bFL(\d+)/(\d+)\b",
        lambda m: f"flight level {int(m.group(1))} to {int(m.group(2))}",
        text,
    )
    text = re.sub(r"\bFL(\d+)\b", lambda m: f"flight level {int(m.group(1))}", text)
    text = re.sub(r"\b(\d+)(KM/H|KMH|KT|MPS)\b", _speed, text)
    text = re.sub(r"\b(\d+)HPA\b", lambda m: f"{int(m.group(1))} hectopascals", text)
    text = re.sub(r"\b(\d+)NM\b", lambda m: f"{int(m.group(1))} nautical miles", text)
    text = re.sub(r"\b(\d+)KM\b", lambda m: f"{int(m.group(1))} kilometres", text)
    text = re.sub(r"\b(\d+)M\b", lambda m: f"{int(m.group(1))} metres", text)
    for pattern, phrase in _ADVISORY_PHRASES:
        text = pattern.sub(phrase, text)
    return " ".join(text.split())


def _iter_advisory_fields(
    tac: str,
    *,
    product: str,
) -> list[tuple[int, int, str, str, int]]:
    """
    Internal helper ``_iter_advisory_fields``.

    Parameters
    ----------
    tac : object
        Argument ``tac``.
    product : object
        Argument ``product``.

    Returns
    -------
    object
        Return value.
    """
    if product not in _ADVISORY_STRUCTURED:
        return []
    # Collect all label hits; when spans overlap prefer the longer (earlier-spec) label.
    hits: list[tuple[int, int, str, str, re.Match[str]]] = []
    for pattern, title_template in _advisory_field_finder(product):
        for m in pattern.finditer(tac):
            label = m.group("label")
            code = re.sub(r"\s+", " ", label.strip())
            hits.append((m.start(), m.end(), code, title_template, m))
    if not hits:
        return []
    hits.sort(key=lambda h: (h[0], -(h[1] - h[0])))
    # Drop overlapping shorter matches (same start or nested under a longer label).
    selected: list[tuple[int, int, str, str, re.Match[str]]] = []
    for hit in hits:
        start, end, _code, _title, _m = hit
        if any(start < prev_end and end > prev_start for prev_start, prev_end, *_ in selected):
            continue
        selected.append(hit)
    selected.sort(key=lambda h: h[0])

    out: list[tuple[int, int, str, str]] = []
    for i, (start, label_end, code, title_template, match) in enumerate(selected):
        value_start = label_end
        value_end = selected[i + 1][0] if i + 1 < len(selected) else len(tac)
        raw_value = tac[value_start:value_end]
        trim = len(raw_value.rstrip())
        body = raw_value[:trim]
        lead = len(body) - len(body.lstrip())
        value_text = " ".join(body.split())
        plain = _plain_advisory_value(value_text)
        title = _advisory_field_title(code, title_template, match)
        explanation = f"{title}: {plain}" if plain else title
        mark_start = value_start + lead
        mark_end = value_start + trim
        if mark_end <= mark_start:
            mark_start, mark_end = start, label_end
        out.append((mark_start, mark_end, code, explanation, start))
    return out


def _token_indices_covering(
    tokens: list[tuple[int, int, str]],
    spans: list[tuple[int, int]],
) -> set[int]:
    """
    Internal helper ``_token_indices_covering``.

    Parameters
    ----------
    tokens : object
        Argument ``tokens``.
    spans : object
        Argument ``spans``.

    Returns
    -------
    object
        Return value.
    """
    covered: set[int] = set()
    for idx, (tstart, tend, _) in enumerate(tokens):
        for start, end in spans:
            if tstart < end and tend > start:
                covered.add(idx)
                break
    return covered


def _classify(
    product: str,
) -> Callable[[str, dict[str, int]], str | None]:
    """
    Internal helper ``_classify``.

    Parameters
    ----------
    product : object
        Argument ``product``.

    Returns
    -------
    object
        Return value.
    """
    if product in {"METAR", "SPECI"}:

        def _metar(tok: str, seen: dict[str, int]) -> str | None:
            """
            Internal helper ``_metar``.

            Parameters
            ----------
            tok : object
                Argument ``tok``.
            seen : object
                Argument ``seen``.

            Returns
            -------
            object
                Return value.
            """
            return _explain_metar_speci(tok, product=product, seen=seen)

        return _metar
    if product == "TAF":

        def _taf(tok: str, seen: dict[str, int]) -> str | None:
            """
            Internal helper ``_taf``.

            Parameters
            ----------
            tok : object
                Argument ``tok``.
            seen : object
                Argument ``seen``.

            Returns
            -------
            object
                Return value.
            """
            return _explain_taf(tok, seen=seen)

        return _taf
    if product in {"SIGMET", "AIRMET"}:

        def _haz(tok: str, seen: dict[str, int]) -> str | None:
            """
            Internal helper ``_haz``.

            Parameters
            ----------
            tok : object
                Argument ``tok``.
            seen : object
                Argument ``seen``.

            Returns
            -------
            object
                Return value.
            """
            return _explain_sigmet_airmet(tok, product=product, seen=seen)

        return _haz
    if product in _ADVISORY_STRUCTURED:

        def _adv(tok: str, seen: dict[str, int]) -> str | None:
            """
            Internal helper ``_adv``.

            Parameters
            ----------
            tok : object
                Argument ``tok``.
            seen : object
                Argument ``seen``.

            Returns
            -------
            object
                Return value.
            """
            return _explain_advisory(tok, product=product, seen=seen)

        return _adv

    def _none(_tok: str, _seen: dict[str, int]) -> str | None:
        """
        Internal helper ``_none``.

        Parameters
        ----------
        _tok : object
            Argument ``_tok``.
        _seen : object
            Argument ``_seen``.

        Returns
        -------
        object
            Return value.
        """
        return None

    return _none


def _coalesce_residuals(
    tokens: list[tuple[int, int, str]],
    explained: set[int],
    tac: str,
) -> list[DecodeResidual]:
    """
    Internal helper ``_coalesce_residuals``.

    Parameters
    ----------
    tokens : object
        Argument ``tokens``.
    explained : object
        Argument ``explained``.
    tac : object
        Argument ``tac``.

    Returns
    -------
    object
        Return value.
    """
    residuals: list[DecodeResidual] = []
    i = 0
    while i < len(tokens):
        if i in explained:
            i += 1
            continue
        start = tokens[i][0]
        end = tokens[i][1]
        j = i + 1
        while j < len(tokens) and j not in explained:
            # Include intervening whitespace in residual text span.
            end = tokens[j][1]
            j += 1
        residuals.append(DecodeResidual(start=start, end=end, text=tac[start:end]))
        i = j
    return residuals


_SPARSE_PRODUCTS = frozenset({"SIGMET", "AIRMET", "VAA", "TCA", "SWXA", "VONA"})


def _sentence_from_segment(seg: DecodeSegment) -> str | None:
    """
    Internal helper ``_sentence_from_segment``.

    Parameters
    ----------
    seg : object
        Argument ``seg``.

    Returns
    -------
    object
        Return value.
    """
    if seg.code == "=" or seg.explanation.lower().startswith("report terminator"):
        return None
    text = seg.explanation.strip()
    if not text:
        return None
    lower = text.lower()
    if "station location" in lower or (
        "location indicator" in lower and "fir" not in lower and "watch office" not in lower
    ):
        for sep in (" — ", " - "):
            if sep in text:
                place = text.split(sep, 1)[1].strip().rstrip(".")
                if place and not place.startswith("("):
                    return f"station {place} ({seg.code.upper()})"
                break
        return f"station {seg.code.upper()}"
    # Prefer the value-bearing half after an em dash when present.
    if " - " in text:
        left, right = text.split(" - ", 1)
        if left.lower().startswith("report type"):
            return text.rstrip(".")
        return right.rstrip(".")
    return text.rstrip(".")


def _build_summary(
    product: str,
    segments: list[DecodeSegment],
    residuals: list[DecodeResidual],
) -> str:
    """
    Build a deterministic plain-language paragraph for the decode panel (F9).

    Parameters
    ----------
    product :
        Uppercase product id.
    segments :
        Value-aware decode segments.
    residuals :
        Undecoded spans; named in a trailing "Not decoded: …" clause.

    Returns
    -------
    str
        One flowing paragraph. Sparse products include "partial decode" wording.
    """
    clauses: list[str] = []
    for seg in segments:
        clause = _sentence_from_segment(seg)
        if clause and (not clauses or clauses[-1] != clause):
            clauses.append(clause)

    if product in _SPARSE_PRODUCTS:
        lead = f"{product} (partial decode)"
        body = "; ".join(clauses) if clauses else "few recognizable groups"
        paragraph = f"{lead}: {body}."
    elif clauses:
        # Lead with product when the first clause is the report type.
        paragraph = "; ".join(clauses) + "."
        paragraph = paragraph[0].upper() + paragraph[1:]
    else:
        paragraph = f"{product} report with no decoded groups."

    if residuals:
        residual_bits = " ".join(r.text for r in residuals)
        # Collapse whitespace for readable "Not decoded" naming.
        residual_bits = " ".join(residual_bits.split())
        paragraph = f"{paragraph} Not decoded: {residual_bits}."

    return paragraph


def _looks_like_ahl_bulletin(text: str) -> bool:
    """
    Internal helper ``_looks_like_ahl_bulletin``.

    Parameters
    ----------
    text : object
        Argument ``text``.

    Returns
    -------
    object
        Return value.
    """
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        return _AHL_LINE.match(stripped) is not None
    return False


def _shift_decode(result: DecodeResult, offset: int) -> DecodeResult:
    """
    Internal helper ``_shift_decode``.

    Parameters
    ----------
    result : object
        Argument ``result``.
    offset : object
        Argument ``offset``.

    Returns
    -------
    object
        Return value.
    """
    return DecodeResult(
        product=result.product,
        segments=[
            DecodeSegment(
                start=s.start + offset,
                end=s.end + offset,
                code=s.code,
                explanation=s.explanation,
            )
            for s in result.segments
        ],
        residuals=[
            DecodeResidual(
                start=r.start + offset,
                end=r.end + offset,
                text=r.text,
            )
            for r in result.residuals
            if r.text.strip()
        ],
        summary=result.summary,
    )


class _BulletinMeta(Protocol):
    """Internal bulletin metadata."""

    ahl: str
    report_count: int


class _BulletinSplit(Protocol):
    """Internal bulletin split result."""

    reports: Sequence[str]
    meta: _BulletinMeta


_bulletin_splitter: Callable[[str, str], object] | None = None


def set_bulletin_splitter(splitter: Callable[[str, str], object] | None) -> None:
    """
    Inject WMO bulletin splitting. Unset means bulletins are not split.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (set_bulletin_splitter)
    2

    Parameters
    ----------
    splitter : object
        Argument ``splitter``.
    """
    global _bulletin_splitter
    _bulletin_splitter = splitter


def _decode_bulletin(tac: str, *, product: str) -> DecodeResult | None:
    """
    Internal helper ``_decode_bulletin``.

    Parameters
    ----------
    tac : object
        Argument ``tac``.
    product : object
        Argument ``product``.

    Returns
    -------
    object
        Return value.
    """
    if not _looks_like_ahl_bulletin(tac):
        return None
    if _bulletin_splitter is None:
        return None
    split_obj = _bulletin_splitter(tac, product)
    if split_obj is None:
        return None
    split = cast(_BulletinSplit, split_obj)

    segments: list[DecodeSegment] = []
    for start, end, code, explanation in _iter_ahl_heading(tac):
        segments.append(DecodeSegment(start=start, end=end, code=code, explanation=explanation))

    residuals: list[DecodeResidual] = []
    summaries: list[str] = []
    search_from = 0
    for report in split.reports:
        pos = tac.find(report, search_from)
        if pos < 0:
            pos = tac.find(report)
        if pos < 0:
            pos = 0
        inner = _shift_decode(_decode_single_report(report, product=product), pos)
        segments.extend(inner.segments)
        residuals.extend(inner.residuals)
        if inner.summary:
            summaries.append(inner.summary.rstrip("."))
        search_from = pos + len(report)

    segments.sort(key=lambda s: (s.start, s.end))
    n = split.meta.report_count
    numbered = " ".join(f"{i + 1}) {clause}." for i, clause in enumerate(summaries))
    summary = f"Bulletin {split.meta.ahl} ({n} report{'s' if n != 1 else ''}). {numbered}".strip()
    return DecodeResult(product=product, segments=segments, residuals=residuals, summary=summary)


def _decode_single_report(tac: str, *, product: str) -> DecodeResult:
    """
    Internal helper ``_decode_single_report``.

    Parameters
    ----------
    tac : object
        Argument ``tac``.
    product : object
        Argument ``product``.

    Returns
    -------
    object
        Return value.
    """
    tokens = _iter_tokens(tac)
    classify = _classify(product)
    seen: dict[str, int] = {}
    segments: list[DecodeSegment] = []
    explained: set[int] = set()

    if product in {"SIGMET", "AIRMET"}:
        heading = _LOOSE_AHL.match(tac.lstrip("\ufeff"))
        if heading is not None:
            lead = len(tac) - len(tac.lstrip("\ufeff"))
            start = lead + heading.start()
            end = lead + heading.end()
            segments.append(
                DecodeSegment(
                    start=start,
                    end=end,
                    code=tac[start:end],
                    explanation=(
                        f"Abbreviated heading {heading.group('ahl')} from "
                        f"{heading.group('cccc')} at {heading.group('yygggg')}"
                    ),
                )
            )
            for idx, (token_start, token_end, _token) in enumerate(tokens):
                if token_start >= start and token_end <= end:
                    explained.add(idx)

    # Advisory products: structured LABEL: value fields first (EV-030 / EV-099).
    if product in _ADVISORY_STRUCTURED:
        field_spans: list[tuple[int, int]] = []
        for start, end, code, explanation in _iter_advisory_ahl(tac, product=product):
            segments.append(DecodeSegment(start=start, end=end, code=code, explanation=explanation))
            field_spans.append((start, end))
        label_starts: list[int] = []
        for mark_start, mark_end, code, explanation, label_start in _iter_advisory_fields(tac, product=product):
            segments.append(DecodeSegment(start=mark_start, end=mark_end, code=code, explanation=explanation))
            field_spans.append((label_start, mark_end))
            label_starts.append(label_start)
        explained |= _token_indices_covering(tokens, field_spans)
        if label_starts:
            first_label = min(label_starts)
            for idx, (_token_start, token_end, _token) in enumerate(tokens):
                if token_end <= first_label:
                    explained.add(idx)

    for idx, (start, end, token) in enumerate(tokens):
        if idx in explained:
            continue
        explanation = classify(token, seen)
        if explanation is None and product in {"METAR", "SPECI"}:
            following = tokens[idx + 1][2] if idx + 1 < len(tokens) else ""
            explanation = _whole_miles(token, following)
        if explanation is None:
            continue
        segments.append(
            DecodeSegment(
                start=start,
                end=end,
                code=token,
                explanation=explanation,
            )
        )
        explained.add(idx)

    segments.sort(key=lambda s: (s.start, s.end))
    residuals = _coalesce_residuals(tokens, explained, tac)
    summary = _build_summary(product, segments, residuals)
    return DecodeResult(product=product, segments=segments, residuals=residuals, summary=summary)


def decode_single_report(tac: str, *, product: str) -> DecodeResult:
    """
    Decode one TAC report without bulletin or COLLECT dispatch.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (decode_single_report)
    2

    Parameters
    ----------
    tac : object
        Argument ``tac``.
    product : object
        Argument ``product``.

    Returns
    -------
    object
        Return value.
    """
    return _decode_single_report(tac, product=product)


def shift_decode(result: DecodeResult, offset: int) -> DecodeResult:
    """
    Translate segment offsets into a parent document string.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (shift_decode)
    2

    Parameters
    ----------
    result : object
        Argument ``result``.
    offset : object
        Argument ``offset``.

    Returns
    -------
    object
        Return value.
    """
    return _shift_decode(result, offset)


def _leading_report_product(tac: str) -> str | None:
    """
    Return the product keyword when the report itself starts with one.

    Parameters
    ----------
    tac : str
        Raw TAC text.

    Returns
    -------
    str | None
        Supported product id, or None when the first word is not one.
    """
    for line in tac.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        first = stripped.split(None, 1)[0].upper().rstrip(":")
        if first in _SUPPORTED:
            return first
        return None
    return None


def decode_tac(tac: str, *, product: str) -> DecodeResult:
    """
    Decode TAC text into ordered explanation segments and residuals.

    Parameters
    ----------
    tac :
        Raw TAC report text, a WMO AHL bulletin, or COLLECT / IWXXM XML with
        contained TAC or leaf fields.
    product :
        One of the F6 product ids or ``SWXA`` (case-insensitive).

    Returns
    -------
    DecodeResult
        ``segments`` for recognized groups; ``residuals`` for undecoded spans;
        ``summary`` plain-language paragraph (F9 / ADR-025).
        METAR/SPECI/TAF aim for rich segments; VAA/TCA/SWXA/VONA use structured
        LABEL fields (EV-030 / EV-099) with explicit residuals for leftovers (G4).
        Multi-report AHL bulletins are split so each report is decoded independently
        (heading is a bulletin-framing segment, not a product residual).
        COLLECT documents decode contained TAC when present, otherwise walk XML
        fields (ADR-045).

    Examples
    --------
    >>> 1 + 1  # docstring smoke (decode_tac)
    2
    """
    product_u = product.upper()
    if product_u in _SUPPORTED:
        leading = _leading_report_product(tac)
        if leading is not None:
            product_u = leading
    if product_u not in _SUPPORTED:
        # Entire body residual - unknown product still returns a well-formed shape.
        text = tac
        residuals = [DecodeResidual(start=0, end=len(text), text=text)] if text else []
        summary = _build_summary(product_u, [], residuals)
        return DecodeResult(product=product_u, segments=[], residuals=residuals, summary=summary)

    from tac_decoding.collect import try_decode_collect

    collected = try_decode_collect(tac, product=product_u)
    if collected is not None:
        return collected

    bulletin = _decode_bulletin(tac, product=product_u)
    if bulletin is not None:
        return bulletin
    return _decode_single_report(tac, product=product_u)


__all__ = [
    "DecodeResidual",
    "DecodeResult",
    "DecodeSegment",
    "decode_tac",
]
