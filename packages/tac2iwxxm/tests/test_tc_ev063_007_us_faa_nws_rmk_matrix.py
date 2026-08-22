"""TC-EV063-007 — US_FAA_NWS RMK matrix fixture pack (EV-063 M7 / #919 slice).

Manifest-driven goldens under ``fixtures/profiles/US_FAA_NWS/`` exercise FMH-1 §12.7
structured REMARKS groups via canonical ``US_FAA_NWS`` (extends TC-EV063-002).

[Corpus: product §F36] [Corpus: tests §TC-EV063] [Corpus: domain-profiles]
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from metar_shared.xml_canonical import canonicalize_xml

from tac2iwxxm import convert

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "profiles" / "US_FAA_NWS"
MANIFEST_PATH = FIXTURES / "manifest.json"
IWXXM_VERSION = "2025-2"
PROFILE = "US_FAA_NWS"
ALIAS = "iwxxm_us"


def _load_manifest() -> dict:
    if not MANIFEST_PATH.is_file():
        pytest.fail(f"missing US_FAA_NWS manifest: {MANIFEST_PATH}")
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def rmk_manifest() -> dict:
    return _load_manifest()


def test_tc_ev063_007_manifest_present(rmk_manifest: dict) -> None:
    """RMK matrix pack lists canonical profile and ≥10 structured remark cases."""
    assert rmk_manifest.get("schema_version") == 1
    assert rmk_manifest.get("profile") == PROFILE
    cases = rmk_manifest.get("cases", [])
    assert len(cases) >= 10
    for case in cases:
        assert (FIXTURES / case["tac"]).is_file()
        assert (FIXTURES / case["golden"]).is_file()
        assert case.get("rule_id", "").startswith("US.METAR.RMK.")


@pytest.mark.parametrize(
    "case_id",
    [
        "rmk_ao2_slp",
        "rmk_pk_wnd",
        "rmk_wshft_fropa",
        "rmk_ltg_dsnt",
        "rmk_var_vis",
        "rmk_sector_vis",
        "rmk_tower_vis",
        "rmk_sky_8",
        "rmk_convective_cb",
        "rmk_hail_gr",
        "rmk_presfr",
        "rmk_recent_wx",
        "rmk_chino",
        "rmk_snincr",
        "rmk_combined",
    ],
)
def test_tc_ev063_007_us_faa_nws_rmk_golden(case_id: str, rmk_manifest: dict) -> None:
    """Canonical US_FAA_NWS convert matches profile fixture goldens."""
    case = next(c for c in rmk_manifest["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")
    expected = (FIXTURES / case["golden"]).read_text(encoding="utf-8")

    result = convert(
        tac,
        product=case["product"],
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    assert result.ok is True, f"{case_id}: {result.issues!r}"
    assert result.semantic_profile == "us_faa_nws"
    assert canonicalize_xml(result.xml or "") == canonicalize_xml(expected)


@pytest.mark.parametrize("case_id", ["rmk_ao2_slp", "rmk_combined", "rmk_ltg_dsnt"])
def test_tc_ev063_007_alias_iwxxm_us_parity(case_id: str, rmk_manifest: dict) -> None:
    """Legacy iwxxm_us alias remains byte-identical to US_FAA_NWS on RMK matrix rows."""
    case = next(c for c in rmk_manifest["cases"] if c["id"] == case_id)
    tac = (FIXTURES / case["tac"]).read_text(encoding="utf-8")

    canonical = convert(
        tac,
        product=case["product"],
        profile=PROFILE,
        iwxxm_version=IWXXM_VERSION,
    )
    alias = convert(
        tac,
        product=case["product"],
        profile=ALIAS,
        iwxxm_version=IWXXM_VERSION,
    )
    assert canonical.ok and alias.ok
    assert canonical.xml == alias.xml
    assert alias.deprecated_alias_used
