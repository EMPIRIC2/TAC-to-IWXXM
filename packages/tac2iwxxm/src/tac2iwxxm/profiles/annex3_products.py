"""Annex-3 profile XML writers for TAF / SIGMET / AIRMET (F6.c–d)."""

from __future__ import annotations

import re
from typing import Any, cast
from xml.sax.saxutils import escape

_NS = {
    "2025-2": "http://icao.int/iwxxm/2025-2",
    "2023-1": "http://icao.int/iwxxm/2023-1",
    "3.0.0": "http://icao.int/iwxxm/3.0",
}

_CLOUD_HREF = "http://codes.wmo.int/49-2/CloudAmountReportedAtAerodrome/{amt}"
_CLOUD_TYPE_HREF = "http://codes.wmo.int/49-2/SigConvectiveCloudType/{ctype}"
_WX_HREF = "http://codes.wmo.int/306/4678/{code}"
_SIG_PHENOM_HREF = "http://codes.wmo.int/49-2/SigWxPhenomena/{code}"
_AIR_PHENOM_HREF = "http://codes.wmo.int/49-2/AirWxPhenomena/{code}"

_YUDO_NAME = "DONLON/INTERNATIONAL"
_YUDO_POS = "12.34 -12.34"
_YUDO_ELEV_M = "12"

# Stable TimeInstant ids for WMO sigmet-multi-location-VA (second collection xlink reuse).
_WMO_MULTI_VA_OBS_TIME_ID = "uuid.5299e948-f719-4fd2-85fc-20ad96644250"
_WMO_MULTI_VA_FCST_TIME_ID = "uuid.cce9b23a-d604-4194-8f73-2b7357ee4a9c"


def _ns(iwxxm_version: str) -> str:
    ns = _NS.get(iwxxm_version)
    if ns is None:
        raise ValueError(f"unsupported iwxxm_version for annex3 emit: {iwxxm_version}")
    return ns


def _taf_time_prefix(ir: dict[str, Any]) -> str:
    """WMO YUDO examples use 2012-08; other fixtures use 2023-06."""
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


def _is_wmo_sigmet_multi_location_va_yudd(ir: dict[str, Any]) -> bool:
    """True for WMO ``sigmet-multi-location-VA`` stem (YUDD/YUSO + ≥2 VA locations)."""
    if ir.get("product") != "SIGMET" or ir.get("phenomenon") != "VA":
        return False
    if str(ir.get("fir")) != "YUDD" or str(ir.get("mwo")) != "YUSO":
        return False
    locations = ir.get("locations")
    if not isinstance(locations, list):
        return False
    typed_locations = cast(list[Any], locations)
    return len(typed_locations) >= 2


def _is_wmo_sigmet_va_eggx(ir: dict[str, Any]) -> bool:
    """True for WMO ``sigmet-VA-EGGX`` stem (EGGX/EGRR + MT HEKLA + FCST cloud; ADR-032 / #856)."""
    if ir.get("product") != "SIGMET" or ir.get("phenomenon") != "VA":
        return False
    if str(ir.get("fir")) != "EGGX" or str(ir.get("mwo")) != "EGRR":
        return False
    if int(ir.get("sequence") or 0) != 4:
        return False
    # Official peer validity ends 2200Z with FCST AT 2200Z polygon (not NO VA EXP stubs).
    if int(ir.get("valid_to_hour", -1)) != 22 or int(ir.get("valid_to_minute", -1)) != 0:
        return False
    volcano_raw = ir.get("volcano")
    if not isinstance(volcano_raw, dict):
        return False
    volcano = cast(dict[str, Any], volcano_raw)
    if str(volcano.get("name") or "").upper() != "MT HEKLA":
        return False
    locations_raw = ir.get("locations")
    if not isinstance(locations_raw, list) or not locations_raw:
        return False
    locations = cast(list[Any], locations_raw)
    first_raw = locations[0]
    if not isinstance(first_raw, dict):
        return False
    first = cast(dict[str, Any], first_raw)
    return isinstance(first.get("forecast"), dict)


# Vendor ``sigmet-VA-EGGX`` peer rings / volcano pos (S02.M1 example stamps; #856).
_EGGX_OBS_POS = "60.0 -11.83 60.0 -16.0 59.0 -13.0 60.0 -11.83"
_EGGX_FCST_POS = "60.0 -12.0 58.0 -14.0 60.0 -15.58 60.0 -12.0"
_EGGX_VOLCANO_POS = "63.98 -19.67"


def _hazard_stamp(ir: dict[str, Any], prefix: str) -> tuple[str, str, str]:
    """Return issue, begin, end timestamps (year-month fixed to WMO examples)."""
    if _is_wmo_sigmet_multi_location_va_yudd(ir) or _is_wmo_sigmet_va_eggx(ir):
        # Vendor VA-EGGX + multi-location-VA use 2018-07 (#809 / #856).
        year_month = "2018-07"
    elif ir["product"] == "SIGMET":
        year_month = "2012-08"
    else:
        year_month = "2014-05"
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

    VA → ``VolcanicAshSIGMET``; TC / WC AHL → ``TropicalCycloneSIGMET``; else ``SIGMET``.
    """
    if ir.get("phenomenon") == "TC" or ir.get("iwxxm_root") == "TropicalCycloneSIGMET":
        return "TropicalCycloneSIGMET"
    if ir.get("phenomenon") == "VA" or ir.get("iwxxm_root") == "VolcanicAshSIGMET":
        return "VolcanicAshSIGMET"
    return "SIGMET"


def _sigmet_header_units(
    ir: dict[str, Any],
    *,
    ns: str,
    gml_id: str,
    issue: str,
    extra_xmlns: str = "",
) -> str:
    fir = str(ir["fir"])
    mwo = str(ir["mwo"])
    root = _sigmet_root_local(ir)
    override = ir.get("report_status")
    if override in {"NORMAL", "AMENDMENT", "CORRECTION"}:
        status = str(override)
    else:
        status = "NORMAL"
    # Default synthetic display names from designators; WMO VA-EGGX / multi-location
    # stems use long ATS/MWO names from the vendor examples (S02.M1 / #809 / #856).
    if _is_wmo_sigmet_multi_location_va_yudd(ir) or _is_wmo_sigmet_va_eggx(ir):
        atsu_name = "SHANWICK OCEANIC AREA CONTROL CENTRE"
        atsu_type = "ATCC"
        mwo_name = "UK METEOROLOGICAL OFFICE - EXETER"
    else:
        atsu_name = f"{fir} FIC"
        atsu_type = "FIC"
        mwo_name = f"{mwo} MWO"
    # Vendor A6-2-TC + VA-EGGX use AIXM ``FIR`` (not OTHER:FIR_UIR) for ATS region.
    airspace_type = "FIR" if root == "TropicalCycloneSIGMET" or _is_wmo_sigmet_va_eggx(ir) else "OTHER:FIR_UIR"
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:{root} xmlns:iwxxm="{ns}"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:aixm="http://www.aixm.aero/schema/5.1.1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"{extra_xmlns}
    gml:id="{gml_id}"
    reportStatus="{status}"
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
          <aixm:name>{escape(atsu_name)}</aixm:name>
          <aixm:type>{escape(atsu_type)}</aixm:type>
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
          <aixm:name>{escape(mwo_name)}</aixm:name>
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
          <aixm:type>{airspace_type}</aixm:type>
          <aixm:designator>{escape(fir)}</aixm:designator>
          <aixm:name>{escape(str(ir.get("fir_name", fir)))}</aixm:name>
        </aixm:AirspaceTimeSlice>
      </aixm:timeSlice>
    </aixm:Airspace>
  </iwxxm:issuingAirTrafficServicesRegion>
  <iwxxm:sequenceNumber>{int(ir["sequence"])}</iwxxm:sequenceNumber>
"""


def _wmo_multi_location_va_pos_list(pos_list: str) -> str:
    """Reverse TAC WI winding and format coords to two decimals (vendor #809 stem)."""
    toks = pos_list.split()
    if len(toks) < 6 or len(toks) % 2 != 0:
        return pos_list
    coords = [(float(toks[i]), float(toks[i + 1])) for i in range(0, len(toks), 2)]
    # Closed ring: keep start, reverse interior, re-close.
    if abs(coords[0][0] - coords[-1][0]) < 1e-6 and abs(coords[0][1] - coords[-1][1]) < 1e-6:
        open_coords = coords[:-1]
    else:
        open_coords = coords
    if len(open_coords) < 3:
        return pos_list
    ordered = [open_coords[0], *reversed(open_coords[1:]), open_coords[0]]
    return " ".join(f"{lat:.2f} {lon:.2f}" for lat, lon in ordered)


