"""TC-F15-001 — CI gate: every emitted Issue.code must be registered (E11-27).

Fails CI when rules emit an unknown code (ADR-028 / F15). Complements the registry
API tests in ``test_tc_f15_001_issue_registry.py``.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from tac_validate import PRODUCTS, lint
from tac_validate.issue_registry import by_code
from tac_validate.models import Issue

PACKAGE_SRC = Path(__file__).resolve().parents[1] / "src" / "tac_validate"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
MANIFEST_PATH = FIXTURES / "manifest.json"
_RULE_MODULES = (PACKAGE_SRC / "rules.py", PACKAGE_SRC / "product_rules.py")


def _assert_registered(code: str) -> None:
    by_code(code)  # raises KeyError if unknown


def test_unknown_code_gate_rejects_unregistered_issue() -> None:
    """Explicit gate: constructing a finding with a bogus code must fail lookup."""
    bogus = Issue(severity="error", code="NOT_REGISTERED_XYZ", message="x")
    with pytest.raises(KeyError):
        _assert_registered(bogus.code)


def test_lint_fixture_emissions_are_registered() -> None:
    """Every code emitted while linting accept/negative fixtures is in the registry."""
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    seen: set[str] = set()

    for case in data["accept"] + data["negative"]:
        tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
        report = lint(tac, product=case["product"])
        for issue in report.issues:
            seen.add(issue.code)
            _assert_registered(issue.code)

    # Parse-gate edges not always covered by fixture packs.
    for tac, product in (
        ("", "METAR"),
        ("KJFK 101851Z 24008KT 10SM FEW250 15/07 A3034", "METAR"),
        ("METAR KJFK 101851Z 24008KT 10SM FEW250 15/07 A3034", "METAR"),
        ("not-a-product", "NOPE"),
    ):
        product_arg = product if product in PRODUCTS or product == "NOPE" else "METAR"
        if product == "NOPE":
            report = lint(tac, product="NOPE")  # type: ignore[arg-type]
        else:
            report = lint(tac, product=product_arg)
        for issue in report.issues:
            seen.add(issue.code)
            _assert_registered(issue.code)

    assert seen, "expected at least one emitted lint code from fixtures/edges"


def _string_const(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _codes_from_issue_call(node: ast.Call) -> list[str]:
    """Extract code= kwargs or positional string from Issue(...) / _issue(...)."""
    codes: list[str] = []
    for kw in node.keywords:
        if kw.arg == "code":
            value = _string_const(kw.value)
            if value is not None:
                codes.append(value)
    # _issue("CODE", "message", ...) — first positional is the code.
    func_name = node.func.id if isinstance(node.func, ast.Name) else ""
    if func_name == "_issue" and node.args:
        value = _string_const(node.args[0])
        if value is not None:
            codes.append(value)
    return codes


def test_rule_module_issue_code_literals_are_registered() -> None:
    """Static scan: Issue/_issue string codes in rule modules must be registered.

    Remains useful until T2.2 migrates emissions onto ``issue_from`` exclusively.
    """
    found: set[str] = set()
    for path in _RULE_MODULES:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = ""
            if isinstance(node.func, ast.Name):
                name = node.func.id
            if name not in {"Issue", "_issue"}:
                continue
            for code in _codes_from_issue_call(node):
                found.add(code)
                _assert_registered(code)
    assert found, "expected Issue/_issue code literals in rule modules"
