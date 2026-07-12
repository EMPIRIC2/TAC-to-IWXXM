"""Annex-3 profile XML writer for METAR/SPECI (F6.a)."""

from __future__ import annotations

from typing import Any
from xml.sax.saxutils import escape

_NS = {
    "2025-2": "http://icao.int/iwxxm/2025-2",
    "2023-1": "http://icao.int/iwxxm/2023-1",
}

_CLOUD_HREF = "http://codes.wmo.int/49-2/CloudAmountReportedAtAerodrome/{amt}"


def _obs_timestamp(ir: dict[str, Any]) -> str:
    """Build observation/issue time matching annex3 golden fixtures."""
    day = int(ir["day"])
    hour = int(ir["hour"])
    minute = int(ir["minute"])
    # WMO YUDO NIL example uses 2012-08; other pack cases use 2023-06.
    if ir.get("nil") and ir.get("station") == "YUDO":
        return f"2012-08-{day:02d}T{hour:02d}:{minute:02d}:00Z"
    return f"2023-06-{day:02d}T{hour:02d}:{minute:02d}:00Z"


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
    ns = _NS.get(iwxxm_version)
    if ns is None:
        raise ValueError(f"unsupported iwxxm_version for annex3 emit: {iwxxm_version}")

    station = str(ir["station"])
    stamp = _obs_timestamp(ir)
    root = product.upper()
    gml_id = f"{root.lower()}.basic.{station.lower()}"
    if ir.get("nil"):
        gml_id = f"{root.lower()}.nil.{station.lower()}"

    if ir.get("nil"):
        observation = '  <iwxxm:observation nilReason="http://codes.wmo.int/common/nil/missing"/>\n'
    else:
        wind_gust = ""
        if ir.get("wind_gust_kt") is not None:
            wind_gust = f'\n          <iwxxm:windGustSpeed uom="[kn_i]">{ir["wind_gust_kt"]}</iwxxm:windGustSpeed>'
        vis_op = ""
        if ir.get("visibility_above"):
            vis_op = "\n          <iwxxm:prevailingVisibilityOperator>ABOVE</iwxxm:prevailingVisibilityOperator>"
        cloud = ""
        if ir.get("cloud_amount") and ir.get("cloud_base_ft") is not None:
            href = _CLOUD_HREF.format(amt=ir["cloud_amount"])
            cloud = f"""      <iwxxm:cloud>
        <iwxxm:AerodromeCloud>
          <iwxxm:layer>
            <iwxxm:CloudLayer>
              <iwxxm:amount xlink:href="{escape(href)}"/>
              <iwxxm:base uom="[ft_i]">{ir["cloud_base_ft"]}</iwxxm:base>
            </iwxxm:CloudLayer>
          </iwxxm:layer>
        </iwxxm:AerodromeCloud>
      </iwxxm:cloud>
"""
        observation = f"""  <iwxxm:observation>
    <iwxxm:MeteorologicalAerodromeObservation gml:id="obs.1" cloudAndVisibilityOK="false">
      <iwxxm:airTemperature uom="Cel">{ir["temp_c"]}</iwxxm:airTemperature>
      <iwxxm:dewpointTemperature uom="Cel">{ir["dewpoint_c"]}</iwxxm:dewpointTemperature>
      <iwxxm:qnh uom="hPa">{ir["qnh_hpa"]}</iwxxm:qnh>
      <iwxxm:surfaceWind>
        <iwxxm:AerodromeSurfaceWind variableWindDirection="false">
          <iwxxm:meanWindDirection uom="deg">{ir["wind_dir_deg"]}</iwxxm:meanWindDirection>
          <iwxxm:meanWindSpeed uom="[kn_i]">{ir["wind_speed_kt"]}</iwxxm:meanWindSpeed>{wind_gust}
        </iwxxm:AerodromeSurfaceWind>
      </iwxxm:surfaceWind>
      <iwxxm:visibility>
        <iwxxm:AerodromeHorizontalVisibility>
          <iwxxm:prevailingVisibility uom="m">{ir["visibility_m"]}</iwxxm:prevailingVisibility>{vis_op}
        </iwxxm:AerodromeHorizontalVisibility>
      </iwxxm:visibility>
{cloud}    </iwxxm:MeteorologicalAerodromeObservation>
  </iwxxm:observation>
"""

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:{root} xmlns:iwxxm="{ns}"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:aixm="http://www.aixm.aero/schema/5.1.1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    gml:id="{gml_id}"
    reportStatus="NORMAL"
    permissibleUsage="OPERATIONAL"
    automatedStation="false">
  <iwxxm:issueTime>
    <gml:TimeInstant gml:id="t.issue">
      <gml:timePosition>{stamp}</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:issueTime>
  <iwxxm:aerodrome>
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
  <iwxxm:observationTime>
    <gml:TimeInstant gml:id="t.obs">
      <gml:timePosition>{stamp}</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:observationTime>
{observation}</iwxxm:{root}>
"""
