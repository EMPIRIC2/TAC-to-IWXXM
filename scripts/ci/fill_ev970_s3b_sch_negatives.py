#!/usr/bin/env python3
"""Fill validate/metar_speci sad+edge_fail with probed Schematron negatives (EV-970 S3b).

Requires native ``iwxxm_validate._rust`` (``make build-iwxxm-validate-native``).

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
CITE = "EV-970-S3b Schematron negative (native)"
OOS_CITE = "#970 EV-970-S3b SCH negative — residual XPath2/codelist (document/index-of)"

_BASE_TAC = "METAR KJFK 121251Z 18008KT 10SM FEW250 22/12 A3012="


def _base_xml() -> str:
    result = convert_tac(
        _BASE_TAC, product="METAR", profile="annex3", iwxxm_version="2025-2"
    )
    if not result.ok or not result.xml:
        raise RuntimeError("base convert failed")
    return result.xml


def _mutations(base: str) -> list[tuple[str, str]]:
    """Return (label, mutated_xml) candidates."""
    out: list[tuple[str, str]] = []
    out.append(
        (
            "amendment",
            base.replace('reportStatus="NORMAL"', 'reportStatus="AMENDMENT"', 1),
        )
    )
    out.append(
        (
            "cloud_vv_and_layer",
            base.replace(
                "<iwxxm:AerodromeCloud>",
                (
                    "<iwxxm:AerodromeCloud>"
                    '<iwxxm:verticalVisibility uom="[ft_i]">500'
                    "</iwxxm:verticalVisibility>"
                ),
                1,
            ),
        )
    )
    # Wrong cloud VV uom only (needs VV present, no layers) — strip layers first
    cloud_only_vv = re.sub(
        r"<iwxxm:AerodromeCloud>.*?</iwxxm:AerodromeCloud>",
        (
            "<iwxxm:AerodromeCloud>"
            '<iwxxm:verticalVisibility uom="deg">500</iwxxm:verticalVisibility>'
            "</iwxxm:AerodromeCloud>"
        ),
        base,
        count=1,
        flags=re.S,
    )
    out.append(("cloud_vv_bad_uom", cloud_only_vv))
    # Temperature uom
    out.append(
        (
            "air_temp_bad_uom",
            re.sub(
                r'(<iwxxm:airTemperature[^>]*uom=")[^"]*"',
                r'\1K"',
                base,
                count=1,
            ),
        )
    )
    out.append(
        (
            "dewpoint_bad_uom",
            re.sub(
                r'(<iwxxm:dewpointTemperature[^>]*uom=")[^"]*"',
                r'\1K"',
                base,
                count=1,
            ),
        )
    )
    out.append(
        (
            "qnh_bad_uom",
            re.sub(r'(<iwxxm:qnh[^>]*uom=")[^"]*"', r'\1Pa"', base, count=1),
        )
    )
    # Wind direction uom / variableDirection exclusivity
    out.append(
        (
            "wind_dir_bad_uom",
            re.sub(
                r'(<iwxxm:meanWindDirection[^>]*uom=")[^"]*"',
                r'\1rad"',
                base,
                count=1,
            ),
        )
    )
    out.append(
        (
            "wind_speed_bad_uom",
            re.sub(
                r'(<iwxxm:meanWindSpeed[^>]*uom=")[^"]*"',
                r'\1m/s"',
                base,
                count=1,
            ),
        )
    )
    # variableDirection=true with meanWindDirection present
    if "variableDirection=" in base:
        out.append(
            (
                "variable_dir_with_mean",
                re.sub(
                    r'variableDirection="false"',
                    'variableDirection="true"',
                    base,
                    count=1,
                ),
            )
        )
    else:
        out.append(
            (
                "variable_dir_with_mean",
                re.sub(
                    r"(<iwxxm:AerodromeSurfaceWind\b)",
                    r'\1 variableDirection="true"',
                    base,
                    count=1,
                ),
            )
        )
    # cloudAndVisibilityOK true with cloud present
    if "cloudAndVisibilityOK=" in base:
        out.append(
            (
                "cavok_with_cloud",
                re.sub(
                    r'cloudAndVisibilityOK="false"',
                    'cloudAndVisibilityOK="true"',
                    base,
                    count=1,
                ),
            )
        )
    # Bad RVR uom if present — inject minimal RVR block
    rvr_xml = base.replace(
        "</iwxxm:MeteorologicalAerodromeObservation>",
        (
            "<iwxxm:rvr><iwxxm:AerodromeRunwayVisualRange>"
            '<iwxxm:meanRVR uom="[ft_i]">600</iwxxm:meanRVR>'
            "</iwxxm:AerodromeRunwayVisualRange></iwxxm:rvr>"
            "</iwxxm:MeteorologicalAerodromeObservation>"
        ),
        1,
    )
    out.append(("rvr_bad_uom", rvr_xml))
    return out


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
            "reason": "No probed native SCH mutation for this pattern yet",
        },
    }


def main() -> int:
    if not rust_available():
        print("native rust required", file=sys.stderr)
        return 1
    base = _base_xml()
    # rule_id -> list of (label, xml) that fire it
    hits: dict[str, list[tuple[str, str]]] = {}
    for label, xml in _mutations(base):
        if xml == base:
            continue
        for rid in _fired_rule_ids(xml):
            hits.setdefault(rid, []).append((label, xml))
            print(f"HIT {rid} via {label}")

    ready_n = oos_n = 0
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
            if bucket in {"happy", "edge_pass"}:
                cases_out.append(case)
                continue
            if bucket in {"sad", "edge_fail"}:
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
                    ready_n += 1
                else:
                    cases_out.append(_oos_case(bucket=bucket, case_id=case_id))
                    oos_n += 1
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
        status = "filled" if pool else "oos-residual"
        print(f"{path.name}: {status} pool={len(pool)}")

    print(f"TOTAL neg_ready={ready_n} oos_residual={oos_n} rules_hit={len(hits)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
