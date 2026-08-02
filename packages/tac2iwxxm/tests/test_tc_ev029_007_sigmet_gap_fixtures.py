"""TC-EV029-007 / F23 deepen T5.1: general SIGMET gap fixtures (lint + convert + validate).

M0 inventory: SIGMET standalone is covered (G1–G3 / A6-1a/1b); remaining deepen is
WS AHL body/BBB matrix and multi-report (example-inventory §A SIGMET gen row; remine
§B.4; WS→LS + BBB→reportStatus). CNL covered via A6-1b seed + AHL CNL fixture.

Product-order smoke (TC-EV029-007 pack seed for gen SIGMET) uses annex3
``sigmet_a6_1a_ts``. BBB→``reportStatus`` reuses ``convert(report_status=)`` with
SIGMET emitter honor (T5.2); ``split_bulletin(product=\"SIGMET\")`` accepts WS AHL
bodies.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures"
SIGMET_FIXTURES = FIXTURES / "sigmet"
ANNEX3 = FIXTURES / "annex3_golden"

IWXXM_VERSION = "2025-2"
PROFILE = "annex3"

# Body has no COR/AMD keyword — status must come from AHL BBB (T5.2).
_BBB_CASES = (
    ("sigmet_ahl_normal.txt", None, "NORMAL"),
    ("sigmet_ahl_rra.txt", "RRA", "NORMAL"),
    ("sigmet_ahl_cca.txt", "CCA", "CORRECTION"),
    ("sigmet_ahl_aaa.txt", "AAA", "AMENDMENT"),
)


def _read_sigmet(name: str) -> str:
    return (SIGMET_FIXTURES / name).read_text(encoding="utf-8")


def _ahl_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    raise AssertionError("fixture missing AHL line")


def _report_status_from_xml(xml: str) -> str | None:
    match = re.search(r'reportStatus="([^"]+)"', xml)
    return match.group(1) if match else None


def test_bulletin_meta_exposes_report_status_for_sigmet() -> None:
    """T5.2: BulletinMeta.report_status for SIGMET AHL CCA (additive; design-note §3.1)."""
    from tac2iwxxm import split_bulletin

    split = split_bulletin(_read_sigmet("sigmet_ahl_cca.txt"), product="SIGMET")
    assert getattr(split.meta, "report_status", None) == "CORRECTION"


@pytest.mark.parametrize(("fixture", "bbb", "status"), _BBB_CASES)
def test_sigmet_ahl_bbb_parse_and_filename(fixture: str, bbb: str | None, status: str) -> None:
    """AHL parse + WS→LS filename (M1 surface; keep-green for M5 pack)."""
    from datetime import UTC, datetime

    from tac2iwxxm import iwxxm_filename, parse_ahl

    text = _read_sigmet(fixture)
    parts = parse_ahl(_ahl_line(text))
    assert parts.tt == "WS"
    assert parts.bbb == bbb
    assert parts.report_status == status
    assert parts.iwxxm_tt == "LS"
    name = iwxxm_filename(parts, issued_at=datetime(2026, 8, 2, 12, 0, 0, tzinfo=UTC))
    assert name.startswith("A_LSUK31EGRR121200")
    assert "A_WS" not in name


@pytest.mark.parametrize(("fixture", "bbb", "status"), _BBB_CASES)
def test_sigmet_ahl_bbb_applied_to_converted_xml(fixture: str, bbb: str | None, status: str) -> None:
    """AHL BBB must drive @reportStatus even when TAC body has no COR/AMD (T5.2)."""
    from tac2iwxxm import convert, parse_ahl, split_bulletin

    split = split_bulletin(_read_sigmet(fixture), product="SIGMET")
    parts = parse_ahl(split.meta.ahl)
    assert parts.report_status == status
    assert split.meta.bbb == bbb

    result = convert(
        split.reports[0],
        product="SIGMET",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
        report_status=parts.report_status,
    )
    assert result.ok is True, f"convert failed for {fixture}: {result.issues!r}"
    assert result.xml is not None
    assert "iwxxm:SIGMET" in result.xml
    assert "iwxxm:VolcanicAshSIGMET" not in result.xml
    assert "iwxxm:TropicalCycloneSIGMET" not in result.xml
    assert _report_status_from_xml(result.xml) == status


def test_sigmet_product_order_lint_convert_validate() -> None:
    """TC-EV029-007 gen SIGMET pack seed: lint → convert → XSD+SCH on accept fixture."""
    from iwxxm_validate import validate
    from tac_validate import lint

    from tac2iwxxm import convert

    tac = (ANNEX3 / "sigmet_a6_1a_ts.tac").read_text(encoding="utf-8")
    lint_report = lint(tac, product="SIGMET")
    assert lint_report.ok is True, [(i.code, i.message) for i in lint_report.issues]

    convert_result = convert(
        tac,
        product="SIGMET",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert convert_result.ok is True, convert_result.issues
    assert convert_result.xml is not None
    assert "iwxxm:SIGMET" in convert_result.xml
    assert "iwxxm:VolcanicAshSIGMET" not in convert_result.xml

    validation = validate(
        convert_result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        levels=("xsd", "schematron"),
    )
    blocking = [i for i in validation.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
    assert not blocking, [(i.code, i.message) for i in blocking]


def test_sigmet_cnl_product_order_lint_convert_validate() -> None:
    """CNL deepen (TC-EV029-006 / remine B.4): A6-1b lint → convert → validate."""
    from iwxxm_validate import validate
    from tac_validate import lint

    from tac2iwxxm import convert

    tac = (ANNEX3 / "sigmet_a6_1b_cnl.tac").read_text(encoding="utf-8")
    lint_report = lint(tac, product="SIGMET")
    assert lint_report.ok is True, [(i.code, i.message) for i in lint_report.issues]

    convert_result = convert(
        tac,
        product="SIGMET",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert convert_result.ok is True, convert_result.issues
    assert convert_result.xml is not None
    assert "iwxxm:SIGMET" in convert_result.xml
    assert 'isCancelReport="true"' in convert_result.xml

    validation = validate(
        convert_result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        levels=("xsd", "schematron"),
    )
    blocking = [i for i in validation.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
    assert not blocking, [(i.code, i.message) for i in blocking]


def test_sigmet_ahl_cnl_split_and_convert() -> None:
    """T5.2: WS AHL + CNL body splits and converts with root iwxxm:SIGMET."""
    from tac2iwxxm import convert, split_bulletin

    split = split_bulletin(_read_sigmet("sigmet_ahl_cnl.txt"), product="SIGMET")
    assert split.meta.tt == "WS"
    assert split.meta.report_count == 1
    result = convert(
        split.reports[0],
        product="SIGMET",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, result.issues
    assert result.xml is not None
    assert "iwxxm:SIGMET" in result.xml
    assert 'isCancelReport="true"' in result.xml


def test_sigmet_multi_ahl_lint_convert_validate_each_report() -> None:
    """Multi-report WS bulletin: each body report lint→convert→validate (shape deepen)."""
    from iwxxm_validate import validate
    from tac_validate import lint

    from tac2iwxxm import convert, split_bulletin

    split = split_bulletin(_read_sigmet("sigmet_multi_ahl.txt"), product="SIGMET")
    assert split.meta.report_count == 2
    for index, tac in enumerate(split.reports):
        lint_report = lint(tac, product="SIGMET")
        assert lint_report.ok is True, f"report[{index}] lint: {[(i.code, i.message) for i in lint_report.issues]}"
        convert_result = convert(
            tac,
            product="SIGMET",
            profile=PROFILE,
            iwxxm_version=IWXXM_VERSION,
        )
        assert convert_result.ok is True, f"report[{index}] convert: {convert_result.issues!r}"
        assert convert_result.xml is not None
        assert "iwxxm:SIGMET" in convert_result.xml
        assert "iwxxm:VolcanicAshSIGMET" not in convert_result.xml
        validation = validate(
            convert_result.xml,
            iwxxm_version=IWXXM_VERSION,
            profile=PROFILE,
            levels=("xsd", "schematron"),
        )
        blocking = [i for i in validation.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
        assert not blocking, f"report[{index}] validate: {[(i.code, i.message) for i in blocking]}"
