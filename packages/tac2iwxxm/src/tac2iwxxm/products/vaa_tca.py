"""VAA / TCA TAC → IR parsers (F6.f annex3 path)."""

from __future__ import annotations

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
_MOV = re.compile(r"\bMOV\s+(?P<dir>N|NE|E|SE|S|SW|W|NW)\s+(?P<spd>\d+)\s*KT\b", re.IGNORECASE)
_FL_BAND = re.compile(r"\bFL(?P<lo>\d{2,3})/(?P<hi>\d{2,3})\b", re.IGNORECASE)
_SFC_FL = re.compile(r"\bSFC/FL(?P<hi>\d{2,3})\b", re.IGNORECASE)
_CLOUD_CHUNK = re.compile(
    r"(?P<level>(?:FL\d{2,3}/\d{2,3}|SFC/FL\d{2,3}))\s+"
    r"(?P<body>.*?)(?=(?:FL\d{2,3}/\d{2,3}|SFC/FL\d{2,3}|NO\s+VA\s+EXP|$))",
    re.IGNORECASE | re.DOTALL,
)
_DIR_DEG = {
    "N": 0,
    "NNE": 22,
    "NE": 45,
    "ENE": 67,
    "E": 90,
    "ESE": 112,
    "SE": 135,
    "SSE": 157,
    "S": 180,
    "SSW": 202,
    "SW": 225,
    "WSW": 247,
    "W": 270,
    "WNW": 292,
    "NW": 315,
    "NNW": 337,
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
    """Return ISO-8601 Zulu stamp from advisory DTG forms."""
    token = token.strip()
    m = _DTG_SHORT.search(token.replace(" ", ""))
    if m:
        return f"{m.group('yyyy')}-{m.group('mm')}-{m.group('dd')}T{m.group('hh')}:{m.group('mi')}:00Z"
    m2 = re.search(r"(?P<yyyy>\d{4})(?P<mm>\d{2})(?P<dd>\d{2})/(?P<hh>\d{2})(?P<mi>\d{2})Z", token)
    if m2:
        return f"{m2.group('yyyy')}-{m2.group('mm')}-{m2.group('dd')}T{m2.group('hh')}:{m2.group('mi')}:00Z"
    return None


def _day_hhmm_to_iso(token: str, *, issue_iso: str) -> str | None:
    """Map ``23/0100Z`` onto the issue year-month."""
    m = _DAY_HHMM.search(token.replace(" ", ""))
    if m is None:
        return None
    year = issue_iso[0:4]
    month = issue_iso[5:7]
    return f"{year}-{month}-{m.group('dd')}T{m.group('hh')}:{m.group('mi')}:00Z"


def _latlon(token: str, *, ndigits: int | None = 2) -> tuple[float, float] | None:
    m = _PSN.search(token)
    if m is None:
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
    if ndigits is None:
        return lat, lon
    return round(lat, ndigits), round(lon, ndigits)


def _point_to_pair(ns: str, lat: str, ew: str, lon: str) -> tuple[float, float]:
    lat_f = int(lat[0:2]) + int(lat[2:4]) / 60.0
    lon_f = int(lon[0:3]) + int(lon[3:5]) / 60.0
    if ns == "S":
        lat_f = -lat_f
    if ew == "W":
        lon_f = -lon_f
    return round(lat_f, 2), round(lon_f, 2)


def _pos_list(points: list[tuple[float, float]]) -> str:
    """Format closed LinearRing posList (TAC order; close to first point)."""
    if not points:
        return ""
    ring = list(points)
    if ring[0] != ring[-1]:
        ring.append(ring[0])
    return " ".join(f"{lat:.2f} {lon:.2f}" for lat, lon in ring)


def _parse_ash_clouds(blob: str) -> list[dict[str, Any]]:
    """Parse one or more FL/SFC ash-cloud polygons (+ optional MOV) from a field blob."""
    upper = " ".join(blob.split())
    if re.search(r"\bNO\s+VA\s+EXP\b", upper):
        return []
    clouds: list[dict[str, Any]] = []
    for match in _CLOUD_CHUNK.finditer(upper):
        level = match.group("level").upper()
        body = match.group("body")
        points = [
            _point_to_pair(m.group("ns"), m.group("lat"), m.group("ew"), m.group("lon")) for m in _POINT.finditer(body)
        ]
        if not points:
            continue
        cloud: dict[str, Any] = {"pos_list": _pos_list(points)}
        sfc = _SFC_FL.search(level)
        band = _FL_BAND.search(level)
        if sfc:
            cloud["lower"] = "GND"
            cloud["lower_ref"] = "SFC"
            cloud["upper_fl"] = int(sfc.group("hi"))
            cloud["upper_ref"] = "STD"
        elif band:
            cloud["lower_fl"] = int(band.group("lo"))
            cloud["upper_fl"] = int(band.group("hi"))
            cloud["lower_ref"] = "STD"
            cloud["upper_ref"] = "STD"
        mov = _MOV.search(body)
        if mov:
            cloud["motion_dir_deg"] = _DIR_DEG[mov.group("dir").upper()]
            cloud["motion_speed_kt"] = int(mov.group("spd"))
        clouds.append(cloud)
    return clouds


def _parse_eruption(details: str) -> tuple[str | None, str]:
    """Split ERUPTION AT DTG from residual eruptionDetails text."""
    text = " ".join(details.split())
    m = _ERUPTION_AT.search(text)
    if not m:
        return None, text
    return _parse_dtg(m.group("dtg")), m.group("rest").strip()


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

    eruption_date, eruption_details = _parse_eruption(fields.get("ERUPTION DETAILS", ""))

    obs_time = _day_hhmm_to_iso(fields.get("OBS VA DTG", ""), issue_iso=issue)
    observation_clouds = _parse_ash_clouds(fields.get("OBS VA CLD", ""))

    forecasts: list[dict[str, Any]] = []
    for hours in (6, 12, 18):
        key = f"FCST VA CLD +{hours} HR"
        raw = fields.get(key, "")
        if not raw:
            continue
        parts = " ".join(raw.split())
        time_iso = _day_hhmm_to_iso(parts, issue_iso=issue)
        if re.search(r"\bNO\s+VA\s+EXP\b", parts.upper()):
            forecasts.append(
                {
                    "hours": hours,
                    "time": time_iso,
                    "status": "NO_VOLCANIC_ASH_EXPECTED",
                    "clouds": [],
                }
            )
        else:
            # Drop leading day/time token before cloud levels.
            cloud_blob = re.sub(r"^\d{2}/\d{4}Z\s*", "", parts)
            forecasts.append(
                {
                    "hours": hours,
                    "time": time_iso,
                    "status": "PROVIDED",
                    "clouds": _parse_ash_clouds(cloud_blob),
                }
            )

    remarks = " ".join(fields.get("RMK", "").split())
    remarks_nil = not remarks or remarks.upper() == "NIL"

    next_adv = _parse_dtg(fields.get("NXT ADVISORY", "")) if fields.get("NXT ADVISORY") else None

    return {
        "ir_version": 1,
        "product": "VAA",
        # F26 theme V2 / TC-F26-006 - advisory root under product=vaa (never VolcanicAshSIGMET).
        "iwxxm_root": "VolcanicAshAdvisory",
        "issue_time": issue,
        "vaac": fields.get("VAAC", "UNKNOWN"),
        "volcano": fields.get("VOLCANO", "UNKNOWN"),
        "area": fields.get("AREA", ""),
        "advisory_number": fields.get("ADVISORY NR", ""),
        "information_source": fields.get("INFO SOURCE", ""),
        "eruption_details": eruption_details,
        "eruption_date": eruption_date,
        "lat": psn[0] if psn else None,
        "lon": psn[1] if psn else None,
        "source_elevation_m": elev_m,
        "observation_time": obs_time,
        "observation_clouds": observation_clouds,
        "forecasts": forecasts,
        "remarks": "" if remarks_nil else remarks,
        "remarks_nil": remarks_nil,
        "next_advisory_time": next_adv,
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
    psn = _latlon(obs, ndigits=None)
    obs_time = _day_hhmm_to_iso(obs, issue_iso=issue)
    max_wind = fields.get("MAX WIND", "")
    wind_m = re.search(r"(\d+)\s*MPS", max_wind.upper())
    pressure = fields.get("C", "")
    pressure_m = re.search(r"(\d+)\s*HPA", pressure.upper())

    cb_raw = " ".join(fields.get("CB", "").split())
    cb: dict[str, Any] | None = None
    if cb_raw.upper() == "NIL":
        cb = {"nil": True}
    else:
        cb_m = _CB_WI.search(cb_raw)
        if cb_m:
            cb = {
                "radius_nm": int(cb_m.group("rad")),
                "upper_fl": int(cb_m.group("fl")) if cb_m.group("fl") else None,
            }

    mov_raw = " ".join(fields.get("MOV", "").split())
    movement: dict[str, Any] | None = None
    mov_m = _MOV_TCA.search(mov_raw)
    if mov_m:
        uom_raw = (mov_m.group("uom") or "KMH").upper().replace("/", "")
        if uom_raw in {"KMH", "KMHR"}:
            speed_uom = "km/h"
        elif uom_raw == "KT":
            speed_uom = "[kn_i]"
        else:
            speed_uom = "m/s"
        movement = {
            "status": "MOVING",
            "direction_deg": _DIR_DEG[mov_m.group("dir").upper()],
            "speed": int(mov_m.group("spd")),
            "speed_uom": speed_uom,
        }
    elif re.search(r"\bSTNR\b", mov_raw.upper()):
        movement = {"status": "STATIONARY"}

    intst_raw = " ".join(fields.get("INTST CHANGE", "").split()).upper()
    intensity_change = _INTST_MAP.get(intst_raw)

    forecasts: list[dict[str, Any]] = []
    for hours in (6, 12, 18, 24):
        psn_key = f"FCST PSN +{hours} HR"
        wind_key = f"FCST MAX WIND +{hours} HR"
        psn_raw = fields.get(psn_key, "")
        if not psn_raw:
            continue
        parts = " ".join(psn_raw.split())
        time_iso = _day_hhmm_to_iso(parts, issue_iso=issue)
        fcst_psn = _latlon(parts, ndigits=None)
        wind_raw = fields.get(wind_key, "")
        wind_fm = re.search(r"(\d+)\s*MPS", wind_raw.upper())
        forecasts.append(
            {
                "hours": hours,
                "time": time_iso,
                "lat": fcst_psn[0] if fcst_psn else None,
                "lon": fcst_psn[1] if fcst_psn else None,
                "max_wind_mps": int(wind_fm.group(1)) if wind_fm else None,
            }
        )

    remarks = " ".join(fields.get("RMK", "").split())
    remarks_nil = not remarks or remarks.upper() == "NIL"

    nxt_raw = " ".join((fields.get("NXT MSG") or fields.get("NXT ADVISORY") or "").split())
    next_nil = bool(re.search(r"\bNO\s+MSG\s+EXP\b", nxt_raw.upper()))
    next_adv = None if next_nil else _parse_dtg(nxt_raw)

    return {
        "ir_version": 1,
        "product": "TCA",
        "issue_time": issue,
        "tcac": fields.get("TCAC", "UNKNOWN"),
        "tc_name": fields.get("TC", "UNKNOWN"),
        "advisory_number": fields.get("ADVISORY NR", ""),
        "observation_time": obs_time,
        "lat": psn[0] if psn else None,
        "lon": psn[1] if psn else None,
        "cb": cb,
        "movement": movement,
        "intensity_change": intensity_change,
        "max_wind_mps": int(wind_m.group(1)) if wind_m else None,
        "central_pressure_hpa": int(pressure_m.group(1)) if pressure_m else None,
        "forecasts": forecasts,
        "remarks": "" if remarks_nil else remarks,
        "remarks_nil": remarks_nil,
        "next_advisory_time": next_adv,
        "next_advisory_nil": next_nil,
        "movement_raw": mov_raw,
        "iwxxm_root": "TropicalCycloneAdvisory",
        "raw": text,
    }


__all__ = ["parse_tca", "parse_vaa"]
