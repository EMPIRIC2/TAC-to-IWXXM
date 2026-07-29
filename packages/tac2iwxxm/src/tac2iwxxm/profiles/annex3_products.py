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
_SIG_PHENOM_HREF = "http://codes.wmo.int/49-2/SigWxPhenomena/{code}"
_AIR_PHENOM_HREF = "http://codes.wmo.int/49-2/AirWxPhenomena/{code}"


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
  <iwxxm:aerodrome>
    <aixm:AirportHeliport gml:id="ad.{station.lower()}">
      <aixm:timeSlice>
        <aixm:AirportHeliportTimeSlice gml:id="ad.ts.{station.lower()}">
          <gml:validTime/>
          <aixm:interpretation>SNAPSHOT</aixm:interpretation>
          <aixm:designator>{escape(station)}</aixm:designator>
          <aixm:locationIndicatorICAO>{escape(station)}</aixm:locationIndicatorICAO>
        </aixm:AirportHeliportTimeSlice>
      </aixm:timeSlice>
    </aixm:AirportHeliport>
  </iwxxm:aerodrome>
  <iwxxm:cancelledReportValidPeriod>
    <gml:TimePeriod gml:id="t.cancelled">
      <gml:beginPosition>{begin}</gml:beginPosition>
      <gml:endPosition>{end}</gml:endPosition>
    </gml:TimePeriod>
  </iwxxm:cancelledReportValidPeriod>