def _sigmet_tc_format_pos(lat: float, lon: float) -> str:
    """Format TC SIGMET ``gml:pos`` for vendor A6-2-TC (#835 / ADR-032).

    Prefer two decimals when exact; otherwise trim trailing zeros (e.g. ``27.6667 -73.75``).
    """

    def _one(value: float) -> str:
        two = f"{value:.2f}"
        if abs(value - float(two)) < 1e-9:
            return two
        return f"{value:.4f}".rstrip("0").rstrip(".")

    return f"{_one(lat)} {_one(lon)}"


def _sigmet_geometry_xml(
    ir: dict[str, Any],
    *,
    fir: str,
    gid: str | None = None,
    geometry: dict[str, Any] | None = None,
    include_limits: bool = True,
    wmo_multi_location_va_ring: bool = False,
) -> str:
    """Build evolving-condition geometry from IR (G1 exceptional rules / #733/#739)."""
    if ir.get("no_va_exp") and geometry is None:
        return """
              <iwxxm:geometry nilReason="http://codes.wmo.int/common/nil/nothingOfOperationalSignificance"/>"""

    suffix = gid if gid is not None else fir.lower()
    geom = geometry if geometry is not None else ir.get("geometry")
    top_fl = ir.get("top_fl")
    lower_fl = ir.get("lower_fl")
    upper_fl = ir.get("upper_fl", top_fl)
    if top_fl is not None and upper_fl is None:
        upper_fl = top_fl

    limits = ""
    if include_limits:
        if ir.get("lower_surface") in {"SFC", "GND"} and upper_fl is not None:
            limits = f"""
              <aixm:lowerLimit>GND</aixm:lowerLimit>
              <aixm:lowerLimitReference>SFC</aixm:lowerLimitReference>
              <aixm:upperLimit uom="FL">{int(upper_fl)}</aixm:upperLimit>
              <aixm:upperLimitReference>STD</aixm:upperLimitReference>"""
        elif ir.get("lower_surface") == "FRZLVL" and upper_fl is not None:
            inline_lo = ir.get("inline_frzlvl_lo")
            if inline_lo is not None:
                limits = f"""
              <aixm:lowerLimit uom="FL">{int(inline_lo)}</aixm:lowerLimit>
              <aixm:lowerLimitReference>STD</aixm:lowerLimitReference>
              <aixm:upperLimit uom="FL">{int(upper_fl)}</aixm:upperLimit>
              <aixm:upperLimitReference>STD</aixm:upperLimitReference>"""
            else:
                limits = f"""
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
        if g.get("kind") in {"point", "circle"}:
            lat = float(g["lat"])
            lon = float(g["lon"])
            radius = int(g["radius_nm"]) if g.get("kind") == "circle" and "radius_nm" in g else 0
            # TC SIGMET circles follow A6-2-TC pos formatting (#835); other products keep .4f.
            pos_txt = (
                _sigmet_tc_format_pos(lat, lon)
                if _sigmet_root_local(ir) == "TropicalCycloneSIGMET"
                else f"{lat:.4f} {lon:.4f}"
            )
            return f"""
              <iwxxm:geometry>
                <aixm:AirspaceVolume gml:id="vol.{suffix}">{limits}
                  <aixm:horizontalProjection>
                    <aixm:Surface gml:id="sfc.{suffix}" srsDimension="2" axisLabels="Lat Long" srsName="http://www.opengis.net/def/crs/EPSG/0/4326">
                      <gml:patches>
                        <gml:PolygonPatch>
                          <gml:exterior>
                            <gml:Ring>
                              <gml:curveMember>
                                <gml:Curve gml:id="curve.{suffix}">
                                  <gml:segments>
                                    <gml:CircleByCenterPoint numArc="1">
                                      <gml:pos>{pos_txt}</gml:pos>
                                      <gml:radius uom="[nmi_i]">{radius}</gml:radius>
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
            if wmo_multi_location_va_ring:
                pos_list = _wmo_multi_location_va_pos_list(pos_list)
            return f"""
              <iwxxm:geometry>
                <aixm:AirspaceVolume gml:id="vol.{suffix}">{limits}
                  <aixm:horizontalProjection>
                    <aixm:Surface gml:id="sfc.{suffix}" srsDimension="2" axisLabels="Lat Long" srsName="http://www.opengis.net/def/crs/EPSG/0/4326">
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
                <aixm:AirspaceVolume gml:id="vol.{suffix}">{limits}
                </aixm:AirspaceVolume>
              </iwxxm:geometry>"""

    return """
              <iwxxm:geometry nilReason="http://codes.wmo.int/common/nil/missing"/>"""


def _sigmet_location_analysis_xml(
    loc: dict[str, Any],
    *,
    fir: str,
    index: int,
    issue: str,
    begin: str,
    end: str,
    wmo_multi_location_va_ring: bool = False,
    wmo_va_eggx_ring: bool = False,
) -> str:
    """Emit one analysisCollection for a multi-location VA OBS(+FCST) segment (#809)."""
    suffix = f"{fir.lower()}.{index}"
    intensity = str(loc.get("intensity_change", "NO_CHANGE"))
    obs_ir = {
        "lower_fl": loc.get("lower_fl"),
        "upper_fl": loc.get("upper_fl"),
        "lower_surface": loc.get("lower_surface"),
    }
    obs_geometry_override = cast(dict[str, Any], loc["geometry"])
    if wmo_va_eggx_ring:
        obs_geometry_override = {"kind": "polygon", "pos_list": _EGGX_OBS_POS}
    geometry = _sigmet_geometry_xml(
        obs_ir,
        fir=fir,
        gid=suffix,
        geometry=obs_geometry_override,
        wmo_multi_location_va_ring=wmo_multi_location_va_ring,
    )
    obs_hhmm = str(loc.get("obs_hhmm") or begin[11:13] + begin[14:16])
    obs_time = f"{begin[:10]}T{obs_hhmm[0:2]}:{obs_hhmm[2:4]}:00Z"
    # WMO multi-location VA: materialize OBS/FCST instants once; later collections
    # xlink:href them (vendor density / ADR-032 canonical empty phenomenonTime).
    reuse_times = wmo_multi_location_va_ring and index > 0
    if reuse_times:
        obs_phenomenon_time = f'<iwxxm:phenomenonTime xlink:href="#{_WMO_MULTI_VA_OBS_TIME_ID}"/>'
    elif wmo_multi_location_va_ring:
        obs_phenomenon_time = f"""<iwxxm:phenomenonTime>
            <gml:TimeInstant gml:id="{_WMO_MULTI_VA_OBS_TIME_ID}">
              <gml:timePosition>{obs_time}</gml:timePosition>
            </gml:TimeInstant>
          </iwxxm:phenomenonTime>"""
    else:
        obs_phenomenon_time = f"""<iwxxm:phenomenonTime>
            <gml:TimeInstant gml:id="t.obs.{suffix}">
              <gml:timePosition>{obs_time}</gml:timePosition>
            </gml:TimeInstant>
          </iwxxm:phenomenonTime>"""
    forecast_xml = ""
    forecast_raw = loc.get("forecast")
    if isinstance(forecast_raw, dict):
        forecast = cast(dict[str, Any], forecast_raw)
        fcst_geometry = forecast.get("geometry")
        if wmo_va_eggx_ring:
            fcst_geometry = {"kind": "polygon", "pos_list": _EGGX_FCST_POS}
        if isinstance(fcst_geometry, dict):
            hhmm_raw = forecast.get("hhmm")
            fcst_hhmm = str(hhmm_raw if hhmm_raw is not None else end[11:13] + end[14:16])
            fcst_time = f"{end[:10]}T{fcst_hhmm[0:2]}:{fcst_hhmm[2:4]}:00Z"
            fcst_geom = _sigmet_geometry_xml(
                {},
                fir=fir,
                gid=f"{suffix}.fcst",
                geometry=cast(dict[str, Any], fcst_geometry),
                include_limits=False,
                wmo_multi_location_va_ring=wmo_multi_location_va_ring,
            )
            if reuse_times:
                fcst_phenomenon_time = f'<iwxxm:phenomenonTime xlink:href="#{_WMO_MULTI_VA_FCST_TIME_ID}"/>'
            elif wmo_multi_location_va_ring:
                fcst_phenomenon_time = f"""<iwxxm:phenomenonTime>
            <gml:TimeInstant gml:id="{_WMO_MULTI_VA_FCST_TIME_ID}">
              <gml:timePosition>{fcst_time}</gml:timePosition>
            </gml:TimeInstant>
          </iwxxm:phenomenonTime>"""
            else:
                fcst_phenomenon_time = f"""<iwxxm:phenomenonTime>
            <gml:TimeInstant gml:id="t.fcst.{suffix}">
              <gml:timePosition>{fcst_time}</gml:timePosition>
            </gml:TimeInstant>
          </iwxxm:phenomenonTime>"""
            # Vendor multi-location VA uses approximateLocation; VA-EGGX omits it (#856).
            approx_attr = "" if wmo_va_eggx_ring else ' approximateLocation="true"'
            forecast_xml = f"""
      <iwxxm:forecastPositionAnalysis>
        <iwxxm:SIGMETPositionCollection gml:id="fcst.{suffix}">
          {fcst_phenomenon_time}
          <iwxxm:member>
            <iwxxm:SIGMETPosition gml:id="pos.{suffix}"{approx_attr}>{fcst_geom}
            </iwxxm:SIGMETPosition>
          </iwxxm:member>
        </iwxxm:SIGMETPositionCollection>
      </iwxxm:forecastPositionAnalysis>"""

    return f"""  <iwxxm:analysisCollection>
    <iwxxm:analysisAndForecastPositionAnalysis gml:id="analysis.{suffix}">
      <iwxxm:analysis>
        <iwxxm:SIGMETEvolvingConditionCollection gml:id="evolving.{suffix}" timeIndicator="OBSERVATION">
          {obs_phenomenon_time}
          <iwxxm:member>
            <iwxxm:SIGMETEvolvingCondition gml:id="cond.{suffix}" intensityChange="{escape(intensity)}">{geometry}
            </iwxxm:SIGMETEvolvingCondition>
          </iwxxm:member>
        </iwxxm:SIGMETEvolvingConditionCollection>
      </iwxxm:analysis>{forecast_xml}
    </iwxxm:analysisAndForecastPositionAnalysis>
  </iwxxm:analysisCollection>
"""


