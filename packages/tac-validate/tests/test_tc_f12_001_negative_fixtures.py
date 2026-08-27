"""TC-F12-001 / E10-21: negative fixture pack + diagnostics (T2.1/T2.2).

Manifest + fixture files always assert. Lint diagnostics assert expected codes
and spans once ``check_product_rules`` is encoded (T2.2).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from tac_validate import PRODUCTS, lint

FIXTURES = Path(__file__).resolve().parent / "fixtures"
MANIFEST_PATH = FIXTURES / "manifest.json"


def _load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _read_tac(rel: str) -> str:
    path = FIXTURES / rel
    assert path.is_file(), f"missing fixture: {path}"
    text = path.read_text(encoding="utf-8")
    assert text.strip(), f"empty fixture: {path}"
    return text


def _negative_cases() -> list[dict[str, Any]]:
    return list(_load_manifest()["negative"])


def _accept_cases() -> list[dict[str, Any]]:
    return list(_load_manifest()["accept"])


def _case_ids(cases: list[dict[str, Any]]) -> list[str]:
    return [str(c["id"]) for c in cases]


def test_manifest_schema_and_fixture_files_exist() -> None:
    data = _load_manifest()
    assert data["schema_version"] == 1
    assert "TAC_VALIDATION.md" in " ".join(data["cite"])
    products_seen: set[str] = set()
    for case in data["negative"]:
        assert case["product"] in PRODUCTS
        assert case["ok"] is False
        assert case["expected_codes"]
        assert (_read_tac(case["tac"])).strip()
        products_seen.add(case["product"])
        assert case["depth"] in {"full_checklist", "template_gate"}
    assert products_seen == set(PRODUCTS)
    for case in data["accept"]:
        assert case["product"] in PRODUCTS
        assert case["ok"] is True
        assert (_read_tac(case["tac"])).strip()


def test_negative_depth_split_matches_e10_21() -> None:
    """E10-21 depth split; F23/F24 deepen SIGMET/AIRMET to full_checklist for themes."""
    data = _load_manifest()
    for case in data["negative"]:
        product = case["product"]
        depth = case["depth"]
        if (
            product in {"METAR", "SPECI", "TAF"}
            or (product == "SIGMET" and case.get("theme") in {"G1", "G2", "V1", "V2", "C1"})
            or (product == "AIRMET" and case.get("theme") in {"A1", "A2", "EV050"})
        ):
            assert depth == "full_checklist"
        else:
            assert depth == "template_gate"


def test_full_checklist_products_have_multiple_negatives() -> None:
    data = _load_manifest()
    counts = {"METAR": 0, "SPECI": 0, "TAF": 0, "SIGMET": 0}
    for case in data["negative"]:
        if case["product"] in counts and case["depth"] == "full_checklist":
            counts[case["product"]] += 1
    assert counts["METAR"] >= 6
    assert counts["SPECI"] >= 3
    assert counts["TAF"] >= 3
    assert counts["SIGMET"] >= 3


def test_template_gate_products_covered() -> None:
    data = _load_manifest()
    gates = {c["product"] for c in data["negative"] if c["depth"] == "template_gate"}
    assert gates >= {"SIGMET", "AIRMET", "VAA", "TCA", "SWXA", "VONA"}
    assert gates == {"SIGMET", "AIRMET", "VAA", "TCA", "SWXA", "VONA"}


@pytest.mark.parametrize("case", _accept_cases(), ids=_case_ids(_accept_cases()))
def test_accept_fixtures_pass_parse_gate(case: dict[str, Any]) -> None:
    """Accept pack must clear parse-gate and product rules."""
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert not any(i.code == "MISSING_PRODUCT_KEYWORD" for i in report.issues)
    assert not any(i.code == "EMPTY_TAC" for i in report.issues)
    assert report.ok is True
    assert not any(i.severity == "error" for i in report.issues)


@pytest.mark.parametrize("case", _negative_cases(), ids=_case_ids(_negative_cases()))
def test_negative_fixtures_emit_expected_diagnostics(case: dict[str, Any]) -> None:
    """Product-rule diagnostics with codes, messages, and spans."""
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert report.ok is False
    codes = {i.code for i in report.issues if i.severity == "error"}
    for expected in case["expected_codes"]:
        assert expected in codes, f"{case['id']}: missing {expected} in {codes}"
    if case.get("require_spans"):
        matched = [i for i in report.issues if i.code in case["expected_codes"] and i.severity == "error"]
        assert matched, f"{case['id']}: no matching error issues"
        assert any(i.start is not None and i.end is not None and i.end > i.start for i in matched), (
            f"{case['id']}: expected start/end spans on diagnostics"
        )
        assert all(i.message.strip() for i in matched)
