"""Focused unit tests for validation orchestrator branch behavior."""

from dataclasses import dataclass

import pytest
from src.schemas.validation import (
    CodelistValidationResult,
    GMLValidationResult,
    SchematronValidationResult,
    ValidationIssue,
    ValidationLayer,
    ValidationResult,
    ValidationSeverity,
    XSDValidationResult,
)
from src.services import validation_orchestrator as orchestrator_module
from src.services.iwxxm_validation_adapter import pkg_issue_to_backend
from src.services.validation_orchestrator import (
    ComprehensiveValidationResult,
    ValidationOrchestrator,
    get_validation_orchestrator,
)

SAMPLE_TAC = "METAR KJFK 112030Z 18012KT 10SM FEW250 15/07 A3005"
SAMPLE_XML = "<root/>"


@dataclass
class DummyValidationOutcome:
    """Simple result object used to exercise pass/fail helper paths."""

    passed: bool
    issues: list


@dataclass
class DummyIsValidOutcome:
    """Alternative result shape using is_valid."""

    is_valid: bool
    issues: list


def make_issue(layer: ValidationLayer, code: str) -> ValidationIssue:
    """Create a validation issue for result objects."""
    return ValidationIssue(
        layer=layer,
        level=ValidationSeverity.ERROR,
        message=f"issue for {code}",
        code=code,
    )


def make_result(layer: ValidationLayer, passed: bool = True, code: str | None = None):
    """Create a validation result with an optional issue."""
    issues = [make_issue(layer, code)] if code else []
    return ValidationResult(passed=passed, layer=layer, issues=issues)


def force_legacy_xml_validators(monkeypatch) -> None:
    """Disable native iwxxm-validate so unit tests exercise lxml validators."""
    monkeypatch.setattr("iwxxm_validate.rust_available", lambda: False)


