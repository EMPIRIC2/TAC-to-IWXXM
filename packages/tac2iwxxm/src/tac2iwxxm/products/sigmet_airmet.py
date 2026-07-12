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

# Common phenomenon tokens → WMO codelist local name.
_SIG_PHENOMENA = (
    ("OBSC TS", "OBSC_TS"),
    ("EMBD TS", "EMBD_TS"),
    ("FRQ TS", "FRQ_TS"),
    ("SQL TS", "SQL_TS"),
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
    return {
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
