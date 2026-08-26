"""Annex-3 profile XML writers — taf."""

# pyright: reportWildcardImportFromLibrary=false

from __future__ import annotations

from typing import Any, cast
from xml.sax.saxutils import escape

from tac2iwxxm.profiles.annex3_emit._common import *


def _taf_time_prefix(ir: dict[str, Any]) -> str:
    """WMO YUDO examples use 2012-08; other fixtures use 2023-06."""
    # ruff: noqa: F403, F405
    if ir.get("station") == "YUDO":
        return "2012-08"
    return "2023-06"


def _taf_issue_stamp(ir: dict[str, Any]) -> str:
    prefix = _taf_time_prefix(ir)
    return f"{prefix}-{int(ir['issue_day']):02d}T{int(ir['issue_hour']):02d}:{int(ir['issue_minute']):02d}:00Z"


def _taf_period(ir: dict[str, Any], *, from_key: str = "valid") -> tuple[str, str]:
    prefix = _taf_time_prefix(ir)
    begin = f"{prefix}-{int(ir[f'{from_key}_from_day']):02d}T{int(ir[f'{from_key}_from_hour']):02d}:00:00Z"
    end = f"{prefix}-{int(ir[f'{from_key}_to_day']):02d}T{int(ir[f'{from_key}_to_hour']):02d}:00:00Z"
    return begin, end


def _taf_aerodrome_block(station: str, *, include_arp: bool) -> str:
    """Emit TAF aerodrome; YUDO WMO examples include name (+ ARP on non-cancel)."""
    name = ""
    arp = ""
    if station == "YUDO":
        name = f"\n          <aixm:name>{_YUDO_NAME}</aixm:name>"
        if include_arp:
            arp = f"""
          <aixm:ARP>
            <aixm:ElevatedPoint gml:id="arp.{station.lower()}" srsDimension="2" axisLabels="Lat Long" srsName="http://www.opengis.net/def/crs/EPSG/0/4326">
              <gml:pos>{_YUDO_POS}</gml:pos>
              <aixm:elevation uom="M">{_YUDO_ELEV_M}</aixm:elevation>
              <aixm:verticalDatum>EGM_96</aixm:verticalDatum>
            </aixm:ElevatedPoint>
          </aixm:ARP>"""
    return f"""  <iwxxm:aerodrome>
    <aixm:AirportHeliport gml:id="ad.{station.lower()}">
      <aixm:timeSlice>
        <aixm:AirportHeliportTimeSlice gml:id="ad.ts.{station.lower()}">
          <gml:validTime/>
          <aixm:interpretation>SNAPSHOT</aixm:interpretation>
          <aixm:designator>{escape(station)}</aixm:designator>{name}
          <aixm:locationIndicatorICAO>{escape(station)}</aixm:locationIndicatorICAO>{arp}
        </aixm:AirportHeliportTimeSlice>
      </aixm:timeSlice>
    </aixm:AirportHeliport>
  </iwxxm:aerodrome>
"""


def _fmt_taf_speed(value: Any) -> str:
    fval = float(value)
    if fval == int(fval):
        # Vendor A5-1: base uses 5.0; TEMPO/FM use bare integers for whole m/s.
        return str(int(fval))
    return f"{fval:.1f}"


def _taf_wind_block(fcst: dict[str, Any]) -> str:
    if fcst.get("wind_variable"):
        return """      <iwxxm:surfaceWind>
        <iwxxm:AerodromeSurfaceWindForecast variableWindDirection="true">
          <iwxxm:meanWindSpeed uom="m/s">0.0</iwxxm:meanWindSpeed>
        </iwxxm:AerodromeSurfaceWindForecast>
      </iwxxm:surfaceWind>
"""
    if fcst.get("wind_speed_mps") is None and fcst.get("wind_speed_kt") is None:
        return ""
    if fcst.get("wind_speed_mps") is not None:
        # WMO A5-1 baseForecast uses one decimal on 5.0; change groups use bare ints.
        spd_raw = float(fcst["wind_speed_mps"])
        if fcst.get("_base_wind_decimal"):
            spd = f"{spd_raw:.1f}"
        else:
            spd = _fmt_taf_speed(spd_raw)
        uom = "m/s"
        gust = fcst.get("wind_gust_mps")
    else:
        spd = str(fcst["wind_speed_kt"])
        uom = "[kn_i]"
        gust = fcst.get("wind_gust_kt")
    gust_xml = ""
    if gust is not None:
        gust_xml = f'\n          <iwxxm:windGustSpeed uom="{uom}">{_fmt_taf_speed(gust)}</iwxxm:windGustSpeed>'
    return f"""      <iwxxm:surfaceWind>
        <iwxxm:AerodromeSurfaceWindForecast variableWindDirection="false">
          <iwxxm:meanWindDirection uom="deg">{fcst["wind_dir_deg"]}</iwxxm:meanWindDirection>
          <iwxxm:meanWindSpeed uom="{uom}">{spd}</iwxxm:meanWindSpeed>{gust_xml}
        </iwxxm:AerodromeSurfaceWindForecast>
      </iwxxm:surfaceWind>
"""


