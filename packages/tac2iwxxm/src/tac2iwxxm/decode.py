"""TAC decode/annotate segments for the operator decode panel (F7 / #702).

Produces ordered ``code`` | explanation segments with character offsets, plus
explicit residuals for undecoded spans (VAA/TCA may be residual-heavy — G4).
"""

from __future__ import annotations

import re
from typing import Callable

import msgspec

from tac2iwxxm.glossary import (
    explain_glossary_token,
    resolve_location_name,
)

_SUPPORTED = frozenset({"AIRMET", "METAR", "SIGMET", "SPECI", "TAF", "VAA", "TCA"})

_WIND = re.compile(r"^(?P<dir>\d{3}|VRB)(?P<spd>\d{2,3})(?:G(?P<gust>\d{2,3}))?(?P<unit>KT|MPS)$")
_VIS_SM = re.compile(r"^(?P<mod>[PM])?(?P<val>\d{1,2})SM$")
_VIS_M = re.compile(r"^\d{4}$")
_CLOUD = re.compile(r"^(?P<amt>FEW|SCT|BKN|OVC|SKC|CLR|NSC|NCD)(?P<hgt>\d{3})?$")
_TEMP = re.compile(r"^(?P<t>M?\d{2})/(?P<td>M?\d{2})$")
_ALT = re.compile(r"^A(?P<val>\d{4})$")
_QNH = re.compile(r"^Q(?P<val>\d{3,4})$")
_TIME_Z = re.compile(r"^(?P<dd>\d{2})(?P<hh>\d{2})(?P<mm>\d{2})Z$")
_STATION = re.compile(r"^[A-Z][A-Z0-9]{3}$")
_TAF_VALID = re.compile(r"^(?P<d1>\d{2})(?P<h1>\d{2})/(?P<d2>\d{2})(?P<h2>\d{2})$")
_TAF_FM = re.compile(r"^FM(?P<dd>\d{2})(?P<hh>\d{2})(?P<mm>\d{2})$")
_TAF_PROB = re.compile(r"^PROB(?P<pct>\d{2})$")
_SIG_VALID = re.compile(r"^(?P<d1>\d{2})(?P<h1>\d{2})(?P<m1>\d{2})/(?P<d2>\d{2})(?P<h2>\d{2})(?P<m2>\d{2})$")
_WX = re.compile(
    r"^(?P<int>\+|-|VC)?"
    r"(?P<desc>MI|PR|BC|DR|BL|SH|TS|FZ)?"
    r"(?P<phen>(?:DZ|RA|SN|SG|IC|PL|GR|GS|UP|BR|FG|FU|VA|DU|SA|HZ|PY|PO|SQ|FC|SS|DS)+)$"
)

_WX_INTENSITY = {"+": "heavy", "-": "light", "VC": "in the vicinity"}
_WX_DESCRIPTOR = {
    "MI": "shallow",
    "PR": "partial",
    "BC": "patches of",
    "DR": "low drifting",
    "BL": "blowing",
    "SH": "showers of",
    "TS": "thunderstorm with",
    "FZ": "freezing",
}
_WX_PHENOMENON = {
    "DZ": "drizzle",
    "RA": "rain",
    "SN": "snow",
    "SG": "snow grains",
    "IC": "ice crystals",
    "PL": "ice pellets",
    "GR": "hail",
    "GS": "small hail",
    "UP": "unknown precipitation",
    "BR": "mist",
    "FG": "fog",
    "FU": "smoke",
    "VA": "volcanic ash",
    "DU": "widespread dust",
    "SA": "sand",
    "HZ": "haze",
    "PY": "spray",
    "PO": "dust whirls",
    "SQ": "squalls",
    "FC": "funnel cloud",
    "SS": "sandstorm",
    "DS": "duststorm",
}
_CLOUD_AMOUNT = {
    "FEW": "Few clouds",
    "SCT": "Scattered clouds",
    "BKN": "Broken clouds",
    "OVC": "Overcast",
    "SKC": "Sky clear",
    "CLR": "Sky clear",
    "NSC": "No significant cloud",
    "NCD": "No cloud detected",
}


def _signed_temp(raw: str) -> int:
    """Parse a TAC temperature field (``M`` prefix = negative) to °C."""
    return -int(raw[1:]) if raw.startswith("M") else int(raw)


def _fmt_wind(m: re.Match[str], *, label: str) -> str:
    direction = m.group("dir")
    speed = int(m.group("spd"))
    unit = "kt" if m.group("unit") == "KT" else "m/s"
    origin = "variable in direction" if direction == "VRB" else f"from {int(direction)}°"
    text = f"{label} — {origin} at {speed} {unit}"
    gust = m.group("gust")
    if gust:
        text += f", gusting {int(gust)} {unit}"
    return text


def _fmt_time(m: re.Match[str], *, label: str) -> str:
    return f"{label} — day {int(m.group('dd'))} at {m.group('hh')}:{m.group('mm')} UTC"