</iwxxm:TAF>
"""

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
  <iwxxm:aerodrome>
    <aixm:AirportHeliport gml:id="ad.{station.lower()}">
      <aixm:timeSlice>
        <aixm:AirportHeliportTimeSlice gml:id="ad.ts.{station.lower()}">
          <gml:validTime/>
          <aixm:interpretation>SNAPSHOT</aixm:interpretation>
          <aixm:designator>{escape(station)}</aixm:designator>
          <aixm:locationIndicatorICAO>{escape(station)}</aixm:locationIndicatorICAO>
        </aixm:AirportHeliportTimeSlice>
      </aixm:timeSlice>
    </aixm:AirportHeliport>
  </iwxxm:aerodrome>
  <iwxxm:baseForecast nilReason="http://codes.wmo.int/common/nil/missing"/>
</iwxxm:TAF>
"""

    begin, end = _taf_period(ir)

    if ir.get("nil"):
        base_fcst = '  <iwxxm:baseForecast nilReason="http://codes.wmo.int/common/nil/missing"/>\n'
    else:
        cavok = "true" if ir.get("cavok") else "false"
        wind = ""
        if ir.get("wind_variable"):
            wind = """      <iwxxm:surfaceWind>
        <iwxxm:AerodromeSurfaceWindForecast variableWindDirection="true">
          <iwxxm:meanWindSpeed uom="m/s">0.0</iwxxm:meanWindSpeed>
        </iwxxm:AerodromeSurfaceWindForecast>
      </iwxxm:surfaceWind>
"""
        elif ir.get("wind_speed_mps") is not None or ir.get("wind_speed_kt") is not None:
            if ir.get("wind_speed_mps") is not None:
                spd = f"{ir['wind_speed_mps']:.1f}"
                uom = "m/s"
            else:
                spd = str(ir["wind_speed_kt"])
                uom = "[kn_i]"
            wind = f"""      <iwxxm:surfaceWind>
        <iwxxm:AerodromeSurfaceWindForecast variableWindDirection="false">
          <iwxxm:meanWindDirection uom="deg">{ir["wind_dir_deg"]}</iwxxm:meanWindDirection>
          <iwxxm:meanWindSpeed uom="{uom}">{spd}</iwxxm:meanWindSpeed>
        </iwxxm:AerodromeSurfaceWindForecast>
      </iwxxm:surfaceWind>
"""
        vis = ""
        cloud = ""
        if not ir.get("cavok"):
            if ir.get("visibility_m") is not None:
                vis = f'      <iwxxm:prevailingVisibility uom="m">{ir["visibility_m"]}</iwxxm:prevailingVisibility>\n'
            if ir.get("cloud_amount") and ir.get("cloud_base_ft") is not None:
                href = _CLOUD_HREF.format(amt=ir["cloud_amount"])
                cloud = f"""      <iwxxm:cloud>
        <iwxxm:AerodromeCloudForecast gml:id="cloud.base.{station.lower()}">
          <iwxxm:layer>
            <iwxxm:CloudLayer>
              <iwxxm:amount xlink:href="{escape(href)}"/>
              <iwxxm:base uom="[ft_i]">{ir["cloud_base_ft"]}</iwxxm:base>
            </iwxxm:CloudLayer>
          </iwxxm:layer>
        </iwxxm:AerodromeCloudForecast>
      </iwxxm:cloud>
"""
        base_fcst = f"""  <iwxxm:baseForecast>
    <iwxxm:MeteorologicalAerodromeForecast gml:id="fcst.base.{station.lower()}" cloudAndVisibilityOK="{cavok}">
      <iwxxm:phenomenonTime xlink:href="#t.valid"/>
{vis}{wind}{cloud}    </iwxxm:MeteorologicalAerodromeForecast>
  </iwxxm:baseForecast>
"""

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
  <iwxxm:aerodrome>
    <aixm:AirportHeliport gml:id="ad.{station.lower()}">
      <aixm:timeSlice>
        <aixm:AirportHeliportTimeSlice gml:id="ad.ts.{station.lower()}">
          <gml:validTime/>
          <aixm:interpretation>SNAPSHOT</aixm:interpretation>
          <aixm:designator>{escape(station)}</aixm:designator>
          <aixm:locationIndicatorICAO>{escape(station)}</aixm:locationIndicatorICAO>
        </aixm:AirportHeliportTimeSlice>
      </aixm:timeSlice>
    </aixm:AirportHeliport>
  </iwxxm:aerodrome>
  <iwxxm:validPeriod>
    <gml:TimePeriod gml:id="t.valid">
      <gml:beginPosition>{begin}</gml:beginPosition>
      <gml:endPosition>{end}</gml:endPosition>
    </gml:TimePeriod>
  </iwxxm:validPeriod>
{base_fcst}</iwxxm:TAF>
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
    """Emit a minimal IWXXM AIRMET document for the annex3 profile."""
    ns = _ns(iwxxm_version)
    fir = str(ir["fir"])
    mwo = str(ir["mwo"])
    issue, begin, end = _hazard_stamp(ir, "airmet")
    phenom = _AIR_PHENOM_HREF.format(code=ir["phenomenon"])
    gml_id = f"airmet.basic.{fir.lower()}"

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
    <iwxxm:AIRMETEvolvingConditionCollection gml:id="evolving.{fir.lower()}" timeIndicator="OBSERVATION">
      <iwxxm:phenomenonTime nilReason="http://codes.wmo.int/common/nil/missing"/>
      <iwxxm:member>
        <iwxxm:AIRMETEvolvingCondition gml:id="cond.{fir.lower()}" intensityChange="WEAKEN">
          <iwxxm:geometry nilReason="http://codes.wmo.int/common/nil/missing"/>
        </iwxxm:AIRMETEvolvingCondition>
      </iwxxm:member>
    </iwxxm:AIRMETEvolvingConditionCollection>
  </iwxxm:analysis>
</iwxxm:AIRMET>
"""


def emit_vaa_annex3(ir: dict[str, Any], *, iwxxm_version: str) -> str:
    """Emit a minimal IWXXM VolcanicAshAdvisory document."""
    ns = _ns(iwxxm_version)
    vaac = str(ir["vaac"])
    volcano = str(ir["volcano"])
    issue = str(ir["issue_time"])
    slug = re.sub(r"[^a-z0-9]+", ".", volcano.lower()).strip(".")
    lat = ir.get("lat")
    lon = ir.get("lon")
    pos = ""
    if lat is not None and lon is not None:
        pos = f"""      <metce:position>
        <gml:Point gml:id="volcano.pos.{slug}" srsDimension="2" axisLabels="Lat Long"
            srsName="http://www.opengis.net/def/crs/EPSG/0/4326">
          <gml:pos>{lat} {lon}</gml:pos>
        </gml:Point>
      </metce:position>
