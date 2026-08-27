"""TC-EV029-007 / F23 deepen T6.1: VA SIGMET gap fixtures (lint + convert + validate).

M0 inventory: VA standalone is covered (V1-V3 / ``sigmet-VA-EGGX`` / multi-loc);
remaining deepen is WV AHL body/BBB matrix and multi-report (example-inventory §A VA
SIGMET row; remine §B.5; WV→LV + BBB→reportStatus). CNL covered via FIR-moved seed +
AHL CNL fixture.

Product-order smoke (TC-EV029-007 pack seed for VA SIGMET) uses annex3
``sigmet_va_eggx``. BBB→``reportStatus`` reuses ``convert(report_status=)`` with
VA emitter honor (T6.2); ``split_bulletin(product=\"SIGMET\")`` must accept WV AHL
bodies (T6.2 - currently WS-only).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures"
VA_SIGMET_FIXTURES = FIXTURES / "va_sigmet"
ANNEX3 = FIXTURES / "annex3_golden"

IWXXM_VERSION = "2025-2"
PROFILE = "annex3"

# Body has no COR/AMD keyword - status must come from AHL BBB (T6.2).
_BBB_CASES = (
    ("va_sigmet_ahl_normal.txt", None, "NORMAL"),
    ("va_sigmet_ahl_rra.txt", "RRA", "NORMAL"),
    ("va_sigmet_ahl_cca.txt", "CCA", "CORRECTION"),
    ("va_sigmet_ahl_aaa.txt", "AAA", "AMENDMENT"),
)


def _read_va_sigmet(name: str) -> str:
    return (VA_SIGMET_FIXTURES / name).read_text(encoding="utf-8")


def _ahl_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    raise AssertionError("fixture missing AHL line")


def _report_status_from_xml(xml: str) -> str | None:
    match = re.search(r'reportStatus="([^"]+)"', xml)
    return match.group(1) if match else None


def test_bulletin_meta_exposes_report_status_for_va_sigmet() -> None:
    """T6.2: BulletinMeta.report_status for WV AHL CCA (additive; design-note §3.1)."""
    from tac2iwxxm import split_bulletin

    split = split_bulletin(_read_va_sigmet("va_sigmet_ahl_cca.txt"), product="SIGMET")
    assert getattr(split.meta, "report_status", None) == "CORRECTION"
    assert split.meta.tt == "WV"


@pytest.mark.parametrize(("fixture", "bbb", "status"), _BBB_CASES)
def test_va_sigmet_ahl_bbb_parse_and_filename(fixture: str, bbb: str | None, status: str) -> None:
    """AHL parse + WV→LV filename (M1 surface; keep-green for M6 pack)."""
    from datetime import UTC, datetime

    from tac2iwxxm import iwxxm_filename, parse_ahl

    text = _read_va_sigmet(fixture)
    parts = parse_ahl(_ahl_line(text))
    assert parts.tt == "WV"
    assert parts.bbb == bbb
    assert parts.report_status == status
    assert parts.iwxxm_tt == "LV"
    name = iwxxm_filename(parts, issued_at=datetime(2026, 8, 2, 12, 0, 0, tzinfo=UTC))
    assert name.startswith("A_LVUK31EGRR121200")
    assert "A_WV" not in name


@pytest.mark.parametrize(("fixture", "bbb", "status"), _BBB_CASES)
def test_va_sigmet_ahl_bbb_applied_to_converted_xml(fixture: str, bbb: str | None, status: str) -> None:
    """AHL BBB must drive @reportStatus on VolcanicAshSIGMET when body has no COR/AMD (T6.2)."""
    from tac2iwxxm import convert, parse_ahl, split_bulletin

    split = split_bulletin(_read_va_sigmet(fixture), product="SIGMET")
    parts = parse_ahl(split.meta.ahl)
    assert parts.report_status == status
    assert split.meta.bbb == bbb
    assert split.meta.tt == "WV"

    result = convert(
        split.reports[0],
        product="SIGMET",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
        report_status=parts.report_status,
    )
    assert result.ok is True, f"convert failed for {fixture}: {result.issues!r}"
    assert result.xml is not None
    assert "iwxxm:VolcanicAshSIGMET" in result.xml
    assert "iwxxm:TropicalCycloneSIGMET" not in result.xml
    # Local-name SIGMET may appear in type names; root element must be VA.
    assert re.search(r"<iwxxm:VolcanicAshSIGMET[\s>]", result.xml) is not None
    assert re.search(r"<iwxxm:SIGMET[\s>]", result.xml) is None
    assert _report_status_from_xml(result.xml) == status


def test_va_sigmet_product_order_lint_convert_validate() -> None:
    """TC-EV029-007 VA SIGMET pack seed: lint → convert → XSD+SCH on accept fixture."""
    from iwxxm_validate import validate
    from tac_validate import lint

    from tac2iwxxm import convert

    tac = (ANNEX3 / "sigmet_va_eggx.tac").read_text(encoding="utf-8")
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
    assert "iwxxm:VolcanicAshSIGMET" in convert_result.xml
    assert re.search(r"<iwxxm:SIGMET[\s>]", convert_result.xml) is None

    validation = validate(
        convert_result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        levels=("xsd", "schematron"),
    )
    blocking = [i for i in validation.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
    assert not blocking, [(i.code, i.message) for i in blocking]


def test_va_sigmet_no_va_exp_product_order_lint_convert_validate() -> None:
    """NO VA EXP deepen (F23 V1): lint → convert → validate under VolcanicAshSIGMET."""
    from iwxxm_validate import validate
    from tac_validate import lint

    from tac2iwxxm import convert

    tac = (ANNEX3 / "sigmet_va_no_va_exp.tac").read_text(encoding="utf-8")
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
    assert "iwxxm:VolcanicAshSIGMET" in convert_result.xml

    validation = validate(
        convert_result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        levels=("xsd", "schematron"),
    )
    blocking = [i for i in validation.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
    assert not blocking, [(i.code, i.message) for i in blocking]


def test_va_sigmet_ahl_cnl_split_and_convert() -> None:
    """T6.2: WV AHL + VA CNL (FIR-moved) splits; cancel under VolcanicAshSIGMET root."""
    from tac2iwxxm import convert, split_bulletin

    split = split_bulletin(_read_va_sigmet("va_sigmet_ahl_cnl.txt"), product="SIGMET")
    assert split.meta.tt == "WV"
    assert split.meta.report_count == 1
    result = convert(
        split.reports[0],
        product="SIGMET",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, result.issues
    assert result.xml is not None
    assert 'isCancelReport="true"' in result.xml
    # WV AHL + FIR-moved CNL is VA family - root must not collapse to general SIGMET.
    assert "iwxxm:VolcanicAshSIGMET" in result.xml
    assert re.search(r"<iwxxm:SIGMET[\s>]", result.xml) is None


def test_va_sigmet_multi_ahl_lint_convert_validate_each_report() -> None:
    """Multi-report WV bulletin: each body report lint→convert→validate (shape deepen)."""
    from iwxxm_validate import validate
    from tac_validate import lint

    from tac2iwxxm import convert, split_bulletin

    split = split_bulletin(_read_va_sigmet("va_sigmet_multi_ahl.txt"), product="SIGMET")
    assert split.meta.report_count == 2
    assert split.meta.tt == "WV"
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
        assert "iwxxm:VolcanicAshSIGMET" in convert_result.xml
        assert re.search(r"<iwxxm:SIGMET[\s>]", convert_result.xml) is None
        validation = validate(
            convert_result.xml,
            iwxxm_version=IWXXM_VERSION,
            profile=PROFILE,
            levels=("xsd", "schematron"),
        )
        blocking = [i for i in validation.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
        assert not blocking, f"report[{index}] validate: {[(i.code, i.message) for i in blocking]}"
