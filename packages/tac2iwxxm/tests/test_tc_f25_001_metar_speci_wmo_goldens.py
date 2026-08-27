"""TC-F25-001 - WMO METAR/SPECI annex3 goldens (S026 / EV-020 T3.1 / F25 themes W1-W2).

Asserts vendor ``metar-A3-1`` / ``speci-A3-2`` are in the annex3 pack and
``canonicalize_xml(convert(...))`` equals vendor golden under default convert
settings (ADR-032 / E20-D3).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from metar_shared.xml_canonical import canonicalize_xml

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"
MANIFEST_PATH = FIXTURES / "manifest.json"
IWXXM_VERSION = "2025-2"
PROFILE = "annex3"

WMO_CASES = (
    ("metar_a3_1", "METAR", "W1", "metar-A3-1", "iwxxm:METAR"),
    ("speci_a3_2", "SPECI", "W2", "speci-A3-2", "iwxxm:SPECI"),
)


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_tc_f25_001_annex3_wmo_metar_speci_themes_present() -> None:
    data = _load_manifest()
    ids = {c["id"] for c in data["cases"]}
    expected_ids = {case_id for case_id, *_ in WMO_CASES}
    assert expected_ids <= ids
    by_id = {c["id"]: c for c in data["cases"]}
    for case_id, product, theme, seed, root in WMO_CASES:
        case = by_id[case_id]
        assert case["product"] == product
        assert case.get("theme") == theme
        assert case.get("seed") == seed
        assert (FIXTURES / case["tac"]).is_file()
        assert (FIXTURES / case["golden"]).is_file()
        golden = (FIXTURES / case["golden"]).read_text(encoding="utf-8")
        assert root in golden


@pytest.mark.parametrize(
    ("case_id", "product", "_theme", "_seed", "root"),
    WMO_CASES,
    ids=[c[0] for c in WMO_CASES],
)
def test_tc_f25_001_wmo_root_element(
    case_id: str,
    product: str,
    _theme: str,
    _seed: str,
    root: str,
) -> None:
    from tac2iwxxm import convert

    case = next(c for c in _load_manifest()["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    result = convert(
        tac,
        product=product,
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"M-parse failed for {case_id}: {result.issues!r}"
    assert root in result.xml


@pytest.mark.parametrize(
    ("case_id", "product", "_theme", "_seed", "_root"),
    WMO_CASES,
    ids=[c[0] for c in WMO_CASES],
)
def test_tc_f25_001_wmo_m_golden(
    case_id: str,
    product: str,
    _theme: str,
    _seed: str,
    _root: str,
) -> None:
    from tac2iwxxm import convert

    case = next(c for c in _load_manifest()["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    golden = (FIXTURES / case["golden"]).read_text(encoding="utf-8")
    result = convert(
        tac,
        product=product,
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"M-parse failed for {case_id}: {result.issues!r}"
    assert canonicalize_xml(result.xml) == canonicalize_xml(golden)


@pytest.mark.parametrize(
    ("case_id", "product", "_theme", "_seed", "_root"),
    WMO_CASES,
    ids=[c[0] for c in WMO_CASES],
)
def test_tc_f25_002_wmo_m_xsd_sch(
    case_id: str,
    product: str,
    _theme: str,
    _seed: str,
    _root: str,
) -> None:
    """TC-F25-002 - XSD+Schematron on F25 METAR/SPECI WMO goldens (T3.3)."""
    from iwxxm_validate import validate

    from tac2iwxxm import convert

    case = next(c for c in _load_manifest()["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    result = convert(
        tac,
        product=product,
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"M-parse failed for {case_id}: {result.issues!r}"
    report = validate(
        result.xml,
        iwxxm_version=IWXXM_VERSION,
        profile=PROFILE,
        levels=("xsd", "schematron"),
    )
    blocking = [i for i in report.issues if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}]
    assert not blocking, f"M-xsd/M-sch blocking for {case_id}: {[(i.code, i.message) for i in blocking]}"
