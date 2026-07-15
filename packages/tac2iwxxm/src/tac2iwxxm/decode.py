"""TAC decode/annotate segments for the operator decode panel (F7 / #702).

Produces ordered ``code`` | explanation segments with character offsets, plus
explicit residuals for undecoded spans (VAA/TCA may be residual-heavy — G4).
"""

from __future__ import annotations

import re
from typing import Callable

import msgspec

_SUPPORTED = frozenset({"AIRMET", "METAR", "SIGMET", "SPECI", "TAF", "VAA", "TCA"})

_WIND = re.compile(r"^(?:\d{3}|VRB)\d{2,3}(?:G\d{2,3})?(?:KT|MPS)$")
_VIS_SM = re.compile(r"^\d{1,2}SM$")
_VIS_M = re.compile(r"^\d{4}$")
_CLOUD = re.compile(r"^(?:FEW|SCT|BKN|OVC|SKC|CLR|NSC|NCD)\d{0,3}$")
_TEMP = re.compile(r"^M?\d{2}/M?\d{2}$")
_ALT = re.compile(r"^A\d{4}$")
_QNH = re.compile(r"^Q\d{3,4}$")
_TIME_Z = re.compile(r"^\d{6}Z$")
_STATION = re.compile(r"^[A-Z][A-Z0-9]{3}$")
_TAF_VALID = re.compile(r"^\d{4}/\d{4}$")
_WX = re.compile(
    r"^(?:\+|-|VC)?"
    r"(?:MI|PR|BC|DR|BL|SH|TS|FZ)?"
    r"(?:DZ|RA|SN|SG|IC|PL|GR|GS|UP|BR|FG|FU|VA|DU|SA|HZ|PY|PO|SQ|FC|SS|DS)+$"
)


class DecodeSegment(msgspec.Struct, frozen=True):
    """One annotated TAC span for the Code | Explanation panel."""

    start: int
    end: int
    code: str
    explanation: str


class DecodeResidual(msgspec.Struct, frozen=True):
    """Undecoded character span (explicit residuals — G4)."""

    start: int
    end: int
    text: str


class DecodeResult(msgspec.Struct, frozen=True):
    """Result of :func:`decode_tac`."""

    product: str
    segments: list[DecodeSegment] = msgspec.field(default_factory=list)
    residuals: list[DecodeResidual] = msgspec.field(default_factory=list)


def _iter_tokens(tac: str) -> list[tuple[int, int, str]]:
    """Return ``(start, end, token)`` for each non-whitespace run in ``tac``."""
    return [(m.start(), m.end(), m.group(0)) for m in re.finditer(r"\S+", tac)]


def _explain_metar_speci(token: str, *, product: str, seen: dict[str, int]) -> str | None:
    upper = token.upper()
    if upper in {"METAR", "SPECI"} and seen.get("rtype", 0) == 0:
        seen["rtype"] = 1
        label = "routine" if upper == "METAR" else "special"
        return f"Report type ({label} meteorological aerodrome report)"
    if upper == "COR":
        return "Correction indicator"
    if upper == "NIL":
        return "Nil report (no observation)"
    if upper == "CAVOK":
        return "Ceiling and visibility OK"
    if upper == "RMK":
        return "Remarks section"
    if upper == "AO1":
        return "Automated station without precipitation discriminator"
    if upper == "AO2":
        return "Automated station with precipitation discriminator"
    if upper.startswith("SLP") and len(upper) == 6 and upper[3:].isdigit():
        return "Sea-level pressure (FMH-1 SLP code)"
    if upper == "=" or token == "=":
        return "Report terminator"
    if _STATION.match(upper) and seen.get("station", 0) == 0 and seen.get("rtype", 0):
        seen["station"] = 1
        return "ICAO station location indicator"
    if _TIME_Z.match(upper):
        return "Observation day-hour-minute (DDHHMMZ)"
    if _WIND.match(upper):
        return "Surface wind group"
    if _VIS_SM.match(upper) or _VIS_M.match(upper):
        return "Prevailing visibility"
    if _CLOUD.match(upper):
        return "Cloud amount/height group"
    if _TEMP.match(upper):
        return "Temperature / dewpoint (°C)"
    if _ALT.match(upper):
        return "Altimeter setting (inHg)"
    if _QNH.match(upper):
        return "QNH (hPa)"
    if _WX.match(upper):
        return "Present weather group"
    if upper.startswith("PK") or upper == "WND":
        return "Peak wind remarks token"
    _ = product
    return None


def _explain_taf(token: str, *, seen: dict[str, int]) -> str | None:
    upper = token.upper()
    if upper == "TAF" and seen.get("rtype", 0) == 0:
        seen["rtype"] = 1
        return "Report type (terminal aerodrome forecast)"
    if upper in {"AMD", "COR"}:
        return "Amendment / correction indicator"
    if upper == "NIL":
        return "Nil forecast"
    if upper == "=":
        return "Report terminator"
    if _STATION.match(upper) and seen.get("station", 0) == 0:
        seen["station"] = 1
        return "ICAO station location indicator"
    if _TIME_Z.match(upper):
        return "Issue time (DDHHMMZ)"
    if _TAF_VALID.match(upper):
        return "Validity period (DDHH/DDHH)"
    if _WIND.match(upper):
        return "Forecast wind group"
    if _VIS_M.match(upper) or _VIS_SM.match(upper):
        return "Forecast visibility"
    if _CLOUD.match(upper):
        return "Forecast cloud group"
    if _ALT.match(upper) or _QNH.match(upper):
        return "Altimeter / QNH group"
    if upper.startswith(("FM", "TEMPO", "BECMG", "PROB")):
        return "Change / probability group"
    if _WX.match(upper):
        return "Forecast weather group"
    return None


