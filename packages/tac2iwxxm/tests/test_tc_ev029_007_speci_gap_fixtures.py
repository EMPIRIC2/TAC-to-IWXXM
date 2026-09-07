"""TC-EV029-007 / F20 deepen T3.1: SPECI gap fixtures (lint + convert + validate).

M0 inventory: SPECI standalone is covered; remaining deepen is AHL body/BBB matrix
and multi-report (example-inventory §A SPECI row; remine §B.2; SP→LP / BBB→reportStatus).

Product-order smoke (TC-EV029-007 pack seed for SPECI) uses annex3 ``speci_a3_2``.
BBB→``reportStatus`` reuses the M2 ``convert(report_status=)`` surface (keep-green for SPECI).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures"
SPECI_FIXTURES = FIXTURES / "speci"
ANNEX3 = FIXTURES / "annex3_golden"

IWXXM_VERSION = "2025-2"
PROFILE = "annex3"

# Body has no COR/AMD keyword - status must come from AHL BBB (M2 surface).
_BBB_CASES = (
    ("speci_ahl_normal.txt", None, "NORMAL"),
    ("speci_ahl_rra.txt", "RRA", "NORMAL"),
    ("speci_ahl_cca.txt", "CCA", "CORRECTION"),
    ("speci_ahl_aaa.txt", "AAA", "AMENDMENT"),
)


def _read_speci(name: str) -> str:
    return (SPECI_FIXTURES / name).read_text(encoding="utf-8")


def _report_status_from_xml(xml: str) -> str | None:
    match = re.search(r'reportStatus="([^"]+)"', xml)
    return match.group(1) if match else None


def test_bulletin_meta_exposes_report_status_for_speci() -> None:
    """BulletinMeta.report_status for SPECI AHL CCA (additive; design-note §3.1)."""
    from tac2iwxxm import split_bulletin

    split = split_bulletin(_read_speci("speci_ahl_cca.txt"), product="SPECI")
    assert getattr(split.meta, "report_status", None) == "CORRECTION"


@pytest.mark.parametrize(("fixture", "bbb", "status"), _BBB_CASES)
def test_speci_ahl_bbb_parse_and_filename(fixture: str, bbb: str | None, status: str) -> None:
    """AHL parse + SP→LP filename (M1 surface; keep-green for M3 pack)."""
    from datetime import UTC, datetime

    from tac2iwxxm import iwxxm_filename, parse_ahl, split_bulletin

    text = _read_speci(fixture)
    split = split_bulletin(text, product="SPECI")
    assert split.meta.tt == "SP"
    assert split.meta.bbb == bbb
    assert split.meta.report_count == 1
    parts = parse_ahl(split.meta.ahl)
    assert parts.report_status == status
    assert parts.iwxxm_tt == "LP"
    name = iwxxm_filename(parts, issued_at=datetime(2026, 8, 2, 12, 30, 0, tzinfo=UTC))
    assert name.startswith("A_LPUS31KZNY121230")
    assert "A_SP" not in name


@pytest.mark.parametrize(("fixture", "bbb", "status"), _BBB_CASES)
def test_speci_ahl_bbb_applied_to_converted_xml(fixture: str, bbb: str | None, status: str) -> None:
    """AHL BBB must drive @reportStatus even when TAC body has no COR/AMD."""
    from tac2iwxxm import convert, parse_ahl, split_bulletin

    split = split_bulletin(_read_speci(fixture), product="SPECI")
    parts = parse_ahl(split.meta.ahl)
    assert parts.report_status == status
    assert split.meta.bbb == bbb

    result = convert(
        split.reports[0],
        product="SPECI",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
        report_status=parts.report_status,
    )
    assert result.ok is True, f"convert failed for {fixture}: {result.issues!r}"
    assert result.xml is not None
    assert "iwxxm:SPECI" in result.xml
    assert _report_status_from_xml(result.xml) == status


def test_speci_product_order_lint_convert_validate() -> None:
    """TC-EV029-007 SPECI pack seed: lint → convert → XSD+SCH on accept fixture."""
    from iwxxm_validate import validate
    from tac_validate import lint

    from tac2iwxxm import convert

    tac = (ANNEX3 / "speci_a3_2.tac").read_text(encoding="utf-8")
    lint_report = lint(tac, product="SPECI")
    assert lint_report.ok is True, [(i.code, i.message) for i in lint_report.issues]

    convert_result = convert(
        tac,
        product="SPECI",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert convert_result.ok is True, convert_result.issues
    assert convert_result.xml is not None
    assert "iwxxm:SPECI" in convert_result.xml

    validation = validate(
        convert_result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        levels=("xsd", "schematron"),
    )
    blocking = [i for i in validation.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
    assert not blocking, [(i.code, i.message) for i in blocking]


def test_speci_multi_ahl_lint_convert_validate_each_report() -> None:
    """Multi-report SP bulletin: each body report lint→convert→validate (shape deepen)."""
    from iwxxm_validate import validate
    from tac_validate import lint

    from tac2iwxxm import convert, split_bulletin

    split = split_bulletin(_read_speci("speci_multi_ahl.txt"), product="SPECI")
    assert split.meta.report_count == 2
    for index, tac in enumerate(split.reports):
        lint_report = lint(tac, product="SPECI")
        assert lint_report.ok is True, f"report[{index}] lint: {[(i.code, i.message) for i in lint_report.issues]}"
        convert_result = convert(
            tac,
            product="SPECI",
            profile=PROFILE,
            iwxxm_version=IWXXM_VERSION,
        )
        assert convert_result.ok is True, f"report[{index}] convert: {convert_result.issues!r}"
        assert convert_result.xml is not None
        assert "iwxxm:SPECI" in convert_result.xml
        validation = validate(
            convert_result.xml,
            iwxxm_version=IWXXM_VERSION,
            profile=PROFILE,
            levels=("xsd", "schematron"),
        )
        blocking = [i for i in validation.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
        assert not blocking, f"report[{index}] validate: {[(i.code, i.message) for i in blocking]}"
