"""Split part body (exec'd into package namespace)."""

from __future__ import annotations


def _rwy_location_description(loc: str) -> str:
    """
    Internal helper ``_rwy_location_description``.

    Parameters
    ----------
    loc : str
        Argument ``loc``.

    Returns
    -------
    str
        Return value.
    """
    m = re.match(r"RWY(?P<rwy>\d{2}[LCR]?)(?:\s+(?P<tdz>TDZ))?$", loc.strip())
    if m is None:
        return loc.replace("RWY", "RUNWAY ", 1)
    desc = f"RUNWAY {m.group('rwy')}"
    if m.group("tdz"):
        desc = f"{desc} TDZ"
    return desc


def _parse_second_location_remark(remarks: str) -> dict[str, Any] | None:
    """
    Internal helper ``_parse_second_location_remark``.

    Parameters
    ----------
    remarks : str
        Argument ``remarks``.

    Returns
    -------
    dict[str, Any] | None
        Return value.
    """
    m = _SECOND_LOC.search(remarks)
    if m is None:
        return None
    if m.group("cig") is None and m.group("vis") is None:
        return None
    entry: dict[str, Any] = {
        "location_description": _rwy_location_description(m.group("loc")),
    }
    if m.group("cig") is not None:
        entry["ceiling_height_ft"] = int(m.group("cig")) * 100
    if m.group("vis") is not None:
        sm = _parse_sm_fraction(m.group("vis"))
        entry["visibility_ft"] = _sm_float_to_ft(sm)
        if m.group("vis_lt"):
            entry["visibility_below_sensor_minimum"] = True
    return entry


def _parse_tower_visibility_remark(remarks: str) -> dict[str, Any] | None:
    """
    Internal helper ``_parse_tower_visibility_remark``.

    Parameters
    ----------
    remarks : str
        Argument ``remarks``.

    Returns
    -------
    dict[str, Any] | None
        Return value.
    """
    m = _TWR_VIS.search(remarks)
    if m is None:
        return None
    sm = _parse_sm_fraction(m.group("vis"))
    entry: dict[str, Any] = {"visibility_m": _sm_float_to_m(sm)}
    if m.group("lt"):
        entry["less_than"] = True
    return entry


def _parse_sector_visibility_remark(remarks: str) -> dict[str, Any] | None:
    """
    Internal helper ``_parse_sector_visibility_remark``.

    Parameters
    ----------
    remarks : str
        Argument ``remarks``.

    Returns
    -------
    dict[str, Any] | None
        Return value.
    """
    m = _SECTOR_VIS.search(remarks)
    if m is None:
        return None
    sm = _parse_sm_fraction(m.group("vis"))
    entry: dict[str, Any] = {
        "visibility_m": _sm_float_to_m(sm),
        "direction_deg": float(_LTG_COMPASS_DEG[m.group("dir")]),
    }
    if m.group("lt"):
        entry["below_sensor_minimum"] = True
    return entry


def _parse_obscuration_remark(remarks: str) -> dict[str, Any] | None:
    """
    Internal helper ``_parse_obscuration_remark``.

    Parameters
    ----------
    remarks : str
        Argument ``remarks``.

    Returns
    -------
    dict[str, Any] | None
        Return value.
    """
    m = _OBSCURATION.search(remarks)
    if m is None:
        return None
    return {
        "height_ft": int(m.group("base")) * 100,
        "amount_href": _CLOUD_AMOUNT_HREF.format(amt=m.group("amt")),
        "weather_href": _WX_4678_HREF.format(code=m.group("wx")),
    }


def _parse_variable_ceiling_remark(remarks: str) -> dict[str, Any] | None:
    """
    Internal helper ``_parse_variable_ceiling_remark``.

    Parameters
    ----------
    remarks : str
        Argument ``remarks``.

    Returns
    -------
    dict[str, Any] | None
        Return value.
    """
    m = _CIG_VAR.search(remarks)
    if m is None:
        return None
    return {
        "minimum_ft": int(m.group("min")) * 100,
        "maximum_ft": int(m.group("max")) * 100,
    }


def _parse_variable_sky_remark(remarks: str) -> dict[str, Any] | None:
    """
    Internal helper ``_parse_variable_sky_remark``.

    Parameters
    ----------
    remarks : str
        Argument ``remarks``.

    Returns
    -------
    dict[str, Any] | None
        Return value.
    """
    m = _SKY_VAR.search(remarks)
    if m is None:
        return None
    return {
        "first_amount_href": _CLOUD_AMOUNT_HREF.format(amt=m.group("a")),
        "second_amount_href": _CLOUD_AMOUNT_HREF.format(amt=m.group("b")),
    }


