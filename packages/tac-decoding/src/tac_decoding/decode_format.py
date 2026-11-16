"""Token formatting helpers for TAC decode.

[Corpus: product §F9]
"""

from __future__ import annotations

import re

from tac_decoding.decode_patterns import *


def _signed_temp(raw: str) -> int:
    """
    Internal helper ``_signed_temp``.

    Parameters
    ----------
    raw : str
        Argument ``raw``.

    Returns
    -------
    int
        Return value.
    """
    return -int(raw[1:]) if raw.startswith("M") else int(raw)


def _fmt_qnh(raw: str) -> str:
    """
    Explain a QNH group and keep the pressure in hectopascals.

    Parameters
    ----------
    raw : str
        Digits from the ``Q`` group.

    Returns
    -------
    str
        Operator sentence for that group.
    """
    return f"QNH {int(raw)} hPa, {_QNH_MEANING}"


def _fmt_valid_period(
    *,
    day1: int,
    hour1: str,
    minute1: str,
    day2: int,
    hour2: str,
    minute2: str,
) -> str:
    """
    Format a TAF or SIGMET/AIRMET validity period for the decode panel.

    Day numbers are calendar days of the current month (TAC has no month
    field in these groups). Same-day and cross-day periods use distinct
    templates so operators see that clearly.

    Parameters
    ----------
    day1 : int
        Start day of month (1-31 from the TAC group).
    hour1 : str
        Start hour digits (``HH``).
    minute1 : str
        Start minute digits (``MM``; TAF uses ``00``).
    day2 : int
        End day of month.
    hour2 : str
        End hour digits.
    minute2 : str
        End minute digits.

    Returns
    -------
    str
        Operator-visible validity sentence with UTC times.
    """
    start = f"{hour1}:{minute1}"
    end = f"{hour2}:{minute2}"
    if day1 == day2:
        return f"Valid on day {day1} of the current month from {start} UTC to {end} UTC"
    return f"Valid from day {day1} of the current month at {start} UTC to day {day2} of the current month at {end} UTC"


def _fmt_wind(m: re.Match[str], *, label: str) -> str:
    """
    Internal helper ``_fmt_wind``.

    Parameters
    ----------
    m : re.Match[str]
        Argument ``m``.

    label : str
        Argument ``label``.

    Returns
    -------
    str
        Return value.
    """
    direction = m.group("dir")
    speed = int(m.group("spd"))
    unit = "kt" if m.group("unit") == "KT" else "m/s"
    origin = "variable in direction" if direction == "VRB" else f"from {int(direction)}°"
    text = f"{label} {origin} at {speed} {unit}"
    gust = m.group("gust")
    if gust:
        text += f", gusting {int(gust)} {unit}"
    return text


def _fmt_time(m: re.Match[str], *, label: str) -> str:
    """
    Internal helper ``_fmt_time``.

    Parameters
    ----------
    m : re.Match[str]
        Argument ``m``.

    label : str
        Argument ``label``.

    Returns
    -------
    str
        Return value.
    """
    return f"{label} on day {int(m.group('dd'))} at {m.group('hh')}:{m.group('mm')} UTC"


def _fmt_vis_sm(m: re.Match[str], *, label: str) -> str:
    """
    Internal helper ``_fmt_vis_sm``.

    Parameters
    ----------
    m : re.Match[str]
        Argument ``m``.

    label : str
        Argument ``label``.

    Returns
    -------
    str
        Return value.
    """
    value = int(m.group("val"))
    prefix = {"P": "more than ", "M": "less than "}.get(m.group("mod") or "", "")
    plural = "s" if value != 1 else ""
    return f"{label} {prefix}{value} statute mile{plural}"


def _fmt_cloud(m: re.Match[str], *, forecast: bool) -> str:
    """
    Internal helper ``_fmt_cloud``.

    Parameters
    ----------
    m : re.Match[str]
        Argument ``m``.

    forecast : bool
        Argument ``forecast``.

    Returns
    -------
    str
        Return value.
    """
    amount = _CLOUD_AMOUNT[m.group("amt")]
    if forecast:
        amount = f"Forecast {amount[0].lower()}{amount[1:]}"
    height = m.group("hgt")
    ctype = m.group("ctype")
    type_note = f" ({_CLOUD_TYPE[ctype]})" if ctype else ""
    if m.group("unk"):
        type_note = f"{type_note}, type not reported"
    if height:
        return f"{amount} at {int(height) * 100:,} ft{type_note}"
    return f"{amount}{type_note}"


def _fmt_wx(m: re.Match[str], *, forecast: bool) -> str:
    """
    Internal helper ``_fmt_wx``.

    Parameters
    ----------
    m : re.Match[str]
        Argument ``m``.

    forecast : bool
        Argument ``forecast``.

    Returns
    -------
    str
        Return value.
    """
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
    if not phrase:
        return f"{label} group"
    return f"{label}: {phrase[0].upper()}{phrase[1:]}"


def _explain_recent_weather(body: str) -> str | None:
    """
    Plain language for a recent-weather group after the ``RE`` prefix.

    Parameters
    ----------
    body : str
        Weather codes after ``RE`` (for example ``TS``, ``SH``, ``SHRA``).

    Returns
    -------
    str | None
        Explanation, or ``None`` when the body is not recent weather.
    """
    if body == "TS":
        return "Recent weather: Thunderstorm"
    if body == "SH":
        return "Recent weather: Showers"
    if body == "VCSH":
        return "Recent weather: Showers in the vicinity"
    if body == "VCTS":
        return "Recent weather: Thunderstorm in the vicinity"
    if m := _WX.match(body):
        phrase = _fmt_wx(m, forecast=False)
        detail = phrase.removeprefix("Weather: ").removeprefix("Weather ")
        return f"Recent weather: {detail}"
    return None
