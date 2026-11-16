"""SIGMET/AIRMET token explainers.

[Corpus: product §F9]
"""

from __future__ import annotations

import re

from tac_decoding.decode_format import _fmt_valid_period
from tac_decoding.decode_geo import (
    _boundary_points,
    _coord_token,
    _in_convective_area,
    _lat_lon_phrase,
)
from tac_decoding.decode_patterns import *
from tac_decoding.decode_tokens import _navaid_chain
from tac_decoding.glossary import explain_glossary_token, meaning_for, resolve_location_name


def _explain_sigmet_airmet(token: str, *, product: str, seen: dict[str, int]) -> str | None:
    """
    Internal helper ``_explain_sigmet_airmet``.

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
    # Drop a lone report-style trailing period, but keep ellipsis (``…`` / ``...``).
    if re.search(r"(?<!\.)\.$", upper):
        upper = upper[:-1]
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
    if _BBB_AMENDMENT.match(upper):
        return f"Amendment ({upper})"
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
        return _fmt_valid_period(
            day1=int(m.group("d1")),
            hour1=m.group("h1"),
            minute1=m.group("m1"),
            day2=int(m.group("d2")),
            hour2=m.group("h2"),
            minute2=m.group("m2"),
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
        if upper not in _CYCLONE_NAME_RESERVED and _CYCLONE_NAME.match(upper) and not meaning_for(upper.split("-")[0]):
            return f"Tropical cyclone ({upper})"
        if upper == "CENTRE":
            return "Centre"
        if upper == "CENTER":
            return "Center"
    if upper == "REF":
        seen["ref"] = 1
        return "Reference"
    if upper == "INTL":
        return "International"
    if upper == "SERIES":
        return "Series"
    if upper in _SIGMET_SERIES and seen.get("ref"):
        return f"Referenced SIGMET series ({upper.capitalize()})"

    if upper == "LINE":
        seen["line"] = 1
        return "Line of coordinates"
    if upper == "WIDE":
        return "Wide"
    if upper == "NM" and seen.get("line"):
        return "Nautical miles"
    if upper.isdigit() and seen.get("line") and len(upper) <= 3 and not seen.get("line_width"):
        seen["line_width"] = 1
        return f"Line width {int(upper)}"
    if upper == "HAIL":
        seen["hail_size"] = 1
        return "Hail"
    if upper == "GUSTS":
        return "Gusts"
    if upper == "TORNADOES":
        seen["hail_size"] = 1
        return "Tornadoes possible"
    # Before ICAO/FIR matching: POSS is a 4-letter token that would otherwise
    # look like a location indicator on US convective hazard trails.
    if upper == "POSS":
        return "Possible"
    if upper.isdigit() and len(upper) <= 2 and seen.get("hail_size"):
        return f"{int(upper)} inch hail"
    if m := _SIG_WIND_RANGE.match(upper):
        unit = _SIG_SPEED_UNIT.get(m.group("unit"), m.group("unit").lower())
        return f"Speed {int(m.group('a'))} to {int(m.group('b'))} {unit}"
    if _SIG_TRAIL_DOTS.match(upper):
        return "Truncated text"
    if upper == "FL":
        seen["fl_expect"] = 1
        return "Flight level"
    if seen.get("fl_expect") and upper.isdigit() and 2 <= len(upper) <= 3:
        seen["fl_expect"] = 0
        return f"Flight level {int(upper)}"

    # MWO designator often carries a trailing hyphen (``YUSO-``).
    icao = upper.rstrip("-")
    if _STATION.match(icao) and icao not in {"LINE", "WIDE", "AREA", "HAIL", "GUSTS"}:
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

    # FIR proper name (e.g. SHANLON, ROSTOV-NA-DONU) when not a known glossary hazard.
    fir_name = upper.replace("-", "")
    if (
        fir_name.isalpha()
        and len(upper) >= 2
        and seen.get("station")
        and not meaning_for(upper.split("-")[0])
        and (not seen.get("fir_name") or seen.get("name_open") or seen.get("after_fir"))
    ):
        seen["fir_name"] = 1
        seen["name_open"] = 1
        seen["after_fir"] = 0
        return f"FIR name ({upper})"

    if m := _ELLIPSIS_HAZARD.match(upper):
        seen["hail_size"] = 1
        head = m.group("head").capitalize()
        tail = m.group("tail")
        if tail:
            return f"{head} and {tail.lower()} possible"
        return f"{head} possible"
    if _IN_WIND_ELLIPSIS.match(upper):
        seen["hail_size"] = 1
        return "Hail size in inches; wind gusts follow"
    if upper == "TO" and seen.get("hail_size"):
        return "To"
    if upper.startswith("IN") and seen.get("hail_size") and not _IN_WIND_ELLIPSIS.match(upper):
        return "Inches"

    # Glossary-backed intensity / hazard / movement tokens (F9 deepen).
    gloss = explain_glossary_token(upper)
    if gloss:
        return gloss
    bare = upper.strip("()")
    if bare and bare != upper:
        return explain_glossary_token(bare)
    return None