def _fmt_vis_sm(m: re.Match[str], *, label: str) -> str:
    value = int(m.group("val"))
    prefix = {"P": "more than ", "M": "less than "}.get(m.group("mod") or "", "")
    plural = "s" if value != 1 else ""
    return f"{label} {prefix}{value} statute mile{plural}"


def _fmt_cloud(m: re.Match[str], *, forecast: bool) -> str:
    amount = _CLOUD_AMOUNT[m.group("amt")]
    if forecast:
        amount = f"Forecast {amount[0].lower()}{amount[1:]}"
    height = m.group("hgt")
    if height:
        return f"{amount} at {int(height) * 100:,} ft"
    return amount


def _fmt_wx(m: re.Match[str], *, forecast: bool) -> str:
    parts: list[str] = []
    intensity = m.group("int")
    if intensity:
        parts.append(_WX_INTENSITY[intensity])
    descriptor = m.group("desc")
    if descriptor:
        parts.append(_WX_DESCRIPTOR[descriptor])
    phen = m.group("phen")
    parts.extend(_WX_PHENOMENON[phen[i : i + 2]] for i in range(0, len(phen), 2))
    phrase = " ".join(parts)
    label = "Forecast weather" if forecast else "Weather"
    return f"{label} — {phrase[0].upper()}{phrase[1:]}" if phrase else f"{label} group"


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
    summary: str = ""


def _iter_tokens(tac: str) -> list[tuple[int, int, str]]:
    """Return ``(start, end, token)`` for each non-whitespace run in ``tac``.

    The report terminator ``=`` is split into its own token even when attached
    to the preceding group (e.g. ``A3011=``) so both spans decode (F9).
    """
    return [(m.start(), m.end(), m.group(0)) for m in re.finditer(r"=|[^\s=]+", tac)]


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
        place = resolve_location_name(upper)
        if place:
            return f"ICAO station {upper} ({place})"
        return f"ICAO station location indicator ({upper})"
    if m := _TIME_Z.match(upper):
        return _fmt_time(m, label="Observation time")
    if m := _WIND.match(upper):
        return _fmt_wind(m, label="Surface wind")
    if m := _VIS_SM.match(upper):
        return _fmt_vis_sm(m, label="Prevailing visibility")
    if _VIS_M.match(upper):
        return f"Prevailing visibility {int(upper)} m"
    if m := _CLOUD.match(upper):
        return _fmt_cloud(m, forecast=False)
    if m := _TEMP.match(upper):
        return f"Temperature {_signed_temp(m.group('t'))} °C, dewpoint {_signed_temp(m.group('td'))} °C"
    if m := _ALT.match(upper):
        return f"Altimeter {int(m.group('val')) / 100:.2f} inHg"
    if m := _QNH.match(upper):
        return f"QNH {int(m.group('val'))} hPa"
    if m := _WX.match(upper):
        return _fmt_wx(m, forecast=False)
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
        place = resolve_location_name(upper)
        if place:
            return f"ICAO station {upper} ({place})"
        return f"ICAO station location indicator ({upper})"
    if m := _TIME_Z.match(upper):
        return _fmt_time(m, label="Issue time")
    if m := _TAF_VALID.match(upper):
        return (
            f"Validity — day {int(m.group('d1'))} {m.group('h1')}:00 UTC"
            f" to day {int(m.group('d2'))} {m.group('h2')}:00 UTC"
        )
    if m := _WIND.match(upper):
        return _fmt_wind(m, label="Forecast wind")
    if _VIS_M.match(upper):
        return f"Forecast visibility {int(upper)} m"
    if m := _VIS_SM.match(upper):
        return _fmt_vis_sm(m, label="Forecast visibility")
    if m := _CLOUD.match(upper):
        return _fmt_cloud(m, forecast=True)
    if m := _ALT.match(upper):
        return f"Altimeter {int(m.group('val')) / 100:.2f} inHg"
    if m := _QNH.match(upper):
        return f"QNH {int(m.group('val'))} hPa"
    if m := _TAF_FM.match(upper):
        return (
            f"From day {int(m.group('dd'))} at {m.group('hh')}:{m.group('mm')} UTC"
            " — rapid change to new prevailing conditions"
        )
    if upper == "TEMPO":
        return "Temporary fluctuations expected during the following period"
    if upper == "BECMG":
        return "Becoming — gradual change during the following period"
    if m := _TAF_PROB.match(upper):
        return f"{int(m.group('pct'))}% probability of the following conditions"
    if upper.startswith(("FM", "TEMPO", "BECMG", "PROB")):
        return "Change / probability group"
    if m := _WX.match(upper):
        return _fmt_wx(m, forecast=True)
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
        place = resolve_location_name(upper)
        if place:
            return f"Originating FIR / location indicator {upper} ({place})"
        return f"Originating FIR / location indicator ({upper})"
    if m := _SIG_VALID.match(upper):
        return (
            f"Valid day {int(m.group('d1'))} {m.group('h1')}:{m.group('m1')} UTC"
            f" to day {int(m.group('d2'))} {m.group('h2')}:{m.group('m2')} UTC"
        )
    # Glossary-backed intensity / hazard / movement tokens (F9 deepen).
    return explain_glossary_token(upper)