def _parse_variable_visibility_remark(remarks: str) -> dict[str, Any] | None:
    """
    Internal helper ``_parse_variable_visibility_remark``.

    Parameters
    ----------
    remarks : str
        Argument ``remarks``.

    Returns
    -------
    dict[str, Any] | None
        Return value.
    """
    m = _VIS_VAR.search(remarks)
    if m is None:
        return None
    entry: dict[str, Any] = {
        "minimum_m": _sm_float_to_m(_parse_sm_fraction(m.group("min"))),
        "maximum_m": _sm_float_to_m(_parse_sm_fraction(m.group("max"))),
    }
    if m.group("lt"):
        entry["below_minimum"] = True
    return entry


def _sky_level_field(token: str, base: int) -> dict[str, str]:
    """
    Internal helper ``_sky_level_field``.

    Parameters
    ----------
    token : str
        Argument ``token``.

    base : int
        Argument ``base``.

    Returns
    -------
    dict[str, str]
        Return value.
    """
    if token == "/":
        return {"nil_reason": _NIL_NOT_OBSERVABLE}
    code = base + int(token)
    return {"href": _BUFR_CLOUD_HREF.format(code=code)}


def _parse_sky_types_remark(remarks: str) -> dict[str, Any] | None:
    """
    Internal helper ``_parse_sky_types_remark``.

    Parameters
    ----------
    remarks : str
        Argument ``remarks``.

    Returns
    -------
    dict[str, Any] | None
        Return value.
    """
    m = _SKY_TYPES.search(remarks)
    if m is None:
        return None
    low = _sky_level_field(m.group("cl"), 30)
    mid = _sky_level_field(m.group("cm"), 20)
    high = _sky_level_field(m.group("ch"), 10)
    sky: dict[str, Any] = {}
    if "href" in low:
        sky["low_href"] = low["href"]
    else:
        sky["low_nil_reason"] = low["nil_reason"]
    if "href" in mid:
        sky["middle_href"] = mid["href"]
    else:
        sky["middle_nil_reason"] = mid["nil_reason"]
    if "href" in high:
        sky["high_href"] = high["href"]
    else:
        sky["high_nil_reason"] = high["nil_reason"]
    return sky


def _parse_convective_remark(remarks: str) -> dict[str, Any] | None:
    """
    Internal helper ``_parse_convective_remark``.

    Parameters
    ----------
    remarks : str
        Argument ``remarks``.

    Returns
    -------
    dict[str, Any] | None
        Return value.
    """
    m = _CONVECTIVE.search(remarks)
    if m is None:
        return None
    ctype = m.group("ctype")
    entry: dict[str, Any] = {
        "cloud_type_href": _CONVECTIVE_TYPE_HREF.format(code=_CONVECTIVE_TYPE_CODES[ctype]),
    }
    dist = m.group("dist")
    if dist:
        entry["qualitative_distance_href"] = _DIST_HREF.format(code=_CONVECTIVE_DIST_CODES[dist])
    sector = _lightning_sector(m.group("sector"))
    if sector is not None:
        entry["sector"] = sector
    mov = m.group("mov")
    if mov:
        entry["direction_of_motion_deg"] = _LTG_COMPASS_DEG[mov]
        # True north as 360 for N (PDF overhead-moving-north sample).
        if mov == "N":
            entry["direction_of_motion_deg"] = 360.0
    return entry


def _parse_hail_size_remark(remarks: str) -> dict[str, Any] | None:
    """
    Internal helper ``_parse_hail_size_remark``.

    Parameters
    ----------
    remarks : str
        Argument ``remarks``.

    Returns
    -------
    dict[str, Any] | None
        Return value.
    """
    m = _HAIL_SIZE.search(remarks)
    if m is None:
        return None
    if m.group("below"):
        inches = _frac_to_inches(m.group("bfrac"))
        return {"maximum_diameter_in": inches, "size_operator": "BELOW"}
    if m.group("whole") is not None and m.group("frac"):
        inches = float(int(m.group("whole"))) + _frac_to_inches(m.group("frac"))
        return {"maximum_diameter_in": inches}
    if m.group("onlyfrac"):
        return {"maximum_diameter_in": _frac_to_inches(m.group("onlyfrac"))}
    if m.group("onlywhole"):
        return {"maximum_diameter_in": float(int(m.group("onlywhole")))}
    return None


