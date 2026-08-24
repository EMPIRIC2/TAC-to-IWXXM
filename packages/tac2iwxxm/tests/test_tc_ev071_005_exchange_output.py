"""TC-EV071-005..009 — CA_ECCC exchange output METAR slice (EV-071 M2 / #1032 / #1040).

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC] [Corpus: tests §TC-EV071]
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

import pytest

from tac2iwxxm import convert, parse_ahl, split_bulletin
from tac2iwxxm.exchange_output import (
    build_ca_eccc_output_spec,
    ca_distribution_path,
    ca_msc_filename,
    ca_wmo_header_designator,
    default_ca_translation_centre,
    format_ca_wmo_ahl,
    issued_at_from_yygggg,
    msc_filename_matches_pattern,
    profile_output_spec_to_dict,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "profiles" / "CA_ECCC"
PROFILE = "ca_eccc"
IWXXM_VERSION = "3.0.0"
_DATAMART_BULLETIN = FIXTURES / "METAR" / "valid" / "metar_datamart.bulletin.txt"


def _attr(xml: str, name: str) -> str | None:
    match = re.search(rf'\b{re.escape(name)}="([^"]*)"', xml)
    return match.group(1) if match else None


def test_tc_ev071_005_msc_metar_filename_pattern() -> None:
    """MSC filename matches ``A_{TTAAiiCCCCYYGGggBBB}_C_{CCC}_{YYYYMMddhhmmss}.xml``."""
    parts = parse_ahl("SAUL31 CYUL 231800")
    issued = datetime(2023, 6, 23, 18, 0, 0, tzinfo=UTC)
    filename = ca_msc_filename(parts, issued_at=issued)
    assert filename == "A_LAUL31CYUL231800_C_CYUL_20230623180000.xml"
    assert msc_filename_matches_pattern(filename)


def test_tc_ev071_006_wmo_header_metar_designator() -> None:
    """METAR WMO header designator is ``A_LACN``; wrong product prefix fails layer-6 check."""
    from iwxxm_validate.ca_exchange_validate import validate_ca_exchange_packaging

    parts = parse_ahl("SAUL31 CYUL 231800")
    assert ca_wmo_header_designator("METAR") == "A_LACN"
    wmo_ahl = format_ca_wmo_ahl(parts, product="METAR")
    assert wmo_ahl == "A_LACN31 CYUL 231800"

    golden = (FIXTURES / "METAR" / "valid" / "metar_basic.golden.xml").read_text(encoding="utf-8")
    assert validate_ca_exchange_packaging(golden, product="METAR", ahl_header=wmo_ahl) == []
    bad = validate_ca_exchange_packaging(golden, product="METAR", ahl_header="A_LTCN31 CYUL 231800")
    assert bad and bad[0].code == "CA_EXCHANGE_AHL_PRODUCT"


def test_tc_ev071_007_translation_centre_metadata_golden() -> None:
    """CA_ECCC convert auto-emits translation centre attrs (#1040)."""
    tac = (FIXTURES / "METAR" / "valid" / "metar_basic.tac").read_text(encoding="utf-8").strip()
    designator, name = default_ca_translation_centre()
    result = convert(tac, product="METAR", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True, result.issues
    assert result.xml is not None
    assert _attr(result.xml, "translationCentreDesignator") == designator
    assert _attr(result.xml, "translationCentreName") == name


def test_tc_ev071_009_datamart_fixture_round_trip() -> None:
    """Operational datamart bulletin round-trips naming + header + layer-6 validate."""
    from iwxxm_validate import validate_iwxxm
    from iwxxm_validate.ca_exchange_validate import validate_ca_exchange_packaging

    if not _DATAMART_BULLETIN.is_file():
        pytest.fail(f"missing datamart bulletin fixture: {_DATAMART_BULLETIN}")

    bulletin = _DATAMART_BULLETIN.read_text(encoding="utf-8")
    split = split_bulletin(bulletin, product="METAR")
    assert split.reports, "bulletin must contain one METAR report"
    parts = parse_ahl(split.meta.ahl)
    issued = issued_at_from_yygggg(parts.yygggg, reference=datetime(2023, 6, 1, tzinfo=UTC))
    filename = ca_msc_filename(parts, issued_at=issued)
    wmo_ahl = format_ca_wmo_ahl(parts, product="METAR")

    result = convert(
        split.reports[0],
        product="METAR",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, result.issues
    assert result.xml is not None

    packaging_issues = validate_ca_exchange_packaging(
        result.xml,
        product="METAR",
        ahl_header=wmo_ahl,
        expected_filename=filename,
        require_translation_centre=True,
    )
    assert packaging_issues == [], [(i.code, i.message) for i in packaging_issues]

    spec = build_ca_eccc_output_spec(product="METAR", parts=parts, issued_at=issued)
    assert spec.suggested_filename == filename
    assert spec.wmo_ahl_header == wmo_ahl

    report = validate_iwxxm(
        result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        product="METAR",
        levels=("xsd", "schematron"),
    )
    exchange_stage = next((s for s in report.stages if s.stage == "exchange"), None)
    assert exchange_stage is not None
    assert exchange_stage.ok is True, [(i.code, i.message) for i in exchange_stage.issues]


def test_tc_ev071_005_exchange_output_helpers(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cover env override, BBB header, distribution path, and spec serialization."""
    monkeypatch.setenv("CA_ECCC_TRANSLATION_CENTRE_DESIGNATOR", "  ")
    monkeypatch.setenv("CA_ECCC_TRANSLATION_CENTRE_NAME", " Custom Centre ")
    designator, name = default_ca_translation_centre()
    assert designator == "CWAO"
    assert name == "Custom Centre"

    parts = parse_ahl("SAUL31 CYUL 231800 AAA")
    assert format_ca_wmo_ahl(parts, product="METAR") == "A_LACN31 CYUL 231800 AAA"
    assert ca_distribution_path("METAR", issuer_code="CYUL", hour=6).endswith("/metar/CYUL/06")

    with pytest.raises(ValueError, match="not defined"):
        ca_wmo_header_designator("SIGMET")
    with pytest.raises(ValueError, match="distribution path"):
        ca_distribution_path("SIGMET", issuer_code="CYUL", hour=1)

    bare_spec = build_ca_eccc_output_spec(product="METAR", include_translation_centre=False)
    assert bare_spec.suggested_filename is None
    assert bare_spec.translation_centre_designator is None

    issued = issued_at_from_yygggg("231800")
    full_spec = build_ca_eccc_output_spec(product="METAR", parts=parts, issued_at=issued)
    payload = profile_output_spec_to_dict(full_spec)
    assert payload["semantic_profile"] == "CA_ECCC"
    assert payload["suggested_filename"] == ca_msc_filename(parts, issued_at=issued)
    assert "translation_centre_designator" in payload
