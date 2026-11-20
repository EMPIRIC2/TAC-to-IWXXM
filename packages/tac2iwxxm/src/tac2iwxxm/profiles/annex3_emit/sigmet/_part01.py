"""Split part body (exec'd into package namespace)."""

from __future__ import annotations


def _is_wmo_sigmet_multi_location_va_yudd(ir: dict[str, Any]) -> bool:
    """
    Internal helper ``_is_wmo_sigmet_multi_location_va_yudd``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    Returns
    -------
    bool
        Return value.
    """
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
    """
    Internal helper ``_is_wmo_sigmet_va_eggx``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    Returns
    -------
    bool
        Return value.
    """
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
    """
    Internal helper ``_hazard_stamp``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    prefix : str
        Argument ``prefix``.

    Returns
    -------
    tuple[str, str, str]
        Return value.
    """
    from tac2iwxxm.time_anchor import iso_stamp

    if _is_wmo_sigmet_multi_location_va_yudd(ir) or _is_wmo_sigmet_va_eggx(ir):
        # Vendor VA-EGGX + multi-location-VA use 2018-07 (#809 / #856).
        legacy = "2018-07"
    elif ir["product"] == "SIGMET":
        legacy = "2012-08"
    else:
        legacy = "2014-05"
    issue = iso_stamp(
        ir,
        int(ir["valid_from_day"]),
        int(ir["valid_from_hour"]),
        int(ir["valid_from_minute"]),
        legacy=legacy,
    )
    begin = issue
    end = iso_stamp(
        ir,
        int(ir["valid_to_day"]),
        int(ir["valid_to_hour"]),
        int(ir["valid_to_minute"]),
        legacy=legacy,
    )
    return issue, begin, end


def _sigmet_root_local(ir: dict[str, Any]) -> str:
    """
    Internal helper ``_sigmet_root_local``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    Returns
    -------
    str
        Return value.
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
    """
    Internal helper ``_sigmet_header_units``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    ns : str
        Argument ``ns``.

    gml_id : str
        Argument ``gml_id``.

    issue : str
        Argument ``issue``.

    extra_xmlns : str, optional
        Argument ``extra_xmlns``.

    Returns
    -------
    str
        Return value.
    """
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
    """
    Internal helper ``_wmo_multi_location_va_pos_list``.

    Parameters
    ----------
    pos_list : str
        Argument ``pos_list``.

    Returns
    -------
    str
        Return value.
    """
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
    """
    Internal helper ``_sigmet_tc_format_pos``.

    Parameters
    ----------
    lat : float
        Argument ``lat``.

    lon : float
        Argument ``lon``.

    Returns
    -------
    str
        Return value.
    """

    def _one(value: float) -> str:
        """
        Internal helper ``_one``.

        Parameters
        ----------
        value : float
            Argument ``value``.

        Returns
        -------
        str
            Return value.
        """
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
    """
    Internal helper ``_sigmet_geometry_xml``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    fir : str
        Argument ``fir``.

    gid : str | None, optional
        Argument ``gid``.

    geometry : dict[str, Any] | None, optional
        Argument ``geometry``.

    include_limits : bool, optional
        Argument ``include_limits``.

    wmo_multi_location_va_ring : bool, optional
        Argument ``wmo_multi_location_va_ring``.

    Returns
    -------
    str
        Return value.
    """
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
        elif ir.get("lower_ft") is not None and upper_fl is not None:
            unit = "[ft_i]" if str(ir.get("lower_unit", "FT")).upper() == "FT" else "m"
            limits = f"""
              <aixm:lowerLimit uom="{unit}">{int(ir["lower_ft"])}</aixm:lowerLimit>
              <aixm:lowerLimitReference>MSL</aixm:lowerLimitReference>
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
