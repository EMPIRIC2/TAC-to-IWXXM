"""TAF TAC → IR parser (F6.c annex3 path / F25 W3)."""

from __future__ import annotations

import re
from typing import Any

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
_VIS_SM = re.compile(r"\b(?P<mod>P)?(?P<vis>\d{1,2})SM\b")
_NCLWS = re.compile(r"\bWS(?P<height>\d{3})/(?P<dir>\d{3})(?P<spd>\d{2,3})KT\b")
_CLOUD = re.compile(r"\b(?P<amt>FEW|SCT|BKN|OVC)(?P<base>\d{3})(?P<ctype>CB|TCU)?\b")
_ALT_INHG = re.compile(r"\bA(?P<alt>\d{4})\b")
_NIL = re.compile(r"\bNIL\b")
_CNL = re.compile(r"\bCNL\b")
_CAVOK = re.compile(r"\bCAVOK\b")
_BECMG = re.compile(
    r"\bBECMG\s+(?P<from>\d{4})/(?P<to>\d{4})\s+(?P<body>.*)$",
    re.DOTALL,
)
_TEMPO = re.compile(
    r"\bTEMPO\s+(?P<from>\d{4})/(?P<to>\d{4})\s+(?P<body>.*)$",
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
    r"(?:DZ|RA|SN|SG|PL|GR|GS|UP|BR|FG|FU|VA|DU|SA|HZ|PY|PO|SQ|FC|SS|DS|IC)+"
    r")(?![A-Z0-9/])"
)
_CHANGE_GROUP = re.compile(
    r"\b(?:BECMG\s+\d{4}/\d{4}|TEMPO\s+\d{4}/\d{4}|FM\d{6})\b.*?(?=\b(?:BECMG\s+\d{4}/\d{4}|TEMPO\s+\d{4}/\d{4}|FM\d{6})\b|$)",
    re.DOTALL,
)


def _modifier_flags(joined: str) -> dict[str, bool]:
    upper = joined.upper()
    # "TAF AMD …" / "TAF COR …" (not station-embedded).
    return {
        "amendment": bool(re.search(r"\bTAF\s+AMD\b", upper)),
        "correction": bool(re.search(r"\bTAF\s+COR\b", upper)),
    }


def _parse_clouds(text: str) -> list[dict[str, Any]]:
    layers: list[dict[str, Any]] = []
    for c in _CLOUD.finditer(text):
        layer: dict[str, Any] = {
            "amount": c.group("amt"),
            "base_ft": int(c.group("base")) * 100,
        }
        if c.group("ctype"):
            layer["cloud_type"] = c.group("ctype")
        layers.append(layer)
    return layers


def _parse_wind(text: str, target: dict[str, Any]) -> None:
    wind = _WIND.search(text)
    if wind is None:
        return
    target["wind_variable"] = wind.group("dir") == "VRB"
    if not target["wind_variable"]:
        target["wind_dir_deg"] = int(wind.group("dir"))
    spd = int(wind.group("spd"))
    if wind.group("uom") == "MPS":
        target["wind_speed_mps"] = float(spd)
        if wind.group("gust"):
            target["wind_gust_mps"] = float(int(wind.group("gust")))
    else:
        target["wind_speed_kt"] = spd
        if wind.group("gust"):
            target["wind_gust_kt"] = int(wind.group("gust"))


def _parse_wx(text: str) -> list[str]:
    return [m.group("wx") for m in _WX_TOKEN.finditer(text)]


_CODE_CA_PRESENT_FORECAST_WEATHER = "https://dd.weather.gc.ca/today/aviation/iwxxm/code-ca/present_and_forecast_weather"


def _ca_forecast_weather_hrefs(wx_tokens: list[str]) -> list[str]:
    """Map MANAIR TAF weather groups to MSC ``present_and_forecast_weather`` hrefs."""
    hrefs: list[str] = []
    for token in wx_tokens:
        if token.upper() == "IC":
            hrefs.append(f"{_CODE_CA_PRESENT_FORECAST_WEATHER}/IC")
    return hrefs