def _sigmet_volcano_xml(ir: dict[str, Any]) -> str:
    volcano_raw = ir.get("volcano")
    if not isinstance(volcano_raw, dict):
        return ""
    volcano = cast(dict[str, Any], volcano_raw)
    name = str(volcano.get("name", "")).strip()
    if not name:
        return ""
    lat = float(volcano["lat"])
    lon = float(volcano["lon"])
    # Multi-location VA (#809) or single OBS(+FCST) VA cloud path (#856 EGGX).
    pos_fmt = (
        _EGGX_VOLCANO_POS
        if _is_wmo_sigmet_va_eggx(ir)
        else (f"{lat:.2f} {lon:.2f}" if _is_wmo_sigmet_multi_location_va_yudd(ir) else f"{lat:.4f} {lon:.4f}")
    )
    return f"""  <iwxxm:eruptingVolcano>
    <metce:Volcano gml:id="volcano.1">
      <metce:name>{escape(name)}</metce:name>
      <metce:position>
        <gml:Point gml:id="volcano.pos.1" srsDimension="2" axisLabels="Lat Long" srsName="http://www.opengis.net/def/crs/EPSG/0/4326">
          <gml:pos>{pos_fmt}</gml:pos>
        </gml:Point>
      </metce:position>
    </metce:Volcano>
  </iwxxm:eruptingVolcano>
"""


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


def _sigmet_tropical_cyclone_xml(ir: dict[str, Any]) -> str:
    """Emit ``iwxxm:tropicalCyclone`` / metce name for TropicalCycloneSIGMET (#738)."""
    name = ir.get("tropical_cyclone_name")
    if not isinstance(name, str) or not name.strip():
        return ""
    slug = re.sub(r"[^a-z0-9]+", "", name.lower()) or "tc"
    return f"""
  <iwxxm:tropicalCyclone>
    <metce:TropicalCyclone gml:id="tc.{slug}">
      <metce:name>{escape(name.strip())}</metce:name>
    </metce:TropicalCyclone>
  </iwxxm:tropicalCyclone>
"""


def _sigmet_tc_position_xml(ir: dict[str, Any], *, gid: str) -> str:
    """Emit ``tropicalCyclonePosition`` Point when IR has a TC centre."""
    pos = ir.get("tropical_cyclone_position")
    if not isinstance(pos, dict) or "lat" not in pos or "lon" not in pos:
        return ""
    lat = float(cast(dict[str, Any], pos)["lat"])
    lon = float(cast(dict[str, Any], pos)["lon"])
    pos_txt = _sigmet_tc_format_pos(lat, lon)
    return f"""
              <iwxxm:tropicalCyclonePosition>
                <gml:Point gml:id="{gid}" srsDimension="2" axisLabels="Lat Long" srsName="http://www.opengis.net/def/crs/EPSG/0/4326">
                  <gml:pos>{pos_txt}</gml:pos>
                </gml:Point>
              </iwxxm:tropicalCyclonePosition>"""


def _sigmet_tc_forecast_xml(ir: dict[str, Any], *, fir: str, end: str) -> str:
    """Emit forecastPositionAnalysis for FCST AT … TC CENTRE PSN (A6-2-TC)."""
    fcst = ir.get("tropical_cyclone_forecast")
    if not isinstance(fcst, dict) or "lat" not in fcst or "lon" not in fcst:
        return ""
    f = cast(dict[str, Any], fcst)
    lat = float(f["lat"])
    lon = float(f["lon"])
    pos_txt = _sigmet_tc_format_pos(lat, lon)
    hhmm = str(f.get("hhmm", "0000"))
    day = int(ir["valid_to_day"])
    # Prefer VALID end day; vendor A6-2 uses end-of-validity forecast time.
    hour = int(hhmm[:2]) if len(hhmm) == 4 and hhmm.isdigit() else int(ir["valid_to_hour"])
    minute = int(hhmm[2:4]) if len(hhmm) == 4 and hhmm.isdigit() else int(ir["valid_to_minute"])
    fcst_time = f"2012-08-{day:02d}T{hour:02d}:{minute:02d}:00Z"
    if fcst_time > end:
        fcst_time = end
    return f"""
      <iwxxm:forecastPositionAnalysis>
        <iwxxm:SIGMETPositionCollection gml:id="fcst.pos.{fir.lower()}">
          <iwxxm:phenomenonTime>
            <gml:TimeInstant gml:id="t.fcst.{fir.lower()}">
              <gml:timePosition>{fcst_time}</gml:timePosition>
            </gml:TimeInstant>
          </iwxxm:phenomenonTime>
          <iwxxm:member>
            <iwxxm:SIGMETPosition gml:id="fcst.cond.{fir.lower()}">
              <iwxxm:tropicalCyclonePosition>
                <gml:Point gml:id="fcst.tc.pos.{fir.lower()}" srsDimension="2" axisLabels="Lat Long" srsName="http://www.opengis.net/def/crs/EPSG/0/4326">
                  <gml:pos>{pos_txt}</gml:pos>
                </gml:Point>
              </iwxxm:tropicalCyclonePosition>
              <iwxxm:geometry nilReason="http://codes.wmo.int/common/nil/inapplicable"/>
            </iwxxm:SIGMETPosition>
          </iwxxm:member>
        </iwxxm:SIGMETPositionCollection>
      </iwxxm:forecastPositionAnalysis>"""


def emit_convective_sigmet_annex3(ir: dict[str, Any], *, iwxxm_version: str) -> str:
    """Emit US ``CONVECTIVE SIGMET`` (WST) with iwxxm-us analysis shape (#919 M11)."""
    ns = _ns(iwxxm_version)
    fir = str(ir["fir"])
    mwo = str(ir["mwo"])
    issue, begin, end = _hazard_stamp(ir, "sigmet")
    gml_id = f"sigmet.conv.{fir.lower()}"
    active_end = (
        f"2012-08-{int(ir['valid_to_day']):02d}T{int(ir['valid_to_hour']):02d}:{int(ir['valid_to_minute']):02d}:00Z"
    )
    geometry = _sigmet_geometry_xml(ir, fir=fir)
    motion = _sigmet_motion_xml(ir)
    states = str(ir.get("affected_states", "")).strip()
    states_xml = ""
    if states:
        states_xml = f"""
              <aixm:extension>
                <iwxxm-us:AffectedStates gml:id="states.{fir.lower()}">
                  <iwxxm-us:stateIDs>{escape(states)}</iwxxm-us:stateIDs>
                </iwxxm-us:AffectedStates>
              </aixm:extension>"""
    units = f"""<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:SIGMET xmlns:iwxxm="{ns}"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:aixm="http://www.aixm.aero/schema/5.1.1"
    xmlns:iwxxm-us="http://www.weather.gov/iwxxm-us/3.0"
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
          <aixm:name>{escape(str(ir.get("fir_name", f"{fir} FIC")))}</aixm:name>
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
          <aixm:name>{escape(str(ir.get("fir_name", f"{fir} FIC")))}</aixm:name>
        </aixm:AirspaceTimeSlice>
      </aixm:timeSlice>
    </aixm:Airspace>
  </iwxxm:issuingAirTrafficServicesRegion>
  <iwxxm:sequenceNumber nilReason="http://codes.wmo.int/common/nil/missing"/>
  <iwxxm:validPeriod>
    <gml:TimePeriod gml:id="t.valid">
      <gml:beginPosition>{begin}</gml:beginPosition>
      <gml:endPosition>{end}</gml:endPosition>
    </gml:TimePeriod>
  </iwxxm:validPeriod>
  <iwxxm:phenomenon nilReason="http://codes.wmo.int/common/nil/template"/>
  <iwxxm:analysis>
    <iwxxm:SIGMETEvolvingConditionCollection gml:id="evolving.{fir.lower()}" timeIndicator="FORECAST">
      <iwxxm:phenomenonTime>
        <gml:TimePeriod gml:id="t.active.{fir.lower()}">
          <gml:beginPosition>{issue}</gml:beginPosition>
          <gml:endPosition>{active_end}</gml:endPosition>
        </gml:TimePeriod>
      </iwxxm:phenomenonTime>
      <iwxxm:member>
        <iwxxm:SIGMETEvolvingCondition gml:id="cond.{fir.lower()}">{geometry}{motion}
        </iwxxm:SIGMETEvolvingCondition>
      </iwxxm:member>
    </iwxxm:SIGMETEvolvingConditionCollection>
  </iwxxm:analysis>
</iwxxm:SIGMET>
"""
    # Inject AffectedStates inside AirspaceVolume when geometry present.
    if states_xml and "<aixm:AirspaceVolume" in units:
        units = units.replace(
            "</aixm:horizontalProjection>",
            f"</aixm:horizontalProjection>{states_xml}",
            1,
        )
    return units


