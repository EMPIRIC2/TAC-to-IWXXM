"""Annex-3 profile XML writers - swxa."""

# pyright: reportWildcardImportFromLibrary=false
# ruff: noqa: F403, F405

from __future__ import annotations

import re
from typing import Any, cast
from xml.sax.saxutils import escape

from tac2iwxxm.profiles.annex3_emit._common import *

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
# ruff: noqa: F403, F405
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
    report_status = str(override) if override in {"NORMAL", "AMENDMENT", "CORRECTION"} else "NORMAL"

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
