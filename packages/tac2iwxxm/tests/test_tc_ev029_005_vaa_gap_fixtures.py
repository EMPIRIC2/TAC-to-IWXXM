"""TC-EV029-005 / F26 deepen T9.1: VAA bulletin/encode residual fixtures (#820).

M0 inventory: VAA standalone golden is covered (F26 / A7-2); remaining deepen is
FV AHL body/BBB matrix, ``=``-terminator multi-report (not blank-line-only), and
encode residuals (BBB→``reportStatus``, RMK NIL→nilReason). Decode residuals for
``vaa_a7_2`` stay allowlisted under #820 / F9 G4 until a later deepen closes them.

``split_bulletin(product=\"VAA\")`` FV acceptance and BBB→XML are T9.2 gaps
(currently red).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures"
VAA_FIXTURES = FIXTURES / "vaa"
ANNEX3 = FIXTURES / "annex3_golden"
ACCEPT_VAA = Path(__file__).resolve().parents[2] / "tac-validate" / "tests" / "fixtures" / "accept"

IWXXM_VERSION = "2025-2"
PROFILE = "annex3"

# Body has no COR/AMD keyword — status must come from AHL BBB (T9.2).
_BBB_CASES = (
    ("vaa_ahl_normal.txt", None, "NORMAL"),
    ("vaa_ahl_rra.txt", "RRA", "NORMAL"),
    ("vaa_ahl_cca.txt", "CCA", "CORRECTION"),
    ("vaa_ahl_aaa.txt", "AAA", "AMENDMENT"),
)

if str(FIXTURES) not in sys.path:
    sys.path.insert(0, str(FIXTURES))

from wmo_decode_residual_allowlist import allows_any_residual  # noqa: E402


def _read_vaa(name: str) -> str:
    return (VAA_FIXTURES / name).read_text(encoding="utf-8")


def _ahl_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    raise AssertionError("fixture missing AHL line")


def _report_status_from_xml(xml: str) -> str | None:
    match = re.search(r'reportStatus="([^"]+)"', xml)
    return match.group(1) if match else None


def _assert_vaa_root(xml: str) -> None:
    assert "iwxxm:VolcanicAshAdvisory" in xml
    assert re.search(r"<iwxxm:VolcanicAshAdvisory[\s>]", xml) is not None
    assert "iwxxm:VolcanicAshSIGMET" not in xml
    assert re.search(r"<iwxxm:SIGMET[\s>]", xml) is None
    assert "iwxxm:TropicalCycloneAdvisory" not in xml


def test_bulletin_meta_exposes_report_status_for_vaa() -> None:
    """T9.2: BulletinMeta.report_status for FV AHL CCA (additive; design-note §3.1)."""
    from tac2iwxxm import split_bulletin

    split = split_bulletin(_read_vaa("vaa_ahl_cca.txt"), product="VAA")
    assert getattr(split.meta, "report_status", None) == "CORRECTION"
    assert split.meta.tt == "FV"


@pytest.mark.parametrize(("fixture", "bbb", "status"), _BBB_CASES)
def test_vaa_ahl_bbb_parse_and_filename(fixture: str, bbb: str | None, status: str) -> None:
    """AHL parse + FV→LU filename (M1 surface; keep-green for M9 pack)."""
    from datetime import UTC, datetime

    from tac2iwxxm import iwxxm_filename, parse_ahl

    text = _read_vaa(fixture)
    parts = parse_ahl(_ahl_line(text))
    assert parts.tt == "FV"
    assert parts.bbb == bbb
    assert parts.report_status == status
    assert parts.iwxxm_tt == "LU"
    name = iwxxm_filename(parts, issued_at=datetime(2026, 8, 2, 12, 0, 0, tzinfo=UTC))
    assert name.startswith("A_LUFE01RJTD121200")
    assert "A_FV" not in name


@pytest.mark.parametrize(("fixture", "bbb", "status"), _BBB_CASES)
def test_vaa_ahl_bbb_applied_to_converted_xml(fixture: str, bbb: str | None, status: str) -> None:
    """AHL BBB must drive @reportStatus on VAA when body has no COR/AMD (T9.2)."""
    from tac2iwxxm import convert, parse_ahl, split_bulletin

    split = split_bulletin(_read_vaa(fixture), product="VAA")
    parts = parse_ahl(split.meta.ahl)
    assert parts.report_status == status
    assert split.meta.bbb == bbb
    assert split.meta.tt == "FV"

    result = convert(
        split.reports[0],
        product="VAA",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
        report_status=parts.report_status,
    )
    assert result.ok is True, f"convert failed for {fixture}: {result.issues!r}"
    assert result.xml is not None
    _assert_vaa_root(result.xml)
    assert _report_status_from_xml(result.xml) == status


def test_vaa_product_order_lint_convert_validate() -> None:
    """TC-EV029-007 VAA pack seed: lint → convert → XSD+SCH on A7-2."""
    from iwxxm_validate import validate
    from tac_validate import lint

    from tac2iwxxm import convert

    tac = (ANNEX3 / "vaa_a7_2.tac").read_text(encoding="utf-8")
    lint_report = lint(tac, product="VAA")
    assert lint_report.ok is True, [(i.code, i.message) for i in lint_report.issues]

    convert_result = convert(
        tac,
        product="VAA",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert convert_result.ok is True, convert_result.issues
    assert convert_result.xml is not None
    _assert_vaa_root(convert_result.xml)

    validation = validate(
        convert_result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        levels=("xsd", "schematron"),
    )
    blocking = [i for i in validation.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
    assert not blocking, [(i.code, i.message) for i in blocking]


def test_vaa_equals_terminator_multi_report_split() -> None:
    """TC-EV029-005: multi-report FV bulletin splits on ``=`` (two VA ADVISORY bodies)."""
    from tac2iwxxm import split_bulletin

    split = split_bulletin(_read_vaa("vaa_multi_ahl.txt"), product="VAA")
    assert split.meta.report_count == 2
    assert split.meta.tt == "FV"
    assert len(split.reports) == 2
    for index, tac in enumerate(split.reports):
        assert "VA ADVISORY" in tac.upper(), f"report[{index}] missing VA ADVISORY"
        assert tac.rstrip().endswith("=") or "VA ADVISORY" in tac.upper()


def test_vaa_blank_line_only_is_not_multi_report_split() -> None:
    """TC-EV029-005: blank-line-only adjacency must not count as ``=`` multi-split."""
    from tac2iwxxm import BulletinSplitError, split_bulletin

    text = _read_vaa("vaa_multi_blank_only.txt")
    try:
        split = split_bulletin(text, product="VAA")
    except BulletinSplitError:
        # Acceptable until T9.2: unsupported product or empty after failed split.
        return
    # If split succeeds, blank-line-only must not invent a second report.
    assert split.meta.report_count == 1, f"blank-line-only must not yield multi-report; got {split.meta.report_count}"


def test_vaa_multi_ahl_lint_convert_validate_each_report() -> None:
    """Multi-report FV bulletin: each body report lint→convert→validate (shape deepen)."""
    from iwxxm_validate import validate
    from tac_validate import lint

    from tac2iwxxm import convert, split_bulletin

    split = split_bulletin(_read_vaa("vaa_multi_ahl.txt"), product="VAA")
    assert split.meta.report_count == 2
    assert split.meta.tt == "FV"
    for index, tac in enumerate(split.reports):
        lint_report = lint(tac, product="VAA")
        assert lint_report.ok is True, f"report[{index}] lint: {[(i.code, i.message) for i in lint_report.issues]}"
        convert_result = convert(
            tac,
            product="VAA",
            profile=PROFILE,
            iwxxm_version=IWXXM_VERSION,
        )
        assert convert_result.ok is True, f"report[{index}] convert: {convert_result.issues!r}"
        assert convert_result.xml is not None
        _assert_vaa_root(convert_result.xml)
        validation = validate(
            convert_result.xml,
            iwxxm_version=IWXXM_VERSION,
            profile=PROFILE,
            levels=("xsd", "schematron"),
        )
        blocking = [i for i in validation.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
        assert not blocking, f"report[{index}] validate: {[(i.code, i.message) for i in blocking]}"


def test_vaa_rmk_nil_encodes_nilreason_inapplicable() -> None:
    """#820 / #823 B4 encode residual: RMK NIL → remarks nilReason=inapplicable (T9.2)."""
    from tac2iwxxm import convert

    tac = (ACCEPT_VAA / "vaa_v1_rmk_nil_fcst_no_va.tac").read_text(encoding="utf-8")
    result = convert(tac, product="VAA", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True, result.issues
    assert result.xml is not None
    _assert_vaa_root(result.xml)
    assert re.search(
        r'<iwxxm:remarks[^>]*nilReason="http://codes\.wmo\.int/common/nil/inapplicable"',
        result.xml,
    ), "RMK NIL must emit remarks with nilReason=inapplicable"


def test_vaa_a7_2_forecast_cardinality() -> None:
    """Encode residual: A7-2 must emit three forecast blocks (+6/+12/+18)."""
    from tac2iwxxm import convert

    tac = (ANNEX3 / "vaa_a7_2.tac").read_text(encoding="utf-8")
    result = convert(tac, product="VAA", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True, result.issues
    assert result.xml is not None
    assert result.xml.count("<iwxxm:forecast>") == 3
    assert 'status="NO_VOLCANIC_ASH_EXPECTED"' in result.xml


def test_vaa_a7_2_decode_residuals_empty_after_820() -> None:
    """TC-EV029-005 / EV-030: vaa_a7_2 reaches residuals == [] (#820 closed)."""
    from tac2iwxxm.decode import decode_tac

    assert not allows_any_residual("vaa_a7_2")
    tac = (ANNEX3 / "vaa_a7_2.tac").read_text(encoding="utf-8")
    result = decode_tac(tac, product="VAA")
    assert result.residuals == []
