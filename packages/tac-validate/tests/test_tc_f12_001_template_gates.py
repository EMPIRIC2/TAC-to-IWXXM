"""TC-F12-001 template+gate coverage for SIGMET/AIRMET/VAA/TCA (T2.1/T2.2)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tac_validate import PRODUCTS, lint
from tac_validate.product_rules import check_product_rules

FIXTURES = Path(__file__).resolve().parent / "fixtures"
MANIFEST_PATH = FIXTURES / "manifest.json"


def _template_cases() -> list[dict[str, Any]]:
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return [c for c in data["negative"] if c["depth"] == "template_gate"]


def _ids(cases: list[dict[str, Any]]) -> list[str]:
    return [str(c["id"]) for c in cases]


def test_template_gate_manifest_cites_a6_or_a2() -> None:
    for case in _template_cases():
        cite = str(case.get("cite", ""))
        assert "A6" in cite or "A2" in cite, case["id"]


def test_product_rules_dispatch_covers_all_seven_products() -> None:
    """Coverage matrix gate: every F6 product has a product_rules path."""
    samples = {
        "METAR": "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=",
        "SPECI": "SPECI KJFK 232045Z 20015G25KT 8SM -SN BKN020 OVC040 12/06 A3001=",
        "TAF": "TAF YUDO 151800Z 1600/1618 13005MPS 9000 BKN020=",
        "SIGMET": (
            "YUDD SIGMET 2 VALID 101200/101600 YUSO-\n"
            "YUDD SHANLON FIR/UIR OBSC TS FCST S OF N54 TOP FL390 MOV E 20KT WKN="
        ),
        "AIRMET": (
            "YUDD AIRMET 1 VALID 151520/151800 YUSO-\nYUDD SHANLON FIR ISOL TS OBS N OF S50 TOP ABV FL100 STNR WKN="
        ),
        "VAA": "VA ADVISORY\nDTG: 20240923/0130Z\nVAAC: TOKYO\n",
        "TCA": "TC ADVISORY\nDTG: 20040925/1900Z\nMAX WIND: 22MPS\n",
    }
    assert set(samples) == set(PRODUCTS)
    for product, tac in samples.items():
        assert check_product_rules(tac, product) == []


@pytest.mark.parametrize("case", _template_cases(), ids=_ids(_template_cases()))
def test_template_gate_diagnostics_are_actionable(case: dict[str, Any]) -> None:
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    report = lint(tac, product=case["product"])
    assert report.ok is False
    errors = [i for i in report.issues if i.severity == "error"]
    assert errors
    for code in case["expected_codes"]:
        hit = next(i for i in errors if i.code == code)
        assert hit.message
        assert hit.start is not None and hit.end is not None
        assert hit.end > hit.start
