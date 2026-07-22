"""TC-F20-001 — TAF/SPECI registry completeness (UJ-031 / ADR-028).

Pass criteria (docs/test-plan.md §TC-F20-001):

* Every TAF/SPECI lint emission uses a registered code
* Catalog export stays in sync for taf/speci-tagged rows
* CI fails on unknown codes; registry row required for new rules
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

import pytest

from tac_validate import lint
from tac_validate.issue_registry import ISSUES, by_code, catalog_entries

PACKAGE_SRC = Path(__file__).resolve().parents[1] / "src" / "tac_validate"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
MANIFEST_PATH = FIXTURES / "manifest.json"
REPO = Path(__file__).resolve().parents[3]
CATALOG_JSON = REPO / "docs" / "domain" / "rules" / "ISSUE_CATALOG.json"
CATALOG_MD = REPO / "docs" / "domain" / "rules" / "ISSUE_CATALOG.md"
_RULE_MODULES = (PACKAGE_SRC / "rules.py", PACKAGE_SRC / "product_rules.py")
_TAF_SPECI = frozenset({"TAF", "SPECI"})


def _load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _case_lists(manifest: dict[str, Any]) -> list[tuple[str, list[dict[str, Any]]]]:
    """Return (section, cases) for every list of fixture dicts with a product field."""
    out: list[tuple[str, list[dict[str, Any]]]] = []
    for key, value in manifest.items():
        if not isinstance(value, list) or not value:
            continue
        if not isinstance(value[0], dict) or "product" not in value[0]:
            continue
        out.append((key, list(value)))
    return out


def _taf_speci_cases(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for _section, rows in _case_lists(manifest):
        for case in rows:
            if case.get("product") in _TAF_SPECI:
                cases.append(case)
    return cases


def _assert_registered(code: str) -> None:
    by_code(code)  # raises KeyError if unknown


def _taf_speci_registry_rows() -> list[Any]:
    return [spec for spec in ISSUES if spec.product == "taf" or "taf" in spec.tags or "speci" in spec.tags]


def test_unknown_code_gate_rejects_unregistered_issue() -> None:
    with pytest.raises(KeyError):
        _assert_registered("NOT_REGISTERED_F20_XYZ")


def test_taf_speci_fixture_emissions_are_registered() -> None:
    """Every code emitted while linting TAF/SPECI fixtures is in the registry."""
    manifest = _load_manifest()
    cases = _taf_speci_cases(manifest)
    assert len(cases) >= 40, f"expected TAF/SPECI fixture pack; got {len(cases)}"

    seen: set[str] = set()
    for case in cases:
        tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
        report = lint(tac, product=case["product"])
        for issue in report.issues:
            seen.add(issue.code)
            _assert_registered(issue.code)

    assert seen, "expected at least one TAF/SPECI lint emission from fixtures"


def test_taf_speci_expected_codes_subset_of_registry() -> None:
    """Every expected_codes entry on TAF/SPECI fixtures is registered."""
    manifest = _load_manifest()
    expected: set[str] = set()
    for case in _taf_speci_cases(manifest):
        for code in case.get("expected_codes", []):
            expected.add(code)
            _assert_registered(code)
    assert expected, "expected TAF/SPECI expected_codes in manifest sections"


def test_taf_product_registry_rows_appear_in_fixtures() -> None:
    """Every product=taf registry row is exercised by a TAF fixture expected_codes."""
    manifest = _load_manifest()
    covered: set[str] = set()
    for case in _taf_speci_cases(manifest):
        if case.get("product") != "TAF":
            continue
        covered.update(case.get("expected_codes", []))

    missing = sorted(spec.code for spec in ISSUES if spec.product == "taf" and spec.code not in covered)
    assert missing == [], f"TAF registry rows missing fixture expected_codes: {missing}"


def test_catalog_includes_taf_speci_registry_rows() -> None:
    """ISSUE_CATALOG export lists every taf/speci-tagged registry code (ADR-028)."""
    assert CATALOG_JSON.is_file(), "missing ISSUE_CATALOG.json — run make catalog-regen"
    assert CATALOG_MD.is_file(), "missing ISSUE_CATALOG.md — run make catalog-regen"

    payload = json.loads(CATALOG_JSON.read_text(encoding="utf-8"))
    catalog_codes = {row["code"] for row in payload["issues"]}
    md = CATALOG_MD.read_text(encoding="utf-8")

    rows = _taf_speci_registry_rows()
    assert rows, "expected taf/speci-tagged registry rows"
    for spec in rows:
        assert spec.code in catalog_codes, f"catalog JSON missing {spec.code}"
        assert f"`{spec.code}`" in md, f"catalog MD missing {spec.code}"


def test_catalog_entries_filters_taf_and_speci() -> None:
    taf_codes = {spec.code for spec in catalog_entries(product="taf")}
    assert "MISSING_VALIDITY" in taf_codes
    assert "INVALID_PROB" in taf_codes
    assert "MISSING_OBS_TIME" not in taf_codes

    speci_codes = {spec.code for spec in catalog_entries(product="SPECI")}
    assert "MISSING_OBS_TIME" in speci_codes
    assert "MISSING_TERMINATOR" in speci_codes
    assert "MISSING_VALIDITY" not in speci_codes


def _string_const(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _codes_from_call(node: ast.Call) -> list[str]:
    codes: list[str] = []
    func_name = node.func.id if isinstance(node.func, ast.Name) else ""
    for kw in node.keywords:
        if kw.arg == "code":
            value = _string_const(kw.value)
            if value is not None:
                codes.append(value)
    if func_name in {"_issue", "issue_from"} and node.args:
        value = _string_const(node.args[0])
        if value is not None:
            codes.append(value)
    return codes


def test_rule_module_issue_code_literals_are_registered() -> None:
    """Static scan: Issue/_issue/issue_from string codes must be registered."""
    found: set[str] = set()
    for path in _RULE_MODULES:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = node.func.id if isinstance(node.func, ast.Name) else ""
            if name not in {"Issue", "_issue", "issue_from"}:
                continue
            for code in _codes_from_call(node):
                found.add(code)
                _assert_registered(code)
    assert found, "expected Issue/_issue/issue_from code literals in rule modules"