def _precip_6_period(hour: int) -> str:
    """
    Internal helper ``_precip_6_period``.

    Parameters
    ----------
    hour : int
        Argument ``hour``.

    Returns
    -------
    str
        Return value.
    """
    if hour % 6 == 0:
        return "PT6H"
    return "PT3H"


def _parse_max_min_temperatures(remarks: str) -> list[dict[str, Any]]:
    """
    Internal helper ``_parse_max_min_temperatures``.

    Parameters
    ----------
    remarks : str
        Argument ``remarks``.

    Returns
    -------
    list[dict[str, Any]]
        Return value.
    """
    rows: list[dict[str, Any]] = []
    max_6 = _RMK_MAX_6H.search(remarks)
    min_6 = _RMK_MIN_6H.search(remarks)
    if max_6 is not None or min_6 is not None:
        row: dict[str, Any] = {"preceding_period": "PT6H"}
        if max_6 is not None:
            row["max_c"] = _tenths_celsius(max_6.group("sign"), max_6.group("ttt"))
        if min_6 is not None:
            row["min_c"] = _tenths_celsius(min_6.group("sign"), min_6.group("ttt"))
        rows.append(row)
    mm24 = _RMK_MAXMIN_24H.search(remarks)
    if mm24 is not None:
        rows.append(
            {
                "preceding_period": "PT24H",
                "max_c": _tenths_celsius(mm24.group("msign"), mm24.group("mttt")),
                "min_c": _tenths_celsius(mm24.group("nsign"), mm24.group("nttt")),
            }
        )
    return rows


def _precip_quantity(hundredths: int, *, period: str) -> dict[str, Any]:
    """
    Internal helper ``_precip_quantity``.

    Parameters
    ----------
    hundredths : int
        Argument ``hundredths``.

    period : str
        Argument ``period``.

    Returns
    -------
    dict[str, Any]
        Return value.
    """
    row: dict[str, Any] = {
        "processed_weather_element_href": _PRECIP_ELEMENT_HREF,
        "value_type_href": _STAT_ACCUM_HREF,
        "value_period": period,
        "uom": "[in_i]",
    }
    if hundredths == 0:
        # FMH P0000 / 60000 / 70000 - less than 0.01" (PDF BELOW sample).
        row["processed_value"] = 0.01
        row["qualifier"] = "BELOW"
    else:
        row["processed_value"] = hundredths / 100.0
    return row


def _parse_recent_weather_remarks(remarks: str) -> list[dict[str, Any]]:
    """
    Internal helper ``_parse_recent_weather_remarks``.

    Parameters
    ----------
    remarks : str
        Argument ``remarks``.

    Returns
    -------
    list[dict[str, Any]]
        Return value.
    """
    rows: list[dict[str, Any]] = []
    for m in _RECENT_WX.finditer(remarks):
        wx = m.group("wx")
        row: dict[str, Any] = {
            "phenomenon_href": _WX_4678_HREF.format(code=wx),
            "wx": wx,
        }
        if m.group("b") is not None:
            btok = m.group("b")
            row["begin_minute"] = int(btok[-2:])
            if len(btok) == 4:
                row["begin_hour"] = int(btok[0:2])
        end_tok = m.group("e") or m.group("e_only")
        if end_tok is not None:
            row["end_minute"] = int(end_tok[-2:])
            if len(end_tok) == 4:
                row["end_hour"] = int(end_tok[0:2])
        rows.append(row)
    return rows


def _parse_processed_precip(remarks: str, hour: int) -> list[dict[str, Any]]:
    """
    Internal helper ``_parse_processed_precip``.

    Parameters
    ----------
    remarks : str
        Argument ``remarks``.

    hour : int
        Argument ``hour``.

    Returns
    -------
    list[dict[str, Any]]
        Return value.
    """
    qty: list[dict[str, Any]] = []
    precip = _RMK_P.search(remarks)
    if precip is not None:
        qty.append(_precip_quantity(int(precip.group("p")), period="PT1H"))
    p6 = _RMK_PRECIP_6.search(remarks)
    if p6 is not None:
        qty.append(_precip_quantity(int(p6.group("p")), period=_precip_6_period(hour)))
    p7 = _RMK_PRECIP_7.search(remarks)
    if p7 is not None:
        qty.append(_precip_quantity(int(p7.group("p")), period="PT24H"))
    return qty
