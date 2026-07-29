"""SIGMET / AIRMET TAC → IR parsers (F6.d annex3 path)."""

from __future__ import annotations

import re
from typing import Any

_SIGMET = re.compile(
    r"^(?P<fir>[A-Z]{4})\s+SIGMET\s+(?P<seq>\d+)\s+VALID\s+"
    r"(?P<from>\d{6})/(?P<to>\d{6})\s+(?P<mwo>[A-Z]{4})-\s*(?P<body>.*)$",
    re.DOTALL | re.IGNORECASE,
)
_AIRMET = re.compile(
    r"^(?P<fir>[A-Z]{4})\s+AIRMET\s+(?P<seq>\d+)\s+VALID\s+"
    r"(?P<from>\d{6})/(?P<to>\d{6})\s+(?P<mwo>[A-Z]{4})-\s*(?P<body>.*)$",
    re.DOTALL | re.IGNORECASE,
)
_CNL = re.compile(
    r"\bCNL\s+SIGMET\s+(?P<cnl_seq>\d+)\s+(?P<cnl_from>\d{6})/(?P<cnl_to>\d{6})\b",
    re.IGNORECASE,
)
_MOV = re.compile(
    r"\bMOV\s+(?P<dir>N|NE|E|SE|S|SW|W|NW)\s+(?P<spd>\d+)\s*KT\b",
    re.IGNORECASE,
)
_TOP_FL = re.compile(r"\bTOP\s+(?:ABV\s+|BLW\s+)?FL(?P<fl>\d{2,3})\b", re.IGNORECASE)
_SE_BOX = re.compile(
    r"\bS OF N(?P<lat>\d{1,2})\s+AND E OF W(?P<lon>\d{1,3})\b",
    re.IGNORECASE,
)
_POINT = re.compile(
    r"\bN(?P<lat_deg>\d{2})(?P<lat_min>\d{2})(?:\d{2})?\s+"
    r"(?P<lon_hemi>[EW])(?P<lon_deg>\d{3})(?P<lon_min>\d{2})(?:\d{2})?\b",
    re.IGNORECASE,
)
_FL_BAND = re.compile(r"\bFL(?P<lo>\d{2,3})/(?P<hi>\d{2,3})\b", re.IGNORECASE)
_SINGLE_FL = re.compile(r"\bFL(?P<fl>\d{2,3})\b", re.IGNORECASE)

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
    ("ISOL TS", "ISOL_TS"),
    ("OCNL TS", "OCNL_TS"),
    ("FRQ TS", "FRQ_TS"),
    ("MTW", "MTW"),
    ("TS", "TS"),
)

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


def _detect_intensity(body: str) -> str:
    upper = body.upper()
    for token, code in _INTENSITY.items():
        if re.search(rf"\b{token}\b", upper):
            return code
    return "NO_CHANGE"


def _enrich_sigmet_body(ir: dict[str, Any], body: str) -> None:
    """Attach G1 exceptional-rule fields from the SIGMET body (F23 / #733)."""
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
        ir.pop("phenomenon", None)
        return

    ir["intensity_change"] = _detect_intensity(body)
    ir["stationary"] = bool(re.search(r"\bSTNR\b", upper))

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

    point = _POINT.search(body)
    if point is not None:
        lat = int(point.group("lat_deg")) + int(point.group("lat_min")) / 60.0
        lon = int(point.group("lon_deg")) + int(point.group("lon_min")) / 60.0
        if point.group("lon_hemi").upper() == "W":
            lon = -lon
        ir["geometry"] = {"kind": "point", "lat": lat, "lon": lon}


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

    text = _normalize(tac)
    match = _SIGMET.match(text)
    if match is None:
        raise ValueError("unable to parse SIGMET header")

    body = match.group("body")
    from_d, from_h, from_m = _parse_valid(match.group("from"))
    to_d, to_h, to_m = _parse_valid(match.group("to"))
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
        "fir_name": "SHANLON FIR/UIR" if "SHANLON" in body.upper() else match.group("fir").upper(),
        "raw": text,
    }
    _enrich_sigmet_body(ir, body)
    # Content-selected IWXXM root under product=sigmet (E19-13 / F23 V2 / TC-F23-006).
    if ir.get("phenomenon") == "VA":
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

    text = _normalize(tac)
    match = _AIRMET.match(text)
    if match is None:
        raise ValueError("unable to parse AIRMET header")

    body = match.group("body")
    from_d, from_h, from_m = _parse_valid(match.group("from"))
    to_d, to_h, to_m = _parse_valid(match.group("to"))
    return {
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


__all__ = ["parse_airmet", "parse_sigmet"]
