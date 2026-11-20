"""Split part body (exec'd into package namespace)."""

from __future__ import annotations


def _enrich_hazard_body(ir: dict[str, Any], body: str) -> None:
    """
    Internal helper ``_enrich_hazard_body``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    body : str
        Argument ``body``.
    """
    upper = body.upper()
    cnl = _CNL.search(body)
    if cnl is not None:
        ir["cancel"] = True
        cnl_seq, cnl_label = _parse_sequence_token(cnl.group("cnl_seq"))
        ir["cancelled_sequence"] = cnl_seq
        if cnl_label != str(cnl_seq):
            ir["cancelled_sequence_label"] = cnl_label
        c_from = _parse_valid(cnl.group("cnl_from"))
        c_to = _parse_valid(cnl.group("cnl_to"))
        ir["cancelled_from_day"] = c_from[0]
        ir["cancelled_from_hour"] = c_from[1]
        ir["cancelled_from_minute"] = c_from[2]
        ir["cancelled_to_day"] = c_to[0]
        ir["cancelled_to_hour"] = c_to[1]
        ir["cancelled_to_minute"] = c_to[2]
        # FIR-moved cancel is VA-family (root VolcanicAshSIGMET); other CNL drop phenom.
        if _CNL_FIR_MOVED.search(body) is not None:
            ir["phenomenon"] = "VA"
            ir["va_cnl_fir_moved"] = True
        else:
            ir.pop("phenomenon", None)
        return
    if _CNL_INCOMPLETE.search(body) is not None:
        raise ValueError("incomplete CNL: cancelled validity period required")

    ir["intensity_change"] = _detect_intensity(body)
    ir["stationary"] = bool(re.search(r"\bSTNR\b", upper))
    if re.search(r"\bOBS\b", upper):
        ir["time_indicator"] = "OBSERVATION"
    elif re.search(r"\bFCST\b", upper):
        ir["time_indicator"] = "FORECAST"
    if _NO_VA_EXP.search(body):
        ir["no_va_exp"] = True

    volcano = _parse_va_eruption(body)
    if volcano is not None:
        ir["volcano"] = volcano

    # Multi-location VA (AND-joined OBS/FCST) or single OBS(+FCST) VA cloud (#809 / #856).
    locations = _parse_va_locations(body) if use_volcanic_ash_locations(str(ir.get("phenomenon", "")), body) else []
    if locations:
        ir["locations"] = locations
        first = locations[0]
        ir["geometry"] = first["geometry"]
        ir["time_indicator"] = "OBSERVATION"
        ir["intensity_change"] = first["intensity_change"]
        if "lower_surface" in first:
            ir["lower_surface"] = first["lower_surface"]
            ir["upper_fl"] = first["upper_fl"]
        if "lower_fl" in first:
            ir["lower_fl"] = first["lower_fl"]
            ir["upper_fl"] = first["upper_fl"]
        _apply_motion(ir, body)
        return

    _apply_motion(ir, body)

    top = _TOP_FL.search(body)
    if top is not None:
        ir["top_fl"] = int(top.group("fl"))
        if "ABV" in top.group(0).upper():
            ir["top_qualifier"] = "ABV"
        elif "BLW" in top.group(0).upper():
            ir["top_qualifier"] = "BLW"

    feet_layer = _FT_FL_LAYER.search(body)
    if feet_layer is not None:
        ir["lower_ft"] = int(feet_layer.group("ft"))
        ir["lower_unit"] = feet_layer.group("unit").upper()
        ir["upper_fl"] = int(feet_layer.group("fl"))
    sfc_fl = _SFC_FL.search(body)
    if feet_layer is None and sfc_fl is not None:
        ir["lower_surface"] = "SFC"
        ir["upper_fl"] = int(sfc_fl.group("fl"))
    elif feet_layer is None:
        frzlvl_band = _FRZLVL_BAND.search(body)
        if frzlvl_band is not None:
            ir["lower_surface"] = "FRZLVL"
            ir["upper_fl"] = int(frzlvl_band.group("fl"))
        inline_frz = _INLINE_FRZLVL.search(body)
        if inline_frz is not None:
            ir["inline_frzlvl_lo"] = int(inline_frz.group("lo"))
            ir["inline_frzlvl_hi"] = int(inline_frz.group("hi"))
        band = _FL_BAND.search(body)
        if band is not None:
            ir["lower_fl"] = int(band.group("lo"))
            ir["upper_fl"] = int(band.group("hi"))
        elif "top_fl" not in ir and "upper_fl" not in ir:
            # Single FL token that is not TOP FLnnn (e.g. FL180 alone).
            singles = list(_SINGLE_FL.finditer(body))
            if len(singles) == 1 and "TOP" not in body.upper()[max(0, singles[0].start() - 4) : singles[0].start()]:
                fl = int(singles[0].group("fl"))
                ir["lower_fl"] = fl
                ir["upper_fl"] = fl

    if ir.get("no_va_exp"):
        # Forecast absence of ash - no geometry ring (V1 / #739).
        return

    vor_geometry = parse_vor_reference_geometry(body)
    if vor_geometry is not None:
        ir["geometry"] = vor_geometry
        return

    # TC SIGMET: name + centre PSN + WI nnNM OF TC CENTRE (+ optional FCST centre).
    tc_name = _TC_NAME.search(body)
    if tc_name is not None and ir.get("phenomenon") == "TC":
        ir["tropical_cyclone_name"] = tc_name.group("name").title()
        obs = _TC_OBS_PSN.search(body)
        if obs is not None:
            ir["tropical_cyclone_position"] = {
                "lat": _point_lat_lon(obs)[0],
                "lon": _point_lat_lon(obs)[1],
            }
        circle = _TC_CIRCLE.search(body)
        if circle is not None and "tropical_cyclone_position" in ir:
            pos = cast(dict[str, float], ir["tropical_cyclone_position"])
            ir["geometry"] = {
                "kind": "circle",
                "lat": pos["lat"],
                "lon": pos["lon"],
                "radius_nm": int(circle.group("nm")),
            }
        fcst = _TC_FCST_PSN.search(body)
        if fcst is not None:
            ir["tropical_cyclone_forecast"] = {
                "hhmm": fcst.group("hhmm"),
                "lat": _point_lat_lon(fcst)[0],
                "lon": _point_lat_lon(fcst)[1],
            }
        if "geometry" in ir:
            return

    se_box = _SE_BOX.search(body)
    if se_box is not None:
        lat = float(se_box.group("lat"))
        lon = -float(se_box.group("lon"))
        # WMO A6-1a-TS style box south/east of the reference lines.
        ir["geometry"] = {
            "kind": "polygon",
            "pos_list": f"{lat:.1f} {lon:.1f} {lat - 4:.1f} {lon:.1f} {lat - 4:.1f} {lon + 4:.1f} {lat:.1f} {lon + 4:.1f} {lat:.1f} {lon:.1f}",
        }
        return

    n_of_s = _N_OF_S.search(body)
    if n_of_s is not None:
        # Vendor airmet-A6-1a-TS box north of Slat (lat…lat+10, lon 50…70).
        lat = -float(n_of_s.group("lat"))
        ir["geometry"] = {
            "kind": "polygon",
            "pos_list": (f"{lat:.1f} 50.0 {lat:.1f} 70.0 {lat + 10:.1f} 70.0 {lat + 10:.1f} 50.0 {lat:.1f} 50.0"),
        }
        return

    if _apply_line_geometry(ir, body):
        return

    # Prefer VA CLD / hazard WI polygon over volcano PSN point (F23 V3 / #739).
    wi = _WI_BLOCK.search(body)
    if wi is not None:
        pts = [_point_lat_lon(m) for m in _POINT.finditer(wi.group("body"))]
        if len(pts) >= 3:
            if pts[0] != pts[-1]:
                pts.append(pts[0])
            pos_list = " ".join(f"{lat:.4f} {lon:.4f}" for lat, lon in pts)
            ir["geometry"] = {"kind": "polygon", "pos_list": pos_list}
            return

    point = _POINT.search(body)
    if point is not None:
        lat, lon = _point_lat_lon(point)
        ir["geometry"] = {"kind": "point", "lat": lat, "lon": lon}


