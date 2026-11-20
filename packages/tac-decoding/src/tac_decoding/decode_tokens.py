"""Low-level TAC token helpers.

[Corpus: product §F9]
"""

from __future__ import annotations

import re

from tac_decoding.decode_patterns import *


def _iter_tokens(tac: str) -> list[tuple[int, int, str]]:
    """
    Internal helper ``_iter_tokens``.

    Parameters
    ----------
    tac : str
        Argument ``tac``.

    Returns
    -------
    list[tuple[int, int, str]]
        Return value.
    """
    return [(m.start(), m.end(), m.group(0)) for m in re.finditer(r"=|[^\s=]+", tac)]


_SPACED_CAVOK_LETTERS = ("C", "A", "V", "O", "K")


def _spaced_cavok_span(
    tokens: list[tuple[int, int, str]],
    index: int,
) -> tuple[int, int] | None:
    """
    Return ``(start, end)`` when ``tokens[index:index+5]`` are spaced CAVOK.

    Live TAF traffic (e.g. HAAB) sometimes emits ``C A V O K`` instead of
    ``CAVOK``. Treat the five single-letter tokens as one ceiling/visibility
    group so decode does not leave them as a residual.

    Parameters
    ----------
    tokens : list[tuple[int, int, str]]
        Token spans from :func:`_iter_tokens`.

    index : int
        Candidate start index.

    Returns
    -------
    tuple[int, int] | None
        Character span covering all five letters, or ``None``.
    """
    if index + 5 > len(tokens):
        return None
    letters = tuple(tokens[index + offset][2].upper() for offset in range(5))
    if letters != _SPACED_CAVOK_LETTERS:
        return None
    return tokens[index][0], tokens[index + 4][1]


def _tenths_c(raw: str) -> str:
    """FMH-1 temperature in tenths, with a leading sign digit.

    Parameters
    ----------
    raw : str
        Four digits. ``0`` is positive and ``1`` is negative.

    Returns
    -------
    str
        Degrees Celsius with one decimal place.
    """
    sign = -1 if raw[0] == "1" else 1
    return f"{sign * int(raw[1:]) / 10:.1f}"


def _pressure_tendency(token: str) -> str | None:
    """FMH-1 group ``5appp``: characteristic and 3-hour change in tenths of hPa.

    Parameters
    ----------
    token : str
        One remarks group.

    Returns
    -------
    str | None
        The tendency in plain language, or None when the group is not ``5appp``.
    """
    match = _PRESSURE_TENDENCY.match(token)
    if match is None:
        return None
    amount = int(match.group("amt")) / 10
    return f"Pressure tendency: {_TENDENCY_CHAR[match.group('char')]}, change {amount:.1f} hPa in 3 hours"


def _precip_amount(token: str) -> str | None:
    """Hourly precipitation ``P####`` in hundredths of an inch. ``P0000`` is a trace.

    Parameters
    ----------
    token : str
        One remarks group.

    Returns
    -------
    str | None
        The amount in plain language, or None when the group is not ``P####``.
    """
    match = _PRECIP_AMOUNT.match(token)
    if match is None:
        return None
    hundredths = int(match.group("amt"))
    if hundredths == 0:
        return "Precipitation trace in the past hour"
    return f"Precipitation {hundredths / 100:.2f} inches in the past hour"


def _us_precip_addenda(token: str) -> str | None:
    """US precip addenda: ``P####``, truncated ``P###``, or ``PP###`` (mm).

    These may appear with or without an explicit ``RMK`` keyword on live TAC.
    """
    if phrase := _precip_amount(token):
        return phrase
    if match := _SHORT_PRECIP.match(token):
        hundredths = int(match.group("amt"))
        if hundredths == 0:
            return "Precipitation trace in the past hour"
        return f"Precipitation {hundredths / 100:.2f} inches in the past hour"
    if match := _PP_PRECIP_MM.match(token):
        tenths = int(match.group("amt"))
        return f"Precipitation {tenths / 10:.1f} mm"
    return None


def _okta_phrase(kind: str, amount: str) -> str:
    """One Canadian remark cloud type and its coverage in oktas.

    Parameters
    ----------
    kind : str
        A two-letter cloud type, or ``TCU``.
    amount : str
        Coverage as a single digit of oktas.

    Returns
    -------
    str
        The type name and coverage.
    """
    count = int(amount)
    unit = "okta" if count == 1 else "oktas"
    return f"{_CA_CLOUD_NAME[kind]} {count} {unit}"