class TestValidationOrchestratorBranches:
    """Exercise key validation orchestrator decision branches."""

    def test_is_validation_passed_variants(self, caplog):
        """Pass/fail helper should support passed and is_valid attributes."""
        orchestrator = ValidationOrchestrator()

        assert orchestrator._is_validation_passed(DummyValidationOutcome(True, []))
        assert not orchestrator._is_validation_passed(DummyValidationOutcome(False, []))
        assert orchestrator._is_validation_passed(DummyIsValidOutcome(True, []))
        assert not orchestrator._is_validation_passed(DummyIsValidOutcome(False, []))

        assert not orchestrator._is_validation_passed(object())
        assert "Unknown result type" in caplog.text

    def test_validate_wellformed_invalid_xml_sets_error_issue(self):
        """Malformed XML should fail layer 3 with issue details."""
        orchestrator = ValidationOrchestrator()

        result = orchestrator.validate_wellformed("<root>")

        assert isinstance(result, ValidationResult)
        assert not result.passed
        assert result.layer == ValidationLayer.XML_WELLFORMED
        assert result.issues
        assert "well-formed" in result.issues[0].message

    def test_validate_wellformed_valid_xml_passes(self):
        """Well-formed XML should pass layer 3 with no issues."""
        orchestrator = ValidationOrchestrator()

        result = orchestrator.validate_wellformed("<root><child/></root>")

        assert result.passed is True
        assert result.layer == ValidationLayer.XML_WELLFORMED
        assert result.issues == []

    def test_validate_xml_schema_helper_delegates_to_adapter(self, monkeypatch):
        """Schema helper should delegate to iwxxm_validation_adapter."""
        orchestrator = ValidationOrchestrator()
        expected = XSDValidationResult(is_valid=True, issues=[], schema_version="2025-2")

        monkeypatch.setattr(
            "src.services.iwxxm_validation_adapter.validate_xml_schema",
            lambda _xml, _version, **kwargs: expected,
        )

        result = orchestrator.validate_xml_schema(SAMPLE_XML, "2025-2")

        assert result is expected

    def test_validate_complete_defaults_to_all_layers(self, monkeypatch):
        """Omitting layers should run the full validation sequence."""
        orchestrator = ValidationOrchestrator()

        monkeypatch.setattr(
            orchestrator.validation_service,
            "validate_airport_icao",
            lambda _tac: make_result(ValidationLayer.AIRPORT_ICAO),
        )
        monkeypatch.setattr(
            orchestrator.validation_service,
            "validate_tac_syntax",
            lambda _tac: make_result(ValidationLayer.TAC_SYNTAX),
        )
        monkeypatch.setattr(
            orchestrator,
            "validate_wellformed",
            lambda _xml: make_result(ValidationLayer.XML_WELLFORMED),
        )
        monkeypatch.setattr(
            orchestrator,
            "validate_xml_schema",
            lambda _xml, _version: XSDValidationResult(is_valid=True, issues=[], schema_version="2025-2"),
        )
        monkeypatch.setattr(
            orchestrator,
            "_validate_schematron",
            lambda _xml, _version: SchematronValidationResult(
                is_valid=True, issues=[], schema_version="2025-2", rules_evaluated=0
            ),
        )
        monkeypatch.setattr(
            orchestrator,
            "_run_gml_layer",
            staticmethod(lambda _xml, _version: GMLValidationResult(is_valid=True, issues=[])),
        )
        monkeypatch.setattr(
            orchestrator,
            "_run_codelist_layer",
            staticmethod(lambda _xml, _version: CodelistValidationResult(is_valid=True, issues=[])),
        )

        result = orchestrator.validate_complete(
            tac_text=SAMPLE_TAC,
            xml_content=SAMPLE_XML,
            version="2025-2",
            layers=None,
            stop_on_error=True,
        )

        assert result.is_valid is True
        assert result.layers_failed == []
        assert set(result.layers_run) == set(ValidationLayer)

    def test_validate_complete_stops_at_layer1_when_blocking_fails(self, monkeypatch):
        """Layer 1 failure with stop_on_error should return early."""
        orchestrator = ValidationOrchestrator()

        issue = make_issue(ValidationLayer.AIRPORT_ICAO, "L1")
        l1_result = ValidationResult(
            passed=False,
            layer=ValidationLayer.AIRPORT_ICAO,
            issues=[issue],
        )

        monkeypatch.setattr(
            orchestrator.validation_service,
            "validate_airport_icao",
            lambda _tac: l1_result,
        )

        result = orchestrator.validate_complete(
            tac_text=SAMPLE_TAC,
            xml_content=SAMPLE_XML,
            version="2025-2",
            layers=[ValidationLayer.AIRPORT_ICAO, ValidationLayer.TAC_SYNTAX],
            stop_on_error=True,
        )

        assert isinstance(result, ComprehensiveValidationResult)
        assert not result.is_valid
        assert result.stopped_at_layer == ValidationLayer.AIRPORT_ICAO
        assert ValidationLayer.AIRPORT_ICAO in result.layers_failed
        assert ValidationLayer.TAC_SYNTAX not in result.layers_run

    def test_validate_complete_continues_when_stop_on_error_false(self, monkeypatch):
        """Non-blocking mode should continue after early-layer failure."""
        orchestrator = ValidationOrchestrator()

        l1_fail = ValidationResult(
            passed=False,
            layer=ValidationLayer.AIRPORT_ICAO,
            issues=[make_issue(ValidationLayer.AIRPORT_ICAO, "L1")],
        )
        l2_pass = ValidationResult(
            passed=True,
            layer=ValidationLayer.TAC_SYNTAX,
            issues=[],
        )

        monkeypatch.setattr(
            orchestrator.validation_service,
            "validate_airport_icao",
            lambda _tac: l1_fail,
        )
        monkeypatch.setattr(
            orchestrator.validation_service,
            "validate_tac_syntax",
            lambda _tac: l2_pass,
        )

        result = orchestrator.validate_complete(
            tac_text=SAMPLE_TAC,
            xml_content=SAMPLE_XML,
            version="2025-2",
            layers=[ValidationLayer.AIRPORT_ICAO, ValidationLayer.TAC_SYNTAX],
            stop_on_error=False,
        )

        assert ValidationLayer.AIRPORT_ICAO in result.layers_failed
        assert ValidationLayer.TAC_SYNTAX in result.layers_passed
        assert result.stopped_at_layer is None

    def test_validate_complete_layer4_uses_validate_xml_schema(self, monkeypatch):
        """Layer 4 should route through validate_xml_schema helper."""
        orchestrator = ValidationOrchestrator()

        l1_pass = ValidationResult(
            passed=True,
            layer=ValidationLayer.AIRPORT_ICAO,
            issues=[],
        )
        l2_pass = ValidationResult(
            passed=True,
            layer=ValidationLayer.TAC_SYNTAX,
            issues=[],
        )
        l3_pass = ValidationResult(
            passed=True,
            layer=ValidationLayer.XML_WELLFORMED,
            issues=[],
        )

        monkeypatch.setattr(
            orchestrator.validation_service,
            "validate_airport_icao",
            lambda _tac: l1_pass,
        )
        monkeypatch.setattr(
            orchestrator.validation_service,
            "validate_tac_syntax",
            lambda _tac: l2_pass,
        )
        monkeypatch.setattr(orchestrator, "validate_wellformed", lambda _xml: l3_pass)

        xml_schema_result = DummyValidationOutcome(
            passed=False,
            issues=[make_issue(ValidationLayer.XML_SCHEMA, "L4")],
        )
        monkeypatch.setattr(
            orchestrator,
            "validate_xml_schema",
            lambda _xml, _version: xml_schema_result,
        )

        result = orchestrator.validate_complete(
            tac_text=SAMPLE_TAC,
            xml_content=SAMPLE_XML,
            version="2025-2",
            layers=[
                ValidationLayer.AIRPORT_ICAO,
                ValidationLayer.TAC_SYNTAX,
                ValidationLayer.XML_WELLFORMED,
                ValidationLayer.XML_SCHEMA,
            ],
            stop_on_error=False,
        )

        assert ValidationLayer.XML_SCHEMA in result.layers_run
        assert ValidationLayer.XML_SCHEMA in result.layers_failed
        assert result.issues_by_layer[ValidationLayer.XML_SCHEMA][0].code == "L4"

    def test_validate_complete_layer4_stop_on_error_returns_early(self, monkeypatch):
        """Blocking schema failure should stop when configured to do so."""
        orchestrator = ValidationOrchestrator()

        monkeypatch.setattr(
            orchestrator.validation_service,
            "validate_airport_icao",
            lambda _tac: make_result(ValidationLayer.AIRPORT_ICAO),
        )
        monkeypatch.setattr(
            orchestrator.validation_service,
            "validate_tac_syntax",
            lambda _tac: make_result(ValidationLayer.TAC_SYNTAX),
        )
        monkeypatch.setattr(
            orchestrator,
            "validate_wellformed",
            lambda _xml: make_result(ValidationLayer.XML_WELLFORMED),
        )
        monkeypatch.setattr(
            orchestrator,
            "validate_xml_schema",
            lambda _xml, _version: make_result(ValidationLayer.XML_SCHEMA, passed=False, code="L4STOP"),
        )

        result = orchestrator.validate_complete(
            tac_text=SAMPLE_TAC,
            xml_content=SAMPLE_XML,
            version="2025-2",
            layers=[
                ValidationLayer.AIRPORT_ICAO,
                ValidationLayer.TAC_SYNTAX,
                ValidationLayer.XML_WELLFORMED,
                ValidationLayer.XML_SCHEMA,
                ValidationLayer.SCHEMATRON,
            ],
            stop_on_error=True,
        )

        assert result.stopped_at_layer == ValidationLayer.XML_SCHEMA
        assert ValidationLayer.XML_SCHEMA in result.layers_failed
        assert ValidationLayer.SCHEMATRON not in result.layers_run

    def test_parallel_layer_warning_paths(self, monkeypatch):
        """Parallel layers with setup warnings still complete via package adapter."""
        orchestrator = ValidationOrchestrator()
        warn_issue = make_issue(ValidationLayer.SCHEMATRON, "SCHEMATRON_SETUP_WARNING")

        monkeypatch.setattr(
            orchestrator,
            "_validate_schematron",
            lambda *_a, **_k: SchematronValidationResult(
                is_valid=True,
                issues=[warn_issue],
                schema_version="2025-2",
                rules_evaluated=0,
            ),
        )
        monkeypatch.setattr(
            orchestrator,
            "_run_gml_layer",
            staticmethod(
                lambda *_a, **_k: GMLValidationResult(
                    is_valid=True,
                    issues=[make_issue(ValidationLayer.GML_REFERENCES, "GML_SETUP_WARNING")],
                )
            ),
        )
        monkeypatch.setattr(
            orchestrator,
            "_run_codelist_layer",
            staticmethod(
                lambda *_a, **_k: CodelistValidationResult(
                    is_valid=True,
                    issues=[make_issue(ValidationLayer.WMO_CODELISTS, "WMO_CODELISTS_SETUP_WARNING")],
                )
            ),
        )

        result = orchestrator.validate_complete(
            tac_text=SAMPLE_TAC,
            xml_content=SAMPLE_XML,
            version="2025-2",
            layers=[
                ValidationLayer.SCHEMATRON,
                ValidationLayer.GML_REFERENCES,
                ValidationLayer.WMO_CODELISTS,
            ],
            stop_on_error=False,
        )

        assert ValidationLayer.SCHEMATRON in result.layers_passed
        assert ValidationLayer.GML_REFERENCES in result.layers_passed
        assert ValidationLayer.WMO_CODELISTS in result.layers_passed

        schematron_issues = result.issues_by_layer[ValidationLayer.SCHEMATRON]
        gml_issues = result.issues_by_layer[ValidationLayer.GML_REFERENCES]
        codelist_issues = result.issues_by_layer[ValidationLayer.WMO_CODELISTS]

        assert schematron_issues[0].code == "SCHEMATRON_SETUP_WARNING"
        assert gml_issues[0].code == "GML_SETUP_WARNING"
        assert codelist_issues[0].code == "WMO_CODELISTS_SETUP_WARNING"

    def test_parallel_layer_runtime_error_adds_validation_error(self, monkeypatch):
        """Runtime failures from parallel futures should mark the layer as failed."""
        orchestrator = ValidationOrchestrator()

        def _boom(*_args, **_kwargs):
            raise RuntimeError("boom")

        monkeypatch.setattr(orchestrator, "_validate_schematron", _boom)

        result = orchestrator.validate_complete(
            tac_text=SAMPLE_TAC,
            xml_content=SAMPLE_XML,
            version="2025-2",
            layers=[ValidationLayer.SCHEMATRON],
            stop_on_error=False,
        )

        assert ValidationLayer.SCHEMATRON in result.layers_run
        assert ValidationLayer.SCHEMATRON in result.layers_failed
        assert result.issues_by_layer[ValidationLayer.SCHEMATRON][0].code == "VALIDATION_ERROR"

    def test_validate_complete_stops_at_layer2_when_enabled(self, monkeypatch):
        orchestrator = ValidationOrchestrator()

        l1_pass = ValidationResult(
            passed=True,
            layer=ValidationLayer.AIRPORT_ICAO,
            issues=[],
        )
        l2_fail = ValidationResult(
            passed=False,
            layer=ValidationLayer.TAC_SYNTAX,
            issues=[make_issue(ValidationLayer.TAC_SYNTAX, "L2")],
        )

        monkeypatch.setattr(orchestrator.validation_service, "validate_airport_icao", lambda _tac: l1_pass)
        monkeypatch.setattr(orchestrator.validation_service, "validate_tac_syntax", lambda _tac: l2_fail)

        result = orchestrator.validate_complete(
            tac_text=SAMPLE_TAC,
            xml_content=SAMPLE_XML,
            version="2025-2",
            layers=[ValidationLayer.AIRPORT_ICAO, ValidationLayer.TAC_SYNTAX],
            stop_on_error=True,
        )

        assert result.stopped_at_layer == ValidationLayer.TAC_SYNTAX
        assert ValidationLayer.TAC_SYNTAX in result.layers_failed

    def test_validate_complete_stops_at_layer3_when_enabled(self, monkeypatch):
        orchestrator = ValidationOrchestrator()

        l1_pass = ValidationResult(passed=True, layer=ValidationLayer.AIRPORT_ICAO, issues=[])
        l2_pass = ValidationResult(passed=True, layer=ValidationLayer.TAC_SYNTAX, issues=[])
        l3_fail = ValidationResult(
            passed=False,
            layer=ValidationLayer.XML_WELLFORMED,
            issues=[make_issue(ValidationLayer.XML_WELLFORMED, "L3")],
        )

        monkeypatch.setattr(orchestrator.validation_service, "validate_airport_icao", lambda _tac: l1_pass)
        monkeypatch.setattr(orchestrator.validation_service, "validate_tac_syntax", lambda _tac: l2_pass)
        monkeypatch.setattr(orchestrator, "validate_wellformed", lambda _xml: l3_fail)

        result = orchestrator.validate_complete(
            tac_text=SAMPLE_TAC,
            xml_content=SAMPLE_XML,
            version="2025-2",
            layers=[
                ValidationLayer.AIRPORT_ICAO,
                ValidationLayer.TAC_SYNTAX,
                ValidationLayer.XML_WELLFORMED,
            ],
            stop_on_error=True,
        )

        assert result.stopped_at_layer == ValidationLayer.XML_WELLFORMED
        assert ValidationLayer.XML_WELLFORMED in result.layers_failed

    def test_validate_complete_layer1_exception_marks_failed(self, monkeypatch):
        orchestrator = ValidationOrchestrator()

        def _raise_layer1(_tac):
            raise RuntimeError("layer1 boom")

        monkeypatch.setattr(orchestrator.validation_service, "validate_airport_icao", _raise_layer1)

        result = orchestrator.validate_complete(
            tac_text=SAMPLE_TAC,
            xml_content=SAMPLE_XML,
            version="2025-2",
            layers=[ValidationLayer.AIRPORT_ICAO],
            stop_on_error=False,
        )

        assert ValidationLayer.AIRPORT_ICAO in result.layers_failed

    def test_validate_complete_layer2_exception_marks_failed(self, monkeypatch):
        orchestrator = ValidationOrchestrator()

        monkeypatch.setattr(
            orchestrator.validation_service,
            "validate_airport_icao",
            lambda _tac: make_result(ValidationLayer.AIRPORT_ICAO),
        )
        monkeypatch.setattr(
            orchestrator.validation_service,
            "validate_tac_syntax",
            lambda _tac: (_ for _ in ()).throw(RuntimeError("layer2 boom")),
        )

        result = orchestrator.validate_complete(
            tac_text=SAMPLE_TAC,
            xml_content=SAMPLE_XML,
            version="2025-2",
            layers=[ValidationLayer.AIRPORT_ICAO, ValidationLayer.TAC_SYNTAX],
            stop_on_error=False,
        )

        assert ValidationLayer.AIRPORT_ICAO in result.layers_passed
        assert ValidationLayer.TAC_SYNTAX in result.layers_failed

    def test_validate_complete_layer3_exception_marks_failed(self, monkeypatch):
        orchestrator = ValidationOrchestrator()

        monkeypatch.setattr(
            orchestrator.validation_service,
            "validate_airport_icao",
            lambda _tac: make_result(ValidationLayer.AIRPORT_ICAO),
        )
        monkeypatch.setattr(
            orchestrator.validation_service,
            "validate_tac_syntax",
            lambda _tac: make_result(ValidationLayer.TAC_SYNTAX),
        )
        monkeypatch.setattr(
            orchestrator,
            "validate_wellformed",
            lambda _xml: (_ for _ in ()).throw(RuntimeError("layer3 boom")),
        )

        result = orchestrator.validate_complete(
            tac_text=SAMPLE_TAC,
            xml_content=SAMPLE_XML,
            version="2025-2",
            layers=[
                ValidationLayer.AIRPORT_ICAO,
                ValidationLayer.TAC_SYNTAX,
                ValidationLayer.XML_WELLFORMED,
            ],
            stop_on_error=False,
        )

        assert ValidationLayer.XML_WELLFORMED in result.layers_failed

    def test_validate_complete_layer4_exception_marks_failed(self, monkeypatch):
        orchestrator = ValidationOrchestrator()

        monkeypatch.setattr(
            orchestrator.validation_service,
            "validate_airport_icao",
            lambda _tac: make_result(ValidationLayer.AIRPORT_ICAO),
        )
        monkeypatch.setattr(
            orchestrator.validation_service,
            "validate_tac_syntax",
            lambda _tac: make_result(ValidationLayer.TAC_SYNTAX),
        )
        monkeypatch.setattr(
            orchestrator,
            "validate_wellformed",
            lambda _xml: make_result(ValidationLayer.XML_WELLFORMED),
        )
        monkeypatch.setattr(
            orchestrator,
            "validate_xml_schema",
            lambda _xml, _version: (_ for _ in ()).throw(RuntimeError("layer4 boom")),
        )

        result = orchestrator.validate_complete(
            tac_text=SAMPLE_TAC,
            xml_content=SAMPLE_XML,
            version="2025-2",
            layers=[
                ValidationLayer.AIRPORT_ICAO,
                ValidationLayer.TAC_SYNTAX,
                ValidationLayer.XML_WELLFORMED,
                ValidationLayer.XML_SCHEMA,
            ],
            stop_on_error=False,
        )

        assert ValidationLayer.XML_SCHEMA in result.layers_failed

    def test_parallel_layers_all_pass(self, monkeypatch):
        orchestrator = ValidationOrchestrator()

        monkeypatch.setattr(
            orchestrator,
            "_validate_schematron",
            lambda *_a, **_k: SchematronValidationResult(
                is_valid=True, issues=[], schema_version="2025-2", rules_evaluated=0
            ),
        )
        monkeypatch.setattr(
            orchestrator,
            "_run_gml_layer",
            staticmethod(lambda *_a, **_k: GMLValidationResult(is_valid=True, issues=[])),
        )
        monkeypatch.setattr(
            orchestrator,
            "_run_codelist_layer",
            staticmethod(lambda *_a, **_k: CodelistValidationResult(is_valid=True, issues=[])),
        )

        result = orchestrator.validate_complete(
            tac_text=SAMPLE_TAC,
            xml_content=SAMPLE_XML,
            version="2025-2",
            layers=[
                ValidationLayer.SCHEMATRON,
                ValidationLayer.GML_REFERENCES,
                ValidationLayer.WMO_CODELISTS,
            ],
            stop_on_error=False,
        )

        assert ValidationLayer.SCHEMATRON in result.layers_passed
        assert ValidationLayer.GML_REFERENCES in result.layers_passed
        assert ValidationLayer.WMO_CODELISTS in result.layers_passed

    def test_validate_complete_layer2_fails_no_stop_continues_to_layer3(self, monkeypatch):
        """Layer 2 fail with stop_on_error=False should continue into layer 3 (covers 201->219)."""
        orchestrator = ValidationOrchestrator()

        monkeypatch.setattr(
            orchestrator.validation_service,
            "validate_airport_icao",
            lambda _tac: make_result(ValidationLayer.AIRPORT_ICAO),
        )
        monkeypatch.setattr(
            orchestrator.validation_service,
            "validate_tac_syntax",
            lambda _tac: make_result(ValidationLayer.TAC_SYNTAX, passed=False, code="L2ERR"),
        )
        monkeypatch.setattr(
            orchestrator,
            "validate_wellformed",
            lambda _xml: make_result(ValidationLayer.XML_WELLFORMED),
        )

        result = orchestrator.validate_complete(
            tac_text=SAMPLE_TAC,
            xml_content=SAMPLE_XML,
            version="2025-2",
            layers=[
                ValidationLayer.AIRPORT_ICAO,
                ValidationLayer.TAC_SYNTAX,
                ValidationLayer.XML_WELLFORMED,
            ],
            stop_on_error=False,
        )

        assert ValidationLayer.TAC_SYNTAX in result.layers_failed
        assert ValidationLayer.XML_WELLFORMED in result.layers_passed
        assert result.stopped_at_layer is None

    def test_validate_complete_layer3_fails_no_stop_continues_to_layer4(self, monkeypatch):
        """Layer 3 fail with stop_on_error=False should continue into layer 4 (covers 235->253)."""
        orchestrator = ValidationOrchestrator()

        monkeypatch.setattr(
            orchestrator.validation_service,
            "validate_airport_icao",
            lambda _tac: make_result(ValidationLayer.AIRPORT_ICAO),
        )
        monkeypatch.setattr(
            orchestrator.validation_service,
            "validate_tac_syntax",
            lambda _tac: make_result(ValidationLayer.TAC_SYNTAX),
        )
        monkeypatch.setattr(
            orchestrator,
            "validate_wellformed",
            lambda _xml: make_result(ValidationLayer.XML_WELLFORMED, passed=False, code="L3ERR"),
        )
        monkeypatch.setattr(
            orchestrator,
            "validate_xml_schema",
            lambda _xml, _version: make_result(ValidationLayer.XML_SCHEMA),
        )

        result = orchestrator.validate_complete(
            tac_text=SAMPLE_TAC,
            xml_content=SAMPLE_XML,
            version="2025-2",
            layers=[
                ValidationLayer.AIRPORT_ICAO,
                ValidationLayer.TAC_SYNTAX,
                ValidationLayer.XML_WELLFORMED,
                ValidationLayer.XML_SCHEMA,
            ],
            stop_on_error=False,
        )

        assert ValidationLayer.XML_WELLFORMED in result.layers_failed
        assert ValidationLayer.XML_SCHEMA in result.layers_passed
        assert result.stopped_at_layer is None

    def test_parallel_gml_only_skips_schematron_check(self, monkeypatch):
        """GML-only parallel run skips SCHEMATRON branch."""
        orchestrator = ValidationOrchestrator()

        monkeypatch.setattr(
            orchestrator,
            "_run_gml_layer",
            staticmethod(lambda *_a, **_k: GMLValidationResult(is_valid=True, issues=[])),
        )

        result = orchestrator.validate_complete(
            tac_text=SAMPLE_TAC,
            xml_content=SAMPLE_XML,
            version="2025-2",
            layers=[ValidationLayer.GML_REFERENCES],
            stop_on_error=False,
        )

        assert ValidationLayer.GML_REFERENCES in result.layers_passed
        assert ValidationLayer.SCHEMATRON not in result.layers_run

    def test_parallel_future_result_with_issues_and_failure(self, monkeypatch):
        """Parallel future returning issues+failure covers failure branch."""
        orchestrator = ValidationOrchestrator()
        issue = make_issue(ValidationLayer.SCHEMATRON, "SCH_FAIL")

        monkeypatch.setattr(
            orchestrator,
            "_validate_schematron",
            lambda *_a, **_k: SchematronValidationResult(
                is_valid=False,
                issues=[issue],
                schema_version="2025-2",
                rules_evaluated=1,
            ),
        )

        result = orchestrator.validate_complete(
            tac_text=SAMPLE_TAC,
            xml_content=SAMPLE_XML,
            version="2025-2",
            layers=[ValidationLayer.SCHEMATRON],
            stop_on_error=False,
        )

        assert ValidationLayer.SCHEMATRON in result.layers_failed
        assert ValidationLayer.SCHEMATRON in result.issues_by_layer
        assert result.issues_by_layer[ValidationLayer.SCHEMATRON][0].code == "SCH_FAIL"
        assert issue in result.all_issues


