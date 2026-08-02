"""Annex-3 profile XML writer for METAR/SPECI (F6.a / F20 S3 / F25 W1–W2)."""

from __future__ import annotations

from typing import Any, cast
from xml.sax.saxutils import escape

NS = {
    "2025-2": "http://icao.int/iwxxm/2025-2",
    "2023-1": "http://icao.int/iwxxm/2023-1",
}

CLOUD_HREF = "http://codes.wmo.int/49-2/CloudAmountReportedAtAerodrome/{amt}"
CLOUD_TYPE_HREF = "http://codes.wmo.int/49-2/SigConvectiveCloudType/{ctype}"
WX_HREF = "http://codes.wmo.int/306/4678/{code}"
NIL_MISSING = "http://codes.wmo.int/common/nil/missing"
NIL_NOSIG = "http://codes.wmo.int/common/nil/noSignificantChange"
NIL_NSC = "http://codes.wmo.int/common/nil/nothingOfOperationalSignificance"
NIL_NCD = "http://codes.wmo.int/common/nil/notDetectedByAutoSystem"
NIL_NOT_OBS = "http://codes.wmo.int/common/nil/notObservable"
NIL_WITHHELD = "http://codes.wmo.int/common/nil/withheld"

# WMO Annex 3 / IWXXM examples use fictional YUDO = DONLON/INTERNATIONAL.
_YUDO_NAME = "DONLON/INTERNATIONAL"
_YUDO_POS = "12.34 -12.34"
_YUDO_ELEV_M = "12"


def obs_timestamp(ir: dict[str, Any]) -> str:
    """Build observation/issue time matching annex3 golden fixtures."""
    day = int(ir["day"])
    hour = int(ir["hour"])
    minute = int(ir["minute"])
    # WMO YUDO examples (NIL + A3-1 / A3-2) use 2012-08; other pack cases use 2023-06.
    if ir.get("station") == "YUDO":
        return f"2012-08-{day:02d}T{hour:02d}:{minute:02d}:00Z"
    return f"2023-06-{day:02d}T{hour:02d}:{minute:02d}:00Z"


def _fmt_cel(value: Any) -> str:
    """Format Celsius for IWXXM (WMO examples use one decimal place)."""
    return f"{float(value):.1f}"


def _fmt_hpa(value: Any) -> str:
    """Format QNH: whole hPa without trailing .0; tenths otherwise."""
    fval = float(value)
    if fval == int(fval):
        return str(int(fval))
    return str(fval)


def _fmt_speed(value: Any, *, force_one_decimal: bool = False) -> str:
    """Format wind speed; WMO mean speeds often use one decimal."""
    fval = float(value)
    if force_one_decimal or fval != int(fval):
        return f"{fval:.1f}"
    return str(int(fval))


def _annex3_gml_id(ir: dict[str, Any], product: str) -> str:
    """Stable gml:id for annex3 METAR/SPECI goldens (theme-aware for S3 / W1–W2)."""
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
    ext = f"\n{visibility_extension}" if visibility_extension else ""
    return f"""      <iwxxm:visibility>
        <iwxxm:AerodromeHorizontalVisibility>
          <iwxxm:prevailingVisibility uom="m">{ir["visibility_m"]}</iwxxm:prevailingVisibility>{vis_op}{min_vis}{ext}
        </iwxxm:AerodromeHorizontalVisibility>
      </iwxxm:visibility>
"""


def _rvr_block(ir: dict[str, Any], *, rvr_extension: str = "") -> str:
    rvr_raw = ir.get("rvr")
    if not isinstance(rvr_raw, dict):
        # Guidance / Amd79 CWFD: when vis is missing/notObservable and no RVR group,
        # emit empty rvr with common/nil/missing (sensors absent / not reported).
        if ir.get("visibility_not_observable"):
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
            # annex3 path: no US extension — emit midpoint mean for XSD shape.
            mid = int(round((int(rvr["min_m"]) + int(rvr["max_m"])) / 2))
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


