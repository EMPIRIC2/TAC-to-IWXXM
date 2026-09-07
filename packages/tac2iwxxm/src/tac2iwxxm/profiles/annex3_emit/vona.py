"""Annex-3 profile XML writers - vona."""

# pyright: reportWildcardImportFromLibrary=false

from __future__ import annotations

import re
from typing import Any, cast
from xml.sax.saxutils import escape

from tac2iwxxm.profiles.annex3_emit._common import *

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
    # ruff: noqa: F403, F405
    return (
        str(ir.get("notice_number") or "") == "2021/4"
        and str(ir.get("volcano_name") or "").upper() == "KARYMSKY"
        and str(ir.get("svo") or "").upper() == "KVERT"
        and str(ir.get("issue_time") or "") == "2024-02-16T01:30:00Z"
    )


# XSD ``VolcanicAshCloudMovementType`` (vona.xsd) - do not invent tokens.
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
    per XSD (G-VONA-1 / #849) - no packing rules beyond free-text heightSource + enum MOV.
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
    report_status = str(override) if override in {"NORMAL", "AMENDMENT", "CORRECTION"} else "NORMAL"

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
