"""TC-EV029-004 / F23 deepen T7.1: TC SIGMET gap fixtures (lint + convert + validate).

M0 inventory: vendor ``sigmet-A6-2-TC`` is covered as XML peer but convert/catalog
are gap (example-inventory §A TC SIGMET row; remine §B.6; WC→LY + BBB→reportStatus).
Root must be ``iwxxm:TropicalCycloneSIGMET`` — not general ``SIGMET``, not TCA
``TropicalCycloneAdvisory``, not ``VolcanicAshSIGMET`` (#738).

Product-order smoke (TC-EV029-007 pack seed for TC SIGMET) uses annex3
``sigmet_a6_2_tc`` (normalized WMO A6-2-TC + ``=`` terminator). BBB→``reportStatus``
reuses ``convert(report_status=)`` with TC emitter honor (T7.2);
``split_bulletin(product=\"SIGMET\")`` must accept WC AHL bodies (T7.2 — currently
WS/WV-only).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures"
TC_SIGMET_FIXTURES = FIXTURES / "tc_sigmet"
ANNEX3 = FIXTURES / "annex3_golden"

IWXXM_VERSION = "2025-2"
PROFILE = "annex3"

# Body has no COR/AMD keyword — status must come from AHL BBB (T7.2).
_BBB_CASES = (
    ("tc_sigmet_ahl_normal.txt", None, "NORMAL"),
    ("tc_sigmet_ahl_rra.txt", "RRA", "NORMAL"),
    ("tc_sigmet_ahl_cca.txt", "CCA", "CORRECTION"),
    ("tc_sigmet_ahl_aaa.txt", "AAA", "AMENDMENT"),
)


def _read_tc_sigmet(name: str) -> str:
    return (TC_SIGMET_FIXTURES / name).read_text(encoding="utf-8")


def _ahl_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    raise AssertionError("fixture missing AHL line")


def _report_status_from_xml(xml: str) -> str | None:
    match = re.search(r'reportStatus="([^"]+)"', xml)
    return match.group(1) if match else None


def _assert_tc_sigmet_root(xml: str) -> None:
    assert "iwxxm:TropicalCycloneSIGMET" in xml
    assert re.search(r"<iwxxm:TropicalCycloneSIGMET[\s>]", xml) is not None
    assert re.search(r"<iwxxm:SIGMET[\s>]", xml) is None
    assert "iwxxm:VolcanicAshSIGMET" not in xml
    assert "iwxxm:TropicalCycloneAdvisory" not in xml


def test_bulletin_meta_exposes_report_status_for_tc_sigmet() -> None:
    """T7.2: BulletinMeta.report_status for WC AHL CCA (additive; design-note §3.1)."""
    from tac2iwxxm import split_bulletin

    split = split_bulletin(_read_tc_sigmet("tc_sigmet_ahl_cca.txt"), product="SIGMET")
    assert getattr(split.meta, "report_status", None) == "CORRECTION"
    assert split.meta.tt == "WC"


@pytest.mark.parametrize(("fixture", "bbb", "status"), _BBB_CASES)
def test_tc_sigmet_ahl_bbb_parse_and_filename(fixture: str, bbb: str | None, status: str) -> None:
    """AHL parse + WC→LY filename (M1 surface; keep-green for M7 pack)."""
    from datetime import UTC, datetime

    from tac2iwxxm import iwxxm_filename, parse_ahl

    text = _read_tc_sigmet(fixture)
    parts = parse_ahl(_ahl_line(text))
    assert parts.tt == "WC"
    assert parts.bbb == bbb
    assert parts.report_status == status
    assert parts.iwxxm_tt == "LY"
    name = iwxxm_filename(parts, issued_at=datetime(2026, 8, 2, 12, 0, 0, tzinfo=UTC))
    assert name.startswith("A_LYUK31EGRR121200")
    assert "A_WC" not in name


@pytest.mark.parametrize(("fixture", "bbb", "status"), _BBB_CASES)
def test_tc_sigmet_ahl_bbb_applied_to_converted_xml(fixture: str, bbb: str | None, status: str) -> None:
    """AHL BBB must drive @reportStatus on TropicalCycloneSIGMET when body has no COR/AMD (T7.2)."""
    from tac2iwxxm import convert, parse_ahl, split_bulletin

    split = split_bulletin(_read_tc_sigmet(fixture), product="SIGMET")
    parts = parse_ahl(split.meta.ahl)
    assert parts.report_status == status
    assert split.meta.bbb == bbb
    assert split.meta.tt == "WC"

    result = convert(
        split.reports[0],
        product="SIGMET",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
        report_status=parts.report_status,
    )
    assert result.ok is True, f"convert failed for {fixture}: {result.issues!r}"
    assert result.xml is not None
    _assert_tc_sigmet_root(result.xml)
    assert _report_status_from_xml(result.xml) == status


def test_tc_sigmet_product_order_lint_convert_validate() -> None:
    """TC-EV029-004 / TC-EV029-007 TC SIGMET pack seed: lint → convert → XSD+SCH."""
    from iwxxm_validate import validate
    from tac_validate import lint

    from tac2iwxxm import convert

    tac = (ANNEX3 / "sigmet_a6_2_tc.tac").read_text(encoding="utf-8")
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
    _assert_tc_sigmet_root(convert_result.xml)

    validation = validate(
        convert_result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        levels=("xsd", "schematron"),
    )
    blocking = [i for i in validation.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
    assert not blocking, [(i.code, i.message) for i in blocking]


def test_tc_sigmet_not_confused_with_tca_advisory() -> None:
    """Adjacency (#738 / TC-F27-006 complement): TC SIGMET path never emits TCA advisory root."""
    from tac2iwxxm import convert

    tac = (ANNEX3 / "sigmet_a6_2_tc.tac").read_text(encoding="utf-8")
    result = convert(
        tac,
        product="SIGMET",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, result.issues
    assert result.xml is not None
    _assert_tc_sigmet_root(result.xml)


def test_tc_sigmet_ahl_cnl_split_and_convert() -> None:
    """T7.2: WC AHL + TC CNL splits; cancel under TropicalCycloneSIGMET root."""
    from tac2iwxxm import convert, split_bulletin

    bulletin = _read_tc_sigmet("tc_sigmet_ahl_cnl.txt")
    split = split_bulletin(bulletin, product="SIGMET")
    assert split.meta.tt == "WC"
    assert split.meta.report_count == 1
    # Full bulletin keeps WC AHL so convert can family-select CNL (no TC token in body).
    result = convert(
        bulletin,
        product="SIGMET",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, result.issues
    assert result.xml is not None
    assert 'isCancelReport="true"' in result.xml
    # WC AHL + CNL is TC family — root must not collapse to general SIGMET / VA / TCA.
    _assert_tc_sigmet_root(result.xml)


def test_tc_sigmet_multi_ahl_lint_convert_validate_each_report() -> None:
    """Multi-report WC bulletin: each body report lint→convert→validate (shape deepen)."""
    from iwxxm_validate import validate
    from tac_validate import lint

    from tac2iwxxm import convert, split_bulletin

    split = split_bulletin(_read_tc_sigmet("tc_sigmet_multi_ahl.txt"), product="SIGMET")
    assert split.meta.report_count == 2
    assert split.meta.tt == "WC"
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
        _assert_tc_sigmet_root(convert_result.xml)
        validation = validate(
            convert_result.xml,
            iwxxm_version=IWXXM_VERSION,
            profile=PROFILE,
            levels=("xsd", "schematron"),
        )
        blocking = [i for i in validation.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
        assert not blocking, f"report[{index}] validate: {[(i.code, i.message) for i in blocking]}"
