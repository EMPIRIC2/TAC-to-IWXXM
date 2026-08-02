"""TC-F6-031 / UJ-012: tac-validate msgspec issues + optional fixes.

Spec: docs/test-plan.md TC-F6-031; docs/api-contract.md lint-tac; ADR-015/016 (Q9=C).
"""

from __future__ import annotations

import ast
from pathlib import Path

import msgspec
import pytest

PACKAGE_SRC = Path(__file__).resolve().parents[1] / "src" / "tac_validate"

PRODUCTS = ("AIRMET", "METAR", "SIGMET", "SPECI", "TAF", "VAA", "TCA", "SWXA")


def test_lint_exports_public_entrypoints() -> None:
    import tac_validate

    assert callable(getattr(tac_validate, "lint", None))
    assert getattr(tac_validate, "Issue", None) is not None
    assert getattr(tac_validate, "Fix", None) is not None
    assert getattr(tac_validate, "LintReport", None) is not None
    assert getattr(tac_validate, "PRODUCTS", None) == PRODUCTS


def test_issue_fix_report_are_msgspec_structs() -> None:
    from tac_validate import Fix, Issue, LintReport

    assert issubclass(Issue, msgspec.Struct)
    assert issubclass(Fix, msgspec.Struct)
    assert issubclass(LintReport, msgspec.Struct)


def test_lint_empty_tac_fails_with_issues() -> None:
    """Parse-gate failure must return non-empty issues (TC-F6-031)."""
    from tac_validate import lint

    report = lint("", product="METAR")
    assert report.ok is False
    assert len(report.issues) >= 1
    assert all(hasattr(i, "severity") and hasattr(i, "code") and hasattr(i, "message") for i in report.issues)


def test_lint_metar_missing_keyword_fails() -> None:
    from tac_validate import lint

    report = lint("KJFK 101851Z 24008KT 10SM FEW250 15/07 A3034", product="METAR")
    assert report.ok is False
    assert any(i.severity == "error" for i in report.issues)


def test_lint_valid_metar_skeleton_passes() -> None:
    from tac_validate import lint

    report = lint(
        "METAR KJFK 101851Z 24008KT 10SM FEW250 15/07 A3034=",
        product="METAR",
    )
    assert report.ok is True
    assert report.issues == []


def test_lint_optional_fixes_on_repairable_input() -> None:
    """When a rule can suggest a repair, fixes[] is populated (Q9=C)."""
    from tac_validate import lint

    # Missing trailing '=' — skeleton may offer normalize_terminator fix
    report = lint(
        "METAR KJFK 101851Z 24008KT 10SM FEW250 15/07 A3034",
        product="METAR",
    )
    assert isinstance(report.fixes, list)
    if report.ok is False:
        # Either issues without fixes, or issues with optional fixes — never silent success
        assert len(report.issues) >= 1
    # If the skeleton offers a terminator fix, shape must match API contract
    for fix in report.fixes:
        assert hasattr(fix, "code") and hasattr(fix, "message")
        assert hasattr(fix, "replacement")


def test_lint_unknown_product_fails() -> None:
    from tac_validate import lint

    report = lint("METAR KJFK 101851Z 24008KT 10SM FEW250 15/07 A3034=", product="NOTAPRODUCT")
    assert report.ok is False
    assert any(i.code == "UNKNOWN_PRODUCT" for i in report.issues)


@pytest.mark.parametrize("product", PRODUCTS)
def test_lint_accepts_all_seven_products(product: str) -> None:
    """Rule-pack skeleton must accept each product id (F6 + F28 SWXA)."""
    from tac_validate import lint

    # Empty input fails parse gate for every product — proves product dispatch exists
    report = lint("", product=product)
    assert report.product == product
    assert report.ok is False
    assert len(report.issues) >= 1


def test_codec_roundtrip_lint_report() -> None:
    from tac_validate import Fix, Issue, LintReport
    from tac_validate.codec import json_decoder, json_encoder

    report = LintReport(
        ok=False,
        product="METAR",
        issues=[Issue(severity="error", code="rule_x", message="bad", location="wind")],
        fixes=[Fix(code="normalize_wind", message="fix wind", replacement="12010KT")],
    )
    decoded = json_decoder.decode(json_encoder.encode(report))
    assert decoded.ok is False
    assert decoded.issues[0].code == "rule_x"
    assert decoded.fixes[0].replacement == "12010KT"


def test_package_has_no_fastapi_or_supabase_imports() -> None:
    forbidden = {"fastapi", "supabase"}
    for path in PACKAGE_SRC.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name.split(".", 1)[0] not in forbidden
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".", 1)[0] not in forbidden
