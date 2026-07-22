"""Annex-3 profile XML writers for TAF / SIGMET / AIRMET (F6.c–d)."""

from __future__ import annotations

import re
from typing import Any
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


def emit_sigmet_annex3(ir: dict[str, Any], *, iwxxm_version: str) -> str:
    """Emit a minimal IWXXM SIGMET document for the annex3 profile."""
    ns = _ns(iwxxm_version)
    fir = str(ir["fir"])
    mwo = str(ir["mwo"])
    issue, begin, end = _hazard_stamp(ir, "sigmet")
    phenom = _SIG_PHENOM_HREF.format(code=ir["phenomenon"])
    gml_id = f"sigmet.basic.{fir.lower()}"

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:SIGMET xmlns:iwxxm="{ns}"
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
          <aixm:type>OTHER:FIR_UIR</aixm:type>
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
  <iwxxm:analysisCollection>
    <iwxxm:analysisAndForecastPositionAnalysis gml:id="analysis.{fir.lower()}">
      <iwxxm:analysis>
        <iwxxm:SIGMETEvolvingConditionCollection gml:id="evolving.{fir.lower()}" timeIndicator="FORECAST">
          <iwxxm:phenomenonTime nilReason="http://codes.wmo.int/common/nil/missing"/>
          <iwxxm:member>
            <iwxxm:SIGMETEvolvingCondition gml:id="cond.{fir.lower()}" intensityChange="WEAKEN">
              <iwxxm:geometry nilReason="http://codes.wmo.int/common/nil/missing"/>
            </iwxxm:SIGMETEvolvingCondition>
          </iwxxm:member>
        </iwxxm:SIGMETEvolvingConditionCollection>
      </iwxxm:analysis>
    </iwxxm:analysisAndForecastPositionAnalysis>
  </iwxxm:analysisCollection>
</iwxxm:SIGMET>
"""


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
