"""Split part body (exec'd into package namespace)."""

from __future__ import annotations


def emit_sigmet_annex3(ir: dict[str, Any], *, iwxxm_version: str) -> str:
    """
    Emit an IWXXM SIGMET / VolcanicAshSIGMET / TropicalCycloneSIGMET document.

    Parameters
    ----------
    ir : dict[str, Any]
        Parsed product fields.

    iwxxm_version : str
        IWXXM release line.

    Returns
    -------
    str
        An IWXXM SIGMET / VolcanicAshSIGMET / TropicalCycloneSIGMET document.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (emit_sigmet_annex3)
    2
    """
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
        from tac2iwxxm.time_anchor import iso_stamp

        c_begin = iso_stamp(
            ir,
            int(ir["cancelled_from_day"]),
            int(ir["cancelled_from_hour"]),
            int(ir["cancelled_from_minute"]),
            legacy="2012-08",
        )
        c_end = iso_stamp(
            ir,
            int(ir["cancelled_to_day"]),
            int(ir["cancelled_to_hour"]),
            int(ir["cancelled_to_minute"]),
            legacy="2012-08",
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

    phenom = _sigmet_phenomenon_href(str(ir["phenomenon"]))
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
