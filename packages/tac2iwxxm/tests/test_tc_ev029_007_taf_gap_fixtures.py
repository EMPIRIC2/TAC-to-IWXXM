"""TC-EV029-007 / F20 deepen T4.1: TAF gap fixtures (lint + convert + validate).

M0 inventory: TAF standalone is covered; remaining deepen is FC/FT AHL body/BBB
matrix and multi-report (example-inventory §A TAF row; remine §B.3; FC/FT→LC/LT
+ BBB→reportStatus).

Product-order smoke (TC-EV029-007 pack seed for TAF) uses annex3 ``taf_a5_1``.
BBB→``reportStatus`` and ``split_bulletin(product=\"TAF\")`` are T4.2 code gaps
(AHL parse/filename keep-green from M1; TAF emitter ignores ``report_status`` IR
today; bulletin split rejects TAF until the FC/FT body splitter lands).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures"
TAF_FIXTURES = FIXTURES / "taf"
ANNEX3 = FIXTURES / "annex3_golden"

IWXXM_VERSION = "2025-2"
PROFILE = "annex3"

# Body has no COR/AMD keyword — status must come from AHL BBB (T4.2).
_BBB_CASES = (
    ("taf_ahl_normal.txt", None, "NORMAL", "FC", "LC"),
    ("taf_ahl_rra.txt", "RRA", "NORMAL", "FC", "LC"),
    ("taf_ahl_cca.txt", "CCA", "CORRECTION", "FC", "LC"),
    ("taf_ahl_aaa.txt", "AAA", "AMENDMENT", "FC", "LC"),
    ("taf_ahl_ft.txt", None, "NORMAL", "FT", "LT"),
)


def _read_taf(name: str) -> str:
    return (TAF_FIXTURES / name).read_text(encoding="utf-8")


def _ahl_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    raise AssertionError("fixture missing AHL line")


def _report_status_from_xml(xml: str) -> str | None:
    match = re.search(r'reportStatus="([^"]+)"', xml)
    return match.group(1) if match else None


def test_bulletin_meta_exposes_report_status_for_taf() -> None:
    """T4.2: BulletinMeta.report_status for TAF AHL CCA (additive; design-note §3.1)."""
    from tac2iwxxm import split_bulletin

    split = split_bulletin(_read_taf("taf_ahl_cca.txt"), product="TAF")
    assert getattr(split.meta, "report_status", None) == "CORRECTION"


@pytest.mark.parametrize(("fixture", "bbb", "status", "tac_tt", "iwxxm_tt"), _BBB_CASES)
def test_taf_ahl_bbb_parse_and_filename(
    fixture: str,
    bbb: str | None,
    status: str,
    tac_tt: str,
    iwxxm_tt: str,
) -> None:
    """AHL parse + FC→LC / FT→LT filename (M1 surface; keep-green for M4 pack)."""
    from datetime import UTC, datetime

    from tac2iwxxm import iwxxm_filename, parse_ahl

    text = _read_taf(fixture)
    parts = parse_ahl(_ahl_line(text))
    assert parts.tt == tac_tt
    assert parts.bbb == bbb
    assert parts.report_status == status
    assert parts.iwxxm_tt == iwxxm_tt
    name = iwxxm_filename(parts, issued_at=datetime(2026, 8, 2, 12, 0, 0, tzinfo=UTC))
    assert name.startswith(f"A_{iwxxm_tt}US31KJFK121200")
    assert f"A_{tac_tt}" not in name


@pytest.mark.parametrize(("fixture", "bbb", "status", "tac_tt", "iwxxm_tt"), _BBB_CASES)
def test_taf_ahl_bbb_applied_to_converted_xml(
    fixture: str,
    bbb: str | None,
    status: str,
    tac_tt: str,
    iwxxm_tt: str,
) -> None:
    """AHL BBB must drive @reportStatus even when TAC body has no COR/AMD (T4.2)."""
    from tac2iwxxm import convert, parse_ahl, split_bulletin

    assert tac_tt in {"FC", "FT"} and iwxxm_tt in {"LC", "LT"}
    split = split_bulletin(_read_taf(fixture), product="TAF")
    parts = parse_ahl(split.meta.ahl)
    assert parts.report_status == status
    assert split.meta.bbb == bbb

    result = convert(
        split.reports[0],
        product="TAF",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
        report_status=parts.report_status,
    )
    assert result.ok is True, f"convert failed for {fixture}: {result.issues!r}"
    assert result.xml is not None
    assert "iwxxm:TAF" in result.xml
    assert _report_status_from_xml(result.xml) == status


def test_taf_product_order_lint_convert_validate() -> None:
    """TC-EV029-007 TAF pack seed: lint → convert → XSD+SCH on accept fixture."""
    from iwxxm_validate import validate
    from tac_validate import lint

    from tac2iwxxm import convert

    tac = (ANNEX3 / "taf_a5_1.tac").read_text(encoding="utf-8")
    lint_report = lint(tac, product="TAF")
    assert lint_report.ok is True, [(i.code, i.message) for i in lint_report.issues]

    convert_result = convert(
        tac,
        product="TAF",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert convert_result.ok is True, convert_result.issues
    assert convert_result.xml is not None
    assert "iwxxm:TAF" in convert_result.xml

    validation = validate(
        convert_result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        levels=("xsd", "schematron"),
    )
    blocking = [i for i in validation.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
    assert not blocking, [(i.code, i.message) for i in blocking]


def test_taf_multi_ahl_lint_convert_validate_each_report() -> None:
    """Multi-report FC bulletin: each body report lint→convert→validate (shape deepen)."""
    from iwxxm_validate import validate
    from tac_validate import lint

    from tac2iwxxm import convert, split_bulletin

    split = split_bulletin(_read_taf("taf_multi_ahl.txt"), product="TAF")
    assert split.meta.report_count == 2
    for index, tac in enumerate(split.reports):
        lint_report = lint(tac, product="TAF")
        assert lint_report.ok is True, f"report[{index}] lint: {[(i.code, i.message) for i in lint_report.issues]}"
        convert_result = convert(
            tac,
            product="TAF",
            profile=PROFILE,
            iwxxm_version=IWXXM_VERSION,
        )
        assert convert_result.ok is True, f"report[{index}] convert: {convert_result.issues!r}"
        assert convert_result.xml is not None
        assert "iwxxm:TAF" in convert_result.xml
        validation = validate(
            convert_result.xml,
            iwxxm_version=IWXXM_VERSION,
            profile=PROFILE,
            levels=("xsd", "schematron"),
        )
        blocking = [i for i in validation.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
        assert not blocking, f"report[{index}] validate: {[(i.code, i.message) for i in blocking]}"
