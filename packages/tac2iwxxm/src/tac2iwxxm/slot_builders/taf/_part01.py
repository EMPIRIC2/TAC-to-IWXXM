"""Split part body (exec'd into package namespace)."""

from __future__ import annotations


def _modifier_flags(joined: str) -> dict[str, bool]:
    """
    Internal helper ``_modifier_flags``.

    Parameters
    ----------
    joined : str
        Argument ``joined``.

    Returns
    -------
    dict[str, bool]
        Return value.
    """
    upper = joined.upper()
    # "TAF AMD …" / "TAF COR …" (not station-embedded).
    return {
        "amendment": bool(re.search(r"\bTAF\s+AMD\b", upper)),
        "correction": bool(re.search(r"\bTAF\s+COR\b", upper)),
    }


def _parse_clouds(text: str) -> list[dict[str, Any]]:
    """
    Internal helper ``_parse_clouds``.

    Parameters
    ----------
    text : str
        Argument ``text``.

    Returns
    -------
    list[dict[str, Any]]
        Return value.
    """
    layers: list[dict[str, Any]] = []
    for c in _CLOUD.finditer(text):
        layer: dict[str, Any] = {"amount": c.group("amt")}
        base = c.group("base")
        if base == "///":
            layer["base_not_observable"] = True
        else:
            layer["base_ft"] = int(base) * 100
        if c.group("ctype"):
            layer["cloud_type"] = c.group("ctype")
        layers.append(layer)
    return layers


def _parse_wind(text: str, target: dict[str, Any]) -> None:
    """
    Internal helper ``_parse_wind``.

    Parameters
    ----------
    text : str
        Argument ``text``.

    target : dict[str, Any]
        Argument ``target``.
    """
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
    """
    Internal helper ``_parse_wx``.

    Parameters
    ----------
    text : str
        Argument ``text``.

    Returns
    -------
    list[str]
        Return value.
    """
    return [m.group("wx") for m in _WX_TOKEN.finditer(text)]


def _ca_forecast_weather_hrefs(wx_tokens: list[str]) -> list[str]:
    """
    Internal helper ``_ca_forecast_weather_hrefs``.

    Parameters
    ----------
    wx_tokens : list[str]
        Argument ``wx_tokens``.

    Returns
    -------
    list[str]
        Return value.
    """
    from tac2iwxxm.code_list_policy import resolve_national_href

    hrefs: list[str] = []
    for token in wx_tokens:
        if token.upper() != "IC":
            continue
        href = resolve_national_href(area="forecast_weather", token="IC")
        hrefs.append(href or f"{_CODE_CA_PRESENT_FORECAST_WEATHER}/IC")
    return hrefs


def _parse_nclws(text: str) -> dict[str, Any] | None:
    """
    Internal helper ``_parse_nclws``.

    Parameters
    ----------
    text : str
        Argument ``text``.

    Returns
    -------
    dict[str, Any] | None
        Return value.
    """
    match = _NCLWS.search(text)
    if match is None:
        return None
    return {
        "layer_top_ft": int(match.group("height")) * 100,
        "wind_dir_deg": int(match.group("dir")),
        "wind_speed_kt": int(match.group("spd")),
    }


def _parse_forecast_body(text: str, *, cavok_ok: bool = True) -> dict[str, Any]:
    """
    Internal helper ``_parse_forecast_body``.

    Parameters
    ----------
    text : str
        Argument ``text``.

    cavok_ok : bool, optional
        Argument ``cavok_ok``.

    Returns
    -------
    dict[str, Any]
        Return value.
    """
    out: dict[str, Any] = {}
    # Parse wind before CAVOK short-circuit — TAF.TAF-7 still requires surfaceWind
    # on non-empty baseForecast even when cloudAndVisibilityOK is true.
    _parse_wind(text, out)
    if cavok_ok and _CAVOK.search(text):
        out["cavok"] = True
        return out
    vis_sm = _VIS_SM.search(text)
    if vis_sm is not None:
        sm = parse_statute_mile_fraction(vis_sm.group("vis"))
        whole = int(sm)
        out["visibility_sm"] = whole if sm == whole else sm
        if vis_sm.group("mod") == "P":
            out["visibility_above"] = True
        else:
            metres, above = prevailing_from_statute_miles(sm)
            out["visibility_above"] = above
            if above or sm != whole:
                out["visibility_m"] = metres
    else:
        vis_km = _VIS_KM.search(text)
        if vis_km is not None:
            km = int(vis_km.group("vis"))
            out["visibility_km"] = km
            out["visibility_m"] = km * 1000
            out["visibility_above"] = km >= 10
            out["visibility_display_uom"] = "[km_i]"
            out["visibility_display_value"] = km
        else:
            vis = _VIS_M.search(text)
            if vis is not None:
                metres, above = prevailing_from_metre_group(int(vis.group("vis")))
                out["visibility_m"] = metres
                out["visibility_above"] = above
    # Cloud / sky state: NSC/NCD exclusive (METAR parity); else VV; else SKC/CLR;
    # else layered FEW/SCT/BKN/OVC. TAF-8 requires iwxxm:cloud whenever CAVOK false.
    if _NSC.search(text):
        out["nsc"] = True
    elif _NCD.search(text):
        out["ncd"] = True
    else:
        vv = _VV.search(text)
        if vv is not None:
            token = vv.group("vv")
            if token == "///":
                out["vertical_visibility_not_observable"] = True
            else:
                out["vertical_visibility_ft"] = int(token) * 100
        elif _SKC_CLR.search(text):
            # CLR maps to CloudAmountReportedAtAerodrome/SKC (no CLR concept URI).
            out["clouds"] = [{"amount": "SKC", "base_inapplicable": True}]
            out["cloud_amount"] = "SKC"
        else:
            clouds = _parse_clouds(text)
            if clouds:
                out["clouds"] = clouds
                out["cloud_amount"] = clouds[0]["amount"]
                if "base_ft" in clouds[0]:
                    out["cloud_base_ft"] = clouds[0]["base_ft"]
    wx = _parse_wx(text)
    if wx:
        out["weather"] = wx
    return out


