"""Split part body (exec'd into package namespace)."""

from __future__ import annotations


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
    """
    Internal helper ``_sigmet_location_analysis_xml``.

    Parameters
    ----------
    loc : dict[str, Any]
        Argument ``loc``.

    fir : str
        Argument ``fir``.

    index : int
        Argument ``index``.

    issue : str
        Argument ``issue``.

    begin : str
        Argument ``begin``.

    end : str
        Argument ``end``.

    wmo_multi_location_va_ring : bool, optional
        Argument ``wmo_multi_location_va_ring``.

    wmo_va_eggx_ring : bool, optional
        Argument ``wmo_va_eggx_ring``.

    Returns
    -------
    str
        Return value.
    """
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
    """
    Internal helper ``_sigmet_volcano_xml``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    Returns
    -------
    str
        Return value.
    """
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


def _motion_deg_text(degrees: int | float) -> str:
    """
    Format a motion bearing, keeping half-degree compass points.

    Parameters
    ----------
    degrees : int | float
        Bearing from true north.

    Returns
    -------
    str
        Whole degrees as an integer, otherwise one decimal place.
    """
    number = float(degrees)
    if number.is_integer():
        return str(int(number))
    return f"{number:.1f}"


def _sigmet_motion_xml(ir: dict[str, Any]) -> str:
    """
    Internal helper ``_sigmet_motion_xml``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    Returns
    -------
    str
        Return value.
    """
    if ir.get("stationary"):
        return """
              <iwxxm:directionOfMotion uom="deg" xsi:nil="true" nilReason="http://codes.wmo.int/common/nil/inapplicable"/>
              <iwxxm:speedOfMotion uom="[kn_i]">0</iwxxm:speedOfMotion>"""
    if "motion_dir_deg" in ir and "motion_speed_kmh" in ir:
        return f"""
              <iwxxm:directionOfMotion uom="deg">{_motion_deg_text(ir["motion_dir_deg"])}</iwxxm:directionOfMotion>
              <iwxxm:speedOfMotion uom="km/h">{int(ir["motion_speed_kmh"])}</iwxxm:speedOfMotion>"""
    if "motion_dir_deg" in ir and "motion_speed_kt" in ir:
        return f"""
              <iwxxm:directionOfMotion uom="deg">{_motion_deg_text(ir["motion_dir_deg"])}</iwxxm:directionOfMotion>
              <iwxxm:speedOfMotion uom="[kn_i]">{int(ir["motion_speed_kt"])}</iwxxm:speedOfMotion>"""
    if "motion_dir_deg" in ir:
        return f"""
              <iwxxm:directionOfMotion uom="deg">{_motion_deg_text(ir["motion_dir_deg"])}</iwxxm:directionOfMotion>"""
    return ""


def _sigmet_tropical_cyclone_xml(ir: dict[str, Any]) -> str:
    """
    Internal helper ``_sigmet_tropical_cyclone_xml``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    Returns
    -------
    str
        Return value.
    """
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
    """
    Internal helper ``_sigmet_tc_position_xml``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    gid : str
        Argument ``gid``.

    Returns
    -------
    str
        Return value.
    """
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
    """
    Internal helper ``_sigmet_tc_forecast_xml``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    fir : str
        Argument ``fir``.

    end : str
        Argument ``end``.

    Returns
    -------
    str
        Return value.
    """
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
    from tac2iwxxm.time_anchor import iso_stamp

    fcst_time = iso_stamp(ir, day, hour, minute, legacy="2012-08")
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
    """
    Emit US ``CONVECTIVE SIGMET`` (WST) with iwxxm-us analysis shape (#919 M11).

    Parameters
    ----------
    ir : dict[str, Any]
        Parsed product fields.

    iwxxm_version : str
        IWXXM release line.

    Returns
    -------
    str
        US ``CONVECTIVE SIGMET`` (WST) with iwxxm-us analysis shape (#919 M11).

    Examples
    --------
    >>> 1 + 1  # docstring smoke (emit_convective_sigmet_annex3)
    2
    """
    ns = _ns(iwxxm_version)
    fir = str(ir["fir"])
    mwo = str(ir["mwo"])
    issue, begin, end = _hazard_stamp(ir, "sigmet")
    gml_id = f"sigmet.conv.{fir.lower()}"
    from tac2iwxxm.time_anchor import iso_stamp

    active_end = iso_stamp(
        ir,
        int(ir["valid_to_day"]),
        int(ir["valid_to_hour"]),
        int(ir["valid_to_minute"]),
        legacy="2012-08",
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
  <iwxxm:analysisCollection>
    <iwxxm:analysisAndForecastPositionAnalysis gml:id="analysis.{fir.lower()}">
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
    </iwxxm:analysisAndForecastPositionAnalysis>
  </iwxxm:analysisCollection>
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
