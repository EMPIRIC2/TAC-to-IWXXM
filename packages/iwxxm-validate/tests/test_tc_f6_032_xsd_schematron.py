"""TC-F6-032 / UJ-DEV-004: iwxxm-validate XSD + Schematron against vendor pins.

Spec: docs/test-plan.md TC-F6-032; docs/spec.md §packages/iwxxm-validate;
ADR-015; ADR-016 (msgspec issue models).

Decision D-S008-T21-sch: mirror current F2 — lxml XSD best-effort; Schematron via
lxml when queryBinding allows, else SCHEMATRON_SKIPPED (non-blocking) for xslt2;
optional Docker/Saxon behind env (soft/separate gate, not required for unit suite).
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
VENDOR_IWXXM = REPO_ROOT / "vendor" / "schemas" / "iwxxm"
VENDOR_IWXXM_US = REPO_ROOT / "vendor" / "schemas" / "iwxxm-us"
EXAMPLE_METAR_2023_1 = VENDOR_IWXXM / "2023-1" / "IWXXM" / "examples" / "metar-A3-1.xml"
XSD_2023_1 = VENDOR_IWXXM / "2023-1" / "IWXXM" / "iwxxm.xsd"
SCH_2023_1 = VENDOR_IWXXM / "2023-1" / "IWXXM" / "rule" / "iwxxm.sch"
PACKAGE_SRC = Path(__file__).resolve().parents[1] / "src" / "iwxxm_validate"


@pytest.fixture(scope="module")
def vendor_metar_xml() -> str:
    assert EXAMPLE_METAR_2023_1.is_file(), f"missing vendor fixture: {EXAMPLE_METAR_2023_1}"
    return EXAMPLE_METAR_2023_1.read_text(encoding="utf-8")


def test_vendor_pins_exist_for_xsd_and_schematron() -> None:
    """Vendor IWXXM pin must expose XSD + Schematron for package validation."""
    assert XSD_2023_1.is_file(), f"missing XSD pin: {XSD_2023_1}"
    assert SCH_2023_1.is_file(), f"missing Schematron pin: {SCH_2023_1}"
    assert VENDOR_IWXXM_US.is_dir(), f"missing iwxxm-us pin tree: {VENDOR_IWXXM_US}"


def test_validate_exports_public_entrypoints() -> None:
    """Package public API: validate() + ValidationReport / Issue models."""
    import iwxxm_validate

    assert callable(getattr(iwxxm_validate, "validate", None))
    assert getattr(iwxxm_validate, "ValidationReport", None) is not None
    assert getattr(iwxxm_validate, "Issue", None) is not None


def test_validate_vendor_metar_returns_structured_report(vendor_metar_xml: str) -> None:
    """Official WMO example runs without crash; report is structured (D-S008-T21-sch).

    XSD may warn/skip on catalog gaps; Schematron may skip xslt2 with
    SCHEMATRON_SKIPPED. Hard fail only on malformed input or blocking errors.
    """
    from iwxxm_validate import validate

    report = validate(
        vendor_metar_xml,
        iwxxm_version="2023-1",
        profile="annex3",
    )

    assert report.iwxxm_version == "2023-1"
    assert report.profile == "annex3"
    assert isinstance(report.ok, bool)
    assert isinstance(report.issues, list)
    # Vendor METAR is well-formed — must not fail as XML_SYNTAX_ERROR
    assert not any(issue.code == "XML_SYNTAX_ERROR" for issue in report.issues)


def test_validate_xslt2_schematron_skipped_non_blocking(vendor_metar_xml: str) -> None:
    """WMO Schematron uses xslt2; lxml path must skip non-blocking (F2 parity)."""
    from iwxxm_validate import validate

    report = validate(
        vendor_metar_xml,
        iwxxm_version="2023-1",
        profile="annex3",
        levels=("schematron",),
    )

    assert report.ok is True
    skipped = [i for i in report.issues if i.code == "SCHEMATRON_SKIPPED"]
    assert len(skipped) >= 1
    assert all(i.severity in {"warning", "info"} for i in skipped)


def test_validate_malformed_xml_fails_with_issues() -> None:
    """Malformed XML must not silently succeed (TC-F6-032 / F2 gate)."""
    from iwxxm_validate import validate

    report = validate(
        "<iwxxm:METAR xmlns:iwxxm='http://icao.int/iwxxm/2023-1'>",
        iwxxm_version="2023-1",
        profile="annex3",
    )

    assert report.ok is False
    assert len(report.issues) >= 1
    assert all(hasattr(issue, "code") and hasattr(issue, "message") for issue in report.issues)
    assert all(hasattr(issue, "severity") for issue in report.issues)


def test_validate_schema_invalid_xml_reports_xsd_or_parse_path() -> None:
    """Well-formed but schema-invalid IWXXM yields structured XSD-layer issues when XSD runs.

    If schema compilation is unavailable (catalog gaps), expect SCHEMA_* codes —
    never silent success with empty issues.
    """
    from iwxxm_validate import validate

    bad = """<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2023-1"
             xmlns:gml="http://www.opengis.net/gml/3.2"
             gml:id="uuid.bad-xsd-fixture"
             reportStatus="NORMAL"
             permissibleUsage="OPERATIONAL">
  <iwxxm:notARealElement>oops</iwxxm:notARealElement>
