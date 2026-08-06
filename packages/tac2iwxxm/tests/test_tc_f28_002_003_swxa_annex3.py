"""TC-F28-002 / TC-F28-003 — SWXA annex3 convert → XSD+SCH + wmoReference peer (F28 theme SX3).

Asserts WMO ``spacewx-A7-3`` is in the annex3 pack, root
``iwxxm:SpaceWeatherAdvisory``, convert → M-xsd/M-sch under default settings.
Golden equality is not required when ``wmoReference`` is set (S02.L1 / ADR-032).

Always write “F28 theme SX3” (not SPECI S1) — D-S036 / EV-029 M11.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"
MANIFEST_PATH = FIXTURES / "manifest.json"
IWXXM_VERSION = "2025-2"
PROFILE = "annex3"

SWXA_CASE_IDS = ("swxa_a7_3", "swxa_a7_4", "swxa_a7_5")
_SWXA_SEEDS = {
    "swxa_a7_3": ("SX3", "spacewx-A7-3"),
    "swxa_a7_4": ("SX4", "spacewx-A7-4"),
    "swxa_a7_5": ("SX5", "spacewx-A7-5"),
}


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _has_root(xml: str, local: str) -> bool:
    return f"<iwxxm:{local} " in xml


def test_tc_f28_002_annex3_swxa_theme_present() -> None:
    data = _load_manifest()
    ids = {c["id"] for c in data["cases"]}
    assert set(SWXA_CASE_IDS) <= ids
    for case in data["cases"]:
        if case["id"] in SWXA_CASE_IDS:
            theme, seed = _SWXA_SEEDS[case["id"]]
            assert case["product"] == "SWXA"
            assert case.get("theme") == theme
            assert case.get("seed") == seed
            assert case.get("wmoReference") is True
            assert (FIXTURES / case["tac"]).is_file()
            assert (FIXTURES / case["golden"]).is_file()
            golden = (FIXTURES / case["golden"]).read_text(encoding="utf-8")
            assert _has_root(golden, "SpaceWeatherAdvisory")


@pytest.mark.parametrize("case_id", SWXA_CASE_IDS)
def test_tc_f28_002_swxa_root_element(case_id: str) -> None:
    from tac2iwxxm import convert

    case = next(c for c in _load_manifest()["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    result = convert(
        tac,
        product="SWXA",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"M-parse failed for {case_id}: {result.issues!r}"
    assert result.product == "SWXA"
    assert _has_root(result.xml, "SpaceWeatherAdvisory")
    assert not _has_root(result.xml, "SIGMET")
    assert not _has_root(result.xml, "VolcanicAshAdvisory")
    assert not _has_root(result.xml, "TropicalCycloneAdvisory")


@pytest.mark.parametrize("case_id", SWXA_CASE_IDS)
def test_tc_f28_002_swxa_m_xsd_sch(case_id: str) -> None:
    from iwxxm_validate import validate

    from tac2iwxxm import convert

    case = next(c for c in _load_manifest()["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    result = convert(
        tac,
        product="SWXA",
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


@pytest.mark.parametrize("case_id", SWXA_CASE_IDS)
def test_tc_f28_003_swxa_wmo_reference_peer(case_id: str) -> None:
    """Vendor peer is staged; equality optional under wmoReference (S02.L1)."""
    from tac2iwxxm import convert

    case = next(c for c in _load_manifest()["cases"] if c["id"] == case_id)
    assert case.get("wmoReference") is True
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    golden = (FIXTURES / case["golden"]).read_text(encoding="utf-8")
    result = convert(
        tac,
        product="SWXA",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True
    assert _has_root(result.xml, "SpaceWeatherAdvisory")
    assert _has_root(golden, "SpaceWeatherAdvisory")
    assert "DONLON" in result.xml.upper()
    # Effect token differs by peer (A7-3 HF COM / A7-4 GNSS / A7-5 RADIATION).
    effect_markers = {
        "swxa_a7_3": "HF_COM",
        "swxa_a7_4": "GNSS",
        "swxa_a7_5": "RADIATION",
    }
    marker = effect_markers[case_id]
    assert marker in result.xml.upper() or marker in result.xml


def test_tc_f28_002_swxa_a7_3_content_signals() -> None:
    from tac2iwxxm import convert
    from tac2iwxxm.products.swxa import parse_swxa

    tac = (FIXTURES / "swxa_a7_3.tac").read_text(encoding="utf-8")
    ir = parse_swxa(tac, product="SWXA")
    assert ir["product"] == "SWXA"
    assert ir.get("iwxxm_root") == "SpaceWeatherAdvisory"
    assert "DONLON" in str(ir.get("swxc", "")).upper()
    result = convert(tac, product="SWXA", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True
    assert "DONLON" in result.xml.upper()
