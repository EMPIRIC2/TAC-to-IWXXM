"""TC-EV067-001 - CA_ECCC metar-speci-ca extensions (EV-067 / #1039).

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC] [Corpus: tests]
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from tac2iwxxm.convert import convert

from metar_shared.xml_canonical import canonicalize_xml

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "profiles" / "CA_ECCC"
MANIFEST_PATH = FIXTURES / "manifest.json"
PROFILE = "ca_eccc"

EV067_CASES = frozenset({"metar_lwis", "metar_sawr", "metar_rmk_icing"})


@pytest.fixture(scope="module")
def golden_manifest() -> dict:
    if not MANIFEST_PATH.is_file():
        pytest.fail(f"missing CA_ECCC golden manifest: {MANIFEST_PATH}")
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


@pytest.mark.parametrize("case_id", sorted(EV067_CASES))
def test_tc_ev067_001_convert_metar_speci_ca(case_id: str, golden_manifest: dict) -> None:
    """LWIS/SAWR roots and Addendum icing encode for profile ca_eccc."""
    case = next(c for c in golden_manifest["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8").strip()
    golden = (FIXTURES / case["golden"]).read_text(encoding="utf-8")
    result = convert(tac, product=case["product"], profile=PROFILE, iwxxm_version="3.0.0")
    assert canonicalize_xml(result.xml) == canonicalize_xml(golden)


@pytest.mark.parametrize("case_id", sorted(EV067_CASES))
def test_tc_ev067_001_m_golden_metar_speci_ca(case_id: str, golden_manifest: dict) -> None:
    """Golden manifest rows for EV-067 are active with rule_id."""
    case = next(c for c in golden_manifest["cases"] if c["id"] == case_id)
    assert case.get("status") == "active"
    assert case.get("rule_id", "").startswith("CA.METAR.")


def test_tc_ev067_002_lwis_root_element() -> None:
    """LWIS TAC emits iwxxm-ca:LWIS substitution-group root."""
    tac = "LWIS CYLA 292000Z AUTO 31006KT M00/M02 A2926="
    result = convert(tac, product="METAR", profile=PROFILE, iwxxm_version="3.0.0")
    assert "<iwxxm-ca:LWIS" in result.xml
    assert "ObservingSystemType/LWIS" in result.xml
    assert "<iwxxm:visibility" not in result.xml


def test_tc_ev067_003_sawr_density_altitude_addendum() -> None:
    """SAWR TAC emits iwxxm-ca:SAWR root with structured densityAltitude."""
    tac = "SAWR CYXX 231800Z AUTO 24010KT 5SM FEW030 M05/M10 A2998 RMK DENSITY ALT 2500FT="
    result = convert(tac, product="METAR", profile=PROFILE, iwxxm_version="3.0.0")
    assert "<iwxxm-ca:SAWR" in result.xml
    assert '<iwxxm-ca:densityAltitude uom="[ft_i]">2500</iwxxm-ca:densityAltitude>' in result.xml
    assert "DENSITY ALT 2500FT" not in result.xml