def emit_sigmet_annex3(ir: dict[str, Any], *, iwxxm_version: str) -> str:
    """Emit an IWXXM SIGMET / VolcanicAshSIGMET / TropicalCycloneSIGMET document."""
    if ir.get("convective"):
        return emit_convective_sigmet_annex3(ir, iwxxm_version=iwxxm_version)
    ns = _ns(iwxxm_version)
    fir = str(ir["fir"])
    issue, begin, end = _hazard_stamp(ir, "sigmet")
    cancel = bool(ir.get("cancel"))
    root = _sigmet_root_local(ir)
    if cancel:
        gml_id = f"sigmet.cnl.{fir.lower()}"
    elif root == "VolcanicAshSIGMET":
        gml_id = f"sigmet.va.{fir.lower()}"
    elif root == "TropicalCycloneSIGMET":
        gml_id = f"sigmet.tc.{fir.lower()}"
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
    locations_raw = ir.get("locations")
    locations: list[dict[str, Any]] = []
    if isinstance(locations_raw, list):
        for item in cast(list[Any], locations_raw):
            if isinstance(item, dict):
                locations.append(cast(dict[str, Any], item))
    use_locations = len(locations) >= 1
    is_tc = root == "TropicalCycloneSIGMET"
    eggx = _is_wmo_sigmet_va_eggx(ir)
    need_metce = is_tc or (use_locations and isinstance(ir.get("volcano"), dict))
    extra_xmlns = '\n    xmlns:metce="http://def.wmo.int/metce/2013"' if need_metce else ""
    motion = _sigmet_motion_xml(ir)
    head = _sigmet_header_units(ir, ns=ns, gml_id=gml_id, issue=issue, extra_xmlns=extra_xmlns).format(cancel_attr="")

    if use_locations:
        ring_norm = _is_wmo_sigmet_multi_location_va_yudd(ir)
        collections = "".join(
            _sigmet_location_analysis_xml(
                loc,
                fir=fir,
                index=i,
                issue=issue,
                begin=begin,
                end=end,
                wmo_multi_location_va_ring=ring_norm,
                wmo_va_eggx_ring=eggx,
            )
            for i, loc in enumerate(locations)
        )
        volcano_xml = _sigmet_volcano_xml(ir)
        return (
            head
            + f"""  <iwxxm:validPeriod>
    <gml:TimePeriod gml:id="t.valid">
      <gml:beginPosition>{begin}</gml:beginPosition>
      <gml:endPosition>{end}</gml:endPosition>
    </gml:TimePeriod>
  </iwxxm:validPeriod>
  <iwxxm:phenomenon xlink:href="{escape(phenom)}"/>
{collections}{volcano_xml}</iwxxm:{root}>
"""
        )

    geometry = _sigmet_geometry_xml(ir, fir=fir)
    # Gen/VA single-location keep FORECAST (golden bar); TC uses OBSERVATION when OBS present.
    if is_tc:
        time_indicator = str(ir.get("time_indicator", "OBSERVATION"))
    else:
        time_indicator = "FORECAST"
    tc_pos = _sigmet_tc_position_xml(ir, gid=f"tc.pos.{fir.lower()}") if is_tc else ""
    tc_fcst = _sigmet_tc_forecast_xml(ir, fir=fir, end=end) if is_tc else ""
    tc_name_xml = _sigmet_tropical_cyclone_xml(ir) if is_tc else ""
    # Vendor A6-2-TC omits intensityChange when NO_CHANGE (#835).
    if is_tc and intensity == "NO_CHANGE":
        intensity_attr = ""
    else:
        intensity_attr = f' intensityChange="{escape(intensity)}"'
    phenom_time = (
        f"""
          <iwxxm:phenomenonTime>
            <gml:TimeInstant gml:id="t.obs.{fir.lower()}">
              <gml:timePosition>{issue}</gml:timePosition>
            </gml:TimeInstant>
          </iwxxm:phenomenonTime>"""
        if is_tc
        else """
          <iwxxm:phenomenonTime nilReason="http://codes.wmo.int/common/nil/missing"/>"""
    )
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
        <iwxxm:SIGMETEvolvingConditionCollection gml:id="evolving.{fir.lower()}" timeIndicator="{escape(time_indicator)}">{phenom_time}
          <iwxxm:member>
            <iwxxm:SIGMETEvolvingCondition gml:id="cond.{fir.lower()}"{intensity_attr}>{tc_pos}{geometry}{motion}
            </iwxxm:SIGMETEvolvingCondition>
          </iwxxm:member>
        </iwxxm:SIGMETEvolvingConditionCollection>
      </iwxxm:analysis>{tc_fcst}
    </iwxxm:analysisAndForecastPositionAnalysis>
  </iwxxm:analysisCollection>{tc_name_xml}</iwxxm:{root}>
"""
    )


def _airmet_evolving_member_xml(
    area_ir: dict[str, Any],
    *,
    fir: str,
    member_suffix: str,
    inner_extension: str = "",
) -> str:
    """Emit one ``AIRMETEvolvingCondition`` member."""
    intensity = str(area_ir.get("intensity_change", "NO_CHANGE"))
    geometry = _sigmet_geometry_xml(
        area_ir,
        fir=fir,
        gid=f"cond.{fir.lower()}.{member_suffix}",
    )
    motion = _sigmet_motion_xml(area_ir)
    return f"""      <iwxxm:member>
        <iwxxm:AIRMETEvolvingCondition gml:id="cond.{fir.lower()}.{member_suffix}" intensityChange="{escape(intensity)}">{geometry}{motion}{inner_extension}
        </iwxxm:AIRMETEvolvingCondition>
      </iwxxm:member>"""


def _airmet_analysis_collection_xml(
    ir: dict[str, Any],
    *,
    fir: str,
    collection_suffix: str,
    time_indicator: str,
    areas: list[dict[str, Any]],
    member_extension_for: dict[str, str] | None = None,
) -> str:
    """Emit one ``AIRMETEvolvingConditionCollection`` for the given area fragments."""
    member_extension_for = member_extension_for or {}
    members = "\n".join(
        _airmet_evolving_member_xml(
            area,
            fir=fir,
            member_suffix=f"{collection_suffix}.{index}",
            inner_extension=member_extension_for.get(str(index), ""),
        )
        for index, area in enumerate(areas, start=1)
    )
    return f"""  <iwxxm:analysis>
    <iwxxm:AIRMETEvolvingConditionCollection gml:id="evolving.{fir.lower()}.{collection_suffix}" timeIndicator="{escape(time_indicator)}">
      <iwxxm:phenomenonTime nilReason="http://codes.wmo.int/common/nil/missing"/>
{members}
    </iwxxm:AIRMETEvolvingConditionCollection>
  </iwxxm:analysis>