def _explain_sigmet_airmet(token: str, *, product: str, seen: dict[str, int]) -> str | None:
    upper = token.upper()
    if upper == product and seen.get("rtype", 0) == 0:
        seen["rtype"] = 1
        return f"Report type ({product})"
    if upper == "=":
        return "Report terminator"
    if _STATION.match(upper) and seen.get("station", 0) == 0:
        seen["station"] = 1
        return "Originating FIR / location indicator"
    if re.match(r"^\d{6}/\d{6}$", upper):
        return "Validity period"
    if upper in {"OBSC", "EMBD", "FRQ", "SQL", "SEV", "MOD", "ISOL", "OCNL"}:
        return "Phenomenon intensity / distribution"
    if upper in {"TS", "ICE", "TURB", "MTW", "DS", "SS", "VA", "TC"}:
        return "Hazard phenomenon"
    return None


def _explain_advisory(token: str, *, product: str, seen: dict[str, int]) -> str | None:
    """Best-effort VAA/TCA keyword spans; most body stays residual (G4)."""
    upper = token.upper()
    if product == "VAA":
        if upper == "VA" and seen.get("va", 0) == 0:
            seen["va"] = 1
            return "Volcanic ash advisory marker"
        if upper == "ADVISORY" and seen.get("adv", 0) == 0:
            seen["adv"] = 1
            return "Advisory product header"
        if upper == "VAA":
            return "Volcanic ash advisory abbreviation"
    if product == "TCA":
        if upper == "TC" and seen.get("tc", 0) == 0:
            seen["tc"] = 1
            return "Tropical cyclone advisory marker"
        if upper == "ADVISORY" and seen.get("adv", 0) == 0:
            seen["adv"] = 1
            return "Advisory product header"
        if upper == "TCA":
            return "Tropical cyclone advisory abbreviation"
    if upper in {"DTG", "VOLCANO", "PSN", "AREA", "SUMMIT", "ADVISORY", "NR", "INFO"}:
        return f"{product} field label"
    return None


def _classify(
    product: str,
) -> Callable[[str, dict[str, int]], str | None]:
    if product in {"METAR", "SPECI"}:

        def _metar(tok: str, seen: dict[str, int]) -> str | None:
            return _explain_metar_speci(tok, product=product, seen=seen)

        return _metar
    if product == "TAF":

        def _taf(tok: str, seen: dict[str, int]) -> str | None:
            return _explain_taf(tok, seen=seen)

        return _taf
    if product in {"SIGMET", "AIRMET"}:

        def _haz(tok: str, seen: dict[str, int]) -> str | None:
            return _explain_sigmet_airmet(tok, product=product, seen=seen)

        return _haz
    if product in {"VAA", "TCA"}:

        def _adv(tok: str, seen: dict[str, int]) -> str | None:
            return _explain_advisory(tok, product=product, seen=seen)

        return _adv

    def _none(_tok: str, _seen: dict[str, int]) -> str | None:
        return None

    return _none


def _coalesce_residuals(
    tokens: list[tuple[int, int, str]],
    explained: set[int],
    tac: str,
) -> list[DecodeResidual]:
    """Merge adjacent unexplained tokens into residual runs."""
    residuals: list[DecodeResidual] = []
    i = 0
    while i < len(tokens):
        if i in explained:
            i += 1
            continue
        start = tokens[i][0]
        end = tokens[i][1]
        j = i + 1
        while j < len(tokens) and j not in explained:
            # Include intervening whitespace in residual text span.
            end = tokens[j][1]
            j += 1
        residuals.append(DecodeResidual(start=start, end=end, text=tac[start:end]))
        i = j
    return residuals


def decode_tac(tac: str, *, product: str) -> DecodeResult:
    """
    Decode TAC text into ordered explanation segments and residuals.

    Parameters
    ----------
    tac :
        Raw TAC report text.
    product :
        One of the seven F6 product ids (case-insensitive).

    Returns
    -------
    DecodeResult
        ``segments`` for recognized groups; ``residuals`` for undecoded spans.
        METAR/SPECI/TAF aim for rich segments; VAA/TCA are best-effort (G4).
    """
    product_u = product.upper()
    if product_u not in _SUPPORTED:
        # Entire body residual — unknown product still returns a well-formed shape.
        text = tac
        residuals = [DecodeResidual(start=0, end=len(text), text=text)] if text else []
        return DecodeResult(product=product_u, segments=[], residuals=residuals)

    tokens = _iter_tokens(tac)
    classify = _classify(product_u)
    seen: dict[str, int] = {}
    segments: list[DecodeSegment] = []
    explained: set[int] = set()

    for idx, (start, end, token) in enumerate(tokens):
        explanation = classify(token, seen)
        if explanation is None:
            continue
        segments.append(
            DecodeSegment(
                start=start,
                end=end,
                code=token,
                explanation=explanation,
            )
        )
        explained.add(idx)

    residuals = _coalesce_residuals(tokens, explained, tac)
    return DecodeResult(product=product_u, segments=segments, residuals=residuals)


__all__ = [
    "DecodeResidual",
    "DecodeResult",
    "DecodeSegment",
    "decode_tac",
]
