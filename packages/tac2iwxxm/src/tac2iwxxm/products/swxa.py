"""SWXA (Space Weather Advisory) TAC → IR parser (F28 / EV-029 M11)."""

from __future__ import annotations

import re
from typing import Any

_FIELD_LINE = re.compile(r"^(?P<key>[A-Z0-9 /+]+?):\s*(?P<val>.*)$")
_DTG_SHORT = re.compile(r"(?P<yyyy>\d{4})(?P<mm>\d{2})(?P<dd>\d{2})/(?P<hh>\d{2})(?P<mi>\d{2})Z")
_DAY_HHMM = re.compile(r"(?P<dd>\d{2})/(?P<hh>\d{2})(?P<mi>\d{2})Z")
_EFFECT_MAP = {
    "HF COM": "HF_COM",
    "HF_COM": "HF_COM",
    "SATCOM": "SATCOM",
    "GNSS": "GNSS",
    "RADIATION": "RADIATION",
}
_INTENSITY = frozenset({"SEV", "MOD"})
_LOCATION = frozenset(
    {
        "HNH",
        "MNH",
        "EQN",
        "EQS",
        "MSH",
        "HSH",
        "DAYLIGHT_SIDE",
        "DAYSIDE",
        "NIGHTSIDE",
        "N80",
        "N70",
        "N60",
    }
)


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
            if cont:  # pragma: no branch — blank lines already skipped above
                prev = out.get(current_key, "")
                out[current_key] = f"{prev} {cont}".strip() if prev else cont
    return out


def _parse_dtg(token: str) -> str | None:
    token = token.strip().replace(" ", "")
    m = _DTG_SHORT.search(token)
    if m:
        return f"{m.group('yyyy')}-{m.group('mm')}-{m.group('dd')}T{m.group('hh')}:{m.group('mi')}:00Z"
    return None


def _day_hhmm_to_iso(token: str, *, issue_iso: str) -> str | None:
    m = _DAY_HHMM.search(token.replace(" ", ""))
    if m is None:
        return None
    return f"{issue_iso[0:4]}-{issue_iso[5:7]}-{m.group('dd')}T{m.group('hh')}:{m.group('mi')}:00Z"


def _normalize_location(tok: str) -> str:
    upper = tok.upper()
    if upper == "DAYSIDE":
        return "DAYLIGHT_SIDE"
    return upper


def _parse_intensity_regions(body: str) -> list[dict[str, Any]]:
    """Parse ``SEV MNH EQN … MOD NIGHTSIDE`` into intensity groups."""
    tokens = body.split()
    groups: list[dict[str, Any]] = []
    current_intensity: str | None = None
    current_locs: list[str] = []
    for tok in tokens:
        upper = tok.upper()
        if upper in _INTENSITY:
            if current_intensity is not None and current_locs:
                groups.append({"intensity": current_intensity, "locations": list(current_locs)})
            current_intensity = upper
            current_locs = []
            continue
        # Skip bare coordinate / FL fragments for v1; location codes only.
        if upper in _LOCATION or re.fullmatch(r"[A-Z]{3}", upper):
            if current_intensity is None:
                current_intensity = "MOD"
            current_locs.append(_normalize_location(upper))
    if current_intensity is not None and current_locs:
        groups.append({"intensity": current_intensity, "locations": list(current_locs)})
    return groups


def _parse_obs_or_fcst(raw: str, *, issue_iso: str) -> dict[str, Any] | None:
    text = raw.strip()
    if not text:
        return None
    if re.search(r"\bNO\s+SWX\s+EXP\b", text, re.IGNORECASE):
        time_iso = _day_hhmm_to_iso(text, issue_iso=issue_iso)
        return {"time": time_iso, "no_swx_exp": True, "groups": []}
    time_iso = _day_hhmm_to_iso(text, issue_iso=issue_iso)
    # Drop leading dd/hhmmZ token before intensity/region grammar.
    body = _DAY_HHMM.sub("", text, count=1).strip()
    groups = _parse_intensity_regions(body)
    return {"time": time_iso, "no_swx_exp": False, "groups": groups}


def parse_swxa(tac: str, *, product: str = "SWXA") -> dict[str, Any]:
    """
    Parse Space Weather Advisory TAC into IR for annex3 emit.

    Parameters
    ----------
    tac :
        SWX ADVISORY text.
    product :
        Must be ``SWXA``.

    Returns
    -------
    dict[str, Any]
        Intermediate representation for ``emit_swxa_annex3``.

    Raises
    ------
    ValueError
        When product is wrong or required fields are missing.
    """
    if product.upper() != "SWXA":
        raise ValueError(f"SWXA parser expected product SWXA, found {product!r}")
    if not re.search(r"\bSWX\s+ADVISORY\b", tac, re.IGNORECASE):
        raise ValueError("SWXA TAC missing SWX ADVISORY header")

    fields = _fields(tac)
    issue = _parse_dtg(fields.get("DTG", ""))
    if not issue:
        raise ValueError("SWXA missing/invalid DTG")
    swxc = fields.get("SWXC", "").strip()
    if not swxc:
        raise ValueError("SWXA missing SWXC")

    effect_raw = fields.get("SWX EFFECT", "").strip().upper()
    effect = _EFFECT_MAP.get(effect_raw, effect_raw.replace(" ", "_") if effect_raw else "")
    advisory_number = fields.get("ADVISORY NR", "").strip()
    replaced = fields.get("NR RPLC", "").strip()
    replaced_list = [p for p in re.split(r"\s+", replaced) if p] if replaced else []

    observation = _parse_obs_or_fcst(fields.get("OBS SWX", ""), issue_iso=issue)
    forecasts: list[dict[str, Any]] = []
    for hours in (6, 12, 18, 24):
        key = f"FCST SWX +{hours} HR"
        parsed = _parse_obs_or_fcst(fields.get(key, ""), issue_iso=issue)
        if parsed is not None:
            parsed["horizon_hours"] = hours
            forecasts.append(parsed)

    rmk = fields.get("RMK", "").strip()
    remarks_nil = rmk.upper() == "NIL"
    nxt = fields.get("NXT ADVISORY", "").strip()
    next_nil = "NO FURTHER" in nxt.upper()
    next_time: str | None = None
    if not next_nil and nxt:
        # WILL BE ISSUED BY yyyymmdd/hhmmZ
        next_time = _parse_dtg(nxt)

    return {
        "product": "SWXA",
        "iwxxm_root": "SpaceWeatherAdvisory",
        "issue_time": issue,
        "swxc": swxc,
        "effect": effect,
        "advisory_number": advisory_number,
        "replaced_advisory_numbers": replaced_list,
        "observation": observation,
        "forecasts": forecasts,
        "remarks": None if remarks_nil else rmk,
        "remarks_nil": remarks_nil,
        "next_advisory_time": next_time,
        "next_advisory_nil": next_nil,
    }


__all__ = ["parse_swxa"]
