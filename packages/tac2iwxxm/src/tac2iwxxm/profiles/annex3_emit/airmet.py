"""Annex-3 profile XML writers - airmet."""

# pyright: reportWildcardImportFromLibrary=false, reportPrivateUsage=false

from __future__ import annotations

from typing import Any, cast
from xml.sax.saxutils import escape

from tac2iwxxm.profiles.annex3_emit._common import *
from tac2iwxxm.profiles.annex3_emit.sigmet import (
    _hazard_stamp,
    _sigmet_geometry_xml,
    _sigmet_motion_xml,
)


def _airmet_evolving_member_xml(
    area_ir: dict[str, Any],
    *,
    fir: str,
    member_suffix: str,
    inner_extension: str = "",
) -> str:
    """Emit one ``AIRMETEvolvingCondition`` member."""
    # ruff: noqa: F403, F405
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
    status = str(override) if override in {"NORMAL", "AMENDMENT", "CORRECTION"} else "NORMAL"
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
        area_list.extend(
            cast(dict[str, Any], obj) for obj in cast(list[object], area_list_raw) if isinstance(obj, dict)
        )
    has_multi = len(area_list) > 1
    has_outlook = outlook_ir is not None
    obs_areas = area_list or [ir]

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
