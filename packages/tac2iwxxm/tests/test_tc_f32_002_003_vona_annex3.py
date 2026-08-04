"""TC-F32-002 / TC-F32-003 — VONA annex3 convert fixtures (S040 / EV-032 T2.4 / F32 theme V3).

Asserts WMO ``vona-A7-1`` is in the annex3 pack, root
``iwxxm:VolcanoObservatoryNoticeForAviation``, MetFeature volcano/ash +
``iwxxm/AviationColourCode`` vocabulary (TC-F32-003). Soft content signals under
``wmoReference``; ADR-032 canonicalize equality waits for T2.6 / TC-F32-004.

Always write “F32 theme V3” (not F23 VA-SIGMET / F26 VAA V3) — #741.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "annex3_golden"
MANIFEST_PATH = FIXTURES / "manifest.json"
VENDOR_STEM = Path(__file__).resolve().parents[3] / ("vendor/schemas/iwxxm/2025-2/IWXXM/examples/vona-A7-1")
AHL_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "vona" / "vona_ahl_wm.txt"
IWXXM_VERSION = "2025-2"
PROFILE = "annex3"
VONA_CASE_IDS = ("vona_a7_1",)
IWXXM_COLOUR = "http://codes.wmo.int/iwxxm/AviationColourCode/"
MET_FEATURE = "http://codes.wmo.int/iwxxm/MeteorologicalFeature/"


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _has_root(xml: str, local: str) -> bool:
    return f"<iwxxm:{local} " in xml or f"<iwxxm:{local}\n" in xml or f"<iwxxm:{local}>" in xml


def test_tc_f32_002_annex3_vona_theme_present() -> None:
    data = _load_manifest()
    ids = {c["id"] for c in data["cases"]}
    assert set(VONA_CASE_IDS) <= ids
    for case in data["cases"]:
        if case["id"] in VONA_CASE_IDS:
            assert case["product"] == "VONA"
            assert case.get("theme") == "V3"
            assert case.get("seed") == "vona-A7-1"
            assert case.get("wmoReference") is True
            assert case.get("soft_compare") is not True
            assert (FIXTURES / case["tac"]).is_file()
            assert (FIXTURES / case["golden"]).is_file()
            golden = (FIXTURES / case["golden"]).read_text(encoding="utf-8")
            assert _has_root(golden, "VolcanoObservatoryNoticeForAviation")
            assert f"{IWXXM_COLOUR}YELLOW" in golden
            assert f"{IWXXM_COLOUR}ORANGE" in golden
            assert f"{MET_FEATURE}VOLCANO" in golden
            assert f"{MET_FEATURE}VOLCANIC_ASH" in golden
            assert "UHPP" in golden  # G-VONA-2 designator not in TAC
            assert "49-2/AviationColourCode" not in golden


def test_tc_f32_002_package_tac_matches_vendor_peer() -> None:
    case = next(c for c in _load_manifest()["cases"] if c["id"] == "vona_a7_1")
    package_tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8").strip()
    vendor_tac = VENDOR_STEM.with_suffix(".tac").read_text(encoding="utf-8").strip()
    assert package_tac == vendor_tac
    assert AHL_FIXTURE.is_file()
    assert AHL_FIXTURE.read_text(encoding="utf-8").lstrip().startswith("WM")


@pytest.mark.parametrize("case_id", VONA_CASE_IDS)
def test_tc_f32_002_vona_root_element(case_id: str) -> None:
    from tac2iwxxm import convert

    case = next(c for c in _load_manifest()["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    result = convert(
        tac,
        product="VONA",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"M-parse failed for {case_id}: {result.issues!r}"
    assert result.product == "VONA"
    assert _has_root(result.xml, "VolcanoObservatoryNoticeForAviation")
    assert not _has_root(result.xml, "VolcanicAshAdvisory")
    assert not _has_root(result.xml, "VolcanicAshSIGMET")
    assert not _has_root(result.xml, "SIGMET")
    assert "iwxxm:SpaceWeatherAdvisory" not in result.xml


@pytest.mark.parametrize("case_id", VONA_CASE_IDS)
def test_tc_f32_003_vona_metfeature_and_colour_codes(case_id: str) -> None:
    """Soft shape asserts — MetFeature volcano/ash + iwxxm AviationColourCode (TC-F32-003)."""
    from tac2iwxxm import convert

    case = next(c for c in _load_manifest()["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    result = convert(
        tac,
        product="VONA",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"M-parse failed for {case_id}: {result.issues!r}"
    xml = result.xml
    assert f"{MET_FEATURE}VOLCANO" in xml
    assert f"{MET_FEATURE}VOLCANIC_ASH" in xml
    assert f"{IWXXM_COLOUR}YELLOW" in xml
    assert f"{IWXXM_COLOUR}ORANGE" in xml
    assert "49-2/AviationColourCode" not in xml
    assert "KARYMSKY" in xml.upper()
    assert "KVERT" in xml.upper()
    assert "DECREASED_ACTIVITY" in xml
    assert "volcanicObservations" in xml
    assert "boundingPeriod" in xml
    assert "boundingVolume" in xml
    assert "ElevatedEnvelope" in xml
    assert "iwxxm/nil/inapplicable" in xml
    assert "UHPP" in xml  # G-VONA-2 fixture/registry constant


@pytest.mark.parametrize("case_id", VONA_CASE_IDS)
def test_tc_f32_002_vona_wmo_reference_peer_soft(case_id: str) -> None:
    """Vendor peer staged; canonicalize equality deferred (wmoReference / soft→strict)."""
    from tac2iwxxm import convert

    case = next(c for c in _load_manifest()["cases"] if c["id"] == case_id)
    assert case.get("wmoReference") is True
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    golden = (FIXTURES / case["golden"]).read_text(encoding="utf-8")
    result = convert(
        tac,
        product="VONA",
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True
    assert _has_root(result.xml, "VolcanoObservatoryNoticeForAviation")
    assert _has_root(golden, "VolcanoObservatoryNoticeForAviation")
    assert "KARYMSKY" in result.xml.upper()
    assert "YELLOW" in result.xml
    assert "ORANGE" in result.xml


def test_tc_f32_002_vona_a7_1_content_signals() -> None:
    from tac2iwxxm import convert
    from tac2iwxxm.products.vona import parse_vona

    tac = (FIXTURES / "vona_a7_1.tac").read_text(encoding="utf-8")
    ir = parse_vona(tac, product="VONA")
    assert ir["product"] == "VONA"
    assert ir.get("iwxxm_root") == "VolcanoObservatoryNoticeForAviation"
    assert "KARYMSKY" in str(ir.get("volcano_name", "")).upper()
    assert str(ir.get("svo", "")).upper() == "KVERT"
    assert ir.get("current_colour") == "YELLOW"
    assert ir.get("previous_colour") == "ORANGE"
    assert ir.get("activity_status") == "DECREASED_ACTIVITY"
    assert ir.get("onset_time") is None
    assert ir.get("duration") is None
    assert ir.get("originating_centre_designator") == "UHPP"
    result = convert(tac, product="VONA", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok is True
    assert _has_root(result.xml, "VolcanoObservatoryNoticeForAviation")
    assert "KVERT" in result.xml