def test_get_validation_orchestrator_singleton():
    """Module-level getter should return a singleton instance."""
    first = get_validation_orchestrator()
    second = get_validation_orchestrator()

    assert first is second


def test_validate_xml_helper_delegates_to_validate_complete(monkeypatch):
    orchestrator = ValidationOrchestrator()
    captured = {}

    def _validate_complete(**kwargs):
        captured.update(kwargs)
        return ComprehensiveValidationResult(
            is_valid=True,
            version=kwargs["version"],
            layers_run=[],
            layers_passed=[],
            layers_failed=[],
            all_issues=[],
        )

    monkeypatch.setattr(orchestrator, "validate_complete", _validate_complete)

    result = orchestrator.validate("<iwxxm:METAR/>", iwxxm_version="2025-2", layers=[ValidationLayer.XML_SCHEMA])

    assert result.is_valid is True
    assert captured["xml_content"] == "<iwxxm:METAR/>"
    assert captured["version"] == "2025-2"
    assert captured["layers"] == [ValidationLayer.XML_SCHEMA]
    assert result.passed is True


@dataclass
class _PkgIssue:
    """Minimal iwxxm_validate.Issue stand-in for native-path mapping."""

    severity: str
    message: str
    location: str | None = None
    code: str = "NATIVE_ISSUE"


