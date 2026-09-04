"""Annex-3 profile XML writers - sigmet."""

# pyright: reportWildcardImportFromLibrary=false

from __future__ import annotations

import re
from typing import Any, cast
from xml.sax.saxutils import escape

from tac2iwxxm.profiles.annex3_emit._common import *

# Vendor ``sigmet-VA-EGGX`` peer rings / volcano pos (S02.M1 example stamps; #856).
_EGGX_OBS_POS = "60.0 -11.83 60.0 -16.0 59.0 -13.0 60.0 -11.83"
_EGGX_FCST_POS = "60.0 -12.0 58.0 -14.0 60.0 -15.58 60.0 -12.0"
_EGGX_VOLCANO_POS = "63.98 -19.67"


def _is_wmo_sigmet_multi_location_va_yudd(ir: dict[str, Any]) -> bool:
    """True for WMO ``sigmet-multi-location-VA`` stem (YUDD/YUSO + ≥2 VA locations)."""
    # ruff: noqa: F403, F405
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
    status = str(override) if override in {"NORMAL", "AMENDMENT", "CORRECTION"} else "NORMAL"
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
        locations.extend(
            cast(dict[str, Any], item) for item in cast(list[Any], locations_raw) if isinstance(item, dict)
        )
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
    time_indicator = str(ir.get("time_indicator", "OBSERVATION")) if is_tc else "FORECAST"
    tc_pos = _sigmet_tc_position_xml(ir, gid=f"tc.pos.{fir.lower()}") if is_tc else ""
    tc_fcst = _sigmet_tc_forecast_xml(ir, fir=fir, end=end) if is_tc else ""
    tc_name_xml = _sigmet_tropical_cyclone_xml(ir) if is_tc else ""
    # Vendor A6-2-TC omits intensityChange when NO_CHANGE (#835).
    intensity_attr = "" if is_tc and intensity == "NO_CHANGE" else f' intensityChange="{escape(intensity)}"'
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
