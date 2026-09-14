#!/usr/bin/env python3
"""Fill validate/metar_speci needs-fixture slots (EV-970 S3).

Happy + edge_pass → ready convert-then-validate smoke (verified).
Sad + edge_fail → oos with cite (SCH-specific negatives deferred).

[Corpus: decisions §ev-970-s3-validate-fill]
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml
from iwxxm_validate import validate as validate_iwxxm

from tac2iwxxm import convert as convert_tac

ROOT = Path(__file__).resolve().parents[2]
VALIDATE_DIR = ROOT / "tests/quality_matrices/testdata/validate/metar_speci"
CITE_READY = "EV-970-S3 validate convert-then-validate smoke"
CITE_OOS = "#970 EV-970-S3 validate SCH negative deferred"

# Thematic TAC pool — probed convert+validate accept before write.
_HAPPY_TACS: list[tuple[str, str]] = [
    ("METAR", "METAR KJFK 121251Z 18008KT 10SM FEW250 22/12 A3012="),
    ("METAR", "METAR KSEA 231800Z 27008KT 10SM SCT025 14/06 A3004="),
    ("METAR", "METAR KBOS 151955Z 22012G20KT 5SM -RA BR BKN012 OVC025 18/16 A2988="),
    ("METAR", "METAR KDEN 101755Z 36015KT 10SM FEW080 SCT120 05/M08 A3035="),
    ("SPECI", "SPECI KJFK 232045Z 20015G25KT 8SM -SN BKN020 OVC040 12/06 A3001="),
]

_EDGE_PASS_TACS: list[tuple[str, str]] = [
    ("METAR", "METAR KJFK 121251Z 18008KT 10SM FEW250 22/12 A3012"),  # missing =
    ("METAR", "METAR  KJFK  121251Z 18008KT 10SM FEW250 22/12 A3012="),
    ("METAR", "METAR KJFK 121251Z 18008KT 10SM FEW250 22/12 A3012 RMK AO2="),
    ("METAR", "METAR KORD 120650Z 27010KT 10SM CLR M02/M08 A3041="),
    ("SPECI", "SPECI KSEA 231910Z 25012KT 3SM BR BKN008 11/10 A2995="),
]


def _probe(product: str, tac: str) -> bool:
    result = convert_tac(tac, product=product, profile="annex3", iwxxm_version="2025-2")
    if not result.ok or not result.xml:
        return False
    report = validate_iwxxm(result.xml, iwxxm_version="2025-2", profile="annex3")
    return bool(report.ok)


def _ready_case(
    *,
    bucket: str,
    case_id: str,
    product: str,
    tac: str,
) -> dict[str, object]:
    return {
        "bucket": bucket,
        "case_id": case_id,
        "status": "ready",
        "tac": tac,
        "expect": {"accept": True},
        "meta": {
            "product": product,
            "profile": "annex3",
            "iwxxm_version": "2025-2",
            "cite": CITE_READY,
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
            "cite": CITE_OOS,
            "reason": "Schematron-specific negative not authored this cycle",
        },
    }


def fill_file(path: Path) -> tuple[int, int]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"bad yaml: {path}")
    rule_id = data.get("rule_id") or path.stem
    cases_out: list[dict[str, object]] = []
    ready_n = 0
    oos_n = 0
    happy_i = 0
    edge_i = 0
    for case in data.get("cases") or []:
        if not isinstance(case, dict):
            continue
        bucket = str(case.get("bucket") or "")
        case_id = str(case.get("case_id") or "")
        status = str(case.get("status") or "").lower()
        if status == "ready" and isinstance(case.get("tac"), str):
            # Keep existing ready smoke slots.
            cases_out.append(case)
            ready_n += 1
            continue
        if bucket in {"happy"}:
            product, tac = _HAPPY_TACS[happy_i % len(_HAPPY_TACS)]
            happy_i += 1
            cases_out.append(
                _ready_case(bucket=bucket, case_id=case_id, product=product, tac=tac)
            )
            ready_n += 1
        elif bucket == "edge_pass":
            product, tac = _EDGE_PASS_TACS[edge_i % len(_EDGE_PASS_TACS)]
            edge_i += 1
            cases_out.append(
                _ready_case(bucket=bucket, case_id=case_id, product=product, tac=tac)
            )
            ready_n += 1
        elif bucket in {"sad", "edge_fail"}:
            cases_out.append(_oos_case(bucket=bucket, case_id=case_id))
            oos_n += 1
        else:
            cases_out.append(_oos_case(bucket=bucket or "sad", case_id=case_id or "01"))
            oos_n += 1

    out = {"rule_id": rule_id, "engine": "validate", "cases": cases_out}
    path.write_text(
        yaml.safe_dump(
            out, sort_keys=False, default_flow_style=False, allow_unicode=True
        ),
        encoding="utf-8",
    )
    return ready_n, oos_n


def main() -> int:
    for product, tac in (*_HAPPY_TACS, *_EDGE_PASS_TACS):
        if not _probe(product, tac):
            print(f"probe failed: {product} {tac!r}", file=sys.stderr)
            return 1
    total_ready = total_oos = 0
    for path in sorted(VALIDATE_DIR.glob("*.yml")):
        ready_n, oos_n = fill_file(path)
        total_ready += ready_n
        total_oos += oos_n
        print(f"{path.name}: ready={ready_n} oos={oos_n}")
    print(f"TOTAL ready={total_ready} oos={total_oos}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
