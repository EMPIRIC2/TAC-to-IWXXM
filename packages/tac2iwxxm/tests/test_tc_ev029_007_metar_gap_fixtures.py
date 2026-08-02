"""TC-EV029-007 / F15 deepen T2.1: METAR gap fixtures (lint + convert + validate).

M0 inventory: METAR is mostly covered; remaining deepen is AHL body/BBB matrix
(example-inventory §C SA row; remine §B.1; IWXXM_CONVERSION §BBB → reportStatus).

Product-order smoke (TC-EV029-007 pack seed for METAR) uses a lint-clean accept
fixture. BBB→``reportStatus`` on convert is the T2.2 code gap (AHL CCA/AAA today
parse correctly but XML stays NORMAL when the TAC body has no COR/AMD keyword).
"""

from __future__ import annotations

import inspect
import re
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures"
METAR_FIXTURES = FIXTURES / "metar"
ANNEX3 = FIXTURES / "annex3_golden"

IWXXM_VERSION = "2025-2"
PROFILE = "annex3"

# Body has no COR/AMD keyword — status must come from AHL BBB (T2.2).
_BBB_CASES = (
    ("metar_ahl_normal.txt", None, "NORMAL"),
    ("metar_ahl_rra.txt", "RRA", "NORMAL"),
    ("metar_ahl_cca.txt", "CCA", "CORRECTION"),
    ("metar_ahl_aaa.txt", "AAA", "AMENDMENT"),
)


def _read_metar(name: str) -> str:
    return (METAR_FIXTURES / name).read_text(encoding="utf-8")


def _report_status_from_xml(xml: str) -> str | None:
    match = re.search(r'reportStatus="([^"]+)"', xml)
    return match.group(1) if match else None


def test_convert_accepts_report_status_kwarg() -> None:
    """T2.2: ``convert(..., report_status=)`` applies AHL BBB → IWXXM reportStatus."""
    from tac2iwxxm import convert

    assert "report_status" in inspect.signature(convert).parameters, (
        "convert must accept report_status for AHL BBB→reportStatus (EV-029 M2 / #823 B3)"
    )


def test_bulletin_meta_exposes_report_status() -> None:
    """T2.2: BulletinMeta carries derived report_status (additive; design-note §3.1)."""
    from tac2iwxxm import split_bulletin

    split = split_bulletin(_read_metar("metar_ahl_cca.txt"), product="METAR")
    assert getattr(split.meta, "report_status", None) == "CORRECTION"


@pytest.mark.parametrize(("fixture", "bbb", "status"), _BBB_CASES)
def test_metar_ahl_bbb_parse_and_filename(fixture: str, bbb: str | None, status: str) -> None:
    """AHL parse + SA→LA filename (M1 surface; keep-green for M2 pack)."""
    from datetime import UTC, datetime

    from tac2iwxxm import iwxxm_filename, parse_ahl, split_bulletin

    text = _read_metar(fixture)
    split = split_bulletin(text, product="METAR")
    assert split.meta.tt == "SA"
    assert split.meta.bbb == bbb
    assert split.meta.report_count == 1
    parts = parse_ahl(split.meta.ahl)
    assert parts.report_status == status
    assert parts.iwxxm_tt == "LA"
    name = iwxxm_filename(parts, issued_at=datetime(2026, 8, 2, 12, 0, 0, tzinfo=UTC))
    assert name.startswith("A_LAUS31KZNY121200")
    assert "A_SA" not in name


@pytest.mark.parametrize(("fixture", "bbb", "status"), _BBB_CASES)
def test_metar_ahl_bbb_applied_to_converted_xml(fixture: str, bbb: str | None, status: str) -> None:
    """AHL BBB must drive @reportStatus even when TAC body has no COR/AMD (T2.2)."""
    from tac2iwxxm import convert, parse_ahl, split_bulletin

    split = split_bulletin(_read_metar(fixture), product="METAR")
    parts = parse_ahl(split.meta.ahl)
    assert parts.report_status == status
    assert split.meta.bbb == bbb

    result = convert(
        split.reports[0],
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
        report_status=parts.report_status,
    )
    assert result.ok is True, f"convert failed for {fixture}: {result.issues!r}"
    assert result.xml is not None
    assert "iwxxm:METAR" in result.xml
    assert _report_status_from_xml(result.xml) == status


def test_metar_product_order_lint_convert_validate() -> None:
    """TC-EV029-007 METAR pack seed: lint → convert → XSD+SCH on accept fixture."""
    from iwxxm_validate import validate
    from tac_validate import lint

    from tac2iwxxm import convert

    tac = (ANNEX3 / "metar_basic.tac").read_text(encoding="utf-8")
    lint_report = lint(tac, product="METAR")
    assert lint_report.ok is True, [(i.code, i.message) for i in lint_report.issues]

    convert_result = convert(
        tac,
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert convert_result.ok is True, convert_result.issues
    assert convert_result.xml is not None
    assert "iwxxm:METAR" in convert_result.xml

    validation = validate(
        convert_result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        levels=("xsd", "schematron"),
    )
    blocking = [i for i in validation.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
    assert not blocking, [(i.code, i.message) for i in blocking]


def test_metar_multi_ahl_lint_convert_validate_each_report() -> None:
    """Multi-report SA bulletin: each body report lint→convert→validate (shape deepen)."""
    from iwxxm_validate import validate
    from tac_validate import lint

    from tac2iwxxm import convert, split_bulletin

    split = split_bulletin((FIXTURES / "metar_multi_ahl.txt").read_text(encoding="utf-8"), product="METAR")
    assert split.meta.report_count == 2
    for index, tac in enumerate(split.reports):
        lint_report = lint(tac, product="METAR")
        assert lint_report.ok is True, f"report[{index}] lint: {[(i.code, i.message) for i in lint_report.issues]}"
        convert_result = convert(
            tac,
            product="METAR",
            profile=PROFILE,
            iwxxm_version=IWXXM_VERSION,
        )
        assert convert_result.ok is True, f"report[{index}] convert: {convert_result.issues!r}"
        assert convert_result.xml is not None
        assert "iwxxm:METAR" in convert_result.xml
        validation = validate(
            convert_result.xml,
            iwxxm_version=IWXXM_VERSION,
            profile=PROFILE,
            levels=("xsd", "schematron"),
        )
        blocking = [i for i in validation.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
        assert not blocking, f"report[{index}] validate: {[(i.code, i.message) for i in blocking]}"
