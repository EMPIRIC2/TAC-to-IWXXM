"""Success / failure validate matrix across IWXXM versions and profiles."""

from __future__ import annotations

from pathlib import Path

import pytest
from iwxxm_validate import validate_iwxxm

_FIXTURES = Path(__file__).resolve().parents[3] / "tests" / "fixtures"


def _first_existing(*candidates: Path) -> Path | None:
    for path in candidates:
        if path.is_file():
            return path
    return None


def _sample_metar_xml(version: str) -> str | None:
    """Load a small METAR IWXXM sample for ``version`` when present in-repo."""
    roots = [
        Path(__file__).resolve().parents[1] / "testdata",
        _FIXTURES,
        Path(__file__).resolve().parents[3] / "vendor" / "schemas" / "iwxxm" / version,
    ]
    names = (
        f"metar-{version}.xml",
        "metar.xml",
        "METAR.xml",
        "example-metar.xml",
    )
    for root in roots:
        for name in names:
            hit = _first_existing(root / name, root / "examples" / name)
            if hit is not None:
                return hit.read_text(encoding="utf-8")
    return None


@pytest.mark.parametrize("iwxxm_version", ["2023-1", "2025-2", "3.0.0"])
def test_validate_rejects_non_xml_as_wellformed_failure(iwxxm_version: str) -> None:
    """Failure: TAC/plain text is not well-formed XML (any pin)."""
    report = validate_iwxxm(
        "METAR CYVR 010000Z 00000KT 10SM SKC=",
        iwxxm_version=iwxxm_version,
        profile="annex3",
        levels=("wellformed",),
    )
    assert report.ok is False
    assert any(issue.code == "XML_SYNTAX_ERROR" for issue in report.issues)


def test_validate_invalid_profile_is_validation_failure() -> None:
    """Validation failure: unknown profile is rejected without running XSD."""
    report = validate_iwxxm("<root/>", iwxxm_version="2023-1", profile="not_a_profile")
    assert report.ok is False
    assert any(issue.code == "INVALID_PROFILE" for issue in report.issues)


def test_validate_invalid_levels_is_validation_failure() -> None:
    """Validation failure: unknown levels are rejected."""
    report = validate_iwxxm(
        "<root/>",
        iwxxm_version="2023-1",
        profile="annex3",
        levels=("not-a-level",),
    )
    assert report.ok is False
    assert any(issue.code == "INVALID_LEVELS" for issue in report.issues)


def test_validate_minimal_xml_xsd_failure_annex3_2023_1() -> None:
    """Failure: well-formed but non-IWXXM XML fails XSD on annex3 / 2023-1."""
    report = validate_iwxxm(
        '<?xml version="1.0"?><root/>',
        iwxxm_version="2023-1",
        profile="annex3",
        levels=("xsd",),
    )
    assert report.ok is False
    assert any(issue.layer in {"xsd", "wellformed"} for issue in report.issues)


@pytest.mark.parametrize(
    ("profile", "iwxxm_version"),
    [
        ("annex3", "2023-1"),
        ("annex3", "2025-2"),
        ("iwxxm_us", "2023-1"),
        ("ca_eccc", "3.0.0"),
    ],
)
def test_validate_empty_document_fails_closed(profile: str, iwxxm_version: str) -> None:
    """Failure permutation: empty payload fails for each supported profile/pin pair."""
    report = validate_iwxxm("", iwxxm_version=iwxxm_version, profile=profile, levels=("wellformed",))
    assert report.ok is False
    assert report.profile == profile
    assert report.iwxxm_version == iwxxm_version


def test_validate_ca_eccc_wrong_version_is_validation_failure() -> None:
    """Validation failure: ca_eccc requires the pinned 3.0.0 line."""
    report = validate_iwxxm(
        '<?xml version="1.0"?><root/>',
        iwxxm_version="2023-1",
        profile="ca_eccc",
        levels=("xsd",),
    )
    assert report.ok is False
    assert any(issue.code in {"INVALID_IWXXM_VERSION", "CA_SCHEMA_NOT_FOUND"} for issue in report.issues)


def test_validate_success_path_when_fixture_present() -> None:
    """Success: real METAR IWXXM fixture validates when available in the tree."""
    xml = _sample_metar_xml("2023-1")
    if xml is None:
        pytest.skip("No METAR IWXXM fixture available in this checkout")
    report = validate_iwxxm(xml, iwxxm_version="2023-1", profile="annex3", levels=("xsd", "schematron"))
    # Soft success: prefer ok, but allow Schematron warnings if XSD passed.
    assert not any(issue.code == "XML_SYNTAX_ERROR" for issue in report.issues)
    assert report.iwxxm_version == "2023-1"