def _taf_day_hour_stamp(ir: dict[str, Any], ddhh: str, *, minute: int = 0) -> str:
    """
    Internal helper ``_taf_day_hour_stamp``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    ddhh : str
        Argument ``ddhh``.

    minute : int, optional
        Argument ``minute``.

    Returns
    -------
    str
        Return value.
    """
    legacy = "2012-08" if ir.get("station") == "YUDO" else "2023-06"
    day = int(ddhh[0:2])
    hour = int(ddhh[2:4])
    return iso_stamp(ir, day, hour, minute, legacy=legacy)


def _taf_valid_end_stamp(ir: dict[str, Any]) -> str:
    """
    Internal helper ``_taf_valid_end_stamp``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    Returns
    -------
    str
        Return value.
    """
    legacy = "2012-08" if ir.get("station") == "YUDO" else "2023-06"
    return iso_stamp(
        ir,
        int(ir["valid_to_day"]),
        int(ir["valid_to_hour"]),
        0,
        legacy=legacy,
    )


def _parse_change_groups(ir: dict[str, Any], body: str) -> list[dict[str, Any]]:
    """
    Internal helper ``_parse_change_groups``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    body : str
        Argument ``body``.

    Returns
    -------
    list[dict[str, Any]]
        Return value.
    """
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
        probable = probability_tempo_parts(chunk)
        if probable is not None:
            indicator, kind, begin, end, forecast_body = probable
            change = {
                "change_indicator": indicator,
                "phenomenon_begin": _taf_day_hour_stamp(ir, begin),
                "phenomenon_end": _taf_day_hour_stamp(ir, end),
            }
            if kind == "EMPO":
                change["tac_change_indicator"] = "EMPO"
            change.update(_parse_forecast_body(forecast_body))
            changes.append(change)
            continue
        if is_unqualified_probability(chunk):
            continue
        tempo = _TEMPO.match(chunk)
        if tempo is not None:
            change: dict[str, Any] = {
                "change_indicator": "TEMPORARY_FLUCTUATIONS",
                "phenomenon_begin": _taf_day_hour_stamp(ir, tempo.group("from")),
                "phenomenon_end": _taf_day_hour_stamp(ir, tempo.group("to")),
            }
            if chunk.upper().startswith("EMPO"):
                change["tac_change_indicator"] = "EMPO"
            change.update(_parse_forecast_body(tempo.group("body")))
            changes.append(change)
            continue
        inter = _INTER.match(chunk)
        if inter is not None:
            # BoM INTER (<30 min). IWXXM has no INTER enum — emit TEMPORARY_FLUCTUATIONS
            # and retain TAC token for remarks/diagnostics (D-EV087-inter-emit).
            change = {
                "change_indicator": "TEMPORARY_FLUCTUATIONS",
                "tac_change_indicator": "INTER",
                "phenomenon_begin": _taf_day_hour_stamp(ir, inter.group("from")),
                "phenomenon_end": _taf_day_hour_stamp(ir, inter.group("to")),
            }
            change.update(_parse_forecast_body(inter.group("body")))
            changes.append(change)
            continue
        fm = _FM.match(chunk)
        if fm is not None:
            stamp = fm.group("stamp")
            legacy = "2012-08" if ir.get("station") == "YUDO" else "2023-06"
            change = {
                "change_indicator": "FROM",
                "phenomenon_begin": iso_stamp(
                    ir,
                    int(stamp[0:2]),
                    int(stamp[2:4]),
                    int(stamp[4:6]),
                    legacy=legacy,
                ),
                "phenomenon_end": _taf_valid_end_stamp(ir),
            }
            change.update(_parse_forecast_body(fm.group("body")))
            changes.append(change)
    return changes
