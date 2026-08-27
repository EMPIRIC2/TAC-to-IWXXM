"""TC-EV029-005 / F27 deepen T10.1: TCA bulletin/encode residual fixtures (#820).

M0 inventory: TCA standalone golden is covered (F27 / A2-2); remaining deepen is
FK AHL body/BBB matrix, ``=``-terminator multi-report (not blank-line-only), and
BBB→``reportStatus``. RMK NIL / NO MSG EXP nilReasons are already encoded (F27);
decode residuals for ``tca_a2_2`` stay allowlisted under #820 / F9 G4.

``split_bulletin(product=\"TCA\")`` FK acceptance and BBB→XML are T10.2 gaps
(currently red).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures"
TCA_FIXTURES = FIXTURES / "tca"
ANNEX3 = FIXTURES / "annex3_golden"
ACCEPT_TCA = Path(__file__).resolve().parents[2] / "tac-validate" / "tests" / "fixtures" / "accept"

IWXXM_VERSION = "2025-2"
PROFILE = "annex3"

# Body has no COR/AMD keyword - status must come from AHL BBB (T10.2).
_BBB_CASES = (
    ("tca_ahl_normal.txt", None, "NORMAL"),
    ("tca_ahl_rra.txt", "RRA", "NORMAL"),
    ("tca_ahl_cca.txt", "CCA", "CORRECTION"),
    ("tca_ahl_aaa.txt", "AAA", "AMENDMENT"),
)

if str(FIXTURES) not in sys.path:
    sys.path.insert(0, str(FIXTURES))

from wmo_decode_residual_allowlist import allows_any_residual  # noqa: E402


def _read_tca(name: str) -> str:
    return (TCA_FIXTURES / name).read_text(encoding="utf-8")


def _ahl_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    raise AssertionError("fixture missing AHL line")


def _report_status_from_xml(xml: str) -> str | None:
    match = re.search(r'reportStatus="([^"]+)"', xml)
    return match.group(1) if match else None


def _assert_tca_root(xml: str) -> None:
    assert "iwxxm:TropicalCycloneAdvisory" in xml
    assert re.search(r"<iwxxm:TropicalCycloneAdvisory[\s>]", xml) is not None
    assert "iwxxm:TropicalCycloneSIGMET" not in xml
    assert re.search(r"<iwxxm:SIGMET[\s>]", xml) is None
    assert "iwxxm:VolcanicAshAdvisory" not in xml


def test_bulletin_meta_exposes_report_status_for_tca() -> None:
    """T10.2: BulletinMeta.report_status for FK AHL CCA (additive; design-note §3.1)."""
    from tac2iwxxm import split_bulletin

    split = split_bulletin(_read_tca("tca_ahl_cca.txt"), product="TCA")
    assert getattr(split.meta, "report_status", None) == "CORRECTION"
    assert split.meta.tt == "FK"


@pytest.mark.parametrize(("fixture", "bbb", "status"), _BBB_CASES)
def test_tca_ahl_bbb_parse_and_filename(fixture: str, bbb: str | None, status: str) -> None:
    """AHL parse + FK→LK filename (M1 surface; keep-green for M10 pack)."""
    from datetime import UTC, datetime

    from tac2iwxxm import iwxxm_filename, parse_ahl

    text = _read_tca(fixture)
    parts = parse_ahl(_ahl_line(text))
    assert parts.tt == "FK"
    assert parts.bbb == bbb
    assert parts.report_status == status
    assert parts.iwxxm_tt == "LK"
    name = iwxxm_filename(parts, issued_at=datetime(2026, 8, 2, 12, 0, 0, tzinfo=UTC))
    assert name.startswith("A_LKAU01ADRM121200")
    assert "A_FK" not in name


@pytest.mark.parametrize(("fixture", "bbb", "status"), _BBB_CASES)
def test_tca_ahl_bbb_applied_to_converted_xml(fixture: str, bbb: str | None, status: str) -> None:
    """AHL BBB must drive @reportStatus on TCA when body has no COR/AMD (T10.2)."""
    from tac2iwxxm import convert, parse_ahl, split_bulletin

    split = split_bulletin(_read_tca(fixture), product="TCA")
    parts = parse_ahl(split.meta.ahl)
    assert parts.report_status == status
    assert split.meta.bbb == bbb
    assert split.meta.tt == "FK"

    result = convert(
        split.reports[0],
        product="TCA",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
        report_status=parts.report_status,
    )
    assert result.ok is True, f"convert failed for {fixture}: {result.issues!r}"
    assert result.xml is not None
    _assert_tca_root(result.xml)
    assert _report_status_from_xml(result.xml) == status


def test_tca_product_order_lint_convert_validate() -> None:
    """TC-EV029-007 TCA pack seed: lint → convert → XSD+SCH on A2-2."""
    from iwxxm_validate import validate
    from tac_validate import lint

    from tac2iwxxm import convert

    tac = (ANNEX3 / "tca_a2_2.tac").read_text(encoding="utf-8")
    lint_report = lint(tac, product="TCA")
    assert lint_report.ok is True, [(i.code, i.message) for i in lint_report.issues]

    convert_result = convert(
        tac,
        product="TCA",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert convert_result.ok is True, convert_result.issues
    assert convert_result.xml is not None
    _assert_tca_root(convert_result.xml)

    validation = validate(
        convert_result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        levels=("xsd", "schematron"),
    )
    blocking = [i for i in validation.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
    assert not blocking, [(i.code, i.message) for i in blocking]


def test_tca_equals_terminator_multi_report_split() -> None:
    """TC-EV029-005: multi-report FK bulletin splits on ``=`` (two TC ADVISORY bodies)."""
    from tac2iwxxm import split_bulletin

    split = split_bulletin(_read_tca("tca_multi_ahl.txt"), product="TCA")
    assert split.meta.report_count == 2
    assert split.meta.tt == "FK"
    assert len(split.reports) == 2
    for index, tac in enumerate(split.reports):
        assert "TC ADVISORY" in tac.upper(), f"report[{index}] missing TC ADVISORY"


def test_tca_blank_line_only_is_not_multi_report_split() -> None:
    """TC-EV029-005: blank-line-only adjacency must not count as ``=`` multi-split."""
    from tac2iwxxm import BulletinSplitError, split_bulletin

    text = _read_tca("tca_multi_blank_only.txt")
    try:
        split = split_bulletin(text, product="TCA")
    except BulletinSplitError:
        return
    assert split.meta.report_count == 1, f"blank-line-only must not yield multi-report; got {split.meta.report_count}"


def test_tca_multi_ahl_lint_convert_validate_each_report() -> None:
    """Multi-report FK bulletin: each body report lint→convert→validate (shape deepen)."""
    from iwxxm_validate import validate
    from tac_validate import lint

    from tac2iwxxm import convert, split_bulletin

    split = split_bulletin(_read_tca("tca_multi_ahl.txt"), product="TCA")
    assert split.meta.report_count == 2
    assert split.meta.tt == "FK"
    for index, tac in enumerate(split.reports):
        lint_report = lint(tac, product="TCA")
        assert lint_report.ok is True, f"report[{index}] lint: {[(i.code, i.message) for i in lint_report.issues]}"
        convert_result = convert(
            tac,
            product="TCA",
            profile=PROFILE,
            iwxxm_version=IWXXM_VERSION,
        )
        assert convert_result.ok is True, f"report[{index}] convert: {convert_result.issues!r}"
        assert convert_result.xml is not None
        _assert_tca_root(convert_result.xml)
        validation = validate(
            convert_result.xml,
            iwxxm_version=IWXXM_VERSION,
            profile=PROFILE,
            levels=("xsd", "schematron"),
        )
        blocking = [i for i in validation.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
        assert not blocking, f"report[{index}] validate: {[(i.code, i.message) for i in blocking]}"


def test_tca_rmk_nil_and_no_msg_exp_nilreasons() -> None:
    """#820 encode keep-green: RMK NIL + NO MSG EXP → nilReason=inapplicable."""
    from tac2iwxxm import convert

    tac = (ACCEPT_TCA / "tca_t1_rmk_nil_no_msg.tac").read_text(encoding="utf-8")
    result = convert(tac, product="TCA", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True, result.issues
    assert result.xml is not None
    _assert_tca_root(result.xml)
    assert re.search(
        r'<iwxxm:remarks[^>]*nilReason="http://codes\.wmo\.int/common/nil/inapplicable"',
        result.xml,
    )
    assert re.search(
        r'<iwxxm:nextAdvisoryTime[^>]*nilReason="http://codes\.wmo\.int/common/nil/inapplicable"',
        result.xml,
    )


def test_tca_a2_2_forecast_cardinality() -> None:
    """Encode residual: A2-2 must emit four forecast blocks (+6/+12/+18/+24)."""
    from tac2iwxxm import convert

    tac = (ANNEX3 / "tca_a2_2.tac").read_text(encoding="utf-8")
    result = convert(tac, product="TCA", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True, result.issues
    assert result.xml is not None
    assert result.xml.count("<iwxxm:forecast>") == 4


def test_tca_a2_2_decode_residuals_empty_after_820() -> None:
    """TC-EV029-005 / EV-030: tca_a2_2 reaches residuals == [] (#820 closed)."""
    from tac2iwxxm.decode import decode_tac

    assert not allows_any_residual("tca_a2_2")
    tac = (ANNEX3 / "tca_a2_2.tac").read_text(encoding="utf-8")
    result = decode_tac(tac, product="TCA")
    assert result.residuals == []
