"""TC-EV069-001..003: CA_ECCC validation deepen (EV-069 / #1035 follow-on).

Spec: docs/test-plan.md TC-EV069-*; layers 5-6 + TAF product XSD gate.
Corpus: [Corpus: product §F2] [Corpus: product §F13] [Corpus: tests]
"""

from __future__ import annotations

from pathlib import Path

import pytest
from iwxxm_validate import rust_available, validate_iwxxm
from iwxxm_validate.ca_eccc_bundle import CA_ECCC_IWXXM_VERSION
from iwxxm_validate.ca_eccc_layers import pending_ca_stages
from iwxxm_validate.ca_eccc_validate import STAGE_CA_XSD, STAGE_CODE_CA, STAGE_WMO_XSD
from iwxxm_validate.ca_exchange_validate import validate_ca_exchange_packaging
from iwxxm_validate.code_ca_registry import (
    CODE_CA_BASE,
    code_ca_membership_ok,
    is_code_ca_href,
    normalize_code_ca_href,
)
from iwxxm_validate.code_ca_validate import validate_code_ca_membership
from iwxxm_validate.models import Issue

REPO_ROOT = Path(__file__).resolve().parents[3]
CA_FIXTURES = REPO_ROOT / "packages" / "tac2iwxxm" / "tests" / "fixtures" / "profiles" / "CA_ECCC"


@pytest.mark.unit
def test_tc_ev069_001_pending_stages_empty_after_ev069() -> None:
    """All CA validation stages are implemented after EV-069."""
    assert pending_ca_stages() == ()


@pytest.mark.unit
def test_tc_ev069_002_taf_nclws_golden_passes_full_ca_stack() -> None:
    """TAF NCLWS golden passes layers 2-6 including product ``taf-ca.xsd``."""
    if not rust_available():
        pytest.skip("iwxxm_validate._rust not built (make build-iwxxm-validate-native)")

    golden = (CA_FIXTURES / "TAF" / "valid" / "taf_nclws.golden.xml").read_text(encoding="utf-8")
    report = validate_iwxxm(
        golden,
        iwxxm_version=CA_ECCC_IWXXM_VERSION,
        profile="ca_eccc",
        product="TAF",
        levels=("xsd", "schematron"),
    )
    stage_ids = [stage.stage for stage in report.stages]
    assert stage_ids == [
        "wellformed",
        "wmo_xsd",
        "wmo_schematron",
        "ca_xsd",
        "code_ca",
        "exchange",
    ]
    assert all(stage.ok for stage in report.stages), [
        (stage.stage, [(i.code, i.message) for i in stage.issues]) for stage in report.stages if not stage.ok
    ]
    assert report.ok is True


@pytest.mark.unit
def test_tc_ev069_003_unknown_code_ca_href_fails_at_code_ca_layer() -> None:
    """Invalid code-ca href fails at layer 5, not earlier layers."""
    golden = (CA_FIXTURES / "METAR" / "valid" / "metar_lwis.golden.xml").read_text(encoding="utf-8")
    bad = golden.replace(
        "https://dd.weather.gc.ca/today/aviation/iwxxm/code-ca/ObservingSystemType/LWIS",
        "https://dd.weather.gc.ca/today/aviation/iwxxm/code-ca/ObservingSystemType/NOT_A_REAL_CODE",
    )
    issues = validate_code_ca_membership(bad)
    assert issues
    assert all(issue.layer == STAGE_CODE_CA for issue in issues)
    assert issues[0].code == "CODE_CA_UNKNOWN"


