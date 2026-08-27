"""TC-EV029-006 - Report-state matrix smoke (T12.2 / M12).

Consolidates family x report-state cells for CI:

* Normal / AMD / COR via AHL BBB → ``@reportStatus``
* CNL via product cancel path (``isCancelReport``) - **not** reportStatus
* NIL via ``nilReason`` / product NIL - **not** reportStatus

Per-family pack seeds remain in ``test_tc_ev029_007_*`` / ``test_tc_ev029_005_*`` /
TC-F28; this module locks the matrix for TC-EV029-006.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures"
ANNEX3 = FIXTURES / "annex3_golden"
IWXXM_VERSION = "2025-2"
PROFILE = "annex3"

# family_id, product, fixture_subdir, fixture_name, expected_bbb, expected_status, root_local
_BBB_CASES: tuple[tuple[str, str, str, str, str | None, str, str], ...] = (
    ("METAR", "METAR", "metar", "metar_ahl_normal.txt", None, "NORMAL", "METAR"),
    ("METAR", "METAR", "metar", "metar_ahl_cca.txt", "CCA", "CORRECTION", "METAR"),
    ("METAR", "METAR", "metar", "metar_ahl_aaa.txt", "AAA", "AMENDMENT", "METAR"),
    ("SPECI", "SPECI", "speci", "speci_ahl_normal.txt", None, "NORMAL", "SPECI"),
    ("SPECI", "SPECI", "speci", "speci_ahl_cca.txt", "CCA", "CORRECTION", "SPECI"),
    ("SPECI", "SPECI", "speci", "speci_ahl_aaa.txt", "AAA", "AMENDMENT", "SPECI"),
    ("TAF", "TAF", "taf", "taf_ahl_normal.txt", None, "NORMAL", "TAF"),
    ("TAF", "TAF", "taf", "taf_ahl_cca.txt", "CCA", "CORRECTION", "TAF"),
    ("TAF", "TAF", "taf", "taf_ahl_aaa.txt", "AAA", "AMENDMENT", "TAF"),
    ("SIGMET", "SIGMET", "sigmet", "sigmet_ahl_normal.txt", None, "NORMAL", "SIGMET"),
    ("SIGMET", "SIGMET", "sigmet", "sigmet_ahl_cca.txt", "CCA", "CORRECTION", "SIGMET"),
    ("SIGMET", "SIGMET", "sigmet", "sigmet_ahl_aaa.txt", "AAA", "AMENDMENT", "SIGMET"),
    ("VA_SIGMET", "SIGMET", "va_sigmet", "va_sigmet_ahl_normal.txt", None, "NORMAL", "VolcanicAshSIGMET"),
    ("VA_SIGMET", "SIGMET", "va_sigmet", "va_sigmet_ahl_cca.txt", "CCA", "CORRECTION", "VolcanicAshSIGMET"),
    ("VA_SIGMET", "SIGMET", "va_sigmet", "va_sigmet_ahl_aaa.txt", "AAA", "AMENDMENT", "VolcanicAshSIGMET"),
    ("TC_SIGMET", "SIGMET", "tc_sigmet", "tc_sigmet_ahl_normal.txt", None, "NORMAL", "TropicalCycloneSIGMET"),
    ("TC_SIGMET", "SIGMET", "tc_sigmet", "tc_sigmet_ahl_cca.txt", "CCA", "CORRECTION", "TropicalCycloneSIGMET"),
    ("TC_SIGMET", "SIGMET", "tc_sigmet", "tc_sigmet_ahl_aaa.txt", "AAA", "AMENDMENT", "TropicalCycloneSIGMET"),
    ("AIRMET", "AIRMET", "airmet", "airmet_ahl_normal.txt", None, "NORMAL", "AIRMET"),
    ("AIRMET", "AIRMET", "airmet", "airmet_ahl_cca.txt", "CCA", "CORRECTION", "AIRMET"),
    ("AIRMET", "AIRMET", "airmet", "airmet_ahl_aaa.txt", "AAA", "AMENDMENT", "AIRMET"),
    ("VAA", "VAA", "vaa", "vaa_ahl_normal.txt", None, "NORMAL", "VolcanicAshAdvisory"),
    ("VAA", "VAA", "vaa", "vaa_ahl_cca.txt", "CCA", "CORRECTION", "VolcanicAshAdvisory"),
    ("VAA", "VAA", "vaa", "vaa_ahl_aaa.txt", "AAA", "AMENDMENT", "VolcanicAshAdvisory"),
    ("TCA", "TCA", "tca", "tca_ahl_normal.txt", None, "NORMAL", "TropicalCycloneAdvisory"),
    ("TCA", "TCA", "tca", "tca_ahl_cca.txt", "CCA", "CORRECTION", "TropicalCycloneAdvisory"),
    ("TCA", "TCA", "tca", "tca_ahl_aaa.txt", "AAA", "AMENDMENT", "TropicalCycloneAdvisory"),
    # SWXA: Normal only in-tree (AMD/COR AHL fixtures absent - document gap, not silent blank).
    ("SWXA", "SWXA", "swxa", "swxa_ahl_normal.txt", None, "NORMAL", "SpaceWeatherAdvisory"),
)

# family_id, product, source ("annex3"|"subdir"), path_or_name, root_local, convert_mode
# convert_mode: "body" = first split report; "bulletin" = full text (AHL needed for family select)
_CNL_CASES: tuple[tuple[str, str, str, str, str, str], ...] = (
    ("TAF", "TAF", "annex3", "taf_cnl.tac", "TAF", "body"),
    ("SIGMET", "SIGMET", "annex3", "sigmet_a6_1b_cnl.tac", "SIGMET", "body"),
    ("VA_SIGMET", "SIGMET", "va_sigmet", "va_sigmet_ahl_cnl.txt", "VolcanicAshSIGMET", "body"),
    ("TC_SIGMET", "SIGMET", "tc_sigmet", "tc_sigmet_ahl_cnl.txt", "TropicalCycloneSIGMET", "bulletin"),
    ("AIRMET", "AIRMET", "airmet", "airmet_ahl_cnl.txt", "AIRMET", "bulletin"),
)

# family_id, product, annex3 tac, root_local
_NIL_CASES: tuple[tuple[str, str, str, str], ...] = (
    ("METAR", "METAR", "metar_nil.tac", "METAR"),
    ("SPECI", "SPECI", "speci_nil.tac", "SPECI"),
    ("TAF", "TAF", "taf_nil.tac", "TAF"),
)

# Explicit gap / N/A cells - must stay listed so the matrix has no silent blanks (TC-EV029-001/006).
_GAP_OR_NA_CELLS: tuple[tuple[str, str, str], ...] = (
    ("SWXA", "AMD", "no AHL AAA fixture in-tree (FIXTURE_GAPS / M11 Normal-only)"),
    ("SWXA", "COR", "no AHL CCA fixture in-tree (FIXTURE_GAPS / M11 Normal-only)"),
    ("SWXA", "CNL", "N/A - SWXA has no product CNL form"),
    ("SWXA", "NIL", "N/A - SWXA uses advisory RMK / NXT paths, not aerodrome NIL"),
    ("METAR", "CNL", "N/A - METAR uses COR/AMD keywords + NIL, not CNL cancel"),
    ("SPECI", "CNL", "N/A - SPECI uses COR + NIL, not CNL cancel"),
    ("VAA", "CNL", "N/A - VAA cancel not AHL reportStatus; RMK NIL = remarks nilReason"),
    ("TCA", "CNL", "N/A - TCA cancel not AHL reportStatus; RMK NIL / NO MSG EXP = nilReason"),
    ("VAA", "NIL", "defer - RMK NIL remarks path covered in TC-EV029-005 (not report NIL)"),
    ("TCA", "NIL", "defer - RMK NIL / NO MSG EXP covered in TC-EV029-005 (not report NIL)"),
    ("VA_SIGMET", "NIL", "N/A - VA SIGMET uses CNL cancel / NO VA EXP, not aerodrome NIL"),
    ("TC_SIGMET", "NIL", "N/A - TC SIGMET uses CNL cancel, not aerodrome NIL"),
    ("AIRMET", "NIL", "N/A - AIRMET uses CNL cancel, not aerodrome NIL"),
    ("SIGMET", "NIL", "N/A - general SIGMET uses CNL cancel, not aerodrome NIL"),
)


def _report_status_from_xml(xml: str) -> str | None:
    match = re.search(r'reportStatus="([^"]+)"', xml)
    return match.group(1) if match else None


def _has_root(xml: str, local: str) -> bool:
    if local == "SIGMET":
        return re.search(r"<iwxxm:SIGMET[\s>]", xml) is not None
    return f"<iwxxm:{local}" in xml


def _read_case(source: str, name: str) -> str:
    path = ANNEX3 / name if source == "annex3" else FIXTURES / source / name
    assert path.is_file(), f"missing fixture: {path}"
    return path.read_text(encoding="utf-8")


def test_report_state_matrix_bbb_cells_locked() -> None:
    """Lock BBB Normal/AMD/COR coverage families (theme map TC-EV029-006)."""
    families = {c[0] for c in _BBB_CASES}
    assert families == {
        "METAR",
        "SPECI",
        "TAF",
        "SIGMET",
        "VA_SIGMET",
        "TC_SIGMET",
        "AIRMET",
        "VAA",
        "TCA",
        "SWXA",
    }
    # Every non-SWXA family must exercise NORMAL + CORRECTION + AMENDMENT.
    for family in families - {"SWXA"}:
        statuses = {c[5] for c in _BBB_CASES if c[0] == family}
        assert statuses == {"NORMAL", "CORRECTION", "AMENDMENT"}, f"{family}: {statuses}"


def test_report_state_gap_cells_documented() -> None:
    """No silent blanks - gap/N/A cells are explicit (COVERAGE_MATRIX / #823 B3)."""
    assert len(_GAP_OR_NA_CELLS) >= 10
    for family, state, note in _GAP_OR_NA_CELLS:
        assert family
        assert state
        assert note


@pytest.mark.parametrize(
    ("family_id", "product", "subdir", "fixture", "bbb", "status", "root_local"),
    _BBB_CASES,
    ids=[f"{c[0]}-{c[5]}" for c in _BBB_CASES],
)
def test_report_state_bbb_to_report_status(
    family_id: str,
    product: str,
    subdir: str,
    fixture: str,
    bbb: str | None,
    status: str,
    root_local: str,
) -> None:
    """AHL BBB drives ``@reportStatus`` when body has no COR/AMD keyword."""
    from tac2iwxxm import convert, parse_ahl, split_bulletin

    text = _read_case(subdir, fixture)
    split = split_bulletin(text, product=product)
    assert split.meta.bbb == bbb
    parts = parse_ahl(split.meta.ahl)
    assert parts.report_status == status

    result = convert(
        split.reports[0],
        product=product,
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
        report_status=parts.report_status,
    )
    assert result.ok is True, f"{family_id}/{fixture} convert: {result.issues!r}"
    assert result.xml is not None
    assert _has_root(result.xml, root_local), f"{family_id}: expected iwxxm:{root_local}"
    assert _report_status_from_xml(result.xml) == status


@pytest.mark.parametrize(
    ("family_id", "product", "source", "name", "root_local", "convert_mode"),
    _CNL_CASES,
    ids=[c[0] for c in _CNL_CASES],
)
def test_report_state_cnl_not_report_status(
    family_id: str,
    product: str,
    source: str,
    name: str,
    root_local: str,
    convert_mode: str,
) -> None:
    """CNL uses ``isCancelReport``; must not be encoded as AMD/COR reportStatus."""
    from tac2iwxxm import convert, split_bulletin

    text = _read_case(source, name)
    if convert_mode == "bulletin":
        payload = text
        split = split_bulletin(text, product=product)
        assert split.meta.report_count >= 1
    else:
        if source == "annex3":
            payload = text
        else:
            split = split_bulletin(text, product=product)
            payload = split.reports[0]

    result = convert(
        payload,
        product=product,
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"{family_id}/{name} convert: {result.issues!r}"
    assert result.xml is not None
    assert _has_root(result.xml, root_local), f"{family_id}: expected iwxxm:{root_local}"
    assert 'isCancelReport="true"' in result.xml, f"{family_id}: CNL must set isCancelReport"
    status = _report_status_from_xml(result.xml)
    assert status == "NORMAL", f"{family_id}: CNL must not use AMD/COR reportStatus, got {status!r}"
    assert status not in {"AMENDMENT", "CORRECTION"}


@pytest.mark.parametrize(
    ("family_id", "product", "tac_name", "root_local"),
    _NIL_CASES,
    ids=[c[0] for c in _NIL_CASES],
)
def test_report_state_nil_not_report_status(
    family_id: str,
    product: str,
    tac_name: str,
    root_local: str,
) -> None:
    """NIL uses nilReason / product NIL; must not be AMD/COR reportStatus."""
    from tac2iwxxm import convert

    tac = _read_case("annex3", tac_name)
    result = convert(
        tac,
        product=product,
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"{family_id}/{tac_name} convert: {result.issues!r}"
    assert result.xml is not None
    assert _has_root(result.xml, root_local), f"{family_id}: expected iwxxm:{root_local}"
    assert "nilReason=" in result.xml, f"{family_id}: NIL must emit nilReason"
    status = _report_status_from_xml(result.xml)
    assert status == "NORMAL", f"{family_id}: NIL must not use AMD/COR reportStatus, got {status!r}"
    assert status not in {"AMENDMENT", "CORRECTION"}
