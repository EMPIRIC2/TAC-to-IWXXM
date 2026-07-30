"""Annex-3 profile XML writers for TAF / SIGMET / AIRMET (F6.c–d)."""

from __future__ import annotations

import re
from typing import Any, cast
from xml.sax.saxutils import escape

_NS = {
    "2025-2": "http://icao.int/iwxxm/2025-2",
    "2023-1": "http://icao.int/iwxxm/2023-1",
}

_CLOUD_HREF = "http://codes.wmo.int/49-2/CloudAmountReportedAtAerodrome/{amt}"
_CLOUD_TYPE_HREF = "http://codes.wmo.int/49-2/SigConvectiveCloudType/{ctype}"
_WX_HREF = "http://codes.wmo.int/306/4678/{code}"
_SIG_PHENOM_HREF = "http://codes.wmo.int/49-2/SigWxPhenomena/{code}"
_AIR_PHENOM_HREF = "http://codes.wmo.int/49-2/AirWxPhenomena/{code}"

_YUDO_NAME = "DONLON/INTERNATIONAL"
_YUDO_POS = "12.34 -12.34"
_YUDO_ELEV_M = "12"


def _ns(iwxxm_version: str) -> str:
    ns = _NS.get(iwxxm_version)
    if ns is None:
        raise ValueError(f"unsupported iwxxm_version for annex3 emit: {iwxxm_version}")
    return ns


def _taf_issue_stamp(ir: dict[str, Any]) -> str:
    # WMO YUDO A5-1 examples use 2012-08.
    return f"2012-08-{int(ir['issue_day']):02d}T{int(ir['issue_hour']):02d}:{int(ir['issue_minute']):02d}:00Z"


def _taf_period(ir: dict[str, Any], *, from_key: str = "valid") -> tuple[str, str]:
    begin = f"2012-08-{int(ir[f'{from_key}_from_day']):02d}T{int(ir[f'{from_key}_from_hour']):02d}:00:00Z"
    end = f"2012-08-{int(ir[f'{from_key}_to_day']):02d}T{int(ir[f'{from_key}_to_hour']):02d}:00:00Z"
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


def emit_taf_annex3(ir: dict[str, Any], *, iwxxm_version: str) -> str:
    """Emit a minimal IWXXM TAF document for the annex3 profile."""
    ns = _ns(iwxxm_version)
    station = str(ir["station"])
    issue = _taf_issue_stamp(ir)
    gml_id = f"taf.basic.{station.lower()}"
    if ir.get("nil"):
        gml_id = f"taf.nil.{station.lower()}"
    elif ir.get("cancel"):
        gml_id = f"taf.cnl.{station.lower()}"

    if ir.get("correction"):
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
            if ir.get("visibility_m") is not None:
                vis = f'      <iwxxm:prevailingVisibility uom="m">{ir["visibility_m"]}</iwxxm:prevailingVisibility>\n'
                if ir.get("visibility_above"):
                    vis += "      <iwxxm:prevailingVisibilityOperator>ABOVE</iwxxm:prevailingVisibilityOperator>\n"
            cloud = _taf_cloud_block(ir, gml_id=f"cloud.base.{station.lower()}")
        base_fcst = f"""  <iwxxm:baseForecast>
    <iwxxm:MeteorologicalAerodromeForecast gml:id="fcst.base.{station.lower()}" cloudAndVisibilityOK="{cavok}">
      <iwxxm:phenomenonTime xlink:href="#uuid.00000000-0000-4000-8000-000000000001"/>
{vis}{wind}{cloud}    </iwxxm:MeteorologicalAerodromeForecast>
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


def _hazard_stamp(ir: dict[str, Any], prefix: str) -> tuple[str, str, str]:
    """Return issue, begin, end timestamps (year-month fixed to WMO examples)."""
    year_month = "2012-08" if ir["product"] == "SIGMET" else "2014-05"
    issue = (
        f"{year_month}-{int(ir['valid_from_day']):02d}T"
        f"{int(ir['valid_from_hour']):02d}:{int(ir['valid_from_minute']):02d}:00Z"
    )
    begin = issue
    end = (
        f"{year_month}-{int(ir['valid_to_day']):02d}T"
        f"{int(ir['valid_to_hour']):02d}:{int(ir['valid_to_minute']):02d}:00Z"
    )
    return issue, begin, end


def _sigmet_root_local(ir: dict[str, Any]) -> str:
    """
    Content-select IWXXM SIGMET family root under HTTP ``product=sigmet`` (E19-13 / F23 V2).

    VA phenomenon TAC → ``VolcanicAshSIGMET``; general non-VA/TC → ``SIGMET``.
    """
    if ir.get("phenomenon") == "VA" or ir.get("iwxxm_root") == "VolcanicAshSIGMET":
        return "VolcanicAshSIGMET"
    return "SIGMET"


def _sigmet_header_units(ir: dict[str, Any], *, ns: str, gml_id: str, issue: str) -> str:
    fir = str(ir["fir"])
    mwo = str(ir["mwo"])
    root = _sigmet_root_local(ir)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:{root} xmlns:iwxxm="{ns}"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:aixm="http://www.aixm.aero/schema/5.1.1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    gml:id="{gml_id}"
    reportStatus="NORMAL"
    permissibleUsage="OPERATIONAL"{{cancel_attr}}>
  <iwxxm:issueTime>
    <gml:TimeInstant gml:id="t.issue">
      <gml:timePosition>{issue}</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:issueTime>
  <iwxxm:issuingAirTrafficServicesUnit>
    <aixm:Unit gml:id="unit.atsu.{fir.lower()}">
      <aixm:timeSlice>
        <aixm:UnitTimeSlice gml:id="unit.atsu.ts.{fir.lower()}">
          <gml:validTime/>
          <aixm:interpretation>SNAPSHOT</aixm:interpretation>
          <aixm:name>{escape(fir)} FIC</aixm:name>
          <aixm:type>FIC</aixm:type>
          <aixm:designator>{escape(fir)}</aixm:designator>
        </aixm:UnitTimeSlice>
      </aixm:timeSlice>
    </aixm:Unit>
  </iwxxm:issuingAirTrafficServicesUnit>
  <iwxxm:originatingMeteorologicalWatchOffice>
    <aixm:Unit gml:id="unit.mwo.{mwo.lower()}">
      <aixm:timeSlice>
        <aixm:UnitTimeSlice gml:id="unit.mwo.ts.{mwo.lower()}">
          <gml:validTime/>
          <aixm:interpretation>SNAPSHOT</aixm:interpretation>
          <aixm:name>{escape(mwo)} MWO</aixm:name>
          <aixm:type>MWO</aixm:type>
          <aixm:designator>{escape(mwo)}</aixm:designator>
        </aixm:UnitTimeSlice>
      </aixm:timeSlice>
    </aixm:Unit>
  </iwxxm:originatingMeteorologicalWatchOffice>
  <iwxxm:issuingAirTrafficServicesRegion>
    <aixm:Airspace gml:id="as.{fir.lower()}">
      <aixm:timeSlice>
        <aixm:AirspaceTimeSlice gml:id="as.ts.{fir.lower()}">
          <gml:validTime/>
          <aixm:interpretation>SNAPSHOT</aixm:interpretation>
          <aixm:type>OTHER:FIR_UIR</aixm:type>
          <aixm:designator>{escape(fir)}</aixm:designator>
          <aixm:name>{escape(str(ir.get("fir_name", fir)))}</aixm:name>
        </aixm:AirspaceTimeSlice>
      </aixm:timeSlice>
    </aixm:Airspace>
  </iwxxm:issuingAirTrafficServicesRegion>
  <iwxxm:sequenceNumber>{int(ir["sequence"])}</iwxxm:sequenceNumber>
"""