def _parse_nclws(text: str) -> dict[str, Any] | None:
    """Parse MANAIR low-level wind shear group ``WShhh/dddffKT``."""
    match = _NCLWS.search(text)
    if match is None:
        return None
    return {
        "layer_top_ft": int(match.group("height")) * 100,
        "wind_dir_deg": int(match.group("dir")),
        "wind_speed_kt": int(match.group("spd")),
    }


def _parse_forecast_body(text: str, *, cavok_ok: bool = True) -> dict[str, Any]:
    """Parse wind / vis / cloud / weather from a base or change-group body."""
    out: dict[str, Any] = {}
    if cavok_ok and _CAVOK.search(text):
        out["cavok"] = True
        return out
    _parse_wind(text, out)
    vis_sm = _VIS_SM.search(text)
    if vis_sm is not None:
        out["visibility_sm"] = int(vis_sm.group("vis"))
        out["visibility_above"] = vis_sm.group("mod") == "P"
    else:
        vis = _VIS_M.search(text)
        if vis is not None:
            metres = int(vis.group("vis"))
            out["visibility_m"] = 10000 if metres >= 9999 else metres
            out["visibility_above"] = metres >= 9999
    clouds = _parse_clouds(text)
    if clouds:
        out["clouds"] = clouds
        out["cloud_amount"] = clouds[0]["amount"]
        out["cloud_base_ft"] = clouds[0]["base_ft"]
    wx = _parse_wx(text)
    if wx:
        out["weather"] = wx
    return out


def _taf_day_hour_stamp(ir: dict[str, Any], ddhh: str, *, minute: int = 0) -> str:
    prefix = "2012-08" if ir.get("station") == "YUDO" else "2023-06"
    day = int(ddhh[0:2])
    hour = int(ddhh[2:4])
    return f"{prefix}-{day:02d}T{hour:02d}:{minute:02d}:00Z"


def _taf_valid_end_stamp(ir: dict[str, Any]) -> str:
    prefix = "2012-08" if ir.get("station") == "YUDO" else "2023-06"
    return f"{prefix}-{int(ir['valid_to_day']):02d}T{int(ir['valid_to_hour']):02d}:00:00Z"


def _parse_change_groups(ir: dict[str, Any], body: str) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for raw in _CHANGE_GROUP.findall(body):
        chunk = raw.strip()
        becmg = _BECMG.match(chunk)
        if becmg is not None:
            change = {
                "change_indicator": "BECOMING",
                "phenomenon_begin": _taf_day_hour_stamp(ir, becmg.group("from")),
                "phenomenon_end": _taf_day_hour_stamp(ir, becmg.group("to")),
            }
            change.update(_parse_forecast_body(becmg.group("body")))
            changes.append(change)
            continue
        tempo = _TEMPO.match(chunk)
        if tempo is not None:
            change = {
                "change_indicator": "TEMPORARY_FLUCTUATIONS",
                "phenomenon_begin": _taf_day_hour_stamp(ir, tempo.group("from")),
                "phenomenon_end": _taf_day_hour_stamp(ir, tempo.group("to")),
            }
            change.update(_parse_forecast_body(tempo.group("body")))
            changes.append(change)
            continue
        fm = _FM.match(chunk)
        if fm is not None:
            stamp = fm.group("stamp")
            change = {
                "change_indicator": "FROM",
                "phenomenon_begin": (f"2012-08-{int(stamp[0:2]):02d}T{int(stamp[2:4]):02d}:{int(stamp[4:6]):02d}:00Z"),
                "phenomenon_end": _taf_valid_end_stamp(ir),
            }
            change.update(_parse_forecast_body(fm.group("body")))
            changes.append(change)
    return changes