@dataclass
class _PkgReport:
    """Minimal validate_iwxxm report stand-in."""

    ok: bool
    issues: list


def test_pkg_issue_to_backend_maps_error_and_warning():
    """Native Issue severity maps to ValidationSeverity (TC-EV055 / Gate C CI)."""
    from iwxxm_validate.models import Issue

    err = pkg_issue_to_backend(
        Issue(severity="error", code="E1", message="bad", layer="xsd", location="L1"),
        layer=ValidationLayer.XML_SCHEMA,
    )
    warn = pkg_issue_to_backend(
        Issue(severity="warning", code="W1", message="soft", layer="schematron"),
        layer=ValidationLayer.SCHEMATRON,
    )
    info = pkg_issue_to_backend(
        Issue(severity="info", code="I1", message="note", layer="gml"),
    )
    assert err.level == ValidationSeverity.ERROR
    assert err.code == "E1"
    assert warn.level == ValidationSeverity.WARNING
    assert warn.layer == ValidationLayer.SCHEMATRON
    assert info.level == ValidationSeverity.INFO
    assert info.layer == ValidationLayer.GML_REFERENCES


def test_validate_xml_schema_native_path(monkeypatch):
    """Adapter XSD path uses validate_iwxxm levels=('xsd',)."""
    from iwxxm_validate.models import Issue, ValidationReport

    called: dict = {}

    def _validate_iwxxm(xml, *, iwxxm_version, profile, levels, product=None):
        called.update(
            {
                "xml": xml,
                "version": iwxxm_version,
                "profile": profile,
                "levels": levels,
            }
        )
        return ValidationReport(
            ok=False,
            iwxxm_version=iwxxm_version,
            profile=profile,
            issues=[
                Issue(severity="error", code="XSD_E", message="xsd fail", layer="xsd"),
            ],
        )

    monkeypatch.setattr("src.services.iwxxm_validation_adapter.validate_iwxxm", _validate_iwxxm)

    result = ValidationOrchestrator().validate_xml_schema("<r/>", "2025-2")
    assert called["levels"] == ("xsd",)
    assert called["version"] == "2025-2"
    assert result.is_valid is False
    assert result.issues[0].code == "XSD_E"
    assert result.schema_version == "2025-2"


