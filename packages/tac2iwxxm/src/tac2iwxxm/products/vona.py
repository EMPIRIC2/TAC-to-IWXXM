"""VONA (Volcano Observatory Notice for Aviation) TAC → IR parser (F32 / EV-032)."""

from __future__ import annotations

import re
from typing import Any

_FIELD_LINE = re.compile(r"^(?P<key>[A-Z0-9 /+]+?):\s*(?P<val>.*)$")
_DTG_SHORT = re.compile(r"(?P<yyyy>\d{4})(?P<mm>\d{2})(?P<dd>\d{2})/(?P<hh>\d{2})(?P<mi>\d{2})Z")
_PSN = re.compile(r"(?P<ns>[NS])(?P<lat>\d{4,5})\s+(?P<ew>[EW])(?P<lon>\d{5,6})")

# G-VONA-2: originatingCentre AIXM designator is not in TAC - fixture/registry map.
_SVO_DESIGNATORS: dict[str, str] = {
    "KVERT": "UHPP",
}

_ACT_STATUS: dict[str, str] = {
    "NIL": "NIL",
    "UNKNOWN": "UNKNOWN",
    "DECREASED ACT": "DECREASED_ACTIVITY",
    "DECREASED_ACTIVITY": "DECREASED_ACTIVITY",
    "HEIGHTENED UNREST": "HEIGHTENED_UNREST",
    "HEIGHTENED_UNREST": "HEIGHTENED_UNREST",
    "ERUPTION ONGOING": "ERUPTION_ONGOING",
    "ERUPTION_ONGOING": "ERUPTION_ONGOING",
    "ERUPTION OCCURRED": "ERUPTION_OCCURRED",
    "ERUPTION_OCCURRED": "ERUPTION_OCCURRED",
}

_ELEV = re.compile(
    r"(?P<val>\d+(?:\.\d+)?)\s*(?P<uom>KM|M)\b",
    re.IGNORECASE,
)
_AHL_LINE = re.compile(r"^[A-Z]{2}[A-Z]{2}\d{2}\s+[A-Z]{4}\s+\d{6}(?:\s+[A-Z]{1,3})?\s*$")


def _fields(text: str) -> dict[str, str]:
    """Collect KEY: value pairs, joining indented continuation lines."""
    out: dict[str, str] = {}
    current_key: str | None = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        match = _FIELD_LINE.match(line.strip())
        if match and re.fullmatch(r"[A-Z0-9 /+]+", match.group("key").strip()):
            current_key = re.sub(r"\s+", " ", match.group("key").strip().upper())
            out[current_key] = match.group("val").strip()
            continue
        if current_key is not None:
            cont = line.strip()
            if cont:
                prev = out.get(current_key, "")
                out[current_key] = f"{prev} {cont}".strip() if prev else cont
    return out


def _parse_dtg(token: str) -> str | None:
    token = token.strip().replace(" ", "")
    m = _DTG_SHORT.search(token)
    if m:
        return f"{m.group('yyyy')}-{m.group('mm')}-{m.group('dd')}T{m.group('hh')}:{m.group('mi')}:00Z"
    return None


def _latlon(token: str, *, ndigits: int = 2) -> tuple[float, float] | None:
    m = _PSN.search(token)
    if m is None:
        return None
    lat_raw = m.group("lat")
    lon_raw = m.group("lon")
    if len(lat_raw) == 4:
        lat = int(lat_raw[0:2]) + int(lat_raw[2:4]) / 60.0
    else:
        lat = int(lat_raw[0:2]) + int(lat_raw[2:4]) / 60.0 + int(lat_raw[4:5]) / 600.0
    if len(lon_raw) == 5:
        lon = int(lon_raw[0:3]) + int(lon_raw[3:5]) / 60.0
    else:
        lon = int(lon_raw[0:3]) + int(lon_raw[3:5]) / 60.0
    if m.group("ns") == "S":
        lat = -lat
    if m.group("ew") == "W":
        lon = -lon
    return round(lat, ndigits), round(lon, ndigits)


def _strip_optional_ahl(tac: str) -> str:
    lines = tac.splitlines()
    if lines and _AHL_LINE.match(lines[0].strip()):
        return "\n".join(lines[1:])
    return tac


def _parse_elevation_m(token: str) -> float | None:
    """Return elevation in metres MSL from ``1536M AMSL`` / ``15KM AMSL``."""
    m = _ELEV.search(token.replace(",", ""))
    if m is None:
        return None
    value = float(m.group("val"))
    if m.group("uom").upper() == "KM":
        return value * 1000.0
    return value