def _sigmet_geometry_xml(ir: dict[str, Any], *, fir: str) -> str:
    """Build evolving-condition geometry from IR (G1 exceptional rules / #733/#739)."""
    if ir.get("no_va_exp"):
        return """
              <iwxxm:geometry nilReason="http://codes.wmo.int/common/nil/nothingOfOperationalSignificance"/>"""

    geom = ir.get("geometry")
    top_fl = ir.get("top_fl")
    lower_fl = ir.get("lower_fl")
    upper_fl = ir.get("upper_fl", top_fl)
    if top_fl is not None and upper_fl is None:
        upper_fl = top_fl

    limits = ""
    if ir.get("lower_surface") in {"SFC", "GND"} and upper_fl is not None:
        limits = f"""
              <aixm:lowerLimit>GND</aixm:lowerLimit>
              <aixm:lowerLimitReference>SFC</aixm:lowerLimitReference>
              <aixm:upperLimit uom="FL">{int(upper_fl)}</aixm:upperLimit>
              <aixm:upperLimitReference>STD</aixm:upperLimitReference>"""
    elif lower_fl is not None and upper_fl is not None:
        limits = f"""
              <aixm:lowerLimit uom="FL">{int(lower_fl)}</aixm:lowerLimit>
              <aixm:lowerLimitReference>STD</aixm:lowerLimitReference>
              <aixm:upperLimit uom="FL">{int(upper_fl)}</aixm:upperLimit>
              <aixm:upperLimitReference>STD</aixm:upperLimitReference>"""
    elif upper_fl is not None:
        limits = f"""
              <aixm:upperLimit uom="FL">{int(upper_fl)}</aixm:upperLimit>
              <aixm:upperLimitReference>STD</aixm:upperLimitReference>"""
        if ir.get("top_qualifier") == "ABV":
            # WMO Guidance / airmet-A6-1a-TS: TOP ABV → maximumLimit nil unknown.
            limits += """
              <aixm:maximumLimit xsi:nil="true" nilReason="unknown"/>"""
        elif ir.get("top_qualifier") == "BLW":
            limits += """
              <aixm:minimumLimit xsi:nil="true" nilReason="unknown"/>"""

    if isinstance(geom, dict):
        g = cast(dict[str, Any], geom)
        if g.get("kind") == "point":
            lat = float(g["lat"])
            lon = float(g["lon"])
            return f"""
              <iwxxm:geometry>
                <aixm:AirspaceVolume gml:id="vol.{fir.lower()}">{limits}
                  <aixm:horizontalProjection>
                    <aixm:Surface gml:id="sfc.{fir.lower()}" srsDimension="2" axisLabels="Lat Long" srsName="http://www.opengis.net/def/crs/EPSG/0/4326">
                      <gml:patches>
                        <gml:PolygonPatch>
                          <gml:exterior>
                            <gml:Ring>
                              <gml:curveMember>
                                <gml:Curve gml:id="curve.{fir.lower()}">
                                  <gml:segments>
                                    <gml:CircleByCenterPoint numArc="1">
                                      <gml:pos>{lat:.4f} {lon:.4f}</gml:pos>
                                      <gml:radius uom="[nmi_i]">0</gml:radius>
                                    </gml:CircleByCenterPoint>
                                  </gml:segments>
                                </gml:Curve>
                              </gml:curveMember>
                            </gml:Ring>
                          </gml:exterior>
                        </gml:PolygonPatch>
                      </gml:patches>
                    </aixm:Surface>
                  </aixm:horizontalProjection>
                </aixm:AirspaceVolume>
              </iwxxm:geometry>"""

        if g.get("kind") == "polygon":
            pos_list = str(g["pos_list"])
            return f"""
              <iwxxm:geometry>
                <aixm:AirspaceVolume gml:id="vol.{fir.lower()}">{limits}
                  <aixm:horizontalProjection>
                    <aixm:Surface gml:id="sfc.{fir.lower()}" srsDimension="2" axisLabels="Lat Long" srsName="http://www.opengis.net/def/crs/EPSG/0/4326">
                      <gml:patches>
                        <gml:PolygonPatch>
                          <gml:exterior>
                            <gml:LinearRing>
                              <gml:posList>{escape(pos_list)}</gml:posList>
                            </gml:LinearRing>
                          </gml:exterior>
                        </gml:PolygonPatch>
                      </gml:patches>
                    </aixm:Surface>
                  </aixm:horizontalProjection>
                </aixm:AirspaceVolume>
              </iwxxm:geometry>"""

    if limits:
        return f"""
              <iwxxm:geometry>
                <aixm:AirspaceVolume gml:id="vol.{fir.lower()}">{limits}
                </aixm:AirspaceVolume>
              </iwxxm:geometry>"""

    return """
              <iwxxm:geometry nilReason="http://codes.wmo.int/common/nil/missing"/>"""


