"""VAA / TCA TAC → IR parsers (F6.f annex3 path)."""

from __future__ import annotations

import re
from typing import Any

_FIELD = re.compile(r"^(?P<key>[A-Z0-9 /+]+?):\s*(?P<val>.+)$", re.MULTILINE)
_DTG = re.compile(r"(?:(?P<yyyy>\d{4}))?(?P<mmdd>\d{8})/(?P<hhmm>\d{4})Z")
_DTG_SHORT = re.compile(r"(?P<yyyy>\d{4})(?P<mm>\d{2})(?P<dd>\d{2})/(?P<hh>\d{2})(?P<mi>\d{2})Z")
_PSN = re.compile(r"(?P<ns>[NS])(?P<lat>\d{4,5})\s+(?P<ew>[EW])(?P<lon>\d{5,6})")


def _fields(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for match in _FIELD.finditer(text):
        key = re.sub(r"\s+", " ", match.group("key").strip().upper())
        out[key] = match.group("val").strip()
    return out


def _parse_dtg(token: str) -> str | None:
    """Return ISO-8601 Zulu stamp from advisory DTG forms."""
    token = token.strip()
    m = _DTG_SHORT.search(token.replace(" ", ""))
    if m:
        return f"{m.group('yyyy')}-{m.group('mm')}-{m.group('dd')}T{m.group('hh')}:{m.group('mi')}:00Z"
    # e.g. 20040925/1900Z
    m2 = re.search(r"(?P<yyyy>\d{4})(?P<mm>\d{2})(?P<dd>\d{2})/(?P<hh>\d{2})(?P<mi>\d{2})Z", token)
    if m2:
        return f"{m2.group('yyyy')}-{m2.group('mm')}-{m2.group('dd')}T{m2.group('hh')}:{m2.group('mi')}:00Z"
    return None


def _latlon(token: str) -> tuple[float, float] | None:
    m = _PSN.search(token.replace(" ", " "))
    if m is None:
        # N5403 E15927
        m = re.search(r"(?P<ns>[NS])(?P<lat>\d{4})\s+(?P<ew>[EW])(?P<lon>\d{5})", token)
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
    return round(lat, 2), round(lon, 2)


def parse_vaa(tac: str, *, product: str = "VAA") -> dict[str, Any]:
    """
    Parse a Volcanic Ash Advisory TAC into IR.

    Parameters
    ----------
    tac :
        VAA TAC text.
    product :
        Expected ``VAA``.
    """
    if product.upper() != "VAA":
        raise ValueError(f"product mismatch: expected VAA, found {product}")

    text = tac.strip()
    if "VA ADVISORY" not in text.upper():
        raise ValueError("unable to parse VAA: missing VA ADVISORY header")

    fields = _fields(text)
    dtg = fields.get("DTG")
    issue = _parse_dtg(dtg or "") if dtg else None
    if issue is None:
        raise ValueError("unable to parse VAA DTG")

    psn = _latlon(fields.get("PSN", ""))
    elev = fields.get("SOURCE ELEV", "")
    elev_m = None
    elev_match = re.search(r"(\d+)\s*M", elev.upper())
    if elev_match:
        elev_m = int(elev_match.group(1))

    return {
        "ir_version": 1,
        "product": "VAA",
        "issue_time": issue,
        "vaac": fields.get("VAAC", "UNKNOWN"),
        "volcano": fields.get("VOLCANO", "UNKNOWN"),
        "area": fields.get("AREA", ""),
        "advisory_number": fields.get("ADVISORY NR", ""),
        "information_source": fields.get("INFO SOURCE", ""),
        "eruption_details": fields.get("ERUPTION DETAILS", ""),
        "lat": psn[0] if psn else None,
        "lon": psn[1] if psn else None,
        "source_elevation_m": elev_m,
        "raw": text,
    }


def parse_tca(tac: str, *, product: str = "TCA") -> dict[str, Any]:
    """
    Parse a Tropical Cyclone Advisory TAC into IR.

    Parameters
    ----------
    tac :
        TCA TAC text.
    product :
        Expected ``TCA``.
    """
    if product.upper() != "TCA":
        raise ValueError(f"product mismatch: expected TCA, found {product}")

    text = tac.strip()
    if "TC ADVISORY" not in text.upper():
        raise ValueError("unable to parse TCA: missing TC ADVISORY header")

    fields = _fields(text)
    dtg = fields.get("DTG")
    issue = _parse_dtg(dtg or "") if dtg else None
    if issue is None:
        raise ValueError("unable to parse TCA DTG")

    obs = fields.get("OBS PSN", "")
    # 25/1800Z N2706 W07306 — take trailing lat/lon
    psn = _latlon(obs)
    max_wind = fields.get("MAX WIND", "")
    wind_m = re.search(r"(\d+)\s*MPS", max_wind.upper())
    pressure = fields.get("C", "")
    pressure_m = re.search(r"(\d+)\s*HPA", pressure.upper())

    return {
        "ir_version": 1,
        "product": "TCA",
        "issue_time": issue,
        "tcac": fields.get("TCAC", "UNKNOWN"),
        "tc_name": fields.get("TC", "UNKNOWN"),
        "advisory_number": fields.get("ADVISORY NR", ""),
        "lat": psn[0] if psn else None,
        "lon": psn[1] if psn else None,
        "max_wind_mps": int(wind_m.group(1)) if wind_m else None,
        "central_pressure_hpa": int(pressure_m.group(1)) if pressure_m else None,
        "movement": fields.get("MOV", ""),
        "raw": text,
    }


__all__ = ["parse_tca", "parse_vaa"]
