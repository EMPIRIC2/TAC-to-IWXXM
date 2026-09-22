#!/usr/bin/env python3
"""EV-970 S3c — fill remaining validate/metar_speci SCH oos via expanded mutations.

Keeps existing ready SCH negatives; only rewrites ``oos`` sad/edge_fail slots when a
probe fires the target ``rule_id``.

Batch B/B2: Wind ``kt`` / Wind-1 extremes / Report-2-6 / Observation-2 /
``document()`` codelist (mirrored ``href``) / Report-9 ARP geometry.

Requires native ``iwxxm_validate._rust``.

[Corpus: decisions §ev-970-s3-validate-fill] [Corpus: product §F13]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml
from iwxxm_validate import rust_available, validate_iwxxm

from tac2iwxxm import convert as convert_tac

ROOT = Path(__file__).resolve().parents[2]
VALIDATE_DIR = ROOT / "tests/quality_matrices/testdata/validate/metar_speci"
CITE = "EV-970-S3c Schematron negative (native Batch B2)"
OOS_CITE = "#970 EV-970-S3c residual — still unprobeable after document()/index-of stand-ins"

_BASE_TACS = [
    "METAR KJFK 121251Z 18008KT 10SM FEW250 22/12 A3012=",
    "METAR KJFK 121251Z 18008KT 1/2SM R04/P6000FT FEW250 22/12 A3012=",
    "METAR KJFK 121251Z 18015G25KT 10SM FEW250 22/12 A3012=",
]


def _convert(tac: str) -> str:
    result = convert_tac(tac, product="METAR", profile="annex3", iwxxm_version="2025-2")
    if not result.ok or not result.xml:
        raise RuntimeError(f"convert failed: {tac[:40]}")
    return result.xml


def _inject_before_obs_close(xml: str, fragment: str) -> str:
    marker = "</iwxxm:MeteorologicalAerodromeObservation>"
    if marker not in xml:
        return xml
    return xml.replace(marker, fragment + marker, 1)


def _mutations(bases: list[str]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for bi, base in enumerate(bases):
        p = f"b{bi}_"
        out.append(
            (
                p + "vis_prevailing_bad_uom",
                re.sub(
                    r'(<iwxxm:prevailingVisibility[^>]*uom=")[^"]*"',
                    r'\1[ft_i]"',
                    base,
                    count=1,
                ),
            )
        )
        out.append(
            (
                p + "vis_inject_prevailing_bad",
                _inject_before_obs_close(
                    base,
                    "<iwxxm:visibility><iwxxm:AerodromeHorizontalVisibility>"
                    '<iwxxm:prevailingVisibility uom="[ft_i]">800'
                    "</iwxxm:prevailingVisibility>"
                    "</iwxxm:AerodromeHorizontalVisibility></iwxxm:visibility>",
                ),
            )
        )
        out.append(
            (
                p + "vis_min_bad_uom",
                _inject_before_obs_close(
                    base,
                    "<iwxxm:visibility><iwxxm:AerodromeHorizontalVisibility>"
                    '<iwxxm:prevailingVisibility uom="m">800</iwxxm:prevailingVisibility>'
                    '<iwxxm:minimumVisibility uom="[ft_i]">400</iwxxm:minimumVisibility>'
                    "</iwxxm:AerodromeHorizontalVisibility></iwxxm:visibility>",
                ),
            )
        )
        out.append(
            (
                p + "vis_min_dir_bad_uom",
                _inject_before_obs_close(
                    base,
                    "<iwxxm:visibility><iwxxm:AerodromeHorizontalVisibility>"
                    '<iwxxm:prevailingVisibility uom="m">800</iwxxm:prevailingVisibility>'
                    '<iwxxm:minimumVisibility uom="m">400</iwxxm:minimumVisibility>'
                    '<iwxxm:minimumVisibilityDirection uom="rad">90'
                    "</iwxxm:minimumVisibilityDirection>"
                    "</iwxxm:AerodromeHorizontalVisibility></iwxxm:visibility>",
                ),
            )
        )
        # Wind-6/7 allow m/s and [kn_i]; illegal legacy "kt" fires both.
        out.append(
            (
                p + "wind_speed_bad_uom_kt",
                re.sub(
                    r'(<iwxxm:meanWindSpeed[^>]*uom=")[^"]*"',
                    r'\1kt"',
                    base,
                    count=1,
                ),
            )
        )
        gust = base
        if "windGustSpeed" in base:
            gust = re.sub(
                r'(<iwxxm:windGustSpeed[^>]*uom=")[^"]*"',
                r'\1kt"',
                base,
                count=1,
            )
        else:
            gust = re.sub(
                r"</iwxxm:AerodromeSurfaceWind>",
                '<iwxxm:windGustSpeed uom="kt">25</iwxxm:windGustSpeed>'
                "</iwxxm:AerodromeSurfaceWind>",
                base,
                count=1,
            )
        out.append((p + "wind_gust_bad_uom_kt", gust))
        out.append(
            (
                p + "wind_speed_and_gust_kt",
                re.sub(
                    r'(<iwxxm:windGustSpeed[^>]*uom=")[^"]*"',
                    r'\1kt"',
                    re.sub(
                        r'(<iwxxm:meanWindSpeed[^>]*uom=")[^"]*"',
                        r'\1kt"',
                        base
                        if "windGustSpeed" in base
                        else re.sub(
                            r"</iwxxm:AerodromeSurfaceWind>",
                            '<iwxxm:windGustSpeed uom="kt">25'
                            "</iwxxm:windGustSpeed></iwxxm:AerodromeSurfaceWind>",
                            base,
                            count=1,
                        ),
                        count=1,
                    ),
                    count=1,
                ),
            )
        )
        out.append(
            (
                p + "wind_extreme_cw_bad",
                re.sub(
                    r"</iwxxm:AerodromeSurfaceWind>",
                    '<iwxxm:extremeClockwiseWindDirection uom="rad">90'
                    "</iwxxm:extremeClockwiseWindDirection>"
                    "</iwxxm:AerodromeSurfaceWind>",
                    base,
                    count=1,
                ),
            )
        )
        out.append(
            (
                p + "wind_extreme_ccw_bad",
                re.sub(
                    r"</iwxxm:AerodromeSurfaceWind>",
                    '<iwxxm:extremeCounterClockwiseWindDirection uom="rad">270'
                    "</iwxxm:extremeCounterClockwiseWindDirection>"
                    "</iwxxm:AerodromeSurfaceWind>",
                    base,
                    count=1,
                ),
            )
        )
        # Wind-1 needs both extremes present with mismatched uoms vs mean.
        out.append(
            (
                p + "wind_extremes_uom_mismatch",
                re.sub(
                    r"</iwxxm:AerodromeSurfaceWind>",
                    '<iwxxm:extremeClockwiseWindDirection uom="rad">90'
                    "</iwxxm:extremeClockwiseWindDirection>"
                    '<iwxxm:extremeCounterClockwiseWindDirection uom="deg">270'
                    "</iwxxm:extremeCounterClockwiseWindDirection>"
                    "</iwxxm:AerodromeSurfaceWind>",
                    base,
                    count=1,
                ),
            )
        )
        out.append(
            (
                p + "wind_mixed_uom",
                re.sub(
                    r'(<iwxxm:meanWindSpeed[^>]*uom=")[^"]*"',
                    r'\1m/s"',
                    re.sub(
                        r'(<iwxxm:meanWindDirection[^>]*uom=")[^"]*"',
                        r'\1deg"',
                        base,
                        count=1,
                    ),
                    count=1,
                ),
            )
        )
        out.append(
            (
                p + "sea_temp_bad_uom",
                _inject_before_obs_close(
                    base,
                    "<iwxxm:seaCondition><iwxxm:AerodromeSeaCondition>"
                    '<iwxxm:seaSurfaceTemperature uom="K">280'
                    "</iwxxm:seaSurfaceTemperature>"
                    "</iwxxm:AerodromeSeaCondition></iwxxm:seaCondition>",
                ),
            )
        )
        out.append(
            (
                p + "sea_wave_bad_uom",
                _inject_before_obs_close(
                    base,
                    "<iwxxm:seaCondition><iwxxm:AerodromeSeaCondition>"
                    '<iwxxm:significantWaveHeight uom="[ft_i]">3'
                    "</iwxxm:significantWaveHeight>"
                    "</iwxxm:AerodromeSeaCondition></iwxxm:seaCondition>",
                ),
            )
        )
        out.append(
            (
                p + "sea_state_and_wave",
                _inject_before_obs_close(
                    base,
                    "<iwxxm:seaCondition><iwxxm:AerodromeSeaCondition>"
                    '<iwxxm:seaState xlink:href="http://codes.wmo.int/bufr4/codeflag/0-22-061/3"/>'
                    '<iwxxm:significantWaveHeight uom="m">1.5'
                    "</iwxxm:significantWaveHeight>"
                    "</iwxxm:AerodromeSeaCondition></iwxxm:seaCondition>",
                ),
            )
        )
        out.append(
            (
                p + "wind_shear_all_and_runway",
                _inject_before_obs_close(
                    base,
                    "<iwxxm:windShear>"
                    '<iwxxm:AerodromeWindShear allRunways="true">'
                    "<iwxxm:runway>"
                    '<aixm:RunwayDirection gml:id="rwy.04">'
                    "<aixm:timeSlice>"
                    '<aixm:RunwayDirectionTimeSlice gml:id="rwy.04.ts">'
                    '<gml:validTime/><aixm:interpretation>SNAPSHOT</aixm:interpretation>'
                    "<aixm:designator>04</aixm:designator>"
                    "</aixm:RunwayDirectionTimeSlice></aixm:timeSlice>"
                    "</aixm:RunwayDirection></iwxxm:runway>"
                    "</iwxxm:AerodromeWindShear></iwxxm:windShear>",
                ),
            )
        )
        out.append(
            (
                p + "nil_cloud_auto",
                re.sub(
                    r"<iwxxm:cloud>.*?</iwxxm:cloud>",
                    (
                        '<iwxxm:cloud nilReason="http://codes.wmo.int/common/nil/'
                        'notDetectedByAutoSystem"/>'
                    ),
                    base,
                    count=1,
                    flags=re.S,
                ),
            )
        )
        out.append(
            (
                p + "cloud_amount_base_nil_auto",
                re.sub(
                    r"<iwxxm:CloudLayer>.*?</iwxxm:CloudLayer>",
                    (
                        "<iwxxm:CloudLayer>"
                        '<iwxxm:amount nilReason="http://codes.wmo.int/common/nil/'
                        'notDetectedByAutoSystem"/>'
                        '<iwxxm:base nilReason="http://codes.wmo.int/common/nil/'
                        'notDetectedByAutoSystem"/>'
                        "</iwxxm:CloudLayer>"
                    ),
                    base,
                    count=1,
                    flags=re.S,
                ),
            )
        )
        # Report-6: empty layer with notDetectedByAutoSystem and no automatedStation.
        out.append(
            (
                p + "report6_layer_nil_auto",
                re.sub(
                    r"<iwxxm:cloud>.*?</iwxxm:cloud>",
                    (
                        "<iwxxm:cloud><iwxxm:AerodromeCloud>"
                        '<iwxxm:layer nilReason="http://codes.wmo.int/common/nil/'
                        'notDetectedByAutoSystem"/>'
                        "</iwxxm:AerodromeCloud></iwxxm:cloud>"
                    ),
                    base,
                    count=1,
                    flags=re.S,
                ),
            )
        )
        out.append(
            (
                p + "non_op_missing_fields",
                base.replace(
                    'permissibleUsage="OPERATIONAL"',
                    'permissibleUsage="NON-OPERATIONAL"',
                    1,
                ),
            )
        )
        # Report-2: NON-OPERATIONAL without issueTime.
        out.append(
            (
                p + "report2_non_op_no_issue_time",
                re.sub(
                    r"<iwxxm:issueTime>.*?</iwxxm:issueTime>\s*",
                    "",
                    base.replace(
                        'permissibleUsage="OPERATIONAL"',
                        'permissibleUsage="NON-OPERATIONAL"',
                        1,
                    ),
                    count=1,
                    flags=re.S,
                ),
            )
        )
        out.append(
            (
                p + "translation_failed_attr",
                re.sub(
                    r"(<iwxxm:METAR\b)",
                    r'\1 translationFailedTAC="METAR BOGUS"',
                    base,
                    count=1,
                ),
            )
        )
        # Report-4: operational report missing observation.
        out.append(
            (
                p + "report4_no_observation",
                re.sub(
                    r"<iwxxm:observation>.*?</iwxxm:observation>\s*",
                    "",
                    base,
                    count=1,
                    flags=re.S,
                ),
            )
        )
        # Report-3: nil observation without issueTime.
        out.append(
            (
                p + "report3_nil_obs_no_issue_time",
                re.sub(
                    r"<iwxxm:issueTime>.*?</iwxxm:issueTime>\s*",
                    "",
                    re.sub(
                        r"<iwxxm:trendForecast>.*?</iwxxm:trendForecast>\s*",
                        "",
                        re.sub(
                            r"<iwxxm:observation>.*?</iwxxm:observation>",
                            (
                                '<iwxxm:observation nilReason="'
                                'http://codes.wmo.int/common/nil/missing"/>'
                            ),
                            base,
                            count=1,
                            flags=re.S,
                        ),
                        count=1,
                        flags=re.S,
                    ),
                    count=1,
                    flags=re.S,
                ),
            )
        )
        # Observation-2: low vis without RVR.
        out.append(
            (
                p + "low_vis_no_rvr",
                re.sub(
                    r"<iwxxm:rvr>.*?</iwxxm:rvr>\s*",
                    "",
                    re.sub(
                        r'(<iwxxm:prevailingVisibility[^>]*>)[^<]*',
                        r"\g<1>800",
                        base,
                        count=1,
                    ),
                    count=1,
                    flags=re.S,
                ),
            )
        )
        out.append(
            (
                p + "trend_cavok_with_cloud",
                _inject_before_obs_close(
                    base,
                    "<iwxxm:trendForecast>"
                    '<iwxxm:MeteorologicalAerodromeTrendForecast '
                    'cloudAndVisibilityOK="true" changeIndicator="BECOMING">'
                    "<iwxxm:cloud><iwxxm:AerodromeCloud><iwxxm:layer>"
                    "<iwxxm:CloudLayer>"
                    '<iwxxm:amount xlink:href="http://codes.wmo.int/49-2/'
                    'CloudAmountReportedAtAerodrome/FEW"/>'
                    '<iwxxm:base uom="[ft_i]">25000</iwxxm:base>'
                    "</iwxxm:CloudLayer></iwxxm:layer></iwxxm:AerodromeCloud>"
                    "</iwxxm:cloud></iwxxm:MeteorologicalAerodromeTrendForecast>"
                    "</iwxxm:trendForecast>",
                ),
            )
        )
        out.append(
            (
                p + "trend_vis_bad_uom",
                _inject_before_obs_close(
                    base,
                    "<iwxxm:trendForecast>"
                    '<iwxxm:MeteorologicalAerodromeTrendForecast '
                    'cloudAndVisibilityOK="false" changeIndicator="BECOMING">'
                    '<iwxxm:prevailingVisibility uom="[ft_i]">3000'
                    "</iwxxm:prevailingVisibility>"
                    "</iwxxm:MeteorologicalAerodromeTrendForecast>"
                    "</iwxxm:trendForecast>",
                ),
            )
        )
        bogus_href = "http://example.invalid/not-a-codelist"
        out.append(
            (
                p + "present_weather_bogus_href",
                _inject_before_obs_close(
                    base,
                    "<iwxxm:presentWeather>"
                    f'<iwxxm:AerodromePresentWeather xlink:href="{bogus_href}"/>'
                    "</iwxxm:presentWeather>",
                ),
            )
        )
        out.append(
            (
                p + "recent_weather_bogus_href",
                _inject_before_obs_close(
                    base,
                    "<iwxxm:recentWeather>"
                    f'<iwxxm:AerodromeRecentWeather xlink:href="{bogus_href}"/>'
                    "</iwxxm:recentWeather>",
                ),
            )
        )
        out.append(
            (
                p + "sea_state_bogus_href",
                _inject_before_obs_close(
                    base,
                    "<iwxxm:seaCondition><iwxxm:AerodromeSeaCondition>"
                    f'<iwxxm:seaState xlink:href="{bogus_href}"/>'
                    "</iwxxm:AerodromeSeaCondition></iwxxm:seaCondition>",
                ),
            )
        )
        out.append(
            (
                p + "sea_surface_state_bogus_href",
                _inject_before_obs_close(
                    base,
                    "<iwxxm:seaCondition><iwxxm:AerodromeSeaCondition>"
                    f'<iwxxm:SeaSurfaceState xlink:href="{bogus_href}"/>'
                    "</iwxxm:AerodromeSeaCondition></iwxxm:seaCondition>",
                ),
            )
        )
        out.append(
            (
                p + "trend_weather_bogus_href",
                _inject_before_obs_close(
                    base,
                    "<iwxxm:trendForecast>"
                    '<iwxxm:MeteorologicalAerodromeTrendForecast '
                    'cloudAndVisibilityOK="false" changeIndicator="BECOMING">'
                    f'<iwxxm:weather xlink:href="{bogus_href}"/>'
                    "</iwxxm:MeteorologicalAerodromeTrendForecast>"
                    "</iwxxm:trendForecast>",
                ),
            )
        )
        # Report-9: ARP pos with srsName but missing srsDimension/axisLabels.
        out.append(
            (
                p + "report9_arp_bad_srs",
                base.replace(
                    "</aixm:AirportHeliportTimeSlice>",
                    (
                        '<aixm:ARP><aixm:ElevatedPoint gml:id="arp.bad" '
                        'srsName="urn:ogc:def:crs:EPSG::4326">'
                        "<gml:pos>40.64 -73.78</gml:pos>"
                        "</aixm:ElevatedPoint></aixm:ARP>"
                        "</aixm:AirportHeliportTimeSlice>"
                    ),
                    1,
                ),
            )
        )
    # drop no-ops / broken
    cleaned: list[tuple[str, str]] = []
    for lab, xml in out:
        if not xml or xml in bases:
            continue
        cleaned.append((lab, xml))
    return cleaned


def _fired_rule_ids(xml: str) -> set[str]:
    report = validate_iwxxm(xml, iwxxm_version="2025-2", profile="annex3")
    if report.ok:
        return set()
    fired: set[str] = set()
    for issue in report.issues:
        if issue.severity != "error":
            continue
        msg = issue.message or ""
        m = re.match(r"(METAR_SPECI\.[A-Za-z0-9_.-]+):", msg)
        if m:
            fired.add(m.group(1))
            continue
        m2 = re.search(r"Element in (iwxxm:\S+) should be a member of code list", msg)
        if m2:
            parts = [p.removeprefix("iwxxm:") for p in m2.group(1).split("/")]
            fired.add("METAR_SPECI." + ".".join(parts))
    return fired


def _neg_case(
    *,
    bucket: str,
    case_id: str,
    rule_id: str,
    xml: str,
    label: str,
) -> dict[str, object]:
    return {
        "bucket": bucket,
        "case_id": case_id,
        "status": "ready",
        "expect": {"accept": False, "sch_ids": [rule_id]},
        "meta": {
            "product": "METAR",
            "profile": "annex3",
            "iwxxm_version": "2025-2",
            "xml": xml,
            "cite": f"{CITE} / {label}",
        },
    }


def _oos_case(*, bucket: str, case_id: str) -> dict[str, object]:
    return {
        "bucket": bucket,
        "case_id": case_id,
        "status": "oos",
        "meta": {
            "product": "METAR",
            "profile": "annex3",
            "cite": OOS_CITE,
            "reason": "Needs index-of / Saxon or richer mutation (Batch B leftover)",
        },
    }


def main() -> int:
    if not rust_available():
        print("native rust required", file=sys.stderr)
        return 1
    bases = [_convert(t) for t in _BASE_TACS]
    hits: dict[str, list[tuple[str, str]]] = {}
    for label, xml in _mutations(bases):
        for rid in _fired_rule_ids(xml):
            hits.setdefault(rid, []).append((label, xml))
    print(f"probed hits for {len(hits)} rules")
    for rid in sorted(hits):
        print(f"  HIT {rid} x{len(hits[rid])}")

    filled = residual = kept = 0
    for path in sorted(VALIDATE_DIR.glob("*.yml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        rule_id = str(data.get("rule_id") or path.stem)
        cases_out: list[dict[str, object]] = []
        pool = hits.get(rule_id, [])
        neg_i = 0
        for case in data.get("cases") or []:
            if not isinstance(case, dict):
                continue
            bucket = str(case.get("bucket") or "")
            case_id = str(case.get("case_id") or "")
            status = str(case.get("status") or "").lower()
            if bucket in {"happy", "edge_pass"} or (
                status == "ready" and bucket in {"sad", "edge_fail"}
            ):
                cases_out.append(case)
                if status == "ready" and bucket in {"sad", "edge_fail"}:
                    kept += 1
                continue
            if bucket in {"sad", "edge_fail"} and status == "oos":
                if pool:
                    label, xml = pool[neg_i % len(pool)]
                    neg_i += 1
                    cases_out.append(
                        _neg_case(
                            bucket=bucket,
                            case_id=case_id,
                            rule_id=rule_id,
                            xml=xml,
                            label=label,
                        )
                    )
                    filled += 1
                else:
                    cases_out.append(_oos_case(bucket=bucket, case_id=case_id))
                    residual += 1
            else:
                cases_out.append(case)
        path.write_text(
            yaml.safe_dump(
                {"rule_id": rule_id, "engine": "validate", "cases": cases_out},
                sort_keys=False,
                default_flow_style=False,
                allow_unicode=True,
            ),
            encoding="utf-8",
        )
    print(f"kept_ready_neg={kept} newly_filled={filled} oos_residual={residual}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