def _sigmet_motion_xml(ir: dict[str, Any]) -> str:
    if ir.get("stationary"):
        return """
              <iwxxm:directionOfMotion uom="deg" xsi:nil="true" nilReason="http://codes.wmo.int/common/nil/inapplicable"/>
              <iwxxm:speedOfMotion uom="[kn_i]">0</iwxxm:speedOfMotion>"""
    if "motion_dir_deg" in ir and "motion_speed_kt" in ir:
        return f"""
              <iwxxm:directionOfMotion uom="deg">{int(ir["motion_dir_deg"])}</iwxxm:directionOfMotion>
              <iwxxm:speedOfMotion uom="[kn_i]">{int(ir["motion_speed_kt"])}</iwxxm:speedOfMotion>"""
    return ""


def emit_sigmet_annex3(ir: dict[str, Any], *, iwxxm_version: str) -> str:
    """Emit an IWXXM SIGMET / VolcanicAshSIGMET document (F6.d / F23 G1–G3 / V2)."""
    ns = _ns(iwxxm_version)
    fir = str(ir["fir"])
    issue, begin, end = _hazard_stamp(ir, "sigmet")
    cancel = bool(ir.get("cancel"))
    root = _sigmet_root_local(ir)
    if cancel:
        gml_id = f"sigmet.cnl.{fir.lower()}"
    elif root == "VolcanicAshSIGMET":
        gml_id = f"sigmet.va.{fir.lower()}"
    else:
        gml_id = f"sigmet.basic.{fir.lower()}"

    if cancel:
        c_begin = (
            f"2012-08-{int(ir['cancelled_from_day']):02d}T"
            f"{int(ir['cancelled_from_hour']):02d}:{int(ir['cancelled_from_minute']):02d}:00Z"
        )
        c_end = (
            f"2012-08-{int(ir['cancelled_to_day']):02d}T"
            f"{int(ir['cancelled_to_hour']):02d}:{int(ir['cancelled_to_minute']):02d}:00Z"
        )
        head = _sigmet_header_units(ir, ns=ns, gml_id=gml_id, issue=issue).format(
            cancel_attr='\n    isCancelReport="true"'
        )
        return (
            head
            + f"""  <iwxxm:validPeriod>
    <gml:TimePeriod gml:id="t.valid">
      <gml:beginPosition>{begin}</gml:beginPosition>
      <gml:endPosition>{end}</gml:endPosition>
    </gml:TimePeriod>
  </iwxxm:validPeriod>
  <iwxxm:cancelledReportSequenceNumber>{int(ir["cancelled_sequence"])}</iwxxm:cancelledReportSequenceNumber>
  <iwxxm:cancelledReportValidPeriod>
    <gml:TimePeriod gml:id="t.cancelled">
      <gml:beginPosition>{c_begin}</gml:beginPosition>
      <gml:endPosition>{c_end}</gml:endPosition>
    </gml:TimePeriod>
  </iwxxm:cancelledReportValidPeriod>
</iwxxm:{root}>
"""
        )

    phenom = _SIG_PHENOM_HREF.format(code=ir["phenomenon"])
    intensity = str(ir.get("intensity_change", "NO_CHANGE"))
    geometry = _sigmet_geometry_xml(ir, fir=fir)
    motion = _sigmet_motion_xml(ir)
    head = _sigmet_header_units(ir, ns=ns, gml_id=gml_id, issue=issue).format(cancel_attr="")
    return (
        head
        + f"""  <iwxxm:validPeriod>
    <gml:TimePeriod gml:id="t.valid">
      <gml:beginPosition>{begin}</gml:beginPosition>
      <gml:endPosition>{end}</gml:endPosition>
    </gml:TimePeriod>
  </iwxxm:validPeriod>
  <iwxxm:phenomenon xlink:href="{escape(phenom)}"/>
  <iwxxm:analysisCollection>
    <iwxxm:analysisAndForecastPositionAnalysis gml:id="analysis.{fir.lower()}">
      <iwxxm:analysis>
        <iwxxm:SIGMETEvolvingConditionCollection gml:id="evolving.{fir.lower()}" timeIndicator="FORECAST">
          <iwxxm:phenomenonTime nilReason="http://codes.wmo.int/common/nil/missing"/>
          <iwxxm:member>
            <iwxxm:SIGMETEvolvingCondition gml:id="cond.{fir.lower()}" intensityChange="{escape(intensity)}">{geometry}{motion}
            </iwxxm:SIGMETEvolvingCondition>
          </iwxxm:member>
        </iwxxm:SIGMETEvolvingConditionCollection>
      </iwxxm:analysis>
    </iwxxm:analysisAndForecastPositionAnalysis>
  </iwxxm:analysisCollection>
</iwxxm:{root}>
"""
    )


