"""Split part body (exec'd into package namespace)."""

from __future__ import annotations


def _celsius(token: str) -> int:
    """
    Internal helper ``_celsius``.

    Parameters
    ----------
    token : str
        Argument ``token``.

    Returns
    -------
    int
        Return value.
    """
    if token.startswith("M"):
        return -int(token[1:])
    return int(token)


def _inhg_to_hpa(alt_token: str) -> float:
    """
    Internal helper ``_inhg_to_hpa``.

    Parameters
    ----------
    alt_token : str
        Argument ``alt_token``.

    Returns
    -------
    float
        Return value.
    """
    inhg = int(alt_token) / 100.0
    return round(inhg * 33.8639, 1)


def _assign_statute_visibility(target: dict[str, Any], token: str) -> None:
    """
    Store a statute-mile group, including a mixed fraction.

    Parameters
    ----------
    target : dict[str, Any]
        Observation map to update.

    token : str
        Miles without the ``SM`` suffix. ``1 1/2`` is one and a half.

    Returns
    -------
    None
    """
    sm = _parse_sm_fraction(token)
    whole = int(sm)
    target["visibility_sm"] = whole if sm == whole else sm
    metres, above = prevailing_from_statute_miles(sm)
    target["visibility_m"] = metres
    target["visibility_above"] = above


def _assign_metre_visibility(target: dict[str, Any], metres: int) -> None:
    """
    Store a metre visibility group on the shared 10 km rule.

    Parameters
    ----------
    target : dict[str, Any]
        Observation or trend map to update.

    metres : int
        The four-digit visibility group.

    Returns
    -------
    None
    """
    value, above = prevailing_from_metre_group(metres)
    target["visibility_m"] = value
    target["visibility_above"] = above


def _assign_reported_visibility(target: dict[str, Any], text: str) -> bool:
    """
    Store prevailing visibility from the observation text.

    A compass group such as ``2000E`` is the visibility when no bare metre
    group or statute-mile group is present.

    Parameters
    ----------
    target : dict[str, Any]
        Observation map to update.

    text : str
        Observation text that may include a trend.

    Returns
    -------
    bool
        True when a visibility group was stored.
    """
    vis_sm = _VIS_SM.search(text)
    if vis_sm is not None:
        _assign_statute_visibility(target, vis_sm.group("vis"))
        return True
    vis_m = _VIS_M.search(text)
    if vis_m is not None:
        _assign_metre_visibility(target, int(vis_m.group("vis")))
        return True
    vis_dir = _VIS_MIN.search(text)
    if vis_dir is not None:
        _assign_metre_visibility(target, int(vis_dir.group("vis")))
        return True
    return False


def _slp_code_to_hpa(code: int) -> float:
    """
    Internal helper ``_slp_code_to_hpa``.

    Parameters
    ----------
    code : int
        Argument ``code``.

    Returns
    -------
    float
        Return value.
    """
    if code < 500:
        return 1000.0 + code / 10.0
    return 900.0 + code / 10.0


def _tenths_celsius(sign: str, digits: str) -> float:
    """
    Internal helper ``_tenths_celsius``.

    Parameters
    ----------
    sign : str
        Argument ``sign``.

    digits : str
        Argument ``digits``.

    Returns
    -------
    float
        Return value.
    """
    value = int(digits) / 10.0
    return -value if sign == "1" else value


def _split_obs_and_trends(body: str) -> tuple[str, list[re.Match[str]]]:
    """
    Internal helper ``_split_obs_and_trends``.

    Parameters
    ----------
    body : str
        Argument ``body``.

    Returns
    -------
    tuple[str, list[re.Match[str]]]
        Return value.
    """
    first = re.search(r"\b(?:BECMG|TEMPO|NOSIG)\b", body)
    if first is None:
        return body, []
    obs = body[: first.start()]
    trends = list(_TREND_GROUP.finditer(body, first.start()))
    return obs, trends


