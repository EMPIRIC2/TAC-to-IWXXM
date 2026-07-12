"""TAF TAC → IR parser (F6.c annex3 path)."""

from __future__ import annotations

import re
from typing import Any

_TAF = re.compile(
    r"^(?:TAF\s+)?(?:AMD\s+|COR\s+)?(?P<station>[A-Z][A-Z0-9]{3})\s+"
    r"(?P<issue>\d{6})Z\s+(?P<valid_from>\d{4})/(?P<valid_to>\d{4})\b(?P<body>.*)$",
    re.DOTALL,
)
_WIND = re.compile(r"\b(?P<dir>\d{3}|VRB)(?P<spd>\d{2,3})(?:G(?P<gust>\d{2,3}))?(?P<uom>KT|MPS)\b")
_VIS_M = re.compile(r"\b(?P<vis>\d{4})\b")
_CLOUD = re.compile(r"\b(?P<amt>FEW|SCT|BKN|OVC)(?P<base>\d{3})\b")
_ALT_INHG = re.compile(r"\bA(?P<alt>\d{4})\b")
_NIL = re.compile(r"\bNIL\b")


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

    match = _TAF.match(joined)
    if match is None:
        raise ValueError("unable to parse TAF header")

    issue = match.group("issue")
    body = match.group("body")
    ir: dict[str, Any] = {
        "ir_version": 1,
        "product": "TAF",
        "station": match.group("station"),
        "issue_day": int(issue[0:2]),
        "issue_hour": int(issue[2:4]),
        "issue_minute": int(issue[4:6]),
        "valid_from_day": int(match.group("valid_from")[0:2]),
        "valid_from_hour": int(match.group("valid_from")[2:4]),
        "valid_to_day": int(match.group("valid_to")[0:2]),
        "valid_to_hour": int(match.group("valid_to")[2:4]),
        "nil": bool(_NIL.search(body)),
        "raw": joined,
    }

    if ir["nil"]:
        return ir

    wind = _WIND.search(body)
    if wind is not None:
        ir["wind_variable"] = wind.group("dir") == "VRB"
        if not ir["wind_variable"]:
            ir["wind_dir_deg"] = int(wind.group("dir"))
        spd = int(wind.group("spd"))
        if wind.group("uom") == "MPS":
            ir["wind_speed_mps"] = float(spd)
        else:
            ir["wind_speed_kt"] = spd

    vis = _VIS_M.search(body)
    if vis is not None:
        ir["visibility_m"] = int(vis.group("vis"))

    cloud = _CLOUD.search(body)
    if cloud is not None:
        ir["cloud_amount"] = cloud.group("amt")
        ir["cloud_base_ft"] = int(cloud.group("base")) * 100

    alt = _ALT_INHG.search(body)
    if alt is not None:
        # US TAF forecast lowest altimeter (hundredths inHg).
        ir["forecast_altimeter_inhg"] = int(alt.group("alt")) / 100.0

    return ir


__all__ = ["parse_taf"]
