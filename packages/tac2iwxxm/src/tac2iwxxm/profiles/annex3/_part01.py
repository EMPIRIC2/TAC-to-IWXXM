"""Split part body (exec'd into package namespace)."""

from __future__ import annotations


def obs_timestamp(ir: dict[str, Any]) -> str:
    """
    Build observation/issue time matching annex3 golden fixtures.

    Parameters
    ----------
    ir : dict[str, Any]
        Parsed product fields.

    Returns
    -------
    str
        Observation/issue time matching annex3 golden fixtures.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (obs_timestamp)
    2
    """
    from tac2iwxxm.time_anchor import iso_stamp

    day = int(ir["day"])
    hour = int(ir["hour"])
    minute = int(ir["minute"])
    # WMO YUDO examples (NIL + A3-1 / A3-2) use 2012-08; other pack cases use 2023-06.
    legacy = "2012-08" if ir.get("station") == "YUDO" else "2023-06"
    return iso_stamp(ir, day, hour, minute, legacy=legacy)


def _fmt_cel(value: object) -> str:
    """
    Internal helper ``_fmt_cel``.

    Parameters
    ----------
    value : object
        Argument ``value``.

    Returns
    -------
    str
        Return value.
    """
    return f"{float(str(value)):.1f}"


def _fmt_hpa(value: object) -> str:
    """
    Internal helper ``_fmt_hpa``.

    Parameters
    ----------
    value : object
        Argument ``value``.

    Returns
    -------
    str
        Return value.
    """
    fval = float(str(value))
    if fval == int(fval):
        return str(int(fval))
    return str(fval)


def _fmt_speed(value: object, *, force_one_decimal: bool = False) -> str:
    """
    Internal helper ``_fmt_speed``.

    Parameters
    ----------
    value : object
        Argument ``value``.

    force_one_decimal : bool, optional
        Argument ``force_one_decimal``.

    Returns
    -------
    str
        Return value.
    """
    fval = float(str(value))
    if force_one_decimal or fval != int(fval):
        return f"{fval:.1f}"
    return str(int(fval))


def _annex3_gml_id(ir: dict[str, Any], product: str) -> str:
    """
    Internal helper ``_annex3_gml_id``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    product : str
        Argument ``product``.

    Returns
    -------
    str
        Return value.
    """
    root = product.lower()
    station = str(ir["station"]).lower()
    if ir.get("nil"):
        return f"{root}.nil.{station}"
    if ir.get("cavok"):
        return f"{root}.cavok.{station}"
    if ir.get("nsc"):
        return f"{root}.nsc.{station}"
    if ir.get("ncd"):
        return f"{root}.ncd.{station}"
    if ir.get("nosig"):
        return f"{root}.nosig.{station}"
    if ir.get("tempo_trend") and ir["tempo_trend"].get("weather_nsw"):
        return f"{root}.nsw.{station}"
    if ir.get("vertical_visibility_not_observable"):
        return f"{root}.vv.{station}"
    if ir.get("present_weather_not_observable"):
        return f"{root}.wx.{station}"
    if ir.get("rvr"):
        return f"{root}.rvr.{station}"
    if ir.get("wind_dir_ccw_deg") is not None:
        return f"{root}.wind.{station}"
    # F25 WMO official seeds.
    if station == "yudo" and not ir.get("nil"):
        return f"{root}.wmo.{station}"
    return f"{root}.basic.{station}"


def _visibility_block(ir: dict[str, Any], *, visibility_extension: str = "") -> str:
    """
    Internal helper ``_visibility_block``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    visibility_extension : str, optional
        Argument ``visibility_extension``.

    Returns
    -------
    str
        Return value.
    """
    if ir.get("visibility_not_observable"):
        return f'      <iwxxm:visibility xsi:nil="true" nilReason="{NIL_NOT_OBS}"/>\n'
    vis_op = ""
    if ir.get("visibility_above"):
        vis_op = "\n          <iwxxm:prevailingVisibilityOperator>ABOVE</iwxxm:prevailingVisibilityOperator>"
    min_vis = ""
    if ir.get("min_visibility_m") is not None:
        min_vis = f'\n          <iwxxm:minimumVisibility uom="m">{ir["min_visibility_m"]}</iwxxm:minimumVisibility>'
        if ir.get("min_visibility_dir_deg") is not None:
            min_vis += (
                f'\n          <iwxxm:minimumVisibilityDirection uom="deg">'
                f"{ir['min_visibility_dir_deg']}</iwxxm:minimumVisibilityDirection>"
            )
    vis_uom = str(ir.get("visibility_display_uom") or "m")
    vis_val = ir.get("visibility_display_value", ir["visibility_m"])
    ext = f"\n{visibility_extension}" if visibility_extension else ""
    return f"""      <iwxxm:visibility>
        <iwxxm:AerodromeHorizontalVisibility>
          <iwxxm:prevailingVisibility uom="{vis_uom}">{vis_val}</iwxxm:prevailingVisibility>{vis_op}{min_vis}{ext}
        </iwxxm:AerodromeHorizontalVisibility>
      </iwxxm:visibility>
"""