@pytest.mark.unit
def test_tc_ev069_004_invalid_ca_extension_still_fails_at_ca_xsd_layer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CA-only XSD failures remain attributed to layer 4 with full stack enabled."""
    from iwxxm_validate import validate_iwxxm

    golden = (CA_FIXTURES / "METAR" / "valid" / "metar_rmk_icing.golden.xml").read_text(encoding="utf-8")

    def fake_run_rust_stage(
        xml_content: str,
        *,
        xsd_path: str,
        sch_path: str,
        catalog_roots: list[str],
        levels: list[str],
        stage_id: str,
    ) -> list[Issue]:
        if stage_id == STAGE_WMO_XSD:
            return []
        if stage_id == STAGE_CA_XSD:
            return [
                Issue(
                    severity="error",
                    code="XSD_VALIDATION_ERROR",
                    message="Canadian extension probe failure",
                    layer=STAGE_CA_XSD,
                )
            ]
        return []

    monkeypatch.setattr("iwxxm_validate.ca_eccc_validate._run_rust_stage", fake_run_rust_stage)
    monkeypatch.setattr("iwxxm_validate.ca_eccc_validate.rust_available", lambda: True)

    report = validate_iwxxm(
        golden,
        iwxxm_version=CA_ECCC_IWXXM_VERSION,
        profile="ca_eccc",
        product="METAR",
        levels=("xsd",),
    )
    wmo_stage = next(s for s in report.stages if s.stage == STAGE_WMO_XSD)
    ca_stage = next(s for s in report.stages if s.stage == STAGE_CA_XSD)
    assert wmo_stage.ok is True
    assert ca_stage.ok is False
    assert "code_ca" not in [s.stage for s in report.stages]
    assert report.ok is False


@pytest.mark.unit
def test_tc_ev069_005_code_ca_registry_helpers() -> None:
    """Registry normalization and membership helpers cover fragment/query stripping."""
    lwis = f"{CODE_CA_BASE}/ObservingSystemType/LWIS"
    assert normalize_code_ca_href(f"{lwis}/?cache=1") == lwis
    assert normalize_code_ca_href(f"{lwis}#fragment") == lwis
    assert is_code_ca_href(lwis) is True
    assert is_code_ca_href("https://example.com/not-code-ca") is False
    assert code_ca_membership_ok(lwis) is True
    assert code_ca_membership_ok(f"{CODE_CA_BASE}/ObservingSystemType/NOT_A_REAL_CODE") is False


@pytest.mark.unit
def test_tc_ev069_006_code_ca_validate_edge_paths() -> None:
    """Syntax errors and duplicate href deduplication are attributed to layer 5."""
    issues = validate_code_ca_membership("<not-xml")
    assert len(issues) == 1
    assert issues[0].code == "XML_SYNTAX_ERROR"
    assert issues[0].layer == STAGE_CODE_CA

    golden = (CA_FIXTURES / "METAR" / "valid" / "metar_lwis.golden.xml").read_text(encoding="utf-8")
    lwis_href = "https://dd.weather.gc.ca/today/aviation/iwxxm/code-ca/ObservingSystemType/LWIS"
    duplicate = golden.replace(
        "</iwxxm-ca:Addendum>",
        f'</iwxxm-ca:Addendum><iwxxm-ca:Addendum><iwxxm-ca:observingSystemType xlink:href="{lwis_href}"/></iwxxm-ca:Addendum>',
        1,
    )
    assert validate_code_ca_membership(duplicate) == []


@pytest.mark.unit
def test_tc_ev069_007_exchange_validate_error_paths() -> None:
    """Exchange layer reports syntax, namespace, attribute, and AHL mismatches."""
    golden = (CA_FIXTURES / "METAR" / "valid" / "metar_lwis.golden.xml").read_text(encoding="utf-8")

    syntax_issues = validate_ca_exchange_packaging("<not-xml")
    assert syntax_issues[0].code == "XML_SYNTAX_ERROR"

    bad_root = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<doc xmlns="http://example.com" xmlns:gml="http://www.opengis.net/gml/3.2" '
        'gml:id="x" reportStatus="NORMAL" permissibleUsage="OPERATIONAL"/>'
    )
    namespace_issues = validate_ca_exchange_packaging(bad_root)
    assert any(issue.code == "CA_EXCHANGE_NAMESPACE" for issue in namespace_issues)

    bad_status = golden.replace('reportStatus="NORMAL"', 'reportStatus="BOGUS"', 1)
    status_issues = validate_ca_exchange_packaging(bad_status)
    assert any(issue.code == "CA_EXCHANGE_REPORT_STATUS" for issue in status_issues)

    bad_usage = golden.replace('permissibleUsage="OPERATIONAL"', 'permissibleUsage="BOGUS"', 1)
    usage_issues = validate_ca_exchange_packaging(bad_usage)
    assert any(issue.code == "CA_EXCHANGE_PERMISSIBLE_USAGE" for issue in usage_issues)

    ahl_issues = validate_ca_exchange_packaging(golden, product="METAR", ahl_header="A_LTCN31 CYUL 291800")
    assert any(issue.code == "CA_EXCHANGE_AHL_PRODUCT" for issue in ahl_issues)

    filename_issues = validate_ca_exchange_packaging(golden, expected_filename="not-a-valid-name.xml")
    assert any(issue.code == "CA_EXCHANGE_FILENAME" for issue in filename_issues)

    centre_issues = validate_ca_exchange_packaging(golden, require_translation_centre=True)
    assert any(issue.code == "CA_EXCHANGE_TRANSLATION_CENTRE" for issue in centre_issues)

    assert validate_ca_exchange_packaging(golden) == []