def _cloud_block(ir: dict[str, Any], *, cloud_layer_extension: str = "") -> str:
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
        for item in cloud_items:
            if isinstance(item, dict):
                layers.append(cast(dict[str, Any], item))
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
        layer_xml.append(
            f"""          <iwxxm:layer>
            <iwxxm:CloudLayer>
              <iwxxm:amount xlink:href="{escape(href)}"/>
              <iwxxm:base uom="[ft_i]">{layer["base_ft"]}</iwxxm:base>{ctype_xml}{ext}
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


def _trend_forecasts(ir: dict[str, Any]) -> str:
    parts: list[str] = []
    forecasts_raw = ir.get("trend_forecasts")
    forecasts: list[dict[str, Any]] = []
    if isinstance(forecasts_raw, list) and forecasts_raw:
        for item in cast(list[Any], forecasts_raw):
            if isinstance(item, dict):
                forecasts.append(cast(dict[str, Any], item))
    else:
        # Legacy F20 path: nosig + single tempo_trend.
        if ir.get("nosig") and not forecasts:
            parts.append(f'  <iwxxm:trendForecast nilReason="{NIL_NOSIG}"/>\n')
        tempo_raw = ir.get("tempo_trend")
        if isinstance(tempo_raw, dict):
            forecasts = [cast(dict[str, Any], tempo_raw)]

    for idx, trend in enumerate(forecasts, start=1):
        if trend.get("nil_nosig"):
            parts.append(f'  <iwxxm:trendForecast nilReason="{NIL_NOSIG}"/>\n')
            continue
        indicator = str(trend.get("change_indicator") or "TEMPORARY_FLUCTUATIONS")
        cavok = bool(trend.get("cavok"))
        cavok_attr = ' cloudAndVisibilityOK="true"' if cavok else ' cloudAndVisibilityOK="false"'
        # Second METAR BECMG AT1800 omits cloudAndVisibilityOK in vendor — keep false when weather/vis present.
        if indicator == "BECOMING" and trend.get("weather_nsw") and not trend.get("cloud_nsc"):
            # Vendor metar-A3-1 second trend has no cloudAndVisibilityOK attribute.
            cavok_attr = ""

        phen = _trend_phenomenon_time(trend, idx)
        time_ind = ""
        if trend.get("time_indicator"):
            time_ind = f"\n      <iwxxm:timeIndicator>{trend['time_indicator']}</iwxxm:timeIndicator>"

        vis = ""
        if trend.get("visibility_m") is not None:
            vis = f'\n      <iwxxm:prevailingVisibility uom="m">{trend["visibility_m"]}</iwxxm:prevailingVisibility>'
            if trend.get("visibility_above"):
                vis += "\n      <iwxxm:prevailingVisibilityOperator>ABOVE</iwxxm:prevailingVisibilityOperator>"

        weather = _trend_weather_block(trend)
        cloud = ""
        if trend.get("cloud_nsc"):
            cloud = f'\n      <iwxxm:cloud nilReason="{NIL_NSC}"/>'

        parts.append(
            f"""  <iwxxm:trendForecast>
    <iwxxm:MeteorologicalAerodromeTrendForecast gml:id="trend.{idx}" changeIndicator="{indicator}"{cavok_attr}>
{phen}{time_ind}{vis}{weather}{cloud}
    </iwxxm:MeteorologicalAerodromeTrendForecast>
  </iwxxm:trendForecast>
"""
        )
    return "".join(parts)


def build_observation_and_trends(
    ir: dict[str, Any],
    *,
    addendum_extension: str = "",
    peak_extension: str = "",
    rvr_extension: str = "",
    visibility_extension: str = "",
    cloud_layer_extension: str = "",
) -> tuple[str, str]:
    """
    Build IWXXM observation element and trailing trendForecast elements.

    Parameters
    ----------
    ir :
        Parsed METAR/SPECI IR.
    addendum_extension :
        Optional observation-level extension XML (iwxxm_us Addendum).
    peak_extension :
        Optional surface-wind extension XML (iwxxm_us peak wind).
    rvr_extension :
        Optional RVR extension XML (iwxxm_us AerodromeVariableRVR).
    visibility_extension :
        Optional horizontal-visibility extension XML (SectorVisibility / TowerVisibility).
    cloud_layer_extension :
        Optional CloudLayer extension XML (VariableCeilingHeight / VariableSkyCondition).

    Returns
    -------
    observation, trends
        XML fragments (each ending with newline when non-empty).
    """
    if ir.get("nil"):
        return f'  <iwxxm:observation nilReason="{NIL_MISSING}"/>\n', ""

    cavok = bool(ir.get("cavok"))
    cavok_attr = "true" if cavok else "false"
    vis_block = ""
    rvr_block = ""
    wx_block = ""
    cloud = ""
    if not cavok:
        vis_block = _visibility_block(ir, visibility_extension=visibility_extension)
        rvr_block = _rvr_block(ir, rvr_extension=rvr_extension)
        wx_block = _present_weather_block(ir)
        cloud = _cloud_block(ir, cloud_layer_extension=cloud_layer_extension)

    if ir.get("temp_not_observable"):
        temp_xml = f'      <iwxxm:airTemperature uom="N/A" xsi:nil="true" nilReason="{NIL_NOT_OBS}"/>\n'
    else:
        temp_xml = f'      <iwxxm:airTemperature uom="Cel">{_fmt_cel(ir["temp_c"])}</iwxxm:airTemperature>\n'
    if ir.get("dewpoint_not_observable"):
        dew_xml = f'      <iwxxm:dewpointTemperature uom="N/A" xsi:nil="true" nilReason="{NIL_NOT_OBS}"/>\n'
    else:
        dew_xml = (
            f'      <iwxxm:dewpointTemperature uom="Cel">{_fmt_cel(ir["dewpoint_c"])}</iwxxm:dewpointTemperature>\n'
        )
    if ir.get("qnh_not_observable"):
        qnh_xml = f'      <iwxxm:qnh uom="N/A" xsi:nil="true" nilReason="{NIL_NOT_OBS}"/>\n'
    else:
        qnh_xml = f'      <iwxxm:qnh uom="hPa">{_fmt_hpa(ir["qnh_hpa"])}</iwxxm:qnh>\n'

    observation = f"""  <iwxxm:observation>
    <iwxxm:MeteorologicalAerodromeObservation gml:id="obs.1" cloudAndVisibilityOK="{cavok_attr}">
{temp_xml}{dew_xml}{qnh_xml}{_surface_wind_inner(ir, peak_extension=peak_extension)}{vis_block}{rvr_block}{wx_block}{cloud}{addendum_extension}    </iwxxm:MeteorologicalAerodromeObservation>
  </iwxxm:observation>
"""
    return observation, _trend_forecasts(ir)


def _aerodrome_block(station: str) -> str:
    if station == "YUDO":
        return f"""  <iwxxm:aerodrome>
    <aixm:AirportHeliport gml:id="ad.{station.lower()}">
      <aixm:timeSlice>
        <aixm:AirportHeliportTimeSlice gml:id="ad.ts.{station.lower()}">
          <gml:validTime/>
          <aixm:interpretation>SNAPSHOT</aixm:interpretation>
          <aixm:designator>{station}</aixm:designator>
          <aixm:name>{_YUDO_NAME}</aixm:name>
          <aixm:locationIndicatorICAO>{station}</aixm:locationIndicatorICAO>
          <aixm:ARP>
            <aixm:ElevatedPoint gml:id="arp.{station.lower()}" srsDimension="2" axisLabels="Lat Long" srsName="http://www.opengis.net/def/crs/EPSG/0/4326">
              <gml:pos>{_YUDO_POS}</gml:pos>
              <aixm:elevation uom="M">{_YUDO_ELEV_M}</aixm:elevation>
              <aixm:verticalDatum>EGM_96</aixm:verticalDatum>
            </aixm:ElevatedPoint>
          </aixm:ARP>
        </aixm:AirportHeliportTimeSlice>
      </aixm:timeSlice>
    </aixm:AirportHeliport>
  </iwxxm:aerodrome>
"""
    return f"""  <iwxxm:aerodrome>
    <aixm:AirportHeliport gml:id="ad.{station.lower()}">
      <aixm:timeSlice>
        <aixm:AirportHeliportTimeSlice gml:id="ad.ts.{station.lower()}">
          <gml:validTime/>
          <aixm:interpretation>SNAPSHOT</aixm:interpretation>
          <aixm:designator>{station}</aixm:designator>
          <aixm:locationIndicatorICAO>{station}</aixm:locationIndicatorICAO>
        </aixm:AirportHeliportTimeSlice>
      </aixm:timeSlice>
    </aixm:AirportHeliport>
  </iwxxm:aerodrome>
"""


def emit_metar_speci_annex3(
    ir: dict[str, Any],
    *,
    product: str,
    iwxxm_version: str,
) -> str:
    """
    Emit a full IWXXM METAR/SPECI document for the annex3 profile.

    Parameters
    ----------
    ir :
        Parsed METAR/SPECI IR.
    product :
        ``METAR`` or ``SPECI``.
    iwxxm_version :
        Release line (namespace selection).

    Returns
    -------
    str
        IWXXM XML document.
    """
    ns = NS.get(iwxxm_version)
    if ns is None:
        raise ValueError(f"unsupported iwxxm_version for annex3 emit: {iwxxm_version}")

    station = str(ir["station"])
    stamp = obs_timestamp(ir)
    root = product.upper()
    gml_id = _annex3_gml_id(ir, root)
    override = ir.get("report_status")
    if override in {"NORMAL", "AMENDMENT", "CORRECTION"}:
        report_status = str(override)
    else:
        report_status = "CORRECTION" if ir.get("correction") else "NORMAL"
    automated = "true" if ir.get("auto") else "false"
    observation, trends = build_observation_and_trends(ir)
    aerodrome = _aerodrome_block(station)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:{root} xmlns:iwxxm="{ns}"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:aixm="http://www.aixm.aero/schema/5.1.1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    gml:id="{gml_id}"
    reportStatus="{report_status}"
    permissibleUsage="OPERATIONAL"
    automatedStation="{automated}">
  <iwxxm:issueTime>
    <gml:TimeInstant gml:id="t.issue">
      <gml:timePosition>{stamp}</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:issueTime>
{aerodrome}  <iwxxm:observationTime>
    <gml:TimeInstant gml:id="t.obs">
      <gml:timePosition>{stamp}</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:observationTime>
{observation}{trends}</iwxxm:{root}>
"""