def _enrich_sigmet_body(ir: dict[str, Any], body: str) -> None:
    """
    Internal helper ``_enrich_sigmet_body``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    body : str
        Argument ``body``.
    """
    _enrich_hazard_body(ir, body)


def _parse_until_token(until: str, *, issue_day: int | None = None) -> tuple[int, int, int]:
    """
    Internal helper ``_parse_until_token``.

    Parameters
    ----------
    until : str
        Argument ``until``.

    issue_day : int | None, optional
        Day of month from the bulletin heading when ``until`` is ``hhmm``.

    Returns
    -------
    tuple[int, int, int]
        Return value.
    """
    if len(until) >= 6:
        return int(until[0:2]), int(until[2:4]), int(until[4:6])
    hour = int(until[0:2])
    minute = int(until[2:4])
    return issue_day if issue_day is not None else 9, hour, minute


def _attach_us_airmet_hazard(ir: dict[str, Any]) -> None:
    """
    Internal helper ``_attach_us_airmet_hazard``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.
    """
    phen = ir.get("phenomenon")
    if phen == "SFC_VIS":
        ir["us_airmet_hazard"] = {
            "href": _NWS_HAZARD_IFR,
            "causing_ifr_conditions": True,
        }


def _split_airmet_main_and_outlook(body: str) -> tuple[str, str | None]:
    """
    Internal helper ``_split_airmet_main_and_outlook``.

    Parameters
    ----------
    body : str
        Argument ``body``.

    Returns
    -------
    tuple[str, str | None]
        Return value.
    """
    match = re.search(r"\bOTLK\b", body, flags=re.IGNORECASE)
    if match is None:
        return body, None
    return body[: match.start()].strip(), body[match.start() :].strip()


