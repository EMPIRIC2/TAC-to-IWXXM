"""TC-F6-003 / T5.4: iwxxm_us TAF (+ thin SIGMET/AIRMET) (F6.c–d).

Spec: docs/test-plan.md TC-F6-003; docs/feature-list.md F6.c–d / F6.b US pattern;
ADR-013 extension blocks. SIGMET/AIRMET US surface is intentionally thin (feature-list
limitations).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from metar_shared.xml_canonical import canonicalize_xml

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "iwxxm_us_golden"
MANIFEST_PATH = FIXTURES / "manifest.json"

IWXXM_VERSION = "2025-2"
PROFILE = "iwxxm_us"
CASE_IDS = ("taf_us_altimeter", "sigmet_us_basic", "airmet_us_basic")


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def golden_manifest() -> dict:
    return _load_manifest()


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_tc_f6_003_non_metar_iwxxm_us_convert(case_id: str, golden_manifest: dict) -> None:
    """US-profile convert for TAF/SIGMET/AIRMET fixtures (T5.4 / T5.5)."""
    from tac2iwxxm import convert

    case = next(c for c in golden_manifest["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    result = convert(
        tac,
        product=case["product"],
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"{case_id}: {result.issues!r}"
    assert result.xml
    assert "www.weather.gov/iwxxm-us" in result.xml
    if case["product"] == "TAF":
        assert "MeteorologicalAerodromeForecastExtension" in result.xml
        assert "altimeter" in result.xml


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_tc_f6_003_non_metar_iwxxm_us_m_golden(case_id: str, golden_manifest: dict) -> None:
    """M-golden equality for non-METAR iwxxm_us fixtures."""
    from tac2iwxxm import convert

    case = next(c for c in golden_manifest["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    expected = canonicalize_xml((FIXTURES / case["golden"]).read_text(encoding="utf-8"))
    result = convert(
        tac,
        product=case["product"],
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok and result.xml
    assert canonicalize_xml(result.xml) == expected