def _canadian_clouds(token: str) -> str | None:
    """Canadian remark clouds, either ``SF8`` or a run such as ``ST3CU1CI1``.

    Parameters
    ----------
    token : str
        One remarks group.

    Returns
    -------
    str | None
        The clouds in plain language, or None when the group is not a cloud run.
    """
    if _CA_CLOUD_AMOUNTS.match(token):
        parts = re.findall(rf"({_CA_CLOUD_TYPE})(\d)", token)
        return "Clouds: " + ", ".join(_okta_phrase(kind, amount) for kind, amount in parts)
    if _CA_CLOUD_ONE.match(token):
        return f"Cloud type ({_CA_CLOUD_NAME[token]})"
    return None


def _whole_miles(token: str, following: str) -> str | None:
    """The whole miles that sit in front of a fractional statute-mile group.

    Parameters
    ----------
    token : str
        A single digit from 1 to 9.
    following : str
        The next group, which must be a fractional mile.

    Returns
    -------
    str | None
        The whole-mile phrase, or None when the pair is not whole miles plus a fraction.
    """
    if not re.fullmatch(r"[1-9]", token):
        return None
    following_upper = following.upper()
    if not _VIS_FRAC.match(following_upper) and not _FRAC_MILE.match(following_upper):
        return None
    return f"Visibility {token} statute mile, plus the following fraction"


def _rvr_bound(raw: str) -> str:
    """A runway visual range limit, including a greater-than or less-than mark.

    Parameters
    ----------
    raw : str
        Digits, or the same digits with a leading ``P`` or ``M``.

    Returns
    -------
    str
        The limit, with ``more than`` or ``less than`` when marked.
    """
    if raw.startswith("P"):
        return f"more than {int(raw[1:])}"
    if raw.startswith("M"):
        return f"less than {int(raw[1:])}"
    return str(int(raw))


def _varying_rvr(token: str) -> str | None:
    """Runway visual range that varies, in metres or feet.

    Parameters
    ----------
    token : str
        One runway visual range group.

    Returns
    -------
    str | None
        The varying or unreported range, or None when the group is a single value.
    """
    missing = _RVR_MISSING.match(token)
    if missing:
        return f"Runway visual range runway {missing.group('rw')}: not reported"
    varying = _RVR_VARY.match(token)
    if varying is None:
        return None
    unit = "ft" if varying.group("unit") == "FT" else "m"
    trend = varying.group("trend")
    trend_txt = {
        "U": ", upward trend",
        "D": ", downward trend",
        "N": ", no distinct trend",
    }.get(trend or "", "")
    return (
        f"Runway visual range runway {varying.group('rw')}: "
        f"varying from {_rvr_bound(varying.group('a'))} {unit} to {_rvr_bound(varying.group('b'))} {unit}"
        f"{trend_txt}"
    )


def _depth_phrase(raw: str) -> str | None:
    """Depth of the runway deposit from the runway state group.

    Parameters
    ----------
    raw : str
        Two digits, or ``//`` when the depth is not significant.

    Returns
    -------
    str | None
        The depth in plain language, or None when the code is unused.
    """
    if raw == "//":
        return "depth not significant"
    if raw == "00":
        return "depth less than 1 mm"
    if raw == "99":
        return "runway not operational"
    depth = int(raw)
    if 1 <= depth <= 90:
        return f"depth {depth} mm"
    centimetres = _RUNWAY_DEPTH_CM.get(depth)
    if centimetres is None:
        return None
    if depth == 98:
        return f"depth {centimetres} cm or more"
    return f"depth {centimetres} cm"


def _friction_phrase(raw: str) -> str | None:
    """Friction coefficient or braking action from the runway state group.

    Parameters
    ----------
    raw : str
        Two digits, or ``//`` when friction is not reported.

    Returns
    -------
    str | None
        The friction in plain language, or None when the code is unused.
    """
    if raw == "//":
        return "friction not reported"
    braking = _RUNWAY_BRAKING.get(raw)
    if braking:
        return f"braking action {braking}"
    if raw == "99":
        return "friction unreliable"
    coefficient = int(raw)
    if 0 <= coefficient <= 90:
        return f"friction coefficient {coefficient / 100:.2f}"
    return None


