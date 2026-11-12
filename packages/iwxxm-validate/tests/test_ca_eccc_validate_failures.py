"""CA_ECCC layered validation failure paths without full GML catalog parse.

[Corpus: tests] — mocks avoid local SCHEMA_PARSE_ERROR / AngleType flakes.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from iwxxm_validate.ca_eccc_layers import STAGE_CA_XSD, STAGE_EXCHANGE, STAGE_WELLFORMED
from iwxxm_validate.ca_eccc_validate import (
    CA_EXTENSION_NS,
    _ca_xsd_probe_document,
    _issues_from_rust,
    _run_rust_stage,
    _validate_ca_xsd_document,
    _validate_ca_xsd_layer,
    validate_ca_eccc_layered,
)
from iwxxm_validate.ca_exchange_validate import validate_ca_exchange_packaging
from iwxxm_validate.models import Issue


def _bundle() -> MagicMock:
    bundle = MagicMock()
    bundle.core_xsd = Path("/tmp/fake-core.xsd")
    bundle.schematron = Path("/tmp/fake-core.sch")
    return bundle


def test_validate_ca_eccc_layered_missing_bundle(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "iwxxm_validate.ca_eccc_validate.resolve_ca_eccc_bundle",
        lambda **_: None,
    )
    report = validate_ca_eccc_layered("<root/>", iwxxm_version="3.0.0")
    assert report.ok is False
    assert report.issues[0].code == "CA_SCHEMA_NOT_FOUND"


def test_validate_ca_eccc_layered_wellformed_error_short_circuits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "iwxxm_validate.ca_eccc_validate.resolve_ca_eccc_bundle",
        lambda **_: _bundle(),
    )
    monkeypatch.setattr("iwxxm_validate.ca_eccc_validate.ca_eccc_catalog_roots", lambda _v: [])
    monkeypatch.setattr("iwxxm_validate.ca_eccc_validate.rust_available", lambda: False)
    report = validate_ca_eccc_layered("<not-xml", iwxxm_version="3.0.0", levels=("xsd",))
    assert report.ok is False
    assert len(report.stages) == 1
    assert report.stages[0].stage == STAGE_WELLFORMED
    assert report.issues[0].code == "XML_SYNTAX_ERROR"


def test_validate_ca_eccc_layered_wmo_xsd_error_skips_later_stages(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "iwxxm_validate.ca_eccc_validate.resolve_ca_eccc_bundle",
        lambda **_: _bundle(),
    )
    monkeypatch.setattr("iwxxm_validate.ca_eccc_validate.ca_eccc_catalog_roots", lambda _v: [])
    monkeypatch.setattr("iwxxm_validate.ca_eccc_validate.rust_available", lambda: False)
    monkeypatch.setattr(
        "iwxxm_validate.ca_eccc_validate.validate_xsd",
        lambda *_a, **_k: [
            Issue(
                severity="error",
                code="XSD_ERROR",
                message="forced xsd failure",
                layer="xsd",
            )
        ],
    )
    xml = "<?xml version='1.0'?><iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/3.0'/>"
    report = validate_ca_eccc_layered(xml, iwxxm_version="3.0.0", product="METAR", levels=("xsd",))
    assert report.ok is False
    assert any(i.code == "XSD_ERROR" for i in report.issues)
    assert not any(s.stage == STAGE_CA_XSD for s in report.stages)
    assert not any(s.stage == STAGE_EXCHANGE for s in report.stages)


def test_validate_ca_eccc_layered_product_xsd_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "iwxxm_validate.ca_eccc_validate.resolve_ca_eccc_bundle",
        lambda **_: _bundle(),
    )
    monkeypatch.setattr("iwxxm_validate.ca_eccc_validate.ca_eccc_catalog_roots", lambda _v: [])
    monkeypatch.setattr("iwxxm_validate.ca_eccc_validate.rust_available", lambda: False)
    monkeypatch.setattr("iwxxm_validate.ca_eccc_validate.validate_xsd", lambda *_a, **_k: [])
    monkeypatch.setattr(
        "iwxxm_validate.ca_eccc_validate.ca_product_has_national_xsd",
        lambda _p: True,
    )
    monkeypatch.setattr(
        "iwxxm_validate.ca_eccc_validate.ca_product_xsd_path",
        lambda _p: None,
    )
    monkeypatch.setattr(
        "iwxxm_validate.ca_eccc_validate.validate_code_ca_membership",
        lambda _xml: [],
    )
    xml = "<?xml version='1.0'?><iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/3.0'/>"
    report = validate_ca_eccc_layered(xml, iwxxm_version="3.0.0", product="METAR", levels=("xsd",))
    assert report.ok is False
    assert any(i.code == "CA_PRODUCT_XSD_NOT_FOUND" for i in report.issues)


def test_validate_ca_xsd_layer_unknown_root_fails() -> None:
    issues = _validate_ca_xsd_layer(
        "<?xml version='1.0'?><other xmlns='http://example.test'/>",
        product="METAR",
        product_xsd=Path("/nonexistent/metar-speci-ca.xsd"),
        core_sch="",
        catalog_roots=[],
    )
    assert issues[0].code == "CA_PRODUCT_ROOT_UNKNOWN"


def test_validate_ca_exchange_packaging_failure_codes() -> None:
    bad = "<?xml version='1.0'?><doc xmlns='http://example.test' reportStatus='WEIRD' permissibleUsage='NOPE'/>"
    issues = validate_ca_exchange_packaging(bad, product="METAR", ahl_header="A_LTCN31 CYUL 291800")
    codes = {i.code for i in issues}
    assert "CA_EXCHANGE_NAMESPACE" in codes
    assert "CA_EXCHANGE_REPORT_STATUS" in codes
    assert "CA_EXCHANGE_PERMISSIBLE_USAGE" in codes
    assert "CA_EXCHANGE_GML_ID" in codes


def test_validate_ca_exchange_packaging_syntax_error() -> None:
    issues = validate_ca_exchange_packaging("<broken")
    assert issues[0].code == "XML_SYNTAX_ERROR"
    assert issues[0].layer == STAGE_EXCHANGE


def test_validate_ca_eccc_layered_exchange_not_applicable_info(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "iwxxm_validate.ca_eccc_validate.resolve_ca_eccc_bundle",
        lambda **_: _bundle(),
    )
    monkeypatch.setattr("iwxxm_validate.ca_eccc_validate.ca_eccc_catalog_roots", lambda _v: [])
    monkeypatch.setattr("iwxxm_validate.ca_eccc_validate.rust_available", lambda: False)
    monkeypatch.setattr("iwxxm_validate.ca_eccc_validate.validate_xsd", lambda *_a, **_k: [])
    monkeypatch.setattr(
        "iwxxm_validate.ca_eccc_validate.ca_product_has_national_xsd",
        lambda _p: False,
    )
    monkeypatch.setattr(
        "iwxxm_validate.ca_eccc_validate.ca_product_has_exchange_output",
        lambda _p: False,
    )
    monkeypatch.setattr(
        "iwxxm_validate.ca_eccc_validate.validate_code_ca_membership",
        lambda _xml: [],
    )
    xml = "<?xml version='1.0'?><iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/3.0'/>"
    report = validate_ca_eccc_layered(xml, iwxxm_version="3.0.0", product="VAA", levels=("xsd",))
    assert any(i.code == "CA_XSD_NOT_APPLICABLE" for i in report.issues)
    assert any(i.code == "CA_EXCHANGE_NOT_APPLICABLE" for i in report.issues)


def test_run_rust_stage_invokes_native_module(monkeypatch: pytest.MonkeyPatch) -> None:
    rust = MagicMock()
    rust.validate_document.return_value = [
        {
            "layer": "xsd",
            "severity": "error",
            "code": "NATIVE_XSD",
            "message": "rust fail",
        }
    ]
    monkeypatch.setattr("iwxxm_validate.ca_eccc_validate.rust_module", lambda: rust)
    issues = _run_rust_stage(
        "<root/>",
        xsd_path="/tmp/x.xsd",
        sch_path="/tmp/x.sch",
        catalog_roots=["/tmp/cat"],
        levels=["xsd"],
        stage_id=STAGE_CA_XSD,
    )
    rust.validate_document.assert_called_once()
    assert issues[0].code == "NATIVE_XSD"
    assert issues[0].layer == STAGE_CA_XSD


def test_issues_from_rust_maps_layers_and_defaults() -> None:
    # When rust layer maps to a different stage than the caller stage_id,
    # the issue keeps the caller stage_id (fail attribution stays on the active stage).
    remapped = _issues_from_rust(
        [
            {"layer": "wellformed", "severity": "error", "code": "WF", "message": "bad"},
            {"layer": "unknown", "message": "fallback"},
        ],
        STAGE_CA_XSD,
    )
    assert remapped[0].layer == STAGE_CA_XSD
    assert remapped[0].code == "WF"
    assert remapped[1].code == "NATIVE_ISSUE"
    assert remapped[1].layer == STAGE_CA_XSD

    same = _issues_from_rust(
        [{"layer": "wellformed", "severity": "error", "code": "WF2", "message": "x"}],
        STAGE_WELLFORMED,
    )
    assert same[0].layer == STAGE_WELLFORMED
    assert same[0].code == "WF2"


def test_validate_ca_xsd_document_uses_rust_when_available(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called: dict[str, object] = {}

    def _fake_rust(
        xml_content: str,
        *,
        xsd_path: str,
        sch_path: str,
        catalog_roots: list[str],
        levels: list[str],
        stage_id: str,
    ) -> list[Issue]:
        called["stage"] = stage_id
        called["levels"] = levels
        return [
            Issue(
                severity="error",
                code="RUST_XSD_FAIL",
                message="mocked rust fail",
                layer=stage_id,
            )
        ]

    monkeypatch.setattr("iwxxm_validate.ca_eccc_validate.rust_available", lambda: True)
    monkeypatch.setattr("iwxxm_validate.ca_eccc_validate._run_rust_stage", _fake_rust)
    issues = _validate_ca_xsd_document(
        "<root/>",
        product_xsd=Path("/tmp/ca.xsd"),
        core_sch="/tmp/core.sch",
        catalog_roots=[],
    )
    assert called["stage"] == STAGE_CA_XSD
    assert called["levels"] == ["xsd"]
    assert issues[0].code == "RUST_XSD_FAIL"


def test_ca_xsd_probe_document_taf_passthrough() -> None:
    frag = "<iwxxm-ca:Addendum xmlns:iwxxm-ca='https://dd.meteo.gc.ca/today/aviation/iwxxm/'/>"
    out = _ca_xsd_probe_document(frag, product="TAF")
    assert out.startswith("<?xml version=")
    assert "Addendum" in out
    assert "LWIS" not in out


def test_validate_ca_xsd_layer_substitution_root_calls_document(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: dict[str, str] = {}

    def _fake_doc(xml_content: str, **_kwargs: object) -> list[Issue]:
        seen["xml"] = xml_content
        return [
            Issue(
                severity="error",
                code="CA_SUB_FAIL",
                message="substitution probe failed",
                layer=STAGE_CA_XSD,
            )
        ]

    monkeypatch.setattr("iwxxm_validate.ca_eccc_validate._validate_ca_xsd_document", _fake_doc)
    xml = (
        f"<?xml version='1.0'?><iwxxm-ca:LWIS xmlns:iwxxm-ca='{CA_EXTENSION_NS}' "
        "reportStatus='NORMAL' permissibleUsage='OPERATIONAL'/>"
    )
    issues = _validate_ca_xsd_layer(
        xml,
        product="METAR",
        product_xsd=Path("/tmp/metar-speci-ca.xsd"),
        core_sch="",
        catalog_roots=[],
    )
    assert issues[0].code == "CA_SUB_FAIL"
    assert "LWIS" in seen["xml"]


def test_validate_ca_eccc_layered_exchange_output_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "iwxxm_validate.ca_eccc_validate.resolve_ca_eccc_bundle",
        lambda **_: _bundle(),
    )
    monkeypatch.setattr("iwxxm_validate.ca_eccc_validate.ca_eccc_catalog_roots", lambda _v: [])
    monkeypatch.setattr("iwxxm_validate.ca_eccc_validate.rust_available", lambda: False)
    monkeypatch.setattr("iwxxm_validate.ca_eccc_validate.validate_xsd", lambda *_a, **_k: [])
    monkeypatch.setattr(
        "iwxxm_validate.ca_eccc_validate.ca_product_has_national_xsd",
        lambda _p: False,
    )
    monkeypatch.setattr(
        "iwxxm_validate.ca_eccc_validate.ca_product_has_exchange_output",
        lambda _p: True,
    )
    monkeypatch.setattr(
        "iwxxm_validate.ca_eccc_validate.validate_code_ca_membership",
        lambda _xml: [],
    )
    monkeypatch.setattr(
        "iwxxm_validate.ca_eccc_validate.validate_ca_exchange_packaging",
        lambda *_a, **_k: [
            Issue(
                severity="error",
                code="CA_EXCHANGE_FORCED",
                message="exchange fail",
                layer=STAGE_EXCHANGE,
            )
        ],
    )
    xml = "<?xml version='1.0'?><iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/3.0'/>"
    report = validate_ca_eccc_layered(xml, iwxxm_version="3.0.0", product="METAR", levels=("xsd",))
    assert report.ok is False
    assert any(i.code == "CA_EXCHANGE_FORCED" for i in report.issues)


def test_validate_ca_eccc_layered_rust_schematron_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "iwxxm_validate.ca_eccc_validate.resolve_ca_eccc_bundle",
        lambda **_: _bundle(),
    )
    monkeypatch.setattr("iwxxm_validate.ca_eccc_validate.ca_eccc_catalog_roots", lambda _v: [])
    monkeypatch.setattr("iwxxm_validate.ca_eccc_validate.rust_available", lambda: True)

    def _fake_rust(
        xml_content: str,
        *,
        xsd_path: str,
        sch_path: str,
        catalog_roots: list[str],
        levels: list[str],
        stage_id: str,
    ) -> list[Issue]:
        if stage_id == STAGE_WELLFORMED or levels == []:
            return []
        if "schematron" in levels:
            return [
                Issue(
                    severity="error",
                    code="SCH_FAIL",
                    message="schematron mocked fail",
                    layer=stage_id,
                )
            ]
        return []

    monkeypatch.setattr("iwxxm_validate.ca_eccc_validate._run_rust_stage", _fake_rust)
    xml = "<?xml version='1.0'?><iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/3.0'/>"
    report = validate_ca_eccc_layered(
        xml,
        iwxxm_version="3.0.0",
        product=None,
        levels=("schematron",),
    )
    assert report.ok is False
    assert any(i.code == "SCH_FAIL" for i in report.issues)
