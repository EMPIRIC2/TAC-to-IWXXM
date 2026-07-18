"""TC-F12-001 / E10-21: negative fixture pack + diagnostics (T2.1).

Manifest + fixture files always assert. Lint diagnostic expectations are
``xfail(strict=True)`` until T2.2 encodes ``check_product_rules``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tac_validate import PRODUCTS, lint

FIXTURES = Path(__file__).resolve().parent / "fixtures"
MANIFEST_PATH = FIXTURES / "manifest.json"

_T22_REASON = "T2.2: encode check_product_rules for F12 checklist/template gates"


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
    data = _load_manifest()
    for case in data["negative"]:
        if case["product"] in {"METAR", "SPECI", "TAF"}:
            assert case["depth"] == "full_checklist"
        else:
            assert case["depth"] == "template_gate"


def test_full_checklist_products_have_multiple_negatives() -> None:
    data = _load_manifest()
    counts = {"METAR": 0, "SPECI": 0, "TAF": 0}
    for case in data["negative"]:
        if case["product"] in counts:
            counts[case["product"]] += 1
    assert counts["METAR"] >= 6
    assert counts["SPECI"] >= 3
    assert counts["TAF"] >= 3


def test_template_gate_products_covered() -> None:
    data = _load_manifest()
    gates = {c["product"] for c in data["negative"] if c["depth"] == "template_gate"}
    assert gates == {"SIGMET", "AIRMET", "VAA", "TCA"}


@pytest.mark.parametrize("case", _accept_cases(), ids=_case_ids(_accept_cases()))
def test_accept_fixtures_pass_parse_gate(case: dict[str, Any]) -> None:
    """Accept pack must clear parse-gate (product keyword present)."""
    report = lint(_read_tac(case["tac"]), product=case["product"])
    assert not any(i.code == "MISSING_PRODUCT_KEYWORD" for i in report.issues)
    assert not any(i.code == "EMPTY_TAC" for i in report.issues)


@pytest.mark.xfail(strict=True, reason=_T22_REASON)
@pytest.mark.parametrize("case", _negative_cases(), ids=_case_ids(_negative_cases()))
def test_negative_fixtures_emit_expected_diagnostics(case: dict[str, Any]) -> None:
    """Product-rule diagnostics — red until T2.2 implements checklist/gates."""
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