def _parse_volcano(token: str) -> tuple[str, str | None]:
    parts = token.strip().split()
    if not parts:
        return "", None
    if len(parts) >= 2 and re.fullmatch(r"\d{5,6}", parts[-1]):
        return " ".join(parts[:-1]), parts[-1]
    return token.strip(), None


def _map_activity(token: str) -> str:
    cleaned = re.sub(r"\s+", " ", token.strip().upper())
    if cleaned in _ACT_STATUS:
        return _ACT_STATUS[cleaned]
    compact = cleaned.replace(" ", "_")
    if compact in _ACT_STATUS:
        return _ACT_STATUS[compact]
    raise ValueError(f"unknown VONA ACT STS token: {token!r}")


def _nilish(token: str) -> bool:
    return token.strip().upper() in {"", "NIL", "NONE"}


def parse_vona(tac: str, *, product: str = "VONA") -> dict[str, Any]:
    """
    Parse VONA TAC into IR for annex3 emit.

    Parameters
    ----------
    tac :
        Standalone labeled VONA report (optional WM AHL line).
    product :
        Must be ``VONA``.

    Returns
    -------
    dict[str, Any]
        Intermediate representation for ``emit_vona_annex3``.

    Raises
    ------
    ValueError
        When product is wrong or required fields are missing.
    """
    if product.upper() != "VONA":
        raise ValueError(f"VONA parser expected product VONA, found {product!r}")

    text = _strip_optional_ahl(tac)
    if not re.search(r"(?m)^\s*VONA\b", text):
        raise ValueError("VONA TAC missing VONA header")

    fields = _fields(text)
    issue = _parse_dtg(fields.get("DTG", ""))
    if not issue:
        raise ValueError("VONA missing/invalid DTG")

    volcano_raw = fields.get("VOLCANO", "").strip()
    if not volcano_raw:
        raise ValueError("VONA missing VOLCANO")
    volcano_name, iavcei = _parse_volcano(volcano_raw)

    psn = _latlon(fields.get("PSN", ""))
    if psn is None:
        raise ValueError("VONA missing/invalid PSN")

    svo = fields.get("SVO", "").strip()
    if not svo:
        raise ValueError("VONA missing SVO")

    current = fields.get("CURRENT COLOUR CODE", "").strip().upper()
    previous = fields.get("PREVIOUS COLOUR CODE", "").strip().upper()
    if not current:
        raise ValueError("VONA missing CURRENT COLOUR CODE")

    act_raw = fields.get("ACT STS", "").strip()
    activity = _map_activity(act_raw) if act_raw else "UNKNOWN"

    onset_raw = fields.get("ONSET", "").strip()
    dur_raw = fields.get("DUR", "").strip()
    onset_time = None if _nilish(onset_raw) else (_parse_dtg(onset_raw) or onset_raw)
    duration = None if _nilish(dur_raw) else dur_raw

    source_elev = _parse_elevation_m(fields.get("SOURCE ELEV", ""))
    ash_hgt = _parse_elevation_m(fields.get("VA CLD HGT", ""))

    designator = _SVO_DESIGNATORS.get(svo.upper())

    return {
        "product": "VONA",
        "iwxxm_root": "VolcanoObservatoryNoticeForAviation",
        "issue_time": issue,
        "phenomenon_time": issue,
        "volcano_name": volcano_name,
        "iavcei_number": iavcei,
        "position": {"lat": psn[0], "lon": psn[1]},
        "state_or_region": fields.get("AREA", "").strip(),
        "source_elevation_m": source_elev,
        "notice_number": fields.get("NOTICE NR", "").strip(),
        "current_colour": current,
        "previous_colour": previous or None,
        "svo": svo,
        "originating_centre_designator": designator,
        "activity_status": activity,
        "onset_time": onset_time,
        "duration": duration,
        "ash_cloud_height_m": ash_hgt,
        "height_source": fields.get("HGT SOURCE", "").strip() or None,
        "movement": fields.get("MOV", "").strip() or None,
        "contacts": fields.get("CTC", "").strip() or None,
        "remarks": fields.get("RMK", "").strip() or None,
        "next_notice": fields.get("NXT NOTICE", "").strip() or None,
    }


__all__ = ["parse_vona"]