def test_validate_xml_schema_includes_wmo_xsd_issues(monkeypatch):
    """Adapter XSD path collects issues tagged layer=wmo_xsd."""
    from iwxxm_validate.models import Issue, ValidationReport

    def _validate_iwxxm(*_a, **_k):
        return ValidationReport(
            ok=False,
            iwxxm_version="2025-2",
            profile="annex3",
            issues=[
                Issue(severity="error", code="WMO_XSD", message="wmo xsd", layer="wmo_xsd"),
            ],
        )

    monkeypatch.setattr("src.services.iwxxm_validation_adapter.validate_iwxxm", _validate_iwxxm)

    from src.services.iwxxm_validation_adapter import validate_xml_schema

    result = validate_xml_schema("<r/>", "2025-2")
    assert result.is_valid is False
    assert result.issues[0].code == "WMO_XSD"
    assert result.issues[0].layer == ValidationLayer.XML_SCHEMA


def test_validate_wellformed_malformed_xml():
    """Adapter well-formed check surfaces parse errors."""
    from src.services.iwxxm_validation_adapter import validate_wellformed

    result = validate_wellformed("<not-closed")
    assert result.passed is False
    assert result.layer == ValidationLayer.XML_WELLFORMED
    assert result.issues


def test_adapter_gml_and_codelist_layers(monkeypatch):
    """Adapter GML and codelist helpers delegate to validate_iwxxm."""
    from iwxxm_validate.models import Issue, ValidationReport
    from src.services.iwxxm_validation_adapter import validate_gml_references, validate_wmo_codelists

    levels_seen: list[tuple[str, ...]] = []

    def _validate_iwxxm(_xml, *, iwxxm_version, profile, levels, product=None):
        levels_seen.append(tuple(levels))
        layer = levels[0]
        return ValidationReport(
            ok=True,
            iwxxm_version=iwxxm_version,
            profile=profile,
            issues=[Issue(severity="warning", code=f"{layer}_W", message="warn", layer=layer)],
        )

    monkeypatch.setattr("src.services.iwxxm_validation_adapter.validate_iwxxm", _validate_iwxxm)

    gml_ok, gml_issues = validate_gml_references("<r/>", "2025-2")
    code_ok, code_issues = validate_wmo_codelists("<r/>", "2025-2")

    assert levels_seen == [("gml",), ("codelists",)]
    assert gml_ok is True
    assert code_ok is True
    assert gml_issues[0].layer == ValidationLayer.GML_REFERENCES
    assert code_issues[0].layer == ValidationLayer.WMO_CODELISTS


