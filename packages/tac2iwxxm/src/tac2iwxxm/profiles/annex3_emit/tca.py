"""Annex-3 profile XML writers - tca."""

# pyright: reportWildcardImportFromLibrary=false

from __future__ import annotations

import re
from typing import Any, cast
from xml.sax.saxutils import escape

from tac2iwxxm.profiles.annex3_emit._common import *

_TCA_FORBIDDEN_ROOTS = frozenset(
    {
        "TropicalCycloneSIGMET",
        "SIGMET",
        "VolcanicAshSIGMET",
        "AIRMET",
        "VolcanicAshAdvisory",
    }
)


def _tca_format_pos(lat: float, lon: float) -> str:
    """Format lat/lon for WMO A2-2-style ``gml:pos`` (up to 5 decimals; ``.00`` for wholes)."""
    # ruff: noqa: F403, F405

    def _one(value: float) -> str:
        s = f"{value:.5f}".rstrip("0")
        if s.endswith("."):
            s += "00"
        return s

    return f"{_one(lat)} {_one(lon)}"


def emit_tca_annex3(ir: dict[str, Any], *, iwxxm_version: str) -> str:
    """
    Emit an IWXXM ``TropicalCycloneAdvisory`` document (F6.f / F27 themes T2-T3).

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
    report_status = str(override) if override in {"NORMAL", "AMENDMENT", "CORRECTION"} else "NORMAL"

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