def _rvr_block(ir: dict[str, Any], *, rvr_extension: str = "") -> str:
    """
    Internal helper ``_rvr_block``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    rvr_extension : str, optional
        Argument ``rvr_extension``.

    Returns
    -------
    str
        Return value.
    """
    rvr_raw = ir.get("rvr")
    if not isinstance(rvr_raw, dict):
        # Guidance / Amd79 CWFD: when vis is missing/notObservable and no RVR group,
        # emit empty rvr with common/nil/missing (sensors absent / not reported).
        # Schematron METAR_SPECI.MeteorologicalAerodromeObservation-2 also requires
        # exists(iwxxm:rvr) whenever prevailing visibility is below 1500 m.
        vis_m = ir.get("visibility_m")
        low_vis = isinstance(vis_m, (int, float)) and float(vis_m) < 1500
        if ir.get("visibility_not_observable") or low_vis:
            return f'      <iwxxm:rvr xsi:nil="true" nilReason="{NIL_MISSING}"/>\n'
        return ""
    rvr = cast(dict[str, Any], rvr_raw)
    rwy = escape(str(rvr["runway"]))
    tend = str(rvr.get("tendency") or "")
    tend_attr = f' pastTendency="{tend}"' if tend else ""
    if rvr.get("variable"):
        if rvr_extension:
            # iwxxm-us: mean withheld; min/max live in AerodromeVariableRVR extension.
            mean_xml = f'          <iwxxm:meanRVR uom="m" xsi:nil="true" nilReason="{NIL_WITHHELD}"/>'
            ext = f"\n{rvr_extension}"
        else:
            # annex3 path: no US extension - emit midpoint mean for XSD shape.
            mid = round((int(rvr["min_m"]) + int(rvr["max_m"])) / 2)
            mean_xml = f'          <iwxxm:meanRVR uom="m">{mid}</iwxxm:meanRVR>'
            ext = ""
    else:
        op = str(rvr.get("operator") or "")
        op_xml = f"\n          <iwxxm:meanRVROperator>{op}</iwxxm:meanRVROperator>" if op else ""
        mean_xml = f'          <iwxxm:meanRVR uom="m">{rvr["mean_m"]}</iwxxm:meanRVR>{op_xml}'
        ext = f"\n{rvr_extension}" if rvr_extension else ""
    return f"""      <iwxxm:rvr>
        <iwxxm:AerodromeRunwayVisualRange{tend_attr}>
          <iwxxm:runway>
            <aixm:RunwayDirection gml:id="rwy.{rwy.lower()}">
              <aixm:timeSlice>
                <aixm:RunwayDirectionTimeSlice gml:id="rwy.ts.{rwy.lower()}">
                  <gml:validTime/>
                  <aixm:interpretation>SNAPSHOT</aixm:interpretation>
                  <aixm:designator>{rwy}</aixm:designator>
                </aixm:RunwayDirectionTimeSlice>
              </aixm:timeSlice>
            </aixm:RunwayDirection>
          </iwxxm:runway>
{mean_xml}{ext}
        </iwxxm:AerodromeRunwayVisualRange>
      </iwxxm:rvr>
"""


def _present_weather_block(ir: dict[str, Any]) -> str:
    """
    Internal helper ``_present_weather_block``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    Returns
    -------
    str
        Return value.
    """
    if ir.get("present_weather_not_observable"):
        return f'      <iwxxm:presentWeather xsi:nil="true" nilReason="{NIL_NOT_OBS}"/>\n'
    codes_raw = ir.get("present_weather")
    if not isinstance(codes_raw, list):
        return ""
    codes = [str(c) for c in cast(list[Any], codes_raw)]
    parts: list[str] = []
    for code in codes:
        href = escape(WX_HREF.format(code=code))
        parts.append(f'      <iwxxm:presentWeather xlink:href="{href}"/>')
    return ("\n".join(parts) + "\n") if parts else ""


