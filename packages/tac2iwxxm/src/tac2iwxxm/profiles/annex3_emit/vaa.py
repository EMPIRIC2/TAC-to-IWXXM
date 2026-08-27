"""Annex-3 profile XML writers - vaa."""

# pyright: reportWildcardImportFromLibrary=false

from __future__ import annotations

import re
from typing import Any
from xml.sax.saxutils import escape

from tac2iwxxm.profiles.annex3_emit._common import *

_VAA_FORBIDDEN_ROOTS = frozenset(
    {
        "VolcanicAshSIGMET",
        "SIGMET",
        "TropicalCycloneSIGMET",
        "AIRMET",
        "TropicalCycloneAdvisory",
    }
)


def _vaa_cloud_extent_xml(cloud: dict[str, Any], *, gid: str) -> str:
    """Emit ashCloudExtent AirspaceVolume (+ optional motion) for one cloud."""
    # ruff: noqa: F403, F405
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
    Emit an IWXXM ``VolcanicAshAdvisory`` document (F6.f / F26 themes V2-V3).

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
    if override in {"NORMAL", "AMENDMENT", "CORRECTION"}:  # noqa: SIM108 — keep branches for per-file coverage
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