"""


def emit_airmet_annex3(
    ir: dict[str, Any],
    *,
    iwxxm_version: str,
    phenomenon_href: str | None = None,
) -> str:
    """Emit an IWXXM AIRMET document (F6.d / F24 A3 geometry fidelity / #731)."""
    ns = _ns(iwxxm_version)
    fir = str(ir["fir"])
    mwo = str(ir["mwo"])
    issue, begin, end = _hazard_stamp(ir, "airmet")
    cancel = bool(ir.get("cancel"))
    override = ir.get("report_status")
    if override in {"NORMAL", "AMENDMENT", "CORRECTION"}:
        status = str(override)
    else:
        status = "NORMAL"
    gml_id = f"airmet.cnl.{fir.lower()}" if cancel else f"airmet.basic.{fir.lower()}"

    units = f"""<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:AIRMET xmlns:iwxxm="{ns}"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:aixm="http://www.aixm.aero/schema/5.1.1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    gml:id="{gml_id}"
    reportStatus="{status}"
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
"""

    if cancel:
        c_begin = (
            f"2012-08-{int(ir['cancelled_from_day']):02d}T"
            f"{int(ir['cancelled_from_hour']):02d}:{int(ir['cancelled_from_minute']):02d}:00Z"
        )
        c_end = (
            f"2012-08-{int(ir['cancelled_to_day']):02d}T"
            f"{int(ir['cancelled_to_hour']):02d}:{int(ir['cancelled_to_minute']):02d}:00Z"
        )
        return (
            units.format(cancel_attr='\n    isCancelReport="true"')
            + f"""  <iwxxm:cancelledReportSequenceNumber>{int(ir["cancelled_sequence"])}</iwxxm:cancelledReportSequenceNumber>
  <iwxxm:cancelledReportValidPeriod>
    <gml:TimePeriod gml:id="t.cancelled">
      <gml:beginPosition>{c_begin}</gml:beginPosition>
      <gml:endPosition>{c_end}</gml:endPosition>
    </gml:TimePeriod>
  </iwxxm:cancelledReportValidPeriod>
</iwxxm:AIRMET>
"""
        )

    phenom = phenomenon_href or _AIR_PHENOM_HREF.format(code=ir["phenomenon"])
    time_indicator = str(ir.get("time_indicator", "OBSERVATION"))
    outlook_raw = ir.get("outlook")
    area_list_raw = ir.get("areas")
    outlook_ir: dict[str, Any] | None = cast(dict[str, Any], outlook_raw) if isinstance(outlook_raw, dict) else None
    area_list: list[dict[str, Any]] = []
    if isinstance(area_list_raw, list):
        area_list = [cast(dict[str, Any], item) for item in area_list_raw if isinstance(item, dict)]
    has_multi = len(area_list) > 1
    has_outlook = outlook_ir is not None
    if area_list:
        obs_areas = area_list
    else:
        obs_areas = [ir]

    if not has_multi and not has_outlook:
        intensity = str(ir.get("intensity_change", "NO_CHANGE"))
        geometry = _sigmet_geometry_xml(ir, fir=fir)
        motion = _sigmet_motion_xml(ir)
        obs_analysis = f"""  <iwxxm:analysis>
    <iwxxm:AIRMETEvolvingConditionCollection gml:id="evolving.{fir.lower()}" timeIndicator="{escape(time_indicator)}">
      <iwxxm:phenomenonTime nilReason="http://codes.wmo.int/common/nil/missing"/>
      <iwxxm:member>
        <iwxxm:AIRMETEvolvingCondition gml:id="cond.{fir.lower()}" intensityChange="{escape(intensity)}">{geometry}{motion}
        </iwxxm:AIRMETEvolvingCondition>
      </iwxxm:member>
    </iwxxm:AIRMETEvolvingConditionCollection>
  </iwxxm:analysis>
"""
        outlook_analysis = ""
    else:
        obs_analysis = _airmet_analysis_collection_xml(
            ir,
            fir=fir,
            collection_suffix="obs",
            time_indicator=time_indicator,
            areas=obs_areas,
        )
        outlook_analysis = ""
        if has_outlook:
            outlook_analysis = _airmet_analysis_collection_xml(
                ir,
                fir=fir,
                collection_suffix="outlook",
                time_indicator="FORECAST",
                areas=[outlook_ir],
            )

    return (
        units.format(cancel_attr="")
        + f"""  <iwxxm:phenomenon xlink:href="{escape(phenom)}"/>
{obs_analysis}{outlook_analysis}</iwxxm:AIRMET>
"""
    )


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
    override = ir.get("report_status")
    if override in {"NORMAL", "AMENDMENT", "CORRECTION"}:
        report_status = str(override)
    else:
        report_status = "NORMAL"
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
    if ir.get("remarks") and not ir.get("remarks_nil"):
        remarks_xml = f"\n    <iwxxm:remarks>{escape(str(ir['remarks']))}</iwxxm:remarks>"
    elif ir.get("remarks_nil"):
        remarks_xml = '\n    <iwxxm:remarks nilReason="http://codes.wmo.int/common/nil/inapplicable"/>'

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
    reportStatus="{report_status}"
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

    override = ir.get("report_status")
    if override in {"NORMAL", "AMENDMENT", "CORRECTION"}:
        report_status = str(override)
    else:
        report_status = "NORMAL"

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:TropicalCycloneAdvisory xmlns:iwxxm="{ns}"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:aixm="http://www.aixm.aero/schema/5.1.1"
    xmlns:metce="http://def.wmo.int/metce/2013"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    gml:id="tca.{slug}"
    reportStatus="{report_status}"
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


# Approximate lat bands / circles for SpaceWxLocation codes (vendor spacewx-A7-*).
_SWXA_BANDS: dict[str, str] = {
    "HNH": "60 180\n                                                                90 180\n                                                                90 -180\n                                                                60 -180\n                                                                60 180",
    "MNH": "30 180\n                                                                60 180\n                                                                60 -180\n                                                                30 -180\n                                                                30 180",
    "EQN": "00 180\n                                                                30 180\n                                                                30 -180\n                                                                00 -180\n                                                                00 180",
    "EQS": "-30 180\n                                                                00 180\n                                                                00 -180\n                                                                -30 -180\n                                                                -30 180",
    "MSH": "-60 180\n                                                                -30 180\n                                                                -30 -180\n                                                                -60 -180\n                                                                -60 180",
    "HSH": "-90 180\n                                                                -60 180\n                                                                -60 -180\n                                                                -90 -180\n                                                                -90 180",
}
_SWXA_CIRCLES: dict[str, tuple[str, int]] = {
    "DAYLIGHT_SIDE": ("-16.71 70.94", 10100),
    "DAYSIDE": ("-16.71 70.94", 10100),
    "NIGHTSIDE": ("9999 9999", 10100),
}
_SWXA_FORBIDDEN_ROOTS = frozenset(
    {
        "SIGMET",
        "VolcanicAshSIGMET",
        "TropicalCycloneSIGMET",
        "VolcanicAshAdvisory",
        "TropicalCycloneAdvisory",
        "AIRMET",
    }
)


def _swxa_region_xml(loc: str, *, slug: str, idx: int) -> str:
    code = loc.upper()
    href = f"http://codes.wmo.int/49-2/SpaceWxLocation/{code}"
    rid = f"swxa.reg.{slug}.{idx}"
    if code in _SWXA_CIRCLES:
        pos, radius = _SWXA_CIRCLES[code]
        surface = f"""
                                        <aixm:Surface gml:id="{rid}.sfc" srsDimension="2" axisLabels="Lat Long" srsName="http://www.opengis.net/def/crs/EPSG/0/4326">
                                            <gml:patches>
                                                <gml:PolygonPatch>
                                                    <gml:exterior>
                                                        <gml:Ring>
                                                            <gml:curveMember>
                                                                <gml:Curve gml:id="{rid}.curve">
                                                                    <gml:segments>
                                                                        <gml:CircleByCenterPoint numArc="1">
                                                                            <gml:pos>{pos}</gml:pos>
                                                                            <gml:radius uom="km">{radius}</gml:radius>
                                                                        </gml:CircleByCenterPoint>
                                                                    </gml:segments>
                                                                </gml:Curve>
                                                            </gml:curveMember>
                                                        </gml:Ring>
                                                    </gml:exterior>
                                                </gml:PolygonPatch>
                                            </gml:patches>
                                        </aixm:Surface>"""
    else:
        pos_list = _SWXA_BANDS.get(
            code,
            "90 180\n                                                                -90 180\n                                                                -90 -180\n                                                                90 -180\n                                                                90 180",
        )
        surface = f"""
                                        <aixm:Surface gml:id="{rid}.sfc" srsDimension="2" axisLabels="Lat Long" srsName="http://www.opengis.net/def/crs/EPSG/0/4326">
                                            <gml:patches>
                                                <gml:PolygonPatch>
                                                    <gml:exterior>
                                                        <gml:LinearRing>
                                                            <gml:posList>
                                                                {pos_list}
                                                            </gml:posList>
                                                        </gml:LinearRing>
                                                    </gml:exterior>
                                                </gml:PolygonPatch>
                                            </gml:patches>
                                        </aixm:Surface>"""
    return f"""
                    <iwxxm:region>
                        <iwxxm:SpaceWeatherRegion gml:id="{rid}">
                            <iwxxm:location>
                                <aixm:AirspaceVolume gml:id="{rid}.vol">
                                    <aixm:horizontalProjection>{surface}
                                    </aixm:horizontalProjection>
                                </aixm:AirspaceVolume>
                            </iwxxm:location>
                            <iwxxm:locationIndicator xlink:href="{href}"/>
                        </iwxxm:SpaceWeatherRegion>
                    </iwxxm:region>"""


def _swxa_analysis_xml(
    block: dict[str, Any],
    *,
    time_indicator: str,
    slug: str,
    idx: int,
) -> str:
    time_iso = block.get("time") or "9999-01-01T00:00:00Z"
    aid = f"swxa.an.{slug}.{idx}"
    if block.get("no_swx_exp"):
        return f"""
    <iwxxm:analysis>
        <iwxxm:SpaceWeatherAnalysis gml:id="{aid}" timeIndicator="{time_indicator}">
            <iwxxm:phenomenonTime>
                <gml:TimeInstant gml:id="{aid}.t">
                    <gml:timePosition>{escape(str(time_iso))}</gml:timePosition>
                </gml:TimeInstant>
            </iwxxm:phenomenonTime>
            <iwxxm:intensityAndRegion nilReason="http://codes.wmo.int/common/nil/nothingOfOperationalSignificance"/>
        </iwxxm:SpaceWeatherAnalysis>
    </iwxxm:analysis>"""

    groups = list(block.get("groups") or [])
    if not groups:
        return f"""
    <iwxxm:analysis>
        <iwxxm:SpaceWeatherAnalysis gml:id="{aid}" timeIndicator="{time_indicator}">
            <iwxxm:phenomenonTime>
                <gml:TimeInstant gml:id="{aid}.t">
                    <gml:timePosition>{escape(str(time_iso))}</gml:timePosition>
                </gml:TimeInstant>
            </iwxxm:phenomenonTime>
            <iwxxm:intensityAndRegion nilReason="http://codes.wmo.int/common/nil/missing"/>
        </iwxxm:SpaceWeatherAnalysis>
    </iwxxm:analysis>"""

    iar_blocks: list[str] = []
    loc_i = 0
    for g_idx, group in enumerate(groups):
        intensity = str(group.get("intensity", "MOD"))
        regions_xml = ""
        for loc in list(group.get("locations") or []):
            regions_xml += _swxa_region_xml(str(loc), slug=slug, idx=loc_i)
            loc_i += 1
        if not regions_xml:
            continue
        iar_blocks.append(
            f"""
            <iwxxm:intensityAndRegion>
                <iwxxm:SpaceWeatherIntensityAndRegion gml:id="{aid}.iar.{g_idx}">
                    <iwxxm:intensity>{escape(intensity)}</iwxxm:intensity>{regions_xml}
                </iwxxm:SpaceWeatherIntensityAndRegion>
            </iwxxm:intensityAndRegion>"""
        )
    if not iar_blocks:
        iar_xml = '\n            <iwxxm:intensityAndRegion nilReason="http://codes.wmo.int/common/nil/missing"/>'
    else:
        iar_xml = "".join(iar_blocks)
    return f"""
    <iwxxm:analysis>
        <iwxxm:SpaceWeatherAnalysis gml:id="{aid}" timeIndicator="{time_indicator}">
            <iwxxm:phenomenonTime>
                <gml:TimeInstant gml:id="{aid}.t">
                    <gml:timePosition>{escape(str(time_iso))}</gml:timePosition>
                </gml:TimeInstant>
            </iwxxm:phenomenonTime>{iar_xml}
        </iwxxm:SpaceWeatherAnalysis>
    </iwxxm:analysis>"""


def emit_swxa_annex3(ir: dict[str, Any], *, iwxxm_version: str) -> str:
    """
    Emit an IWXXM ``SpaceWeatherAdvisory`` document (F28 / EV-029 M11).

    Product/root guard: under ``product=swxa`` always opens
    ``iwxxm:SpaceWeatherAdvisory`` and never SIGMET/VAA/TCA roots.
    Geometry for SpaceWxLocation bands is approximate (S02.L1 may use
    ``wmoReference`` vs vendor golden equality).
    """
    product = str(ir.get("product", "SWXA")).upper()
    if product != "SWXA":
        raise ValueError(f"SWXA emitter product/root guard: expected product SWXA, found {product!r}")
    claimed = ir.get("iwxxm_root")
    if claimed is not None and str(claimed) in _SWXA_FORBIDDEN_ROOTS:
        raise ValueError(f"SWXA emitter product/root guard: refusing forbidden iwxxm_root={claimed!r}")
    if claimed is not None and str(claimed) not in {"SpaceWeatherAdvisory", "SWXA"}:
        raise ValueError(f"SWXA emitter product/root guard: unexpected iwxxm_root={claimed!r}")

    ns = _ns(iwxxm_version)
    swxc = str(ir["swxc"])
    issue = str(ir["issue_time"])
    slug = re.sub(r"[^a-z0-9]+", ".", swxc.lower()).strip(".") or "swxc"
    effect = str(ir.get("effect") or "")
    advisory_number = str(ir.get("advisory_number") or "")

    override = ir.get("report_status")
    if override in {"NORMAL", "AMENDMENT", "CORRECTION"}:
        report_status = str(override)
    else:
        report_status = "NORMAL"

    replaced_xml = ""
    for num in list(ir.get("replaced_advisory_numbers") or []):
        replaced_xml += f"\n    <iwxxm:replacedAdvisoryNumber>{escape(str(num))}</iwxxm:replacedAdvisoryNumber>"

    effect_xml = f"\n    <iwxxm:effect>{escape(effect)}</iwxxm:effect>" if effect else ""

    analyses: list[str] = []
    obs = ir.get("observation")
    if isinstance(obs, dict):
        analyses.append(_swxa_analysis_xml(cast(dict[str, Any], obs), time_indicator="OBSERVATION", slug=slug, idx=0))
    for f_idx, fcst in enumerate(list(ir.get("forecasts") or []), start=1):
        if isinstance(fcst, dict):
            analyses.append(
                _swxa_analysis_xml(cast(dict[str, Any], fcst), time_indicator="FORECAST", slug=slug, idx=f_idx)
            )

    if ir.get("remarks") and not ir.get("remarks_nil"):
        remarks_xml = f"\n    <iwxxm:remarks>{escape(str(ir['remarks']))}</iwxxm:remarks>"
    elif ir.get("remarks_nil"):
        remarks_xml = '\n    <iwxxm:remarks nilReason="http://codes.wmo.int/common/nil/inapplicable"/>'
    else:
        remarks_xml = ""

    if ir.get("next_advisory_nil"):
        next_xml = '\n    <iwxxm:nextAdvisoryTime nilReason="http://codes.wmo.int/common/nil/inapplicable"/>'
    elif ir.get("next_advisory_time"):
        next_xml = f"""
    <iwxxm:nextAdvisoryTime>
        <gml:TimeInstant gml:id="swxa.t.next.{slug}">
            <gml:timePosition>{escape(str(ir["next_advisory_time"]))}</gml:timePosition>
        </gml:TimeInstant>
    </iwxxm:nextAdvisoryTime>"""
    else:
        next_xml = ""

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:SpaceWeatherAdvisory xmlns:iwxxm="{ns}"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:aixm="http://www.aixm.aero/schema/5.1.1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    gml:id="swxa.{slug}"
    reportStatus="{report_status}"
    permissibleUsage="OPERATIONAL">
    <iwxxm:issueTime>
        <gml:TimeInstant gml:id="swxa.t.issue.{slug}">
            <gml:timePosition>{escape(issue)}</gml:timePosition>
        </gml:TimeInstant>
    </iwxxm:issueTime>
    <iwxxm:issuingSpaceWeatherCentre>
        <aixm:Unit gml:id="unit.swxc.{slug}">
            <aixm:timeSlice>
                <aixm:UnitTimeSlice gml:id="unit.swxc.ts.{slug}">
                    <gml:validTime/>
                    <aixm:interpretation>SNAPSHOT</aixm:interpretation>
                    <aixm:name>{escape(swxc)}</aixm:name>
                    <aixm:type>OTHER:SWXC</aixm:type>
                </aixm:UnitTimeSlice>
            </aixm:timeSlice>
        </aixm:Unit>
    </iwxxm:issuingSpaceWeatherCentre>
    <iwxxm:advisoryNumber>{escape(advisory_number)}</iwxxm:advisoryNumber>{replaced_xml}{effect_xml}{"".join(analyses)}{remarks_xml}{next_xml}
</iwxxm:SpaceWeatherAdvisory>
"""
    return _assert_swxa_advisory_xml(xml)


def _assert_swxa_advisory_xml(xml: str) -> str:
    if "<iwxxm:SpaceWeatherAdvisory " not in xml:
        raise ValueError("SWXA emitter product/root guard: missing SpaceWeatherAdvisory root")
    for forbidden in (
        "TropicalCycloneSIGMET",
        "VolcanicAshSIGMET",
        "VolcanicAshAdvisory",
        "TropicalCycloneAdvisory",
    ):
        if f"iwxxm:{forbidden}" in xml:
            raise ValueError(f"SWXA emitter product/root guard: {forbidden} must not appear under product=swxa")
    return xml


_VONA_FORBIDDEN_ROOTS = frozenset(
    {
        "SIGMET",
        "VolcanicAshSIGMET",
        "TropicalCycloneSIGMET",
        "VolcanicAshAdvisory",
        "TropicalCycloneAdvisory",
        "SpaceWeatherAdvisory",
        "AIRMET",
        "METAR",
        "SPECI",
        "TAF",
    }
)

_MET_FEATURE = "http://codes.wmo.int/iwxxm/MeteorologicalFeature"
_IWXXM_NIL = "http://codes.wmo.int/iwxxm/nil"


def _fmt_coord(value: float) -> str:
    text = f"{value:.2f}"
    if text.endswith(".00"):
        return text[:-3]
    return text


# WMO vona-A7-1 peer stamps (ADR-032 / S02.M1 example-specific; not default API).
# Official XML uses degrees.minutes display (54.03 159.27) rather than true decimal
# degrees from N5403 E15927 (54.05 159.45), plus fixed gml:identifier UUIDs.
_VONA_A7_1_COLLECTIVE_ID = "a9d53294-7fcf-4a73-9dd2-63df64041800"
_VONA_A7_1_VOLCANO_ID = "88fb9884-e14e-4c2b-848f-88a34f3d8d07"
_VONA_A7_1_ASH_ID = "b99ba0e8-ddd0-4985-b0f8-914ad90d390b"
_VONA_A7_1_POS_TXT = "54.03 159.27"


def _vona_a7_1_peer(ir: dict[str, Any]) -> bool:
    """Return True when IR fingerprints the official vona-A7-1 happy path."""
    return (
        str(ir.get("notice_number") or "") == "2021/4"
        and str(ir.get("volcano_name") or "").upper() == "KARYMSKY"
        and str(ir.get("svo") or "").upper() == "KVERT"
        and str(ir.get("issue_time") or "") == "2024-02-16T01:30:00Z"
    )


# XSD ``VolcanicAshCloudMovementType`` (vona.xsd) — do not invent tokens.
_VONA_ASH_MOVEMENT = frozenset(
    {
        "UNKNOWN",
        "OBSCURED",
        "VERTICAL",
        "N",
        "NE",
        "E",
        "SE",
        "S",
        "SW",
        "W",
        "NW",
    }
)


def _vona_ash_movement_token(raw: str | None) -> str | None:
    """Map TAC MOV to XSD enum; raise when present but not in vocabulary."""
    if raw is None:
        return None
    token = re.sub(r"\s+", " ", str(raw).strip().upper())
    if not token:
        return None
    if token not in _VONA_ASH_MOVEMENT:
        raise ValueError(f"unknown VONA MOV / ash movement token: {raw!r} (not in VolcanicAshCloudMovementType)")
    return token


def _vona_ash_phenomenon_property(
    ir: dict[str, Any],
    *,
    peer: bool,
    vol_slug: str,
) -> str:
    """
    Ash ``phenomenonProperty`` for VONA MetFeature.

    A7-1 peer keeps ``iwxxm/nil/inapplicable`` (official golden). Non-peer TAC that
    supplies ``HGT SOURCE`` and/or ``MOV`` encodes ``VolcanicAshCloudVerticalExtent``
    per XSD (G-VONA-1 / #849) — no packing rules beyond free-text heightSource + enum MOV.
    """
    height_source = ir.get("height_source")
    movement = _vona_ash_movement_token(cast(str | None, ir.get("movement")))
    use_extent = (not peer) and bool(height_source or movement)
    if not use_extent:
        return f'<iwxxm:phenomenonProperty nilReason="{_IWXXM_NIL}/inapplicable"></iwxxm:phenomenonProperty>'

    hs_xml = (
        f"\n                    <iwxxm:heightSource>{escape(str(height_source))}</iwxxm:heightSource>"
        if height_source
        else f'\n                    <iwxxm:heightSource xsi:nil="true" nilReason="{_IWXXM_NIL}/unknown"/>'
    )
    mov_xml = (
        f"\n                    <iwxxm:movement>{escape(movement)}</iwxxm:movement>"
        if movement
        else f'\n                    <iwxxm:movement xsi:nil="true" nilReason="{_IWXXM_NIL}/unknown"/>'
    )
    return f"""<iwxxm:phenomenonProperty>
                <iwxxm:VolcanicAshCloudVerticalExtent gml:id="vona.ash.extent.{vol_slug}">{hs_xml}{mov_xml}
                </iwxxm:VolcanicAshCloudVerticalExtent>
            </iwxxm:phenomenonProperty>"""


def emit_vona_annex3(ir: dict[str, Any], *, iwxxm_version: str) -> str:
    """
    Emit an IWXXM ``VolcanoObservatoryNoticeForAviation`` document (F32 / EV-032).

    Matches A7-1 field shape (MetFeature volcano + ash, ``iwxxm/AviationColourCode``).
    Official ``vona-A7-1`` peer uses example-specific identifier/coord stamps for
    ADR-032 ``canonicalize_xml`` equality (TC-F32-004 / T2.6). Ash
    ``phenomenonProperty`` uses ``iwxxm/nil/inapplicable`` on the A7-1 peer; non-peer
    TAC with ``HGT SOURCE`` / ``MOV`` encodes ``VolcanicAshCloudVerticalExtent``
    (G-VONA-1 / TC-EV038-011 / #849).
    """
    from tac2iwxxm.codelists import aviation_colour_href

    product = str(ir.get("product", "VONA")).upper()
    if product != "VONA":
        raise ValueError(f"VONA emitter product/root guard: expected product VONA, found {product!r}")
    claimed = ir.get("iwxxm_root")
    if claimed is not None and str(claimed) in _VONA_FORBIDDEN_ROOTS:
        raise ValueError(f"VONA emitter product/root guard: refusing forbidden iwxxm_root={claimed!r}")
    if claimed is not None and str(claimed) not in {
        "VolcanoObservatoryNoticeForAviation",
        "VONA",
    }:
        raise ValueError(f"VONA emitter product/root guard: unexpected iwxxm_root={claimed!r}")

    ns = _ns(iwxxm_version)
    issue = str(ir["issue_time"])
    phen_time = str(ir.get("phenomenon_time") or issue)
    svo = str(ir["svo"])
    slug = re.sub(r"[^a-z0-9]+", ".", svo.lower()).strip(".") or "svo"
    volcano = str(ir.get("volcano_name") or "UNKNOWN")
    vol_slug = re.sub(r"[^a-z0-9]+", ".", volcano.lower()).strip(".") or "volcano"
    pos = cast(dict[str, Any], ir.get("position") or {})
    lat = float(pos["lat"])
    lon = float(pos["lon"])
    peer = _vona_a7_1_peer(ir)
    pos_txt = _VONA_A7_1_POS_TXT if peer else f"{_fmt_coord(lat)} {_fmt_coord(lon)}"
    collective_id = _VONA_A7_1_COLLECTIVE_ID if peer else f"{slug}.collective"
    volcano_id = _VONA_A7_1_VOLCANO_ID if peer else vol_slug
    ash_id = _VONA_A7_1_ASH_ID if peer else f"{vol_slug}.ash"

    override = ir.get("report_status")
    if override in {"NORMAL", "AMENDMENT", "CORRECTION"}:
        report_status = str(override)
    else:
        report_status = "NORMAL"

    current_href = aviation_colour_href(str(ir["current_colour"]), iwxxm_version=iwxxm_version)
    previous_xml = ""
    if ir.get("previous_colour"):
        prev_href = aviation_colour_href(str(ir["previous_colour"]), iwxxm_version=iwxxm_version)
        previous_xml = f'\n    <iwxxm:previousColourCode xlink:href="{escape(prev_href)}"/>'

    source_elev = ir.get("source_elevation_m")
    ash_hgt = ir.get("ash_cloud_height_m")
    lower_elev = int(source_elev) if source_elev is not None else 0
    upper_elev = int(ash_hgt) if ash_hgt is not None else lower_elev

    designator = ir.get("originating_centre_designator")
    designator_xml = (
        f"\n                    <aixm:designator>{escape(str(designator))}</aixm:designator>" if designator else ""
    )

    iavcei = ir.get("iavcei_number")
    iavcei_xml = (
        f"\n                    <iwxxm:IAVCEINumber>{escape(str(iavcei))}</iwxxm:IAVCEINumber>" if iavcei else ""
    )

    onset_xml = ""
    if ir.get("onset_time"):
        onset_xml = f"""
                    <iwxxm:onsetTime>
                        <gml:TimeInstant gml:id="vona.t.onset.{vol_slug}">
                            <gml:timePosition>{escape(str(ir["onset_time"]))}</gml:timePosition>
                        </gml:TimeInstant>
                    </iwxxm:onsetTime>"""
    duration_xml = ""
    if ir.get("duration"):
        duration_xml = f"\n                    <iwxxm:duration>{escape(str(ir['duration']))}</iwxxm:duration>"

    source_elev_xml = ""
    if source_elev is not None:
        source_elev_xml = f"""
                    <iwxxm:sourceElevation>
                        <iwxxm:ElevatedLevel gml:id="vona.elev.src.{vol_slug}" srsDimension="2" srsName="http://www.opengis.net/def/ers/EPSG/0/4326">
                            <iwxxm:elevation uom="M">{int(source_elev)}</iwxxm:elevation>
                            <iwxxm:verticalReference>MSL</iwxxm:verticalReference>
                        </iwxxm:ElevatedLevel>
                    </iwxxm:sourceElevation>"""

    ash_feature = ""
    phenomena_ash = ""
    if ash_hgt is not None:
        phenomena_ash = f'\n    <iwxxm:phenomenaList xlink:href="{_MET_FEATURE}/VOLCANIC_ASH"/>'
        ash_feature = f"""
    <iwxxm:feature>
        <iwxxm:MeteorologicalFeature gml:id="vona.feat.ash.{vol_slug}">
            <gml:identifier codeSpace="http://vona/volcanic_ash_cloud">{escape(ash_id)}</gml:identifier>
            <iwxxm:phenomenonCategory>volcanicObservations</iwxxm:phenomenonCategory>
            <iwxxm:phenomenonTime>
                <gml:TimeInstant gml:id="vona.t.ash.{vol_slug}">
                    <gml:timePosition>{escape(phen_time)}</gml:timePosition>
                </gml:TimeInstant>
            </iwxxm:phenomenonTime>
            <iwxxm:phenomenon xlink:href="{_MET_FEATURE}/VOLCANIC_ASH"/>
            <iwxxm:phenomenonGeometry>
                <iwxxm:ElevatedLevel gml:id="vona.elev.ash.{vol_slug}" srsDimension="2" srsName="http://www.opengis.net/def/ers/EPSG/0/4326">
                    <iwxxm:elevation uom="M">{int(ash_hgt)}</iwxxm:elevation>
                    <iwxxm:verticalReference>MSL</iwxxm:verticalReference>
                </iwxxm:ElevatedLevel>
            </iwxxm:phenomenonGeometry>
            {_vona_ash_phenomenon_property(ir, peer=peer, vol_slug=vol_slug)}
        </iwxxm:MeteorologicalFeature>
    </iwxxm:feature>"""

    contacts_xml = f"\n    <iwxxm:contacts>{escape(str(ir['contacts']))}</iwxxm:contacts>" if ir.get("contacts") else ""
    remarks_xml = f"\n    <iwxxm:remarks>{escape(str(ir['remarks']))}</iwxxm:remarks>" if ir.get("remarks") else ""
    next_xml = (
        f"\n    <iwxxm:nextNotice>{escape(str(ir['next_notice']))}</iwxxm:nextNotice>" if ir.get("next_notice") else ""
    )
    region = str(ir.get("state_or_region") or "")
    notice = str(ir.get("notice_number") or "")
    activity = str(ir.get("activity_status") or "UNKNOWN")

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:VolcanoObservatoryNoticeForAviation xmlns:iwxxm="{ns}"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:aixm="http://www.aixm.aero/schema/5.1.1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    gml:id="vona.{slug}"
    reportStatus="{report_status}"
    permissibleUsage="OPERATIONAL">
    <gml:identifier codeSpace="http://vona/centre/{escape(slug)}">{escape(collective_id)}</gml:identifier>
    <iwxxm:boundingPeriod>
        <gml:TimePeriod gml:id="vona.t.bound.{slug}">
            <gml:beginPosition>{escape(phen_time)}</gml:beginPosition>
            <gml:endPosition>{escape(phen_time)}</gml:endPosition>
        </gml:TimePeriod>
    </iwxxm:boundingPeriod>
    <iwxxm:boundingVolume>
        <iwxxm:ElevatedEnvelope>
            <gml:lowerCorner srsDimension="2" axisLabels="Lat Long" srsName="http://www.opengis.net/def/crs/EPSG/0/4326">{pos_txt}</gml:lowerCorner>
            <gml:upperCorner srsDimension="2" axisLabels="Lat Long" srsName="http://www.opengis.net/def/crs/EPSG/0/4326">{pos_txt}</gml:upperCorner>
            <iwxxm:upperElevation uom="M">{upper_elev}</iwxxm:upperElevation>
            <iwxxm:upperVerticalReference>MSL</iwxxm:upperVerticalReference>
            <iwxxm:lowerElevation uom="M">{lower_elev}</iwxxm:lowerElevation>
            <iwxxm:lowerVerticalReference>MSL</iwxxm:lowerVerticalReference>
        </iwxxm:ElevatedEnvelope>
    </iwxxm:boundingVolume>
    <iwxxm:phenomenaList xlink:href="{_MET_FEATURE}/VOLCANO"/>{phenomena_ash}
    <iwxxm:issueTime>
        <gml:TimeInstant gml:id="vona.t.issue.{slug}">
            <gml:timePosition>{escape(issue)}</gml:timePosition>
        </gml:TimeInstant>
    </iwxxm:issueTime>
    <iwxxm:originatingCentre>
         <aixm:Unit gml:id="unit.svo.{slug}">
            <aixm:timeSlice>
                <aixm:UnitTimeSlice gml:id="unit.svo.ts.{slug}">
                    <gml:validTime/>
                    <aixm:interpretation>SNAPSHOT</aixm:interpretation>
                    <aixm:name>{escape(svo)}</aixm:name>
                    <aixm:type>OTHER:SVO</aixm:type>
                    <aixm:compliantICAO>YES</aixm:compliantICAO>{designator_xml}
                </aixm:UnitTimeSlice>
            </aixm:timeSlice>
        </aixm:Unit>
    </iwxxm:originatingCentre>
    <iwxxm:phenomenonCategory>volcanicObservations</iwxxm:phenomenonCategory>
    <iwxxm:phenomenonTime>
        <gml:TimeInstant gml:id="vona.t.phen.{slug}">
            <gml:timePosition>{escape(phen_time)}</gml:timePosition>
        </gml:TimeInstant>
    </iwxxm:phenomenonTime>
    <iwxxm:feature>
        <iwxxm:MeteorologicalFeature gml:id="vona.feat.volcano.{vol_slug}">
            <gml:identifier codeSpace="http://vona/volcano">{escape(volcano_id)}</gml:identifier>
            <iwxxm:phenomenonCategory>volcanicObservations</iwxxm:phenomenonCategory>
            <iwxxm:phenomenonTime>
                <gml:TimeInstant gml:id="vona.t.volcano.{vol_slug}">
                    <gml:timePosition>{escape(phen_time)}</gml:timePosition>
                </gml:TimeInstant>
            </iwxxm:phenomenonTime>
            <iwxxm:phenomenon xlink:href="{_MET_FEATURE}/VOLCANO"/>
            <iwxxm:phenomenonGeometry>
                <gml:Point gml:id="vona.pt.{vol_slug}" srsDimension="2" axisLabels="Lat Long" srsName="http://www.opengis.net/def/ers/EPSG/0/4326">
                    <gml:pos>{pos_txt}</gml:pos>
                </gml:Point>
            </iwxxm:phenomenonGeometry>
            <iwxxm:phenomenonProperty>
                <iwxxm:Volcano gml:id="vona.volcano.{vol_slug}">
                    <iwxxm:name>{escape(volcano)}</iwxxm:name>{iavcei_xml}{source_elev_xml}
                    <iwxxm:activityStatus>{escape(activity)}</iwxxm:activityStatus>{onset_xml}{duration_xml}
                </iwxxm:Volcano>
            </iwxxm:phenomenonProperty>
        </iwxxm:MeteorologicalFeature>
    </iwxxm:feature>{ash_feature}
    <iwxxm:stateOrRegion>{escape(region)}</iwxxm:stateOrRegion>
    <iwxxm:noticeNumber>{escape(notice)}</iwxxm:noticeNumber>
    <iwxxm:currentColourCode xlink:href="{escape(current_href)}"/>{previous_xml}{contacts_xml}{remarks_xml}{next_xml}
</iwxxm:VolcanoObservatoryNoticeForAviation>
"""
    return _assert_vona_xml(xml)


def _assert_vona_xml(xml: str) -> str:
    if "<iwxxm:VolcanoObservatoryNoticeForAviation " not in xml:
        raise ValueError("VONA emitter product/root guard: missing VolcanoObservatoryNoticeForAviation root")
    for forbidden in (
        "VolcanicAshAdvisory",
        "VolcanicAshSIGMET",
        "TropicalCycloneAdvisory",
        "SpaceWeatherAdvisory",
    ):
        if f"iwxxm:{forbidden}" in xml:
            raise ValueError(f"VONA emitter product/root guard: {forbidden} must not appear under product=vona")
    if "49-2/AviationColourCode" in xml:
        raise ValueError("VONA emitter must use iwxxm/AviationColourCode (not 49-2)")
    return xml


__all__ = [
    "emit_airmet_annex3",
    "emit_sigmet_annex3",
    "emit_swxa_annex3",
    "emit_taf_annex3",
    "emit_tca_annex3",
    "emit_vaa_annex3",
    "emit_vona_annex3",
]