def parse_taf(tac: str, *, product: str = "TAF") -> dict[str, Any]:
    """
    Parse a single TAF TAC report into a versioned IR dict.

    Parameters
    ----------
    tac :
        TAC text (optional leading ``TAF`` keyword).
    product :
        Expected ``TAF``.

    Returns
    -------
    dict
        Intermediate representation for annex3 emit.

    Raises
    ------
    ValueError
        When the product mismatches or required groups are missing.
    """
    if product.upper() != "TAF":
        raise ValueError(f"product mismatch: expected TAF, found {product}")

    text = tac.strip().rstrip("=").strip()
    # Drop bulletin AHL if present (first line without TAF/station pattern).
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    joined = " ".join(lines)
    if not joined.upper().startswith("TAF"):
        joined = f"TAF {joined}"

    mods = _modifier_flags(joined)

    match = _TAF_NIL_ONLY.match(joined)
    if match is not None:
        issue = match.group("issue")
        return {
            "ir_version": 1,
            "product": "TAF",
            "station": match.group("station"),
            "issue_day": int(issue[0:2]),
            "issue_hour": int(issue[2:4]),
            "issue_minute": int(issue[4:6]),
            "nil": True,
            "amendment": mods["amendment"],
            "correction": mods["correction"],
            "raw": joined,
        }

    match = _TAF.match(joined)
    if match is None:
        raise ValueError("unable to parse TAF header")

    issue = match.group("issue")
    body = match.group("body") or ""
    valid_from = match.group("valid_from")
    valid_to = match.group("valid_to")
    if valid_from is None or valid_to is None:
        if not _NIL.search(body):
            raise ValueError("unable to parse TAF header")
        return {
            "ir_version": 1,
            "product": "TAF",
            "station": match.group("station"),
            "issue_day": int(issue[0:2]),
            "issue_hour": int(issue[2:4]),
            "issue_minute": int(issue[4:6]),
            "nil": True,
            "amendment": mods["amendment"],
            "correction": mods["correction"],
            "raw": joined,
        }

    ir: dict[str, Any] = {
        "ir_version": 1,
        "product": "TAF",
        "station": match.group("station"),
        "issue_day": int(issue[0:2]),
        "issue_hour": int(issue[2:4]),
        "issue_minute": int(issue[4:6]),
        "valid_from_day": int(valid_from[0:2]),
        "valid_from_hour": int(valid_from[2:4]),
        "valid_to_day": int(valid_to[0:2]),
        "valid_to_hour": int(valid_to[2:4]),
        "nil": bool(_NIL.search(body)),
        "cancel": bool(_CNL.search(body)),
        "cavok": bool(_CAVOK.search(body)),
        "amendment": mods["amendment"],
        "correction": mods["correction"],
        "raw": joined,
    }

    if ir["nil"] or ir["cancel"]:
        return ir

    # Split base body from change groups.
    first_change = re.search(r"\b(?:BECMG\s+\d{4}/\d{4}|TEMPO\s+\d{4}/\d{4}|FM\d{6})\b", body)
    base_body = body if first_change is None else body[: first_change.start()]
    change_body = "" if first_change is None else body[first_change.start() :]

    base = _parse_forecast_body(base_body, cavok_ok=True)
    ir.update(base)
    if ir.get("cavok"):
        ir["cavok"] = True

    nclws = _parse_nclws(base_body)
    if nclws is not None:
        ir["nclws"] = nclws

    wx_hrefs = _ca_forecast_weather_hrefs(list(ir.get("weather") or []))
    if wx_hrefs:
        ir["ca_forecast_weather_hrefs"] = wx_hrefs

    alt = _ALT_INHG.search(base_body)
    if alt is not None:
        # US TAF forecast lowest altimeter (hundredths inHg).
        ir["forecast_altimeter_inhg"] = int(alt.group("alt")) / 100.0

    if change_body:
        changes = _parse_change_groups(ir, change_body)
        if changes:
            ir["change_forecasts"] = changes

    return ir


__all__ = ["parse_taf"]
