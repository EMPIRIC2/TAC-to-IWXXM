"""T3.2 / TC-F13-001: parity suite stubs vs lxml + golden IWXXM (xfail until T3.3).

Spec: docs/test-plan.md TC-F13-001; feature-list F13; E10-22.

Until T3.3 ships ``validate_iwxxm`` + Rust well-formed/XSD/Schematron, parity cases are
``xfail(strict=True)``. Baseline lxml ``validate()`` cases stay green so the corpus is wired.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
VENDOR_EXAMPLE = REPO_ROOT / "vendor" / "schemas" / "iwxxm" / "2023-1" / "IWXXM" / "examples" / "metar-A3-1.xml"
ANNEX3_GOLDEN = REPO_ROOT / "packages" / "tac2iwxxm" / "tests" / "fixtures" / "annex3_golden"
IWXXM_US_GOLDEN = REPO_ROOT / "packages" / "tac2iwxxm" / "tests" / "fixtures" / "iwxxm_us_golden"

_T33 = "T3.3: Rust well-formed+XSD+Schematron + validate_iwxxm SDK"


@dataclass(frozen=True)
class _ParityCase:
    case_id: str
    xml_path: Path
    iwxxm_version: str
    profile: str


def _parity_cases() -> list[_ParityCase]:
    cases = [
        _ParityCase("vendor_metar_a3_1", VENDOR_EXAMPLE, "2023-1", "annex3"),
        _ParityCase(
            "annex3_metar_basic",
            ANNEX3_GOLDEN / "metar_basic.golden.xml",
            "2023-1",
            "annex3",
        ),
        _ParityCase(
            "annex3_speci_basic",
            ANNEX3_GOLDEN / "speci_basic.golden.xml",
            "2023-1",
            "annex3",
        ),
        _ParityCase(
            "us_metar_ao2_slp",
            IWXXM_US_GOLDEN / "metar_us_ao2_slp.golden.xml",
            "2023-1",
            "iwxxm_us",
        ),
    ]
    return cases


def _case_ids(cases: list[_ParityCase]) -> list[str]:
    return [c.case_id for c in cases]


def test_parity_corpus_paths_exist() -> None:
    """Golden + vendor fixtures for TC-F13-001 must be present (T3.2 wiring)."""
    for case in _parity_cases():
        assert case.xml_path.is_file(), f"missing parity fixture: {case.xml_path}"


@pytest.mark.parametrize("case", _parity_cases(), ids=_case_ids(_parity_cases()))
def test_lxml_baseline_validate_on_golden(case: _ParityCase) -> None:
    """lxml path runs on golden corpus (parity reference until Rust cutover)."""
    from iwxxm_validate import validate

    xml = case.xml_path.read_text(encoding="utf-8")
    report = validate(xml, iwxxm_version=case.iwxxm_version, profile=case.profile)
    assert report.iwxxm_version == case.iwxxm_version
    assert report.profile == case.profile
    assert isinstance(report.ok, bool)
    assert not any(issue.code == "XML_SYNTAX_ERROR" for issue in report.issues)


@pytest.mark.xfail(strict=True, reason=_T33)
def test_validate_iwxxm_export_exists() -> None:
    """F13 SDK entrypoint ``validate_iwxxm`` (lands in T3.3)."""
    import iwxxm_validate

    assert callable(getattr(iwxxm_validate, "validate_iwxxm", None))


@pytest.mark.parametrize("case", _parity_cases(), ids=_case_ids(_parity_cases()))
@pytest.mark.xfail(strict=True, reason=_T33)
def test_rust_parity_matches_lxml_issue_codes(case: _ParityCase) -> None:
    """Native ``validate_iwxxm`` must match lxml ``ok`` + error codes on golden XML."""
    from iwxxm_validate import validate, validate_iwxxm

    xml = case.xml_path.read_text(encoding="utf-8")
    lxml_report = validate(xml, iwxxm_version=case.iwxxm_version, profile=case.profile)
    rust_report = validate_iwxxm(xml, iwxxm_version=case.iwxxm_version, profile=case.profile)

    assert rust_report.ok == lxml_report.ok
    lxml_errors = {i.code for i in lxml_report.issues if i.severity == "error"}
    rust_errors = {i.code for i in rust_report.issues if i.severity == "error"}
    assert rust_errors == lxml_errors


@pytest.mark.xfail(strict=True, reason=_T33)
def test_rust_parity_malformed_xml_fails() -> None:
    """Native path must fail malformed XML (TC-F13-001 / well-formed gate)."""
    from iwxxm_validate import validate_iwxxm

    report = validate_iwxxm(
        "<iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/2023-1'>",
        iwxxm_version="2023-1",
        profile="annex3",
    )
    assert report.ok is False
    assert len(report.issues) >= 1


@pytest.mark.xfail(strict=True, reason=_T33)
def test_rust_schematron_not_skipped_when_native() -> None:
    """Rust Schematron must evaluate (not SCHEMATRON_SKIPPED) when extension is built."""
    from iwxxm_validate import rust_available, validate_iwxxm

    assert rust_available() is True
    xml = VENDOR_EXAMPLE.read_text(encoding="utf-8")
    report = validate_iwxxm(
        xml,
        iwxxm_version="2023-1",
        profile="annex3",
        levels=("schematron",),
    )
    skipped = [i for i in report.issues if i.code == "SCHEMATRON_SKIPPED"]
    assert skipped == []
