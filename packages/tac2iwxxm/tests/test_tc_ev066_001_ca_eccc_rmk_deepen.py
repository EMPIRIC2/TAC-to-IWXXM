"""TC-EV066-001..003 - CA_ECCC MANOBS RMK + altimeter deepen (EV-066 / #916).

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC] [Corpus: tests §TC-EV066]
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from metar_shared.xml_canonical import canonicalize_xml

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "profiles" / "CA_ECCC"
MANIFEST_PATH = FIXTURES / "manifest.json"

IWXXM_VERSION = "3.0.0"
PROFILE = "ca_eccc"

EV066_CASE_IDS = (
    "metar_rmk_presrr",
    "metar_alt_not_obs",
    "metar_rmk_slp_t",
)


@pytest.fixture(scope="module")
def golden_manifest() -> dict:
    if not MANIFEST_PATH.is_file():
        pytest.fail(f"missing CA_ECCC golden manifest: {MANIFEST_PATH}")
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


@pytest.mark.parametrize("case_id", EV066_CASE_IDS)
def test_tc_ev066_001_convert_ca_eccc_rmk_deepen(case_id: str, golden_manifest: dict) -> None:
    """TC-EV066-001..003: EV-066 golden pack converts on IWXXM 3.0.0 + iwxxm-ca."""
    from tac2iwxxm import convert

    case = next(c for c in golden_manifest["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")

    result = convert(
        tac,
        product=case["product"],
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"convert failed for {case_id}: {result.issues!r}"
    assert result.xml
    assert "iwxxm-ca" in result.xml


@pytest.mark.parametrize("case_id", EV066_CASE_IDS)
def test_tc_ev066_001_m_golden_ca_eccc_rmk_deepen(case_id: str, golden_manifest: dict) -> None:
    """TC-EV066-001..003: canonicalize(convert) == golden fixture."""
    from tac2iwxxm import convert

    case = next(c for c in golden_manifest["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    expected_xml = (FIXTURES / case["golden"]).read_text(encoding="utf-8")

    result = convert(
        tac,
        product=case["product"],
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok
    assert result.xml
    assert canonicalize_xml(result.xml) == canonicalize_xml(expected_xml)


def test_tc_ev066_002_presrr_rising_indicator(golden_manifest: dict) -> None:
    """TC-EV066-001: PRESRR maps to RISING pressureChangeIndicator."""
    from tac2iwxxm import convert

    case = next(c for c in golden_manifest["cases"] if c["id"] == "metar_rmk_presrr")
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    result = convert(tac, product="METAR", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok
    assert result.xml
    assert "PressureChangingRapidly/RISING" in result.xml


def test_tc_ev066_002_altimeter_not_observable_nil_qnh(golden_manifest: dict) -> None:
    """TC-EV066-002: A//// emits nil-reason QNH without altimeter_inhg."""
    from tac2iwxxm import convert

    case = next(c for c in golden_manifest["cases"] if c["id"] == "metar_alt_not_obs")
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    result = convert(tac, product="METAR", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok
    assert result.xml
    assert 'nilReason="http://codes.wmo.int/common/nil/notObservable"' in result.xml
    assert "1019." not in result.xml  # no spurious QNH value from A////


def test_tc_ev066_003_slp_and_hourly_t_addendum(golden_manifest: dict) -> None:
    """TC-EV066-003: SLP in Addendum; additive T retained in humanReadableText."""
    from tac2iwxxm import convert

    case = next(c for c in golden_manifest["cases"] if c["id"] == "metar_rmk_slp_t")
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    result = convert(tac, product="METAR", profile=PROFILE, iwxxm_version=IWXXM_VERSION)
    assert result.ok
    assert result.xml
    assert "<iwxxm-ca:seaLevelPressure" in result.xml
    assert "<iwxxm-ca:humanReadableText>T01230101</iwxxm-ca:humanReadableText>" in result.xml