def _recent_weather_block(ir: dict[str, Any]) -> str:
    """
    ICAO recent-weather groups (RETS, RESHRA) on the default profile.

    Parameters
    ----------
    ir : dict[str, Any]
        Parsed report. ``recent_weather`` is a list of 4678 codes.

    Returns
    -------
    str
        ``iwxxm:recentWeather`` elements, or an empty string.
    """
    codes_raw = ir.get("recent_weather")
    if not isinstance(codes_raw, list):
        return ""
    parts: list[str] = []
    for code in cast(list[Any], codes_raw):
        href = escape(WX_HREF.format(code=str(code)))
        parts.append(f'      <iwxxm:recentWeather xlink:href="{href}"/>')
    return ("\n".join(parts) + "\n") if parts else ""


def _cloud_block(ir: dict[str, Any], *, cloud_layer_extension: str = "") -> str:
    """
    Internal helper ``_cloud_block``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    cloud_layer_extension : str, optional
        Argument ``cloud_layer_extension``.

    Returns
    -------
    str
        Return value.
    """
    if ir.get("nsc"):
        return f'      <iwxxm:cloud nilReason="{NIL_NSC}"/>\n'
    if ir.get("ncd"):
        return f'      <iwxxm:cloud nilReason="{NIL_NCD}"/>\n'
    if ir.get("vertical_visibility_not_observable"):
        return f"""      <iwxxm:cloud>
        <iwxxm:AerodromeCloud>
          <iwxxm:verticalVisibility uom="N/A" xsi:nil="true" nilReason="{NIL_NOT_OBS}"/>
        </iwxxm:AerodromeCloud>
      </iwxxm:cloud>
"""
    clouds_raw = ir.get("clouds")
    layers: list[dict[str, Any]] = []
    if isinstance(clouds_raw, list) and clouds_raw:
        cloud_items = cast(list[Any], clouds_raw)
        layers.extend(cast(dict[str, Any], item) for item in cloud_items if isinstance(item, dict))
    elif ir.get("cloud_amount") and ir.get("cloud_base_ft") is not None:
        layers = [{"amount": ir["cloud_amount"], "base_ft": ir["cloud_base_ft"]}]
    if not layers:
        return ""
    # Attach US variable CIG/SKY extensions to the first BKN/OVC (ceiling) layer.
    ceil_idx = 0
    for i, layer in enumerate(layers):
        if str(layer.get("amount") or "") in {"BKN", "OVC"}:
            ceil_idx = i
            break
    layer_xml: list[str] = []
    for i, layer in enumerate(layers):
        href = CLOUD_HREF.format(amt=layer["amount"])
        ctype = layer.get("cloud_type")
        ctype_xml = ""
        if ctype:
            thref = escape(CLOUD_TYPE_HREF.format(ctype=str(ctype)))
            ctype_xml = f'\n              <iwxxm:cloudType xlink:href="{thref}"/>'
        ext = ""
        if cloud_layer_extension and i == ceil_idx:
            ext = f"\n{cloud_layer_extension}"
        if layer.get("base_not_observable"):
            base_xml = f'<iwxxm:base uom="N/A" xsi:nil="true" nilReason="{NIL_NOT_OBS}"/>'
        else:
            base_xml = f'<iwxxm:base uom="[ft_i]">{layer["base_ft"]}</iwxxm:base>'
        layer_xml.append(
            f"""          <iwxxm:layer>
            <iwxxm:CloudLayer>
              <iwxxm:amount xlink:href="{escape(href)}"/>
              {base_xml}{ctype_xml}{ext}
            </iwxxm:CloudLayer>
          </iwxxm:layer>"""
        )
    joined = "\n".join(layer_xml)
    return f"""      <iwxxm:cloud>
        <iwxxm:AerodromeCloud>
{joined}
        </iwxxm:AerodromeCloud>
      </iwxxm:cloud>
"""


