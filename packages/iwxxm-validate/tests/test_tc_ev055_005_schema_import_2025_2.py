"""TC-EV055-005: SCHEMA_IMPORT_WARNING fixed for IWXXM 2025-2 (hard — native path).

Spec: docs/test-plan.md TC-EV055-005; AC5; #979; D-S064-xsd-hard=1.
Root cause: lxml XMLSchema cannot resolve GML ``AbstractFeature`` substitutionGroup
for ``{http://icao.int/iwxxm/2025-2}BasicReport``; native xmloxide + catalog roots can.
Corpus: [Corpus: product §F2] [Corpus: tests]
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
VENDOR_2025_2_METAR = REPO_ROOT / "vendor" / "schemas" / "iwxxm" / "2025-2" / "IWXXM" / "examples" / "metar-A3-1.xml"


@pytest.fixture(scope="module")
def metar_2025_2_xml() -> str:
    assert VENDOR_2025_2_METAR.is_file(), f"missing fixture {VENDOR_2025_2_METAR}"
    return VENDOR_2025_2_METAR.read_text(encoding="utf-8")


def test_tc_ev055_005_native_xsd_no_schema_import_warning(metar_2025_2_xml: str) -> None:
    """Native validate_iwxxm must run strict XSD for 2025-2 (no SCHEMA_IMPORT_WARNING)."""
    from iwxxm_validate import rust_available, validate_iwxxm

    if not rust_available():
        pytest.skip("iwxxm_validate._rust not built (make build-iwxxm-validate-native)")

    report = validate_iwxxm(
        metar_2025_2_xml,
        iwxxm_version="2025-2",
        profile="annex3",
        levels=("xsd",),
    )
    warned = [i for i in report.issues if i.code == "SCHEMA_IMPORT_WARNING"]
    assert warned == [], f"unexpected SCHEMA_IMPORT_WARNING: {warned}"
    assert report.ok is True


def test_tc_ev055_005_lxml_still_documents_import_gap(metar_2025_2_xml: str) -> None:
    """Engine matrix: lxml soft-skips 2025-2 XSD compile (substitutionGroup / GML)."""
    from iwxxm_validate import validate

    report = validate(
        metar_2025_2_xml,
        iwxxm_version="2025-2",
        profile="annex3",
        levels=("xsd",),
    )
    assert any(i.code == "SCHEMA_IMPORT_WARNING" for i in report.issues)


def test_tc_ev055_005_metrics_entrypoint_uses_native(metar_2025_2_xml: str) -> None:
    """Quality-metrics validate helper must not emit SCHEMA_IMPORT_WARNING when native is built."""
    from iwxxm_validate import rust_available
    from iwxxm_validate.metrics_validate import validate_for_quality_metrics

    if not rust_available():
        pytest.skip("iwxxm_validate._rust not built (make build-iwxxm-validate-native)")

    report = validate_for_quality_metrics(
        metar_2025_2_xml,
        iwxxm_version="2025-2",
        profile="annex3",
    )
    assert not any(i.code == "SCHEMA_IMPORT_WARNING" for i in report.issues)