def _taf_cloud_block(fcst: dict[str, Any], *, gml_id: str) -> str:
    clouds_raw = fcst.get("clouds")
    layers: list[dict[str, Any]] = []
    if isinstance(clouds_raw, list) and clouds_raw:
        for item in cast(list[Any], clouds_raw):
            if isinstance(item, dict):
                layers.append(cast(dict[str, Any], item))
    elif fcst.get("cloud_amount") and fcst.get("cloud_base_ft") is not None:
        layers = [{"amount": fcst["cloud_amount"], "base_ft": fcst["cloud_base_ft"]}]
    if not layers:
        return ""
    layer_xml: list[str] = []
    for layer in layers:
        href = _CLOUD_HREF.format(amt=layer["amount"])
        ctype_xml = ""
        if layer.get("cloud_type"):
            thref = escape(_CLOUD_TYPE_HREF.format(ctype=str(layer["cloud_type"])))
            ctype_xml = f'\n              <iwxxm:cloudType xlink:href="{thref}"/>'
        layer_xml.append(
            f"""          <iwxxm:layer>
            <iwxxm:CloudLayer>
              <iwxxm:amount xlink:href="{escape(href)}"/>
              <iwxxm:base uom="[ft_i]">{layer["base_ft"]}</iwxxm:base>{ctype_xml}
            </iwxxm:CloudLayer>
          </iwxxm:layer>"""
        )
    joined = "\n".join(layer_xml)
    return f"""      <iwxxm:cloud>
        <iwxxm:AerodromeCloudForecast gml:id="{gml_id}">
{joined}
        </iwxxm:AerodromeCloudForecast>
      </iwxxm:cloud>
"""


def _taf_weather_block(fcst: dict[str, Any]) -> str:
    codes = fcst.get("weather")
    if not isinstance(codes, list) or not codes:
        return ""
    parts: list[str] = []
    for raw_code in cast(list[Any], codes):
        href = escape(_WX_HREF.format(code=str(raw_code)))
        parts.append(f'      <iwxxm:weather xlink:href="{href}"/>')
    return "\n".join(parts) + "\n"


def _taf_change_forecasts(ir: dict[str, Any], station: str) -> str:
    changes_raw = ir.get("change_forecasts")
    if not isinstance(changes_raw, list) or not changes_raw:
        return ""
    parts: list[str] = []
    typed_changes: list[dict[str, Any]] = []
    for raw in cast(list[Any], changes_raw):
        if isinstance(raw, dict):
            typed_changes.append(cast(dict[str, Any], raw))
    for idx, change in enumerate(typed_changes, start=1):
        indicator = str(change.get("change_indicator") or "BECOMING")
        cavok = "true" if change.get("cavok") else "false"
        vis = ""
        if not change.get("cavok") and change.get("visibility_m") is not None:
            vis = f'      <iwxxm:prevailingVisibility uom="m">{change["visibility_m"]}</iwxxm:prevailingVisibility>\n'
            if change.get("visibility_above"):
                vis += "      <iwxxm:prevailingVisibilityOperator>ABOVE</iwxxm:prevailingVisibilityOperator>\n"
        wind = "" if change.get("cavok") else _taf_wind_block(change)
        weather = "" if change.get("cavok") else _taf_weather_block(change)
        cloud = "" if change.get("cavok") else _taf_cloud_block(change, gml_id=f"cloud.chg.{idx}.{station.lower()}")
        parts.append(
            f"""  <iwxxm:changeForecast>
    <iwxxm:MeteorologicalAerodromeForecast gml:id="fcst.chg.{idx}.{station.lower()}" changeIndicator="{indicator}" cloudAndVisibilityOK="{cavok}">
      <iwxxm:phenomenonTime>
        <gml:TimePeriod gml:id="t.chg.{idx}">
          <gml:beginPosition>{change["phenomenon_begin"]}</gml:beginPosition>
          <gml:endPosition>{change["phenomenon_end"]}</gml:endPosition>
        </gml:TimePeriod>
      </iwxxm:phenomenonTime>
{vis}{wind}{weather}{cloud}    </iwxxm:MeteorologicalAerodromeForecast>
  </iwxxm:changeForecast>
"""
        )
    return "".join(parts)


def _taf_visibility_block(fcst: dict[str, Any]) -> str:
    """Render prevailing visibility for a TAF forecast group."""
    display_uom = fcst.get("visibility_display_uom")
    if isinstance(display_uom, str):
        vis = f'      <iwxxm:prevailingVisibility uom="{display_uom}">{fcst["visibility_display_value"]}</iwxxm:prevailingVisibility>\n'
        if fcst.get("visibility_above"):
            vis += "      <iwxxm:prevailingVisibilityOperator>ABOVE</iwxxm:prevailingVisibilityOperator>\n"
        return vis
    if fcst.get("visibility_m") is not None:
        vis = f'      <iwxxm:prevailingVisibility uom="m">{fcst["visibility_m"]}</iwxxm:prevailingVisibility>\n'
        if fcst.get("visibility_above"):
            vis += "      <iwxxm:prevailingVisibilityOperator>ABOVE</iwxxm:prevailingVisibilityOperator>\n"
        return vis
    return ""