def _runway_state(token: str) -> str | None:
    """The legacy runway state group, including a cleared runway.

    Parameters
    ----------
    token : str
        One group such as ``R19/290052`` or ``R06L/CLRD62``.

    Returns
    -------
    str | None
        The runway state in plain language, or None when it is runway visual range.
    """
    cleared = _RUNWAY_CLEARED.match(token)
    if cleared:
        friction = _friction_phrase(cleared.group("fric"))
        if friction is None:
            return None
        return f"Runway state runway {cleared.group('rw')}: contamination ceased, {friction}"
    state = _RUNWAY_STATE.match(token)
    if state is None:
        return None
    depth = _depth_phrase(state.group("depth"))
    friction = _friction_phrase(state.group("fric"))
    if depth is None or friction is None:
        return None
    return (
        f"Runway state runway {state.group('rw')}: {_RUNWAY_DEPOSIT[state.group('dep')]}, "
        f"{_RUNWAY_EXTENT[state.group('ext')]}, {depth}, {friction}"
    )


def _qfe(token: str) -> str | None:
    """Aerodrome pressure in millimetres of mercury, with hectopascals when sent.

    Parameters
    ----------
    token : str
        One group such as ``QFE747`` or ``QFE747/0996``.

    Returns
    -------
    str | None
        The field pressure, or None when the group is not QFE.
    """
    match = _QFE.match(token)
    if match is None:
        return None
    millimetres = int(match.group("mm"))
    reported = match.group("hpa")
    if reported:
        return f"QFE {millimetres} mmHg ({int(reported)} hPa), the pressure at the aerodrome"
    hectopascals = round(millimetres * 1013.25 / 760)
    return f"QFE {millimetres} mmHg (about {hectopascals} hPa), the pressure at the aerodrome"


def _wx_clock(raw: str) -> str:
    """Minutes past the hour, or an hour and minute when four digits are present.

    Parameters
    ----------
    raw : str
        Two digits of minutes, or four digits of hour and minute.

    Returns
    -------
    str
        A clock phrase for that time.
    """
    if len(raw) == 4:
        return f"at {raw[:2]}:{raw[2:]}"
    return f"at {raw} minutes past the hour"


def _wx_began_or_ended(token: str) -> str | None:
    """One weather type, or several glued together, with began and ended times.

    Parameters
    ----------
    token : str
        A remarks group such as ``RAB19`` or ``RAE2055DZB08E10``.

    Returns
    -------
    str | None
        The begin and end times, or None when the group is not a weather-time chain.
    """
    pos = 0
    clauses: list[str] = []
    while pos < len(token):
        kind = next((name for name in _WX_TIME_NAME if token.startswith(name, pos)), None)
        if kind is None:
            return None
        pos += len(kind)
        edges: list[str] = []
        while pos < len(token) and token[pos] in "BE":
            word = "began" if token[pos] == "B" else "ended"
            pos += 1
            four = token[pos : pos + 4]
            two = token[pos : pos + 2]
            if len(four) == 4 and four.isdigit() and _wx_four_digits(token, pos):
                edges.append(f"{word} {_wx_clock(four)}")
                pos += 4
            elif len(two) == 2 and two.isdigit():
                edges.append(f"{word} {_wx_clock(two)}")
                pos += 2
            else:
                return None
        if not edges:
            return None
        sentence = f"{_WX_TIME_NAME[kind]} {edges[0]}"
        if len(edges) > 1:
            sentence += "".join(f" and {edge}" for edge in edges[1:])
        clauses.append(sentence)
    return ". ".join(clauses)


def _wx_four_digits(token: str, pos: int) -> bool:
    """True when four digits end the token, or a new edge or weather type follows.

    Parameters
    ----------
    token : str
        The full weather-time group.
    pos : int
        Index of the first of the four digits.

    Returns
    -------
    bool
        Whether those four digits are an hour and minute.
    """
    nxt = token[pos + 4 : pos + 6]
    if not nxt:
        return True
    if nxt[0] in "BE":
        return True
    return any(nxt.startswith(name) for name in _WX_TIME_NAME)


def _navaid_chain(token: str) -> str | None:
    """A hyphenated run of navaids with no distance, such as ``TRV-PBI``.

    Parameters
    ----------
    token : str
        One group from a convective ``FROM`` line.

    Returns
    -------
    str | None
        The navaids in order, or None when a part is not a navaid name.
    """
    parts = token.split("-")
    if len(parts) < 2 or any(part == "" for part in parts):
        return None
    if not all(re.fullmatch(r"[A-Z]{2,5}", part) for part in parts):
        return None
    return "Navaids " + " to ".join(parts)
