"""Advisory (VAA/TCA/SWXA/VONA) token explainers and AHL helpers.

[Corpus: product §F9]
"""

from __future__ import annotations

import re

from tac_decoding.decode_patterns import *
from tac_decoding.glossary import explain_glossary_token


def _explain_advisory(token: str, *, product: str, seen: dict[str, int]) -> str | None:
    """
    Internal helper ``_explain_advisory``.

    Parameters
    ----------
    token : str
        Argument ``token``.

    product : str
        Argument ``product``.

    seen : dict[str, int]
        Argument ``seen``.

    Returns
    -------
    str | None
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
    product : str
        Argument ``product``.

    Returns
    -------
    list[tuple[re.Pattern[str], str]]
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
    label : str
        Argument ``label``.

    title_template : str
        Argument ``title_template``.

    match : re.Match[str]
        Argument ``match``.

    Returns
    -------
    str
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
_AHL_BBB_TOKEN = re.compile(r"^(?:AA|CC|RR)[A-X]\b")


def _iter_ahl_heading(tac: str) -> list[tuple[int, int, str, str]]:
    """
    Internal helper ``_iter_ahl_heading``.

    Parameters
    ----------
    tac : str
        Argument ``tac``.

    Returns
    -------
    list[tuple[int, int, str, str]]
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
    segments: list[tuple[int, int, str, str]] = [(start, end, code, explanation)]
    # Optional WMO BBB after YYGGgg (CCx / RRx / AAx). Bulletin split consumes the
    # heading line including BBB, so decode must emit the BBB token explicitly.
    rest = tac[end:]
    space = len(rest) - len(rest.lstrip(" \t"))
    bbb_at = end + space
    bbb_m = _AHL_BBB_TOKEN.match(tac[bbb_at:])
    if bbb_m is not None:
        bbb = bbb_m.group(0)
        bbb_end = bbb_at + len(bbb)
        if bbb.startswith("RR"):
            bbb_explanation = f"Delayed report ({bbb})"
        elif bbb.startswith("CC"):
            bbb_explanation = f"Correction ({bbb})"
        else:
            bbb_explanation = f"Amendment ({bbb})"
        segments.append((bbb_at, bbb_end, bbb, bbb_explanation))
    return segments


def _iter_advisory_ahl(tac: str, *, product: str) -> list[tuple[int, int, str, str]]:
    """
    Internal helper ``_iter_advisory_ahl``.

    Parameters
    ----------
    tac : str
        Argument ``tac``.

    product : str
        Argument ``product``.

    Returns
    -------
    list[tuple[int, int, str, str]]
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