"""
    elev = ""
    if ir.get("source_elevation_m") is not None:
        elev = f'  <iwxxm:sourceElevationAMSL uom="m">{ir["source_elevation_m"]}</iwxxm:sourceElevationAMSL>\n'
    area = ""
    if ir.get("area"):
        area = f"  <iwxxm:stateOrRegion>{escape(str(ir['area']))}</iwxxm:stateOrRegion>\n"

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:VolcanicAshAdvisory xmlns:iwxxm="{ns}"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:aixm="http://www.aixm.aero/schema/5.1.1"
    xmlns:metce="http://def.wmo.int/metce/2013"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    gml:id="vaa.basic.{slug}"
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
      <metce:name>{escape(volcano)}</metce:name>
{pos}    </metce:EruptingVolcano>
  </iwxxm:volcano>
{area}{elev}  <iwxxm:advisoryNumber>{escape(str(ir.get("advisory_number", "")))}</iwxxm:advisoryNumber>
  <iwxxm:informationSource>{escape(str(ir.get("information_source", "")))}</iwxxm:informationSource>
  <iwxxm:eruptionDetails>{escape(str(ir.get("eruption_details", "")))}</iwxxm:eruptionDetails>
  <iwxxm:observation nilReason="http://codes.wmo.int/common/nil/missing"/>
</iwxxm:VolcanicAshAdvisory>
"""


def emit_tca_annex3(ir: dict[str, Any], *, iwxxm_version: str) -> str:
    """Emit a minimal IWXXM TropicalCycloneAdvisory document."""
    ns = _ns(iwxxm_version)
    tcac = str(ir["tcac"])
    name = str(ir["tc_name"])
    issue = str(ir["issue_time"])
    slug = re.sub(r"[^a-z0-9]+", ".", name.lower()).strip(".")
    lat = ir.get("lat")
    lon = ir.get("lon")
    pos = ""
    if lat is not None and lon is not None:
        pos = f"""  <iwxxm:tropicalCyclonePosition>
    <gml:Point gml:id="tc.pos.{slug}" srsDimension="2" axisLabels="Lat Long"
        srsName="http://www.opengis.net/def/crs/EPSG/0/4326">
      <gml:pos>{lat} {lon}</gml:pos>
    </gml:Point>
  </iwxxm:tropicalCyclonePosition>
"""
    wind = ""
    if ir.get("max_wind_mps") is not None:
        wind = f'  <iwxxm:maximumSurfaceWindSpeed uom="m/s">{ir["max_wind_mps"]}.0</iwxxm:maximumSurfaceWindSpeed>\n'
    pressure = ""
    if ir.get("central_pressure_hpa") is not None:
        pressure = f'  <iwxxm:centralPressure uom="hPa">{ir["central_pressure_hpa"]}</iwxxm:centralPressure>\n'

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:TropicalCycloneAdvisory xmlns:iwxxm="{ns}"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:aixm="http://www.aixm.aero/schema/5.1.1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    gml:id="tca.basic.{slug}"
    reportStatus="NORMAL"
    permissibleUsage="OPERATIONAL">
  <iwxxm:issueTime>
    <gml:TimeInstant gml:id="t.issue">
      <gml:timePosition>{issue}</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:issueTime>
  <iwxxm:issuingTropicalCycloneAdvisoryCentre>
    <aixm:Unit gml:id="unit.tcac.{tcac.lower()}">
      <aixm:timeSlice>
        <aixm:UnitTimeSlice gml:id="unit.tcac.ts.{tcac.lower()}">
          <gml:validTime/>
          <aixm:interpretation>SNAPSHOT</aixm:interpretation>
          <aixm:name>{escape(tcac)}</aixm:name>
          <aixm:type>OTHER:TCAC</aixm:type>
        </aixm:UnitTimeSlice>
      </aixm:timeSlice>
    </aixm:Unit>
  </iwxxm:issuingTropicalCycloneAdvisoryCentre>
  <iwxxm:tropicalCycloneName>{escape(name)}</iwxxm:tropicalCycloneName>
  <iwxxm:advisoryNumber>{escape(str(ir.get("advisory_number", "")))}</iwxxm:advisoryNumber>
{pos}{pressure}{wind}</iwxxm:TropicalCycloneAdvisory>
"""


__all__ = [
    "emit_airmet_annex3",
    "emit_sigmet_annex3",
    "emit_taf_annex3",
    "emit_tca_annex3",
    "emit_vaa_annex3",
]