</iwxxm:METAR>
"""
    report = validate(bad, iwxxm_version="2023-1", profile="annex3", levels=("xsd",))

    assert len(report.issues) >= 1
    codes = {issue.code for issue in report.issues}
    layers = {issue.layer for issue in report.issues}
    assert layers & {"xsd", "xml_schema", "schema"} or any(
        c.startswith("SCHEMA_") or c.startswith("XSD_") or "SCHEMA" in c for c in codes
    )


def test_validate_xsd_only_level_does_not_emit_schematron(vendor_metar_xml: str) -> None:
    """levels=('xsd',) must not emit Schematron issues."""
    from iwxxm_validate import validate

    report = validate(
        vendor_metar_xml,
        iwxxm_version="2023-1",
        profile="annex3",
        levels=("xsd",),
    )

    assert not any(issue.layer == "schematron" for issue in report.issues)
    assert not any(issue.code == "SCHEMATRON_SKIPPED" for issue in report.issues)


def test_validate_iwxxm_us_profile_resolves_without_fastapi() -> None:
    """profile=iwxxm_us is accepted (fail-closed on bad XML is OK)."""
    from iwxxm_validate import validate

    stub = """<?xml version="1.0" encoding="UTF-8"?>
<root xmlns="http://icao.int/iwxxm/2023-1"/>
"""
    report = validate(stub, iwxxm_version="2023-1", profile="iwxxm_us")
    assert hasattr(report, "ok")
    assert report.profile == "iwxxm_us"


def test_validate_ca_eccc_profile_resolves_without_fastapi() -> None:
    """TC-EV064-003: profile=ca_eccc accepted when vendor pin present."""
    from iwxxm_validate import validate
    from iwxxm_validate.paths import ca_xsd_path

    assert ca_xsd_path() is not None, "iwxxm-ca vendor pin required for TC-EV064-003"

    stub = """<?xml version="1.0" encoding="UTF-8"?>
<root xmlns="http://icao.int/iwxxm/3.0"/>
"""
    report = validate(stub, iwxxm_version="3.0.0", profile="ca_eccc")
    assert hasattr(report, "ok")
    assert report.profile == "ca_eccc"
    assert report.issues[0].code != "CA_SCHEMA_NOT_FOUND"


def test_validate_ca_eccc_rejects_wrong_iwxxm_version() -> None:
    """TC-EV064-003: ca_eccc requires IWXXM 3.0.0 operational line."""
    from iwxxm_validate import validate

    report = validate("<root/>", iwxxm_version="2025-2", profile="ca_eccc")
    assert report.ok is False
    assert report.issues[0].code == "INVALID_IWXXM_VERSION"


def test_package_has_no_fastapi_or_supabase_imports() -> None:
    """SoC: iwxxm-validate must not import FastAPI or Supabase (spec.md)."""
    forbidden = {"fastapi", "supabase"}
    for path in PACKAGE_SRC.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".", 1)[0]
                    assert root not in forbidden, f"{path} imports {alias.name}"
            elif isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".", 1)[0]
                assert root not in forbidden, f"{path} imports from {node.module}"


def test_issue_models_are_msgspec_structs() -> None:
    """ADR-016: package issue / report models use msgspec.Struct."""
    import msgspec

    from iwxxm_validate import Issue, ValidationReport

    assert issubclass(Issue, msgspec.Struct)
    assert issubclass(ValidationReport, msgspec.Struct)
