"""TC-F4-001: validate each profile on its own IWXXM package pin."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest
from iwxxm_validate import validate, validate_iwxxm
from iwxxm_validate.models import ValidationReport
from iwxxm_validate.native import rust_available

REPO_ROOT = Path(__file__).resolve().parents[3]
METAR_2025_2 = REPO_ROOT / "vendor/schemas/iwxxm/2025-2/IWXXM/examples/metar-A3-1.xml"
METAR_3_0 = REPO_ROOT / "vendor/schemas/iwxxm/3.0.0/IWXXM/examples/metar-A3-1.xml"
_PLAIN_REJECTION = "This file uses an IWXXM package this profile does not accept."
_INTERNAL_TOKENS = ("[Corpus:", "ADR-", "EV-", "TC-", "docs/", "#1273")
_NATIVE_REQUIRED = (
    "iwxxm_validate._rust is required for CA_ECCC IWXXM 3.0.0 XSD "
    "(lxml hits SCHEMA_PARSE on gml:AngleType). "
    "Run: make build-iwxxm-validate-native "
    "or bash scripts/ci/ensure_iwxxm_validate_native.sh"
)

ValidateFn = Callable[..., ValidationReport]


def _require_native_for_ca_eccc() -> None:
    """Fail closed when the native engine is missing (EV-068 CA_ECCC gate)."""
    if not rust_available():
        pytest.fail(_NATIVE_REQUIRED)


def _assert_plain_rejection(report: ValidationReport) -> None:
    assert report.ok is False
    rejection = next(issue for issue in report.issues if issue.code == "DECLARED_PACKAGE_NOT_ALLOWED")
    assert rejection.message == _PLAIN_REJECTION
    for token in _INTERNAL_TOKENS:
        assert token not in rejection.message


@pytest.mark.unit
@pytest.mark.parametrize("validate_fn", [validate, validate_iwxxm])
def test_tc_f4_001_canada_metar_validates_on_3_0_0(validate_fn: ValidateFn) -> None:
    """A Canada 3.0.0 METAR validates when that profile pin is selected."""
    _require_native_for_ca_eccc()
    report = validate_fn(
        METAR_3_0.read_text(encoding="utf-8"),
        iwxxm_version="3.0.0",
        profile="ca_eccc",
        product="METAR",
    )
    assert report.ok is True
    assert report.iwxxm_version == "3.0.0"
    assert report.profile == "ca_eccc"


@pytest.mark.unit
@pytest.mark.parametrize("validate_fn", [validate, validate_iwxxm])
def test_tc_f4_001_annex3_metar_validates_on_2025_2(validate_fn: ValidateFn) -> None:
    """A 2025-2 METAR validates on Annex 3 and that run does not select 3.0.0."""
    report = validate_fn(
        METAR_2025_2.read_text(encoding="utf-8"),
        iwxxm_version="2025-2",
        profile="annex3",
        product="METAR",
    )
    assert report.ok is True
    assert report.iwxxm_version == "2025-2"
    assert report.profile == "annex3"


@pytest.mark.unit
@pytest.mark.parametrize("validate_fn", [validate, validate_iwxxm])
def test_tc_f4_001_rejects_a_different_allowed_line(validate_fn: ValidateFn) -> None:
    """A 2025-2 file is not validated as the 2023-1 line."""
    report = validate_fn(
        METAR_2025_2.read_text(encoding="utf-8"),
        iwxxm_version="2023-1",
        profile="annex3",
        product="METAR",
    )
    _assert_plain_rejection(report)
    assert report.iwxxm_version == "2023-1"


@pytest.mark.unit
@pytest.mark.parametrize("validate_fn", [validate, validate_iwxxm])
@pytest.mark.parametrize("profile", ["annex3", "iwxxm_us"])
def test_tc_f4_001_global_profile_rejects_declared_iwxxm_3(
    validate_fn: ValidateFn,
    profile: str,
) -> None:
    """Annex 3 and IWXXM-US reject a file that declares the Canada 3.0 package."""
    report = validate_fn(
        METAR_3_0.read_text(encoding="utf-8"),
        iwxxm_version="2025-2",
        profile=profile,
        product="METAR",
    )
    _assert_plain_rejection(report)
    assert report.iwxxm_version == "2025-2"


@pytest.mark.unit
@pytest.mark.parametrize("validate_fn", [validate, validate_iwxxm])
def test_tc_f4_001_canada_rejects_declared_2025_2(validate_fn: ValidateFn) -> None:
    """Canada rejects a file that declares the 2025-2 package."""
    report = validate_fn(
        METAR_2025_2.read_text(encoding="utf-8"),
        iwxxm_version="3.0.0",
        profile="ca_eccc",
        product="METAR",
    )
    _assert_plain_rejection(report)


@pytest.mark.unit
def test_tc_f4_001_missing_namespace_is_not_a_package_rejection() -> None:
    """A document with no IWXXM namespace keeps the requested line."""
    report = validate("<root/>", iwxxm_version="2025-2", profile="annex3")
    assert all(issue.code != "DECLARED_PACKAGE_NOT_ALLOWED" for issue in report.issues)
    assert report.iwxxm_version == "2025-2"


@pytest.mark.unit
def test_tc_f4_001_annex3_rejects_a_matching_canada_pin() -> None:
    """Asking Annex 3 for 3.0.0 does not accept a file that declares that package."""
    report = validate(
        METAR_3_0.read_text(encoding="utf-8"),
        iwxxm_version="3.0.0",
        profile="annex3",
        product="METAR",
    )
    _assert_plain_rejection(report)
    assert report.iwxxm_version == "3.0.0"


@pytest.mark.unit
def test_tc_f4_001_annex3_rejects_a_retired_namespace() -> None:
    """A retired IWXXM namespace is not accepted on the global profile."""
    xml = '<?xml version="1.0"?><iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2021-2"/>'
    report = validate(xml, iwxxm_version="2025-2", profile="annex3", product="METAR")
    _assert_plain_rejection(report)