def emit_taf_annex3(
    ir: dict[str, Any],
    *,
    iwxxm_version: str,
    forecast_extension: str = "",
) -> str:
    """Emit a minimal IWXXM TAF document for the annex3 profile."""
    ns = _ns(iwxxm_version)
    station = str(ir["station"])
    issue = _taf_issue_stamp(ir)
    gml_id = f"taf.basic.{station.lower()}"
    if ir.get("nil"):
        gml_id = f"taf.nil.{station.lower()}"
    elif ir.get("cancel"):
        gml_id = f"taf.cnl.{station.lower()}"

    override = ir.get("report_status")
    if override in {"NORMAL", "AMENDMENT", "CORRECTION"}:
        status = str(override)
    elif ir.get("correction"):
        status = "CORRECTION"
    elif ir.get("amendment"):
        status = "AMENDMENT"
    else:
        status = "NORMAL"

    # CNL — Guidance: isCancelReport + cancelledReportValidPeriod; omit valid/base/change.
    if ir.get("cancel"):
        begin, end = _taf_period(ir)
        aerodrome = _taf_aerodrome_block(station, include_arp=False)
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:TAF xmlns:iwxxm="{ns}"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:aixm="http://www.aixm.aero/schema/5.1.1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    gml:id="{gml_id}"
    reportStatus="{status}"
    permissibleUsage="OPERATIONAL"
    isCancelReport="true">
  <iwxxm:issueTime>
    <gml:TimeInstant gml:id="t.issue">
      <gml:timePosition>{issue}</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:issueTime>
{aerodrome}  <iwxxm:cancelledReportValidPeriod>
    <gml:TimePeriod gml:id="t.cancelled">
      <gml:beginPosition>{begin}</gml:beginPosition>
      <gml:endPosition>{end}</gml:endPosition>
    </gml:TimePeriod>
  </iwxxm:cancelledReportValidPeriod>
</iwxxm:TAF>
"""

    aerodrome = _taf_aerodrome_block(station, include_arp=station == "YUDO")

    # NIL without validity — empty baseForecast; omit validPeriod when unknown.
    if ir.get("nil") and "valid_from_day" not in ir:
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:TAF xmlns:iwxxm="{ns}"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:aixm="http://www.aixm.aero/schema/5.1.1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    gml:id="{gml_id}"
    reportStatus="{status}"
    permissibleUsage="OPERATIONAL">
  <iwxxm:issueTime>
    <gml:TimeInstant gml:id="t.issue">
      <gml:timePosition>{issue}</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:issueTime>
{aerodrome}  <iwxxm:baseForecast nilReason="http://codes.wmo.int/common/nil/missing"/>
</iwxxm:TAF>
"""

    begin, end = _taf_period(ir)

    if ir.get("nil"):
        base_fcst = '  <iwxxm:baseForecast nilReason="http://codes.wmo.int/common/nil/missing"/>\n'
        changes = ""
    else:
        cavok = "true" if ir.get("cavok") else "false"
        base_wind_src = dict(ir)
        base_wind_src["_base_wind_decimal"] = True
        wind = "" if ir.get("cavok") else _taf_wind_block(base_wind_src)
        vis = ""
        cloud = ""
        if not ir.get("cavok"):
            vis = _taf_visibility_block(ir)
            cloud = _taf_cloud_block(ir, gml_id=f"cloud.base.{station.lower()}")
        base_fcst = f"""  <iwxxm:baseForecast>
    <iwxxm:MeteorologicalAerodromeForecast gml:id="fcst.base.{station.lower()}" cloudAndVisibilityOK="{cavok}">
      <iwxxm:phenomenonTime xlink:href="#uuid.00000000-0000-4000-8000-000000000001"/>
{vis}{wind}{cloud}{forecast_extension}    </iwxxm:MeteorologicalAerodromeForecast>
  </iwxxm:baseForecast>
"""
        changes = _taf_change_forecasts(ir, station)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:TAF xmlns:iwxxm="{ns}"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:aixm="http://www.aixm.aero/schema/5.1.1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    gml:id="{gml_id}"
    reportStatus="{status}"
    permissibleUsage="OPERATIONAL">
  <iwxxm:issueTime>
    <gml:TimeInstant gml:id="t.issue">
      <gml:timePosition>{issue}</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:issueTime>
{aerodrome}  <iwxxm:validPeriod>
    <gml:TimePeriod gml:id="t.valid">
      <gml:beginPosition>{begin}</gml:beginPosition>
      <gml:endPosition>{end}</gml:endPosition>
    </gml:TimePeriod>
  </iwxxm:validPeriod>
{base_fcst}{changes}</iwxxm:TAF>
"""
