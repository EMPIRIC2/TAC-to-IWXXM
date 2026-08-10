"""TC-EV050-007 / AC7 — dual-profile annex3 vs iwxxm_us lint harness (S059)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tac_validate import lint
from tac_validate.dual_profile import compare_lint_profiles
from tac_validate.profiles import (
    F6_DUAL_PROFILE_PRODUCTS,
    IWXXM_US_PRODUCTS,
    PROFILE_ANNEX3,
    PROFILE_IWXXM_US,
    iwxxm_us_applicable,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"
MANIFEST = json.loads((FIXTURES / "manifest.json").read_text(encoding="utf-8"))

# One representative accept TAC per product for the dual-profile matrix.
_REPRESENTATIVE: dict[str, str] = {
    "METAR": "accept/metar_basic.tac",
    "SPECI": "accept/speci_basic.tac",
    "TAF": "accept/taf_basic.tac",
    "SIGMET": "accept/sigmet_basic.tac",
    "AIRMET": "accept/airmet_a2_phenomenon.tac",
    "VAA": "accept/vaa_basic.tac",
    "TCA": "accept/tca_basic.tac",
    "SWXA": "accept/swxa_sx1_hf_com.tac",
    "VONA": "accept/vona_basic.tac",
}


def _read(rel: str) -> str:
    path = FIXTURES / rel
    assert path.is_file(), f"missing fixture {path}"
    return path.read_text(encoding="utf-8")


def test_f6_matrix_covers_all_products() -> None:
    assert set(F6_DUAL_PROFILE_PRODUCTS) == set(_REPRESENTATIVE)
    dual = {p for p in F6_DUAL_PROFILE_PRODUCTS if iwxxm_us_applicable(p)}
    na = {p for p in F6_DUAL_PROFILE_PRODUCTS if not iwxxm_us_applicable(p)}
    assert dual == set(IWXXM_US_PRODUCTS)
    assert na == {"VAA", "TCA", "SWXA", "VONA"}


@pytest.mark.parametrize("product", sorted(IWXXM_US_PRODUCTS))
def test_dual_applicable_no_unclassified_divergence(product: str) -> None:
    tac = _read(_REPRESENTATIVE[product])
    result = compare_lint_profiles(tac, product=product)
    assert result.disposition == "dual"
    assert result.ok, result.note
    assert result.iwxxm_us_codes is not None
    # L3 membership codes must match across profiles.
    mem_a = {c for c in result.annex3_codes if c == "UNKNOWN_WMO_MEMBERSHIP"}
    mem_u = {c for c in result.iwxxm_us_codes if c == "UNKNOWN_WMO_MEMBERSHIP"}
    assert mem_a == mem_u


@pytest.mark.parametrize("product", ["VAA", "TCA", "SWXA", "VONA"])
def test_na_products_iwxxm_us_not_fail(product: str) -> None:
    tac = _read(_REPRESENTATIVE[product])
    result = compare_lint_profiles(tac, product=product)
    assert result.disposition == "na"
    assert result.ok is True
    assert result.iwxxm_us_codes is None
    with pytest.raises(ValueError, match="not applicable"):
        lint(tac, product=product, profile=PROFILE_IWXXM_US)


def test_membership_sad_matches_across_dual_profiles() -> None:
    tac = _read("negative/metar/unknown_recent_weather.tac")
    result = compare_lint_profiles(tac, product="METAR")
    assert result.disposition == "dual"
    assert result.ok, result.note
    assert result.iwxxm_us_codes is not None
    assert "UNKNOWN_WMO_MEMBERSHIP" in result.annex3_codes
    assert "UNKNOWN_WMO_MEMBERSHIP" in result.iwxxm_us_codes


def test_lint_rejects_unknown_profile() -> None:
    with pytest.raises(ValueError, match="unsupported lint profile"):
        lint("METAR KJFK 121255Z 18008KT 10SM SCT040 22/18 A2992=", product="METAR", profile="nope")


def test_default_profile_is_annex3() -> None:
    tac = _read("accept/metar_basic.tac")
    a = lint(tac, product="METAR")
    b = lint(tac, product="METAR", profile=PROFILE_ANNEX3)
    assert {i.code for i in a.issues} == {i.code for i in b.issues}


def test_harness_fails_on_unclassified_divergence(monkeypatch: pytest.MonkeyPatch) -> None:
    """Comparator must fail when profiles diverge on a non-allowlisted code."""
    from tac_validate import dual_profile as dp

    def _fake_codes(tac_text: str, *, product: str, profile: str) -> frozenset[str]:
        if profile == PROFILE_ANNEX3:
            return frozenset({"SHARED"})
        return frozenset({"SHARED", "SUSPECT_TRUE_ERROR"})

    monkeypatch.setattr(dp, "_issue_codes", _fake_codes)
    result = dp.compare_lint_profiles("METAR …", product="METAR")
    assert result.ok is False
    assert "SUSPECT_TRUE_ERROR" in result.unclassified_divergent
