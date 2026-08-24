"""TC-EV1061 — CA_ECCC SIGMET exchange output emit (#1061 / EV-076).

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC] [Corpus: tests §TC-EV1061]
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tac2iwxxm.ca_ops_corpus import extract_iwxxm_from_collect, load_ops_manifest, ops_fixture_root
from tac2iwxxm.exchange_output import (
    build_ca_eccc_output_spec,
    build_ca_eccc_output_spec_from_msc_filename,
    ca_wmo_header_designator,
    msc_filename_matches_pattern,
    parse_msc_exchange_filename,
    profile_output_spec_to_dict,
)

_REPO = Path(__file__).resolve().parents[3]
_CATALOG = _REPO / "docs" / "domain" / "profiles" / "catalog.yaml"
_FIXTURES = ops_fixture_root(_REPO)


def _sigmet_ops_cases() -> list[dict]:
    manifest = load_ops_manifest(_FIXTURES / "ops_manifest.json")
    return [case for case in manifest["cases"] if case["product"] == "SIGMET"]


def test_tc_ev1061_001_catalog_sigmet_exchange_slice() -> None:
    text = _CATALOG.read_text(encoding="utf-8")
    assert "ev076_slice: [SIGMET]" in text
    assert "ev074_validate_first: [VAA]" in text


def test_tc_ev1061_002_sigmet_wmo_header_designator() -> None:
    assert ca_wmo_header_designator("SIGMET") == "A_LSCN"
    assert ca_wmo_header_designator("SIGMET", sigmet_kind="weather") == "A_LSCN"
    assert ca_wmo_header_designator("SIGMET", sigmet_kind="va") == "A_LVCN"
    assert ca_wmo_header_designator("SIGMET", sigmet_kind="tc") == "A_LYCN"
    assert ca_wmo_header_designator("SIGMET", sigmet_kind="unknown") == "A_LSCN"


@pytest.mark.parametrize("case", _sigmet_ops_cases(), ids=lambda c: c["id"])
def test_tc_ev1061_003_ops_output_spec_from_msc_filename(case: dict) -> None:
    """Ops SIGMET fixtures expand MSC filename + WMO header output spec."""
    source_filename = case.get("source_filename")
    assert source_filename
    spec = build_ca_eccc_output_spec_from_msc_filename(
        product="SIGMET",
        source_filename=source_filename,
        sigmet_kind=case.get("sigmet_kind"),
    )
    assert spec is not None
    assert spec.wmo_header_designator == "A_LSCN"
    assert spec.suggested_filename == source_filename
    assert spec.wmo_ahl_header is not None
    assert spec.wmo_ahl_header.startswith("A_LSCN")
    assert msc_filename_matches_pattern(spec.suggested_filename)


@pytest.mark.parametrize("case", _sigmet_ops_cases(), ids=lambda c: c["id"])
def test_tc_ev1061_004_ops_sigmet_layer6_packaging(case: dict) -> None:
    """SIGMET ops IWXXM passes layer-6 packaging checks with MSC filename context."""
    from iwxxm_validate.ca_exchange_validate import validate_ca_exchange_packaging

    raw = (_FIXTURES / case["ops_xml"]).read_text(encoding="utf-8")
    inner = extract_iwxxm_from_collect(raw)
    assert inner is not None

    spec = build_ca_eccc_output_spec_from_msc_filename(
        product="SIGMET",
        source_filename=case["source_filename"],
        sigmet_kind=case.get("sigmet_kind"),
        include_translation_centre=False,
    )
    assert spec is not None
    issues = validate_ca_exchange_packaging(
        inner,
        product="SIGMET",
        ahl_header=spec.wmo_ahl_header,
        expected_filename=spec.suggested_filename,
        require_translation_centre=False,
    )
    assert issues == [], [(issue.code, issue.message) for issue in issues]


def test_tc_ev1061_005_parse_msc_exchange_filename_helpers() -> None:
    filename = "A_LSCN22CWAO241540_C_CWAO_20260824154038.xml"
    parsed = parse_msc_exchange_filename(filename)
    assert parsed is not None
    parts, issued = parsed
    assert parts.iwxxm_tt == "LS"
    assert parts.aa == "CN"
    assert parts.cccc == "CWAO"
    assert issued.year == 2026

    assert parse_msc_exchange_filename("not-an-msc-name.xml") is None
    bbb_parsed = parse_msc_exchange_filename(
        "A_LSCN22CWAO241540AAA_C_CWAO_20260824154038.xml",
    )
    assert bbb_parsed is not None
    bbb_parts, _ = bbb_parsed
    assert bbb_parts.bbb == "AAA"
    assert " AAA" in bbb_parts.ahl

    assert (
        build_ca_eccc_output_spec_from_msc_filename(
            product="SIGMET",
            source_filename="bad",
        )
        is None
    )


def test_tc_ev1061_006_output_spec_serialization_without_translation_centre() -> None:
    spec = build_ca_eccc_output_spec(product="SIGMET", include_translation_centre=False)
    payload = profile_output_spec_to_dict(spec)
    assert payload["wmo_header_designator"] == "A_LSCN"
    assert "translation_centre_designator" not in payload