def _split_frzlvl_section(body: str) -> tuple[str, str | None]:
    """
    Internal helper ``_split_frzlvl_section``.

    Parameters
    ----------
    body : str
        Argument ``body``.

    Returns
    -------
    tuple[str, str | None]
        Return value.
    """
    match = _FRZLVL_SECTION.search(body)
    if match is None:
        return body, None
    return body[: match.start()].strip(), body[match.start() :].strip()


def _strip_conus_airmet_lead(body: str) -> str:
    """
    Internal helper ``_strip_conus_airmet_lead``.

    Parameters
    ----------
    body : str
        Argument ``body``.

    Returns
    -------
    str
        Return value.
    """
    if not _CONUS_AIR_LEAD.match(body):
        return body
    from_match = re.search(r"\bFROM\b", body, flags=re.IGNORECASE)
    if from_match is not None:
        return body[from_match.start() :].strip()
    bounded = re.search(r"\bBOUNDED BY\b", body, flags=re.IGNORECASE)
    if bounded is not None:
        return body[bounded.start() :].strip()
    mod_match = re.search(r"\bMOD\s+", body, flags=re.IGNORECASE)
    if mod_match is not None:
        return body[mod_match.start() :].strip()
    return body


def _phenomenon_from_conus_for_text(for_text: str) -> str:
    """
    Internal helper ``_phenomenon_from_conus_for_text``.

    Parameters
    ----------
    for_text : str
        Argument ``for_text``.

    Returns
    -------
    str
        Return value.
    """
    upper = for_text.upper()
    if "ICE" in upper:
        return "MOD_ICE"
    if "TURB" in upper:
        return "MOD_TURB"
    if "IFR" in upper or "VIS" in upper:
        return "SFC_VIS"
    if "MTN" in upper and "OBSC" in upper:
        return "MT_OBSC"
    # CONUS FOR-text may omit a catalog token; keep a stable default for that path only.
    return _detect_phenomenon(for_text, _AIR_PHENOMENA) or "TS"


def _parse_frzlvl_section(text: str) -> dict[str, Any]:
    """
    Internal helper ``_parse_frzlvl_section``.

    Parameters
    ----------
    text : str
        Argument ``text``.

    Returns
    -------
    dict[str, Any]
        Return value.
    """
    section: dict[str, Any] = {"isopleths": []}
    ranging = _FRZLVL_RANGING.search(text)
    if ranging is not None:
        section["ranging_from"] = ranging.group("from").upper()
        section["ranging_to"] = int(ranging.group("to"))
    multi = _MULT_FRZLVL.search(text)
    if multi is not None:
        section["multiple_levels"] = True
        section["multi_lo"] = int(multi.group("lo"))
        section["multi_hi"] = int(multi.group("hi"))
    else:
        section["multiple_levels"] = False
    for match in _FRZLVL_ALG.finditer(text):
        section["isopleths"].append(
            {
                "alt": match.group("alt").upper(),
                "boundary": match.group("boundary").strip(),
            }
        )
    return section