def _hhmm_to_stamp(ir: dict[str, Any], hhmm: str) -> str:
    """
    Internal helper ``_hhmm_to_stamp``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    hhmm : str
        Argument ``hhmm``.

    Returns
    -------
    str
        Return value.
    """
    from tac2iwxxm.time_anchor import iso_stamp

    hour = int(hhmm[0:2])
    minute = int(hhmm[2:4])
    day = int(ir["day"])
    # Match annex3 emit stamp month/year for YUDO WMO examples.
    legacy = "2012-08" if str(ir.get("station")) == "YUDO" else "2023-06"
    return iso_stamp(ir, day, hour, minute, legacy=legacy)


def _obs_stamp(ir: dict[str, Any]) -> str:
    """
    Internal helper ``_obs_stamp``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    Returns
    -------
    str
        Return value.
    """
    from tac2iwxxm.time_anchor import iso_stamp

    day = int(ir["day"])
    hour = int(ir["hour"])
    minute = int(ir["minute"])
    legacy = "2012-08" if str(ir.get("station")) == "YUDO" else "2023-06"
    return iso_stamp(ir, day, hour, minute, legacy=legacy)


def _parse_trend_group(ir: dict[str, Any], kind: str, body: str) -> dict[str, Any] | None:
    """
    Internal helper ``_parse_trend_group``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    kind : str
        Argument ``kind``.

    body : str
        Argument ``body``.

    Returns
    -------
    dict[str, Any] | None
        Return value.
    """
    if kind == "NOSIG":
        return {"change_indicator": "NOSIG", "nil_nosig": True}

    trend: dict[str, Any] = {
        "change_indicator": ("BECOMING" if kind == "BECMG" else "TEMPORARY_FLUCTUATIONS"),
    }
    tl = _TREND_TL.search(body)
    at = _TREND_AT.search(body)
    fm = _TREND_FM.search(body)
    if tl is not None:
        trend["time_indicator"] = "UNTIL"
        trend["phenomenon_begin"] = _obs_stamp(ir)
        trend["phenomenon_end"] = _hhmm_to_stamp(ir, tl.group("hhmm"))
    elif at is not None:
        trend["time_indicator"] = "AT"
        trend["phenomenon_at"] = _hhmm_to_stamp(ir, at.group("hhmm"))
    elif fm is not None:
        trend["time_indicator"] = "FROM"
        trend["phenomenon_at"] = _hhmm_to_stamp(ir, fm.group("hhmm"))

    # Visibility: prefer 9999 / 4-digit metres; SM uncommon in ICAO trends.
    if re.search(r"\b9999\b", body):
        _assign_metre_visibility(trend, 9999)
    else:
        vis_m = _VIS_M.search(body)
        if vis_m is not None:
            _assign_metre_visibility(trend, int(vis_m.group("vis")))

    if re.search(r"\bNSW\b", body):
        trend["weather_nsw"] = True
    else:
        wx_codes: list[str] = []
        for wx_m in _WX_TOKEN.finditer(body):
            token = wx_m.group("wx")
            if token != "//":
                wx_codes.append(token)
        if wx_codes:
            trend["weather"] = wx_codes

    if _NSC.search(body):
        trend["cloud_nsc"] = True
    if _CAVOK.search(body):
        trend["cavok"] = True

    return trend


def _lightning_type_code(raw: str) -> str | None:
    """
    Internal helper ``_lightning_type_code``.

    Parameters
    ----------
    raw : str
        Argument ``raw``.

    Returns
    -------
    str | None
        Return value.
    """
    if not raw:
        return None
    parts: list[str] = []
    i = 0
    while i < len(raw):
        if raw.startswith("IC", i):
            parts.append("IC")
            i += 2
        elif raw.startswith("CC", i):
            parts.append("CC")
            i += 2
        elif raw.startswith("CG", i):
            parts.append("CG")
            i += 2
        else:
            return None
    uniq = frozenset(parts)
    if uniq == frozenset({"IC", "CC", "CG"}):
        return "CCCGIC"
    if uniq == frozenset({"IC", "CG"}):
        return "ICCG"
    if uniq == frozenset({"CC", "CG"}):
        return "CCCG"
    if uniq == frozenset({"IC", "CC"}):
        return "ICCC"
    if len(uniq) == 1:
        return next(iter(uniq))
    return "".join(parts)