def test_validate_xml_schema_native_exception_propagates(monkeypatch):
    """Package validation exceptions propagate from adapter (no legacy fallback)."""
    monkeypatch.setattr(
        "src.services.iwxxm_validation_adapter.validate_iwxxm",
        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("native xsd down")),
    )

    with pytest.raises(RuntimeError, match="native xsd down"):
        ValidationOrchestrator().validate_xml_schema("<r/>", "2023-1")


def test_validate_schematron_native_path(monkeypatch):
    """Adapter Schematron path uses validate_iwxxm levels=('schematron',)."""
    from iwxxm_validate.models import Issue, ValidationReport

    called: dict = {}

    def _validate_iwxxm(xml, *, iwxxm_version, profile, levels, product=None):
        called["levels"] = levels
        return ValidationReport(
            ok=True,
            iwxxm_version=iwxxm_version,
            profile=profile,
            issues=[
                Issue(severity="warning", code="SCH_W", message="sch warn", layer="schematron"),
            ],
        )

    monkeypatch.setattr("src.services.iwxxm_validation_adapter.validate_iwxxm", _validate_iwxxm)

    result = ValidationOrchestrator()._validate_schematron("<r/>", "2025-2")
    assert called["levels"] == ("schematron",)
    assert result.is_valid is True
    assert result.issues[0].code == "SCH_W"
    assert result.rules_evaluated == 1


def test_validate_schematron_native_exception_propagates(monkeypatch):
    """Package Schematron exceptions propagate from adapter."""
    monkeypatch.setattr(
        "src.services.iwxxm_validation_adapter.validate_iwxxm",
        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("native sch down")),
    )

    with pytest.raises(RuntimeError, match="native sch down"):
        ValidationOrchestrator()._validate_schematron("<r/>", "2025-2")