def emit_airmet_annex3(ir: dict[str, Any], *, iwxxm_version: str) -> str:
    """Emit an IWXXM AIRMET document (F6.d / F24 A3 geometry fidelity / #731)."""
    ns = _ns(iwxxm_version)
    fir = str(ir["fir"])
    mwo = str(ir["mwo"])
    issue, begin, end = _hazard_stamp(ir, "airmet")
    phenom = _AIR_PHENOM_HREF.format(code=ir["phenomenon"])
    gml_id = f"airmet.basic.{fir.lower()}"
    intensity = str(ir.get("intensity_change", "NO_CHANGE"))
    time_indicator = str(ir.get("time_indicator", "OBSERVATION"))
    geometry = _sigmet_geometry_xml(ir, fir=fir)
    motion = _sigmet_motion_xml(ir)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:AIRMET xmlns:iwxxm="{ns}"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:aixm="http://www.aixm.aero/schema/5.1.1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    gml:id="{gml_id}"
    reportStatus="NORMAL"
    permissibleUsage="OPERATIONAL">
  <iwxxm:issueTime>
    <gml:TimeInstant gml:id="t.issue">
      <gml:timePosition>{issue}</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:issueTime>
  <iwxxm:issuingAirTrafficServicesUnit>
    <aixm:Unit gml:id="unit.atsu.{fir.lower()}">
      <aixm:timeSlice>
        <aixm:UnitTimeSlice gml:id="unit.atsu.ts.{fir.lower()}">
          <gml:validTime/>
          <aixm:interpretation>SNAPSHOT</aixm:interpretation>
          <aixm:name>{escape(fir)} FIC</aixm:name>
          <aixm:type>FIC</aixm:type>
          <aixm:designator>{escape(fir)}</aixm:designator>
        </aixm:UnitTimeSlice>
      </aixm:timeSlice>
    </aixm:Unit>
  </iwxxm:issuingAirTrafficServicesUnit>
  <iwxxm:originatingMeteorologicalWatchOffice>
    <aixm:Unit gml:id="unit.mwo.{mwo.lower()}">
      <aixm:timeSlice>
        <aixm:UnitTimeSlice gml:id="unit.mwo.ts.{mwo.lower()}">
          <gml:validTime/>
          <aixm:interpretation>SNAPSHOT</aixm:interpretation>
          <aixm:name>{escape(mwo)} MWO</aixm:name>
          <aixm:type>MWO</aixm:type>
          <aixm:designator>{escape(mwo)}</aixm:designator>
        </aixm:UnitTimeSlice>
      </aixm:timeSlice>
    </aixm:Unit>
  </iwxxm:originatingMeteorologicalWatchOffice>
  <iwxxm:issuingAirTrafficServicesRegion>
    <aixm:Airspace gml:id="as.{fir.lower()}">
      <aixm:timeSlice>
        <aixm:AirspaceTimeSlice gml:id="as.ts.{fir.lower()}">
          <gml:validTime/>
          <aixm:interpretation>SNAPSHOT</aixm:interpretation>
          <aixm:type>FIR</aixm:type>
          <aixm:designator>{escape(fir)}</aixm:designator>
          <aixm:name>{escape(str(ir.get("fir_name", fir)))}</aixm:name>
        </aixm:AirspaceTimeSlice>
      </aixm:timeSlice>
    </aixm:Airspace>
  </iwxxm:issuingAirTrafficServicesRegion>
  <iwxxm:sequenceNumber>{int(ir["sequence"])}</iwxxm:sequenceNumber>
  <iwxxm:validPeriod>
    <gml:TimePeriod gml:id="t.valid">
      <gml:beginPosition>{begin}</gml:beginPosition>
      <gml:endPosition>{end}</gml:endPosition>
    </gml:TimePeriod>
  </iwxxm:validPeriod>
  <iwxxm:phenomenon xlink:href="{escape(phenom)}"/>
  <iwxxm:analysis>
    <iwxxm:AIRMETEvolvingConditionCollection gml:id="evolving.{fir.lower()}" timeIndicator="{escape(time_indicator)}">
      <iwxxm:phenomenonTime nilReason="http://codes.wmo.int/common/nil/missing"/>
      <iwxxm:member>
        <iwxxm:AIRMETEvolvingCondition gml:id="cond.{fir.lower()}" intensityChange="{escape(intensity)}">{geometry}{motion}
        </iwxxm:AIRMETEvolvingCondition>
      </iwxxm:member>
    </iwxxm:AIRMETEvolvingConditionCollection>
  </iwxxm:analysis>