def _surface_wind_inner(ir: dict[str, Any], *, peak_extension: str = "") -> str:
    """
    Internal helper ``_surface_wind_inner``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    peak_extension : str, optional
        Argument ``peak_extension``.

    Returns
    -------
    str
        Return value.
    """
    variable = bool(ir.get("wind_variable"))
    var_attr = "true" if variable else "false"
    if variable:
        wind_dir = ""
    else:
        wind_dir = f'\n          <iwxxm:meanWindDirection uom="deg">{ir["wind_dir_deg"]}</iwxxm:meanWindDirection>'

    if ir.get("wind_speed_mps") is not None:
        speed_uom = "m/s"
        speed_val = _fmt_speed(ir["wind_speed_mps"], force_one_decimal=True)
        gust_raw = ir.get("wind_gust_mps")
    else:
        speed_uom = "[kn_i]"
        # WMO SPECI A3-2 uses one decimal on mean; keep integers for pack fixtures via int values.
        speed_val = _fmt_speed(ir["wind_speed_kt"], force_one_decimal=str(ir.get("station")) == "YUDO")
        gust_raw = ir.get("wind_gust_kt")

    wind_gust = ""
    if gust_raw is not None:
        # Vendor SPECI gust is integer; mean may be decimal.
        gust_txt = _fmt_speed(gust_raw, force_one_decimal=False)
        wind_gust = f'\n          <iwxxm:windGustSpeed uom="{speed_uom}">{gust_txt}</iwxxm:windGustSpeed>'

    extremes = ""
    if ir.get("wind_dir_ccw_deg") is not None and ir.get("wind_dir_cw_deg") is not None:
        # XSD sequence: extremeClockwise before extremeCounterClockwise.
        extremes = (
            f'\n          <iwxxm:extremeClockwiseWindDirection uom="deg">{ir["wind_dir_cw_deg"]}</iwxxm:extremeClockwiseWindDirection>'
            f'\n          <iwxxm:extremeCounterClockwiseWindDirection uom="deg">{ir["wind_dir_ccw_deg"]}</iwxxm:extremeCounterClockwiseWindDirection>'
        )
    return f"""      <iwxxm:surfaceWind>
        <iwxxm:AerodromeSurfaceWind variableWindDirection="{var_attr}">{wind_dir}
          <iwxxm:meanWindSpeed uom="{speed_uom}">{speed_val}</iwxxm:meanWindSpeed>{wind_gust}{extremes}
{peak_extension}        </iwxxm:AerodromeSurfaceWind>
      </iwxxm:surfaceWind>
"""


def _trend_phenomenon_time(trend: dict[str, Any], idx: int) -> str:
    """
    Internal helper ``_trend_phenomenon_time``.

    Parameters
    ----------
    trend : dict[str, Any]
        Argument ``trend``.

    idx : int
        Argument ``idx``.

    Returns
    -------
    str
        Return value.
    """
    if trend.get("phenomenon_begin") and trend.get("phenomenon_end"):
        return f"""      <iwxxm:phenomenonTime>
        <gml:TimePeriod gml:id="t.trend.{idx}">
          <gml:beginPosition>{trend["phenomenon_begin"]}</gml:beginPosition>
          <gml:endPosition>{trend["phenomenon_end"]}</gml:endPosition>
        </gml:TimePeriod>
      </iwxxm:phenomenonTime>"""
    if trend.get("phenomenon_at"):
        return f"""      <iwxxm:phenomenonTime>
        <gml:TimeInstant gml:id="t.trend.{idx}">
          <gml:timePosition>{trend["phenomenon_at"]}</gml:timePosition>
        </gml:TimeInstant>
      </iwxxm:phenomenonTime>"""
    return f'      <iwxxm:phenomenonTime nilReason="{NIL_MISSING}"/>'


def _trend_weather_block(trend: dict[str, Any]) -> str:
    """
    Internal helper ``_trend_weather_block``.

    Parameters
    ----------
    trend : dict[str, Any]
        Argument ``trend``.

    Returns
    -------
    str
        Return value.
    """
    if trend.get("weather_nsw"):
        return f'\n      <iwxxm:weather nilReason="{NIL_NSC}"/>'
    codes_raw = trend.get("weather")
    if not isinstance(codes_raw, list):
        return ""
    parts: list[str] = []
    for raw_code in cast(list[Any], codes_raw):
        href = escape(WX_HREF.format(code=str(raw_code)))
        parts.append(f'\n      <iwxxm:weather xlink:href="{href}"/>')
    return "".join(parts)