def _try_parse_conus_airmet(text: str) -> dict[str, Any] | None:
    """
    Internal helper ``_try_parse_conus_airmet``.

    Parameters
    ----------
    text : str
        Argument ``text``.

    Returns
    -------
    dict[str, Any] | None
        Return value.
    """
    match = _CONUS_AIRMET.match(text)
    if match is None:
        return None
    until_day, until_hour, until_minute = _parse_until_token(match.group("until"))
    issue_day, issue_hour, issue_minute = until_day, until_hour, until_minute
    if match.group("issue"):
        issue_day, issue_hour, issue_minute = _parse_valid(match.group("issue"))
    elif match.group("wmo_time"):
        issue_day, issue_hour, issue_minute = _parse_valid(match.group("wmo_time"))
    fir = (match.group("faa_zone") or match.group("wmo_cccc") or "KKCI").upper()
    mwo = (match.group("wmo_cccc") or "KKCI").upper()
    body = _strip_conus_airmet_lead(match.group("body").strip())
    return {
        "fir": fir,
        "mwo": mwo,
        "sequence": int(match.group("upd")),
        "valid_from_day": issue_day,
        "valid_from_hour": issue_hour,
        "valid_from_minute": issue_minute,
        "valid_to_day": until_day,
        "valid_to_hour": until_hour,
        "valid_to_minute": until_minute,
        "phenomenon": _phenomenon_from_conus_for_text(match.group("for_text")),
        "fir_name": fir,
        "conus_series": match.group("series").upper(),
        "conus_update": int(match.group("upd")),
        "conus_for_text": match.group("for_text").strip(),
        "header_style": "conus_updt",
        "body": body,
    }


def _split_airmet_areas(body: str) -> list[str]:
    """
    Internal helper ``_split_airmet_areas``.

    Parameters
    ----------
    body : str
        Argument ``body``.

    Returns
    -------
    list[str]
        Return value.
    """
    segments = [segment.strip() for segment in _AIR_AREA_BOUNDARY.split(body) if segment.strip()]
    return segments if len(segments) > 1 else [body]


def _airmet_area_ir(segment: str, *, default_phenomenon: str | None = None) -> dict[str, Any]:
    """
    Internal helper ``_airmet_area_ir``.

    Parameters
    ----------
    segment : str
        Argument ``segment``.

    default_phenomenon : str | None, optional
        Argument ``default_phenomenon``.

    Returns
    -------
    dict[str, Any]
        Return value.
    """
    area: dict[str, Any] = {}
    area_phenomenon = default_phenomenon or _detect_phenomenon(segment, _AIR_PHENOMENA)
    if area_phenomenon is not None:
        area["phenomenon"] = area_phenomenon
    _enrich_hazard_body(area, segment)
    return area


def _parse_airmet_outlook(outlook_text: str, *, default_phenomenon: str) -> dict[str, Any]:
    """
    Internal helper ``_parse_airmet_outlook``.

    Parameters
    ----------
    outlook_text : str
        Argument ``outlook_text``.

    default_phenomenon : str
        Argument ``default_phenomenon``.

    Returns
    -------
    dict[str, Any]
        Return value.
    """
    match = _OTLK_VALID.search(outlook_text)
    if match is None:
        raise ValueError("unable to parse AIRMET outlook valid period")
    from_hhmm = match.group("from")
    to_hhmm = match.group("to")
    tail = outlook_text[match.end() :].strip()
    if tail.startswith("..."):
        tail = tail[3:].strip()
    outlook = _airmet_area_ir(tail, default_phenomenon=default_phenomenon)
    outlook["valid_from_hour"] = int(from_hhmm[0:2])
    outlook["valid_from_minute"] = int(from_hhmm[2:4])
    outlook["valid_to_hour"] = int(to_hhmm[0:2])
    outlook["valid_to_minute"] = int(to_hhmm[2:4])
    return outlook