def _lightning_sector(sector_tok: str | None) -> dict[str, Any] | None:
    """
    Internal helper ``_lightning_sector``.

    Parameters
    ----------
    sector_tok : str | None
        Argument ``sector_tok``.

    Returns
    -------
    dict[str, Any] | None
        Return value.
    """
    if not sector_tok:
        return None
    if sector_tok == "ALQDS":
        return {"in_all_quadrants": True}
    dirs = sector_tok.split("-")
    if any(d not in _LTG_COMPASS_DEG for d in dirs):
        return None
    first = _LTG_COMPASS_DEG[dirs[0]]
    last = _LTG_COMPASS_DEG[dirs[-1]]
    return {
        "in_all_quadrants": False,
        "ccw_deg": (first - 22.5) % 360.0,
        "cw_deg": (last + 22.5) % 360.0,
    }


def _parse_lightning_remark(remarks: str) -> dict[str, Any] | None:
    """
    Internal helper ``_parse_lightning_remark``.

    Parameters
    ----------
    remarks : str
        Argument ``remarks``.

    Returns
    -------
    dict[str, Any] | None
        Return value.
    """
    m = _LTG_REMARK.search(remarks)
    if m is None:
        return None
    entry: dict[str, Any] = {}
    freq = m.group("freq")
    if freq:
        entry["frequency_href"] = _FREQ_HREF.format(code=_LTG_FREQ_CODES[freq])
    type_code = _lightning_type_code(m.group("type") or "")
    if type_code:
        entry["type_href"] = _TYPE_HREF.format(code=type_code)
    dist = m.group("dist")
    if dist:
        entry["qualitative_distance_href"] = _DIST_HREF.format(code=_LTG_DIST_CODES[dist])
    sector = _lightning_sector(m.group("sector"))
    if sector is not None:
        entry["sector"] = sector
    return entry or None


def _frac_to_inches(frac: str) -> float:
    """
    Internal helper ``_frac_to_inches``.

    Parameters
    ----------
    frac : str
        Argument ``frac``.

    Returns
    -------
    float
        Return value.
    """
    num_s, den_s = frac.split("/", 1)
    return int(num_s) / float(int(den_s))


def _parse_sm_fraction(token: str) -> float:
    """
    Internal helper ``_parse_sm_fraction``.

    Parameters
    ----------
    token : str
        Argument ``token``.

    Returns
    -------
    float
        Return value.
    """
    parts = token.split()
    if len(parts) == 2 and "/" in parts[1]:
        return float(int(parts[0])) + _frac_to_inches(parts[1])
    if len(parts) == 1 and "/" in parts[0]:
        return _frac_to_inches(parts[0])
    return float(int(parts[0]))


def parse_statute_mile_fraction(token: str) -> float:
    """
    Parse a statute-mile token with the existing fraction parser.

    Parameters
    ----------
    token : str
        Miles without the ``SM`` suffix. ``1 1/2`` is one and a half.

    Returns
    -------
    float
        Statute miles.

    Examples
    --------
    >>> parse_statute_mile_fraction("1 1/2")
    1.5
    >>> parse_statute_mile_fraction("10")
    10.0
    """
    return _parse_sm_fraction(token)


def _sm_float_to_m(sm: float) -> int:
    """
    Internal helper ``_sm_float_to_m``.

    Parameters
    ----------
    sm : float
        Argument ``sm``.

    Returns
    -------
    int
        Return value.
    """
    return round(sm * 1609.344)