</iwxxm:AIRMET>
"""


_VAA_FORBIDDEN_ROOTS = frozenset(
    {
        "VolcanicAshSIGMET",
        "SIGMET",
        "TropicalCycloneSIGMET",
        "AIRMET",
        "TropicalCycloneAdvisory",
    }
)

_TCA_FORBIDDEN_ROOTS = frozenset(
    {
        "TropicalCycloneSIGMET",
        "SIGMET",
        "VolcanicAshSIGMET",
        "AIRMET",
        "VolcanicAshAdvisory",
    }
)


def _vaa_cloud_extent_xml(cloud: dict[str, Any], *, gid: str) -> str:
    """Emit ashCloudExtent AirspaceVolume (+ optional motion) for one cloud."""
    if cloud.get("lower") == "GND":
        limits = f"""
                            <aixm:upperLimit uom="FL">{int(cloud["upper_fl"])}</aixm:upperLimit>
                            <aixm:upperLimitReference>STD</aixm:upperLimitReference>
                            <aixm:lowerLimit>GND</aixm:lowerLimit>
                            <aixm:lowerLimitReference>SFC</aixm:lowerLimitReference>"""
    else:
        limits = f"""
                            <aixm:upperLimit uom="FL">{int(cloud["upper_fl"])}</aixm:upperLimit>
                            <aixm:upperLimitReference>STD</aixm:upperLimitReference>
                            <aixm:lowerLimit uom="FL">{int(cloud["lower_fl"])}</aixm:lowerLimit>
                            <aixm:lowerLimitReference>STD</aixm:lowerLimitReference>"""
    pos_list = escape(str(cloud["pos_list"]))
    motion = ""
    if "motion_dir_deg" in cloud and "motion_speed_kt" in cloud:
        motion = f"""
                    <iwxxm:directionOfMotion uom="deg">{int(cloud["motion_dir_deg"])}</iwxxm:directionOfMotion>
                    <iwxxm:speedOfMotion uom="[kn_i]">{int(cloud["motion_speed_kt"])}</iwxxm:speedOfMotion>"""
    return f"""
                    <iwxxm:ashCloudExtent>
                        <aixm:AirspaceVolume gml:id="{gid}.vol">{limits}
                            <aixm:horizontalProjection>
                                <aixm:Surface gml:id="{gid}.sfc" srsDimension="2" axisLabels="Lat Long" srsName="http://www.opengis.net/def/crs/EPSG/0/4326">
                                    <gml:patches>
                                        <gml:PolygonPatch>
                                            <gml:exterior>
                                                <gml:LinearRing>
                                                    <gml:posList>{pos_list}</gml:posList>
                                                </gml:LinearRing>
                                            </gml:exterior>
                                        </gml:PolygonPatch>
                                    </gml:patches>
                                </aixm:Surface>
                            </aixm:horizontalProjection>
                        </aixm:AirspaceVolume>
                    </iwxxm:ashCloudExtent>{motion}"""


def emit_vaa_annex3(ir: dict[str, Any], *, iwxxm_version: str) -> str:
    """
    Emit an IWXXM ``VolcanicAshAdvisory`` document (F6.f / F26 themes V2–V3).

    Product/root guard (TC-F26-006 / #736): under ``product=vaa`` this emitter
    always opens ``iwxxm:VolcanicAshAdvisory`` and never ``VolcanicAshSIGMET``
    (or other SIGMET-family / TCA roots). Rejects IR that claims a forbidden
    ``iwxxm_root`` or non-VAA ``product``.
    """
    product = str(ir.get("product", "VAA")).upper()
    if product != "VAA":
        raise ValueError(f"VAA emitter product/root guard: expected product VAA, found {product!r}")
    claimed = ir.get("iwxxm_root")
    if claimed is not None and str(claimed) in _VAA_FORBIDDEN_ROOTS:
        raise ValueError(
            f"VAA emitter product/root guard: refusing forbidden iwxxm_root={claimed!r} "
            "(never emit VolcanicAshSIGMET under product=vaa)"
        )
    if claimed is not None and str(claimed) not in {"VolcanicAshAdvisory", "VAA"}:
        raise ValueError(f"VAA emitter product/root guard: unexpected iwxxm_root={claimed!r}")

    ns = _ns(iwxxm_version)
    vaac = str(ir["vaac"])
    volcano = str(ir["volcano"])
    issue = str(ir["issue_time"])
    slug = re.sub(r"[^a-z0-9]+", ".", volcano.lower()).strip(".")
    lat = ir.get("lat")
    lon = ir.get("lon")
    pos = ""
    if lat is not None and lon is not None:
        pos = f"""
            <metce:position>
                <gml:Point gml:id="volcano.pos.{slug}" srsDimension="2" axisLabels="Lat Long" srsName="http://www.opengis.net/def/crs/EPSG/0/4326">
                    <gml:pos>{lat} {lon}</gml:pos>
                </gml:Point>
            </metce:position>"""
    eruption_date_xml = ""
    if ir.get("eruption_date"):
        eruption_date_xml = f"\n            <metce:eruptionDate>{escape(str(ir['eruption_date']))}</metce:eruptionDate>"
    elev = ""
    if ir.get("source_elevation_m") is not None:
        elev = f'\n    <iwxxm:sourceElevationAMSL uom="m">{ir["source_elevation_m"]}</iwxxm:sourceElevationAMSL>'
    area = ""
    if ir.get("area"):
        area = f"\n    <iwxxm:stateOrRegion>{escape(str(ir['area']))}</iwxxm:stateOrRegion>"

    obs_clouds: list[dict[str, Any]] = list(ir.get("observation_clouds") or [])
    if obs_clouds and ir.get("observation_time"):
        ash_xml: list[str] = []
        for idx, cloud in enumerate(obs_clouds):
            extent = _vaa_cloud_extent_xml(cloud, gid=f"obs.cloud.{idx}")
            ash_xml.append(
                f"""
            <iwxxm:ashCloud>
                <iwxxm:VolcanicAshCloudObservedOrEstimated gml:id="obs.cloud.{idx}">{extent}
                </iwxxm:VolcanicAshCloudObservedOrEstimated>
            </iwxxm:ashCloud>"""
            )
        observation = f"""
    <iwxxm:observation>
        <iwxxm:VolcanicAshObservedOrEstimatedConditions gml:id="obs.{slug}" status="PROVIDED">
            <iwxxm:phenomenonTime>
                <gml:TimeInstant gml:id="t.obs">
                    <gml:timePosition>{escape(str(ir["observation_time"]))}</gml:timePosition>
                </gml:TimeInstant>
            </iwxxm:phenomenonTime>{"".join(ash_xml)}
        </iwxxm:VolcanicAshObservedOrEstimatedConditions>
    </iwxxm:observation>"""
    else:
        observation = '\n    <iwxxm:observation nilReason="http://codes.wmo.int/common/nil/missing"/>'

    forecast_blocks: list[str] = []
    for idx, fcst in enumerate(list(ir.get("forecasts") or [])):
        status = str(fcst.get("status", "PROVIDED"))
        time_iso = fcst.get("time")
        if not time_iso:
            continue
        clouds: list[dict[str, Any]] = list(fcst.get("clouds") or [])
        ash_xml_fcst: list[str] = []
        for cidx, cloud in enumerate(clouds):
            extent = _vaa_cloud_extent_xml(cloud, gid=f"fcst.{idx}.cloud.{cidx}")
            # Forecast clouds have no motion in WMO A7-2.
            extent = re.sub(
                r"\n\s*<iwxxm:directionOfMotion.*?</iwxxm:speedOfMotion>",
                "",
                extent,
                flags=re.DOTALL,
            )
            ash_xml_fcst.append(
                f"""
            <iwxxm:ashCloud>
                <iwxxm:VolcanicAshCloudForecast gml:id="fcst.{idx}.cloud.{cidx}">{extent}
                </iwxxm:VolcanicAshCloudForecast>
            </iwxxm:ashCloud>"""
            )
        forecast_blocks.append(
            f"""
    <iwxxm:forecast>
        <iwxxm:VolcanicAshForecastConditions gml:id="fcst.{idx}" status="{escape(status)}">
            <iwxxm:phenomenonTime>
                <gml:TimeInstant gml:id="t.fcst.{idx}">
                    <gml:timePosition>{escape(str(time_iso))}</gml:timePosition>
                </gml:TimeInstant>
            </iwxxm:phenomenonTime>{"".join(ash_xml_fcst)}
        </iwxxm:VolcanicAshForecastConditions>
    </iwxxm:forecast>"""
        )

    remarks_xml = ""
    if ir.get("remarks"):
        remarks_xml = f"\n    <iwxxm:remarks>{escape(str(ir['remarks']))}</iwxxm:remarks>"

    next_xml = ""
    if ir.get("next_advisory_time"):
        next_xml = f"""
    <iwxxm:nextAdvisoryTime>
        <gml:TimeInstant gml:id="t.next">
            <gml:timePosition>{escape(str(ir["next_advisory_time"]))}</gml:timePosition>
        </gml:TimeInstant>
    </iwxxm:nextAdvisoryTime>"""

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:VolcanicAshAdvisory xmlns:iwxxm="{ns}"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:aixm="http://www.aixm.aero/schema/5.1.1"
    xmlns:metce="http://def.wmo.int/metce/2013"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    gml:id="vaa.{slug}"
    reportStatus="NORMAL"
    permissibleUsage="OPERATIONAL">
    <iwxxm:issueTime>
        <gml:TimeInstant gml:id="t.issue">
            <gml:timePosition>{issue}</gml:timePosition>
        </gml:TimeInstant>
    </iwxxm:issueTime>
    <iwxxm:issuingVolcanicAshAdvisoryCentre>
        <aixm:Unit gml:id="unit.vaac.{vaac.lower()}">
            <aixm:timeSlice>
                <aixm:UnitTimeSlice gml:id="unit.vaac.ts.{vaac.lower()}">
                    <gml:validTime/>
                    <aixm:interpretation>SNAPSHOT</aixm:interpretation>
                    <aixm:name>{escape(vaac)}</aixm:name>
                    <aixm:type>OTHER:VAAC</aixm:type>
                </aixm:UnitTimeSlice>
            </aixm:timeSlice>
        </aixm:Unit>
    </iwxxm:issuingVolcanicAshAdvisoryCentre>
    <iwxxm:volcano>
        <metce:EruptingVolcano gml:id="volcano.{slug}">
            <metce:name>{escape(volcano)}</metce:name>{pos}{eruption_date_xml}
        </metce:EruptingVolcano>
    </iwxxm:volcano>{area}{elev}
    <iwxxm:advisoryNumber>{escape(str(ir.get("advisory_number", "")))}</iwxxm:advisoryNumber>
    <iwxxm:informationSource>{escape(str(ir.get("information_source", "")))}</iwxxm:informationSource>
    <iwxxm:eruptionDetails>{escape(str(ir.get("eruption_details", "")))}</iwxxm:eruptionDetails>{observation}{"".join(forecast_blocks)}{remarks_xml}{next_xml}
</iwxxm:VolcanicAshAdvisory>
"""
    if "<iwxxm:VolcanicAshAdvisory " not in xml:
        raise ValueError("VAA emitter product/root guard: missing VolcanicAshAdvisory root")
    if "<iwxxm:VolcanicAshSIGMET " in xml or "iwxxm:VolcanicAshSIGMET" in xml:
        raise ValueError("VAA emitter product/root guard: VolcanicAshSIGMET must not appear under product=vaa")
    return xml


def _tca_format_pos(lat: float, lon: float) -> str:
    """Format lat/lon for WMO A2-2-style ``gml:pos`` (up to 5 decimals; ``.00`` for wholes)."""

    def _one(value: float) -> str:
        s = f"{value:.5f}".rstrip("0")
        if s.endswith("."):
            s += "00"
        return s

    return f"{_one(lat)} {_one(lon)}"


def emit_tca_annex3(ir: dict[str, Any], *, iwxxm_version: str) -> str:
    """
    Emit an IWXXM ``TropicalCycloneAdvisory`` document (F6.f / F27 themes T2–T3).

    Product/root guard (TC-F27-006 / #737): under ``product=tca`` this emitter
    always opens ``iwxxm:TropicalCycloneAdvisory`` and never
    ``TropicalCycloneSIGMET`` (or other SIGMET-family / VAA roots). Rejects IR
    that claims a forbidden ``iwxxm_root`` or non-TCA ``product``.

    Vendor fidelity (TC-F27-002 / A2-2): observation + forecasts + RMK NIL →
    ``remarks`` with ``nilReason=inapplicable``.
    """
    product = str(ir.get("product", "TCA")).upper()
    if product != "TCA":
        raise ValueError(f"TCA emitter product/root guard: expected product TCA, found {product!r}")
    claimed = ir.get("iwxxm_root")
    if claimed is not None and str(claimed) in _TCA_FORBIDDEN_ROOTS:
        raise ValueError(
            f"TCA emitter product/root guard: refusing forbidden iwxxm_root={claimed!r} "
            "(never emit TropicalCycloneSIGMET under product=tca)"
        )
    if claimed is not None and str(claimed) not in {"TropicalCycloneAdvisory", "TCA"}:
        raise ValueError(f"TCA emitter product/root guard: unexpected iwxxm_root={claimed!r}")

    ns = _ns(iwxxm_version)
    tcac = str(ir["tcac"])
    name = str(ir["tc_name"])
    issue = str(ir["issue_time"])
    slug = re.sub(r"[^a-z0-9]+", ".", name.lower()).strip(".")
    lat = ir.get("lat")
    lon = ir.get("lon")

    observation = ""
    if lat is not None and lon is not None and ir.get("observation_time"):
        pos_txt = _tca_format_pos(float(lat), float(lon))
        cb_raw = ir.get("cb")
        cb: dict[str, Any] = cast(dict[str, Any], cb_raw) if isinstance(cb_raw, dict) else {}
        if cb.get("nil"):
            cb_xml = (
                '\n            <iwxxm:cumulonimbusCloudLocation nilReason="http://codes.wmo.int/common/nil/missing"/>'
            )
        elif cb.get("radius_nm") is not None:
            fl_raw = cb.get("upper_fl")
            fl: int | None = int(fl_raw) if fl_raw is not None else None
            fl_xml = (
                f"""
                    <aixm:upperLimit uom="FL">{fl}</aixm:upperLimit>
                    <aixm:upperLimitReference>STD</aixm:upperLimitReference>"""
                if fl is not None
                else ""
            )
            radius_nm = int(cb["radius_nm"])
            cb_xml = f"""
            <iwxxm:cumulonimbusCloudLocation>
                <aixm:AirspaceVolume gml:id="cb.{slug}">
                    {fl_xml}
                    <aixm:horizontalProjection>
                        <aixm:Surface gml:id="cb.sfc.{slug}" srsDimension="2" axisLabels="Lat Long" srsName="http://www.opengis.net/def/crs/EPSG/0/4326">
                            <gml:patches>
                                <gml:PolygonPatch>
                                    <gml:exterior>
                                        <gml:Ring>
                                            <gml:curveMember>
                                                <gml:Curve gml:id="cb.curve.{slug}">
                                                    <gml:segments>
                                                        <gml:CircleByCenterPoint numArc="1">
                                                            <gml:pos>{pos_txt}</gml:pos>
                                                            <gml:radius uom="[nmi_i]">{radius_nm}</gml:radius>
                                                        </gml:CircleByCenterPoint>
                                                    </gml:segments>
                                                </gml:Curve>
                                            </gml:curveMember>
                                        </gml:Ring>
                                    </gml:exterior>
                                </gml:PolygonPatch>
                            </gml:patches>
                        </aixm:Surface>
                    </aixm:horizontalProjection>
                </aixm:AirspaceVolume>
            </iwxxm:cumulonimbusCloudLocation>"""
        else:
            cb_xml = ""

        mov_raw = ir.get("movement")
        mov: dict[str, Any] = cast(dict[str, Any], mov_raw) if isinstance(mov_raw, dict) else {}
        mov_xml = ""
        if mov.get("status") == "MOVING":
            direction_deg = int(mov["direction_deg"])
            speed = int(mov["speed"])
            speed_uom = str(mov.get("speed_uom", "km/h"))
            mov_xml = f"""
            <iwxxm:movement>MOVING</iwxxm:movement>
            <iwxxm:movementDirection uom="deg">{direction_deg}</iwxxm:movementDirection>
            <iwxxm:movementSpeed uom="{escape(speed_uom)}">{speed}</iwxxm:movementSpeed>"""
        elif mov.get("status") == "STATIONARY":
            mov_xml = "\n            <iwxxm:movement>STATIONARY</iwxxm:movement>"

        intst = ""
        if ir.get("intensity_change"):
            intst = (
                f"\n            <iwxxm:intensityChange>{escape(str(ir['intensity_change']))}</iwxxm:intensityChange>"
            )

        pressure = ""
        if ir.get("central_pressure_hpa") is not None:
            pressure = (
                f'\n            <iwxxm:centralPressure uom="hPa">{ir["central_pressure_hpa"]}</iwxxm:centralPressure>'
            )

        wind = ""
        if ir.get("max_wind_mps") is not None:
            wind = f'\n            <iwxxm:maximumSurfaceWindSpeed uom="m/s">{ir["max_wind_mps"]}</iwxxm:maximumSurfaceWindSpeed>'

        observation = f"""
    <iwxxm:observation>
        <iwxxm:TropicalCycloneObservedConditions gml:id="obs.{slug}">
            <iwxxm:phenomenonTime>
                <gml:TimeInstant gml:id="t.obs">
                    <gml:timePosition>{escape(str(ir["observation_time"]))}</gml:timePosition>
                </gml:TimeInstant>
            </iwxxm:phenomenonTime>
            <iwxxm:tropicalCyclonePosition>
                <gml:Point gml:id="obs.pos.{slug}" srsDimension="2" axisLabels="Lat Long" srsName="http://www.opengis.net/def/crs/EPSG/0/4326">
                    <gml:pos>{pos_txt}</gml:pos>
                </gml:Point>
            </iwxxm:tropicalCyclonePosition>{cb_xml}{mov_xml}{intst}{pressure}{wind}
        </iwxxm:TropicalCycloneObservedConditions>
    </iwxxm:observation>"""

    forecast_blocks: list[str] = []
    for idx, fcst in enumerate(list(ir.get("forecasts") or [])):
        time_iso = fcst.get("time")
        flat = fcst.get("lat")
        flon = fcst.get("lon")
        if not time_iso or flat is None or flon is None:
            continue
        pos_txt = _tca_format_pos(float(flat), float(flon))
        wind_xml = ""
        if fcst.get("max_wind_mps") is not None:
            wind_xml = f'\n            <iwxxm:maximumSurfaceWindSpeed uom="m/s">{fcst["max_wind_mps"]}</iwxxm:maximumSurfaceWindSpeed>'
        forecast_blocks.append(
            f"""
    <iwxxm:forecast>
        <iwxxm:TropicalCycloneForecastConditions gml:id="fcst.{idx}">
            <iwxxm:phenomenonTime>
                <gml:TimeInstant gml:id="t.fcst.{idx}">
                    <gml:timePosition>{escape(str(time_iso))}</gml:timePosition>
                </gml:TimeInstant>
            </iwxxm:phenomenonTime>
            <iwxxm:tropicalCyclonePosition>
                <gml:Point gml:id="fcst.pos.{idx}" srsDimension="2" axisLabels="Lat Long" srsName="http://www.opengis.net/def/crs/EPSG/0/4326">
                    <gml:pos>{pos_txt}</gml:pos>
                </gml:Point>
            </iwxxm:tropicalCyclonePosition>{wind_xml}
        </iwxxm:TropicalCycloneForecastConditions>
    </iwxxm:forecast>"""
        )

    if ir.get("remarks") and not ir.get("remarks_nil"):
        remarks_xml = f"\n    <iwxxm:remarks>{escape(str(ir['remarks']))}</iwxxm:remarks>"
    else:
        remarks_xml = '\n    <iwxxm:remarks nilReason="http://codes.wmo.int/common/nil/inapplicable"/>'

    if ir.get("next_advisory_nil"):
        next_xml = '\n    <iwxxm:nextAdvisoryTime nilReason="http://codes.wmo.int/common/nil/inapplicable"/>'
    elif ir.get("next_advisory_time"):
        next_xml = f"""
    <iwxxm:nextAdvisoryTime>
        <gml:TimeInstant gml:id="t.next">
            <gml:timePosition>{escape(str(ir["next_advisory_time"]))}</gml:timePosition>
        </gml:TimeInstant>
    </iwxxm:nextAdvisoryTime>"""
    else:
        next_xml = ""

    # Minimal fallback when observation block absent (sparse IR / adjacency fixtures).
    fallback = ""
    if not observation:
        pos = ""
        if lat is not None and lon is not None:
            pos_txt = _tca_format_pos(float(lat), float(lon))
            pos = f"""
    <iwxxm:tropicalCyclonePosition>
        <gml:Point gml:id="tc.pos.{slug}" srsDimension="2" axisLabels="Lat Long" srsName="http://www.opengis.net/def/crs/EPSG/0/4326">
            <gml:pos>{pos_txt}</gml:pos>
        </gml:Point>
    </iwxxm:tropicalCyclonePosition>"""
        pressure = ""
        if ir.get("central_pressure_hpa") is not None:
            pressure = f'\n    <iwxxm:centralPressure uom="hPa">{ir["central_pressure_hpa"]}</iwxxm:centralPressure>'
        wind = ""
        if ir.get("max_wind_mps") is not None:
            wind = (
                f'\n    <iwxxm:maximumSurfaceWindSpeed uom="m/s">{ir["max_wind_mps"]}</iwxxm:maximumSurfaceWindSpeed>'
            )
        fallback = f"{pos}{pressure}{wind}"

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:TropicalCycloneAdvisory xmlns:iwxxm="{ns}"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:aixm="http://www.aixm.aero/schema/5.1.1"
    xmlns:metce="http://def.wmo.int/metce/2013"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    gml:id="tca.{slug}"
    reportStatus="NORMAL"
    permissibleUsage="OPERATIONAL">
    <iwxxm:issueTime>
        <gml:TimeInstant gml:id="t.issue">
            <gml:timePosition>{escape(issue)}</gml:timePosition>
        </gml:TimeInstant>
    </iwxxm:issueTime>
    <iwxxm:issuingTropicalCycloneAdvisoryCentre>
        <aixm:Unit gml:id="unit.tcac.{tcac.lower()}">
            <aixm:timeSlice>
                <aixm:UnitTimeSlice gml:id="unit.tcac.ts.{tcac.lower()}">
                    <gml:validTime/>
                    <aixm:interpretation>SNAPSHOT</aixm:interpretation>
                    <aixm:type>OTHER:TCAC</aixm:type>
                    <aixm:designator>{escape(tcac)}</aixm:designator>
                </aixm:UnitTimeSlice>
            </aixm:timeSlice>
        </aixm:Unit>
    </iwxxm:issuingTropicalCycloneAdvisoryCentre>
    <iwxxm:tropicalCycloneName>
        <metce:TropicalCyclone gml:id="tc.{slug}">
            <metce:name>{escape(name)}</metce:name>
        </metce:TropicalCyclone>
    </iwxxm:tropicalCycloneName>
    <iwxxm:advisoryNumber>{escape(str(ir.get("advisory_number", "")))}</iwxxm:advisoryNumber>{observation}{"".join(forecast_blocks)}{fallback}{remarks_xml}{next_xml}
</iwxxm:TropicalCycloneAdvisory>
"""
    return _assert_tca_advisory_xml(xml)


def _assert_tca_advisory_xml(xml: str) -> str:
    if "<iwxxm:TropicalCycloneAdvisory " not in xml:
        raise ValueError("TCA emitter product/root guard: missing TropicalCycloneAdvisory root")
    if "<iwxxm:TropicalCycloneSIGMET " in xml or "iwxxm:TropicalCycloneSIGMET" in xml:
        raise ValueError("TCA emitter product/root guard: TropicalCycloneSIGMET must not appear under product=tca")
    return xml


__all__ = [
    "emit_airmet_annex3",
    "emit_sigmet_annex3",
    "emit_taf_annex3",
    "emit_tca_annex3",
    "emit_vaa_annex3",
]