def _explain_advisory(token: str, *, product: str, seen: dict[str, int]) -> str | None:
    """Best-effort VAA/TCA keyword spans; most body stays residual (G4)."""
    upper = token.upper()
    if product == "VAA":
        if upper == "VA" and seen.get("va", 0) == 0:
            seen["va"] = 1
            return explain_glossary_token(upper, fallback="Volcanic ash advisory marker")
        if upper == "ADVISORY" and seen.get("adv", 0) == 0:
            seen["adv"] = 1
            return explain_glossary_token(upper, fallback="Advisory product header")
        if upper == "VAA":
            return explain_glossary_token(upper, fallback="Volcanic ash advisory abbreviation")
    if product == "TCA":
        if upper == "TC" and seen.get("tc", 0) == 0:
            seen["tc"] = 1
            return explain_glossary_token(upper, fallback="Tropical cyclone advisory marker")
        if upper == "ADVISORY" and seen.get("adv", 0) == 0:
            seen["adv"] = 1
            return explain_glossary_token(upper, fallback="Advisory product header")
        if upper == "TCA":
            return explain_glossary_token(upper, fallback="Tropical cyclone advisory abbreviation")
    if upper in {"DTG", "VOLCANO", "PSN", "AREA", "SUMMIT", "ADVISORY", "NR", "INFO"}:
        return explain_glossary_token(upper, fallback=f"{product} field label")
    return explain_glossary_token(upper)


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


_SPARSE_PRODUCTS = frozenset({"SIGMET", "AIRMET", "VAA", "TCA"})


def _sentence_from_segment(seg: DecodeSegment) -> str | None:
    """Turn a value-aware explanation into a summary clause (skip terminators)."""
    if seg.code == "=" or seg.explanation.lower().startswith("report terminator"):
        return None
    text = seg.explanation.strip()
    if not text:
        return None
    lower = text.lower()
    if "station location" in lower or "location indicator" in lower:
        return f"station {seg.code.upper()}"
    # Prefer the value-bearing half after an em dash when present.
    if " — " in text:
        left, right = text.split(" — ", 1)
        if left.lower().startswith("report type"):
            return text.rstrip(".")
        return right.rstrip(".")
    return text.rstrip(".")


def _build_summary(
    product: str,
    segments: list[DecodeSegment],
    residuals: list[DecodeResidual],
) -> str:
    """
    Build a deterministic plain-language paragraph for the decode panel (F9).

    Parameters
    ----------
    product :
        Uppercase product id.
    segments :
        Value-aware decode segments.
    residuals :
        Undecoded spans; named in a trailing "Not decoded: …" clause.

    Returns
    -------
    str
        One flowing paragraph. Sparse products include "partial decode" wording.
    """
    clauses: list[str] = []
    for seg in segments:
        clause = _sentence_from_segment(seg)
        if clause:
            clauses.append(clause)

    if product in _SPARSE_PRODUCTS:
        lead = f"{product} (partial decode)"
        body = "; ".join(clauses) if clauses else "few recognizable groups"
        paragraph = f"{lead}: {body}."
    elif clauses:
        # Lead with product when the first clause is the report type.
        paragraph = "; ".join(clauses) + "."
        paragraph = paragraph[0].upper() + paragraph[1:]
    else:
        paragraph = f"{product} report with no decoded groups."

    if residuals:
        residual_bits = " ".join(r.text for r in residuals)
        # Collapse whitespace for readable "Not decoded" naming.
        residual_bits = " ".join(residual_bits.split())
        paragraph = f"{paragraph} Not decoded: {residual_bits}."

    return paragraph


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
        ``segments`` for recognized groups; ``residuals`` for undecoded spans;
        ``summary`` plain-language paragraph (F9 / ADR-025).
        METAR/SPECI/TAF aim for rich segments; VAA/TCA are best-effort (G4).
    """
    product_u = product.upper()
    if product_u not in _SUPPORTED:
        # Entire body residual — unknown product still returns a well-formed shape.
        text = tac
        residuals = [DecodeResidual(start=0, end=len(text), text=text)] if text else []
        summary = _build_summary(product_u, [], residuals)
        return DecodeResult(product=product_u, segments=[], residuals=residuals, summary=summary)

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
    summary = _build_summary(product_u, segments, residuals)
    return DecodeResult(product=product_u, segments=segments, residuals=residuals, summary=summary)


__all__ = [
    "DecodeResidual",
    "DecodeResult",
    "DecodeSegment",
    "decode_tac",
]
