"""TC-EV055-004: Schematron enabled for IWXXM 2025-2 (hard — native path).

Spec: docs/test-plan.md TC-EV055-004; AC4; #980; D-S064-sch-hard=1.
Corpus: [Corpus: product §F13] [Corpus: tests]
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


def test_tc_ev055_004_native_schematron_not_skipped(metar_2025_2_xml: str) -> None:
    """Native validate_iwxxm must evaluate 2025-2 Schematron (no SCHEMATRON_SKIPPED)."""
    from iwxxm_validate import rust_available, validate_iwxxm

    if not rust_available():
        pytest.skip("iwxxm_validate._rust not built (make build-iwxxm-validate-native)")

    report = validate_iwxxm(
        metar_2025_2_xml,
        iwxxm_version="2025-2",
        profile="annex3",
        levels=("schematron",),
    )
    skipped = [i for i in report.issues if i.code == "SCHEMATRON_SKIPPED"]
    assert skipped == [], f"unexpected SCHEMATRON_SKIPPED: {skipped}"


def test_tc_ev055_004_lxml_still_documents_xslt2_skip(metar_2025_2_xml: str) -> None:
    """Engine matrix: lxml path soft-skips xslt2 (documented; not the Quality metrics path)."""
    from iwxxm_validate import validate

    report = validate(
        metar_2025_2_xml,
        iwxxm_version="2025-2",
        profile="annex3",
        levels=("schematron",),
    )
    assert any(i.code == "SCHEMATRON_SKIPPED" for i in report.issues)


def test_tc_ev055_004_metrics_entrypoint_uses_native(metar_2025_2_xml: str) -> None:
    """Quality-metrics validate helper must not emit SCHEMATRON_SKIPPED when native is built."""
    from iwxxm_validate import rust_available
    from iwxxm_validate.metrics_validate import validate_for_quality_metrics

    if not rust_available():
        pytest.skip("iwxxm_validate._rust not built (make build-iwxxm-validate-native)")

    report = validate_for_quality_metrics(
        metar_2025_2_xml,
        iwxxm_version="2025-2",
        profile="annex3",
    )
    assert not any(i.code == "SCHEMATRON_SKIPPED" for i in report.issues)
