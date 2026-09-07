"""TC-EV029-007 / F24 deepen T8.1: AIRMET gap fixtures (lint + convert + validate).

M0 inventory: AIRMET standalone is covered (F24 / A6-1a-TS); remaining deepen is
WA AHL body/BBB matrix and multi-report (example-inventory §A AIRMET row; remine
§B.7; WA→LW + BBB→reportStatus). AIRMET CNL peer absent from pin - synthetic CNL
AHL fixture (FIXTURE_GAPS).

Product-order smoke uses annex3 ``airmet_a6_1a_ts``. BBB→``reportStatus`` and
``split_bulletin(product=\"AIRMET\")`` WA acceptance are T8.2 gaps (currently red).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures"
AIRMET_FIXTURES = FIXTURES / "airmet"
ANNEX3 = FIXTURES / "annex3_golden"

IWXXM_VERSION = "2025-2"
PROFILE = "annex3"

# Body has no COR/AMD keyword - status must come from AHL BBB (T8.2).
_BBB_CASES = (
    ("airmet_ahl_normal.txt", None, "NORMAL"),
    ("airmet_ahl_rra.txt", "RRA", "NORMAL"),
    ("airmet_ahl_cca.txt", "CCA", "CORRECTION"),
    ("airmet_ahl_aaa.txt", "AAA", "AMENDMENT"),
)


def _read_airmet(name: str) -> str:
    return (AIRMET_FIXTURES / name).read_text(encoding="utf-8")


def _ahl_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    raise AssertionError("fixture missing AHL line")


def _report_status_from_xml(xml: str) -> str | None:
    match = re.search(r'reportStatus="([^"]+)"', xml)
    return match.group(1) if match else None


def _assert_airmet_root(xml: str) -> None:
    assert "iwxxm:AIRMET" in xml
    assert re.search(r"<iwxxm:AIRMET[\s>]", xml) is not None
    assert re.search(r"<iwxxm:SIGMET[\s>]", xml) is None
    assert "iwxxm:VolcanicAshSIGMET" not in xml
    assert "iwxxm:TropicalCycloneSIGMET" not in xml


def test_bulletin_meta_exposes_report_status_for_airmet() -> None:
    """T8.2: BulletinMeta.report_status for WA AHL CCA (additive; design-note §3.1)."""
    from tac2iwxxm import split_bulletin

    split = split_bulletin(_read_airmet("airmet_ahl_cca.txt"), product="AIRMET")
    assert getattr(split.meta, "report_status", None) == "CORRECTION"
    assert split.meta.tt == "WA"


@pytest.mark.parametrize(("fixture", "bbb", "status"), _BBB_CASES)
def test_airmet_ahl_bbb_parse_and_filename(fixture: str, bbb: str | None, status: str) -> None:
    """AHL parse + WA→LW filename (M1 surface; keep-green for M8 pack)."""
    from datetime import UTC, datetime

    from tac2iwxxm import iwxxm_filename, parse_ahl

    text = _read_airmet(fixture)
    parts = parse_ahl(_ahl_line(text))
    assert parts.tt == "WA"
    assert parts.bbb == bbb
    assert parts.report_status == status
    assert parts.iwxxm_tt == "LW"
    name = iwxxm_filename(parts, issued_at=datetime(2026, 8, 2, 12, 0, 0, tzinfo=UTC))
    assert name.startswith("A_LWUK31EGRR121200")
    assert "A_WA" not in name


@pytest.mark.parametrize(("fixture", "bbb", "status"), _BBB_CASES)
def test_airmet_ahl_bbb_applied_to_converted_xml(fixture: str, bbb: str | None, status: str) -> None:
    """AHL BBB must drive @reportStatus on AIRMET when body has no COR/AMD (T8.2)."""
    from tac2iwxxm import convert, parse_ahl, split_bulletin

    split = split_bulletin(_read_airmet(fixture), product="AIRMET")
    parts = parse_ahl(split.meta.ahl)
    assert parts.report_status == status
    assert split.meta.bbb == bbb
    assert split.meta.tt == "WA"

    result = convert(
        split.reports[0],
        product="AIRMET",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
        report_status=parts.report_status,
    )
    assert result.ok is True, f"convert failed for {fixture}: {result.issues!r}"
    assert result.xml is not None
    _assert_airmet_root(result.xml)
    assert _report_status_from_xml(result.xml) == status


def test_airmet_product_order_lint_convert_validate() -> None:
    """TC-EV029-007 AIRMET pack seed: lint → convert → XSD+SCH on A6-1a-TS."""
    from iwxxm_validate import validate
    from tac_validate import lint

    from tac2iwxxm import convert

    tac = (ANNEX3 / "airmet_a6_1a_ts.tac").read_text(encoding="utf-8")
    lint_report = lint(tac, product="AIRMET")
    assert lint_report.ok is True, [(i.code, i.message) for i in lint_report.issues]

    convert_result = convert(
        tac,
        product="AIRMET",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert convert_result.ok is True, convert_result.issues
    assert convert_result.xml is not None
    _assert_airmet_root(convert_result.xml)

    validation = validate(
        convert_result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        levels=("xsd", "schematron"),
    )
    blocking = [i for i in validation.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
    assert not blocking, [(i.code, i.message) for i in blocking]


def test_airmet_ahl_cnl_split_and_convert() -> None:
    """T8.2: WA AHL + AIRMET CNL splits; cancel under iwxxm:AIRMET root."""
    from tac2iwxxm import convert, split_bulletin

    bulletin = _read_airmet("airmet_ahl_cnl.txt")
    split = split_bulletin(bulletin, product="AIRMET")
    assert split.meta.tt == "WA"
    assert split.meta.report_count == 1
    result = convert(
        bulletin,
        product="AIRMET",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, result.issues
    assert result.xml is not None
    assert 'isCancelReport="true"' in result.xml
    _assert_airmet_root(result.xml)


def test_airmet_multi_ahl_lint_convert_validate_each_report() -> None:
    """Multi-report WA bulletin: each body report lint→convert→validate (shape deepen)."""
    from iwxxm_validate import validate
    from tac_validate import lint

    from tac2iwxxm import convert, split_bulletin

    split = split_bulletin(_read_airmet("airmet_multi_ahl.txt"), product="AIRMET")
    assert split.meta.report_count == 2
    assert split.meta.tt == "WA"
    for index, tac in enumerate(split.reports):
        lint_report = lint(tac, product="AIRMET")
        assert lint_report.ok is True, f"report[{index}] lint: {[(i.code, i.message) for i in lint_report.issues]}"
        convert_result = convert(
            tac,
            product="AIRMET",
            profile=PROFILE,
            iwxxm_version=IWXXM_VERSION,
        )
        assert convert_result.ok is True, f"report[{index}] convert: {convert_result.issues!r}"
        assert convert_result.xml is not None
        _assert_airmet_root(convert_result.xml)
        validation = validate(
            convert_result.xml,
            iwxxm_version=IWXXM_VERSION,
            profile=PROFILE,
            levels=("xsd", "schematron"),
        )
        blocking = [i for i in validation.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
        assert not blocking, f"report[{index}] validate: {[(i.code, i.message) for i in blocking]}"
