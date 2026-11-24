"""Drop-guard: national semantic profiles removed (FR-019..022 / M1).

[Corpus: fr] epic #1688
"""

from __future__ import annotations

import pytest
from tac2iwxxm.profile_registry import (
    canonical_semantic_profile_wire_ids,
    known_semantic_profile_ids,
    resolve_semantic_profile,
    supported_report_variants_for_profile,
)

from tac2iwxxm import convert

_DROPPED_WIRE_IDS = [
    "US_FAA_NWS",
    "iwxxm_us",
    "CA_ECCC",
    "ca_eccc",
    "AU_BOM",
    "NZ_CAA_MET",
    "US_MILITARY",
    "LATAM_TAF",
    "UK_METOFFICE",
    "BR_DECEA",
    "KR_KMA",
    "JP_JMA",
    "IN_IMD",
    "HK_HKO",
    "US_NWS_CONVECTIVE_SIGMET",
    "US_NWS_G_AIRMET",
    "US_NWS_VONA",
    "CA_MSC_SIGMET",
]

_SAMPLE_METAR = "METAR KJFK 221953Z 18010KT 10SM FEW050 22/12 A3012="


@pytest.mark.parametrize("profile_id", _DROPPED_WIRE_IDS)
def test_dropped_national_profiles_do_not_resolve(profile_id: str) -> None:
    """Dropped national ids are unknown to the semantic registry."""
    assert resolve_semantic_profile(profile_id) is None
    assert profile_id.lower().replace("-", "_") not in known_semantic_profile_ids()


def test_baseline_icao_remains() -> None:
    """Single baseline ICAO_2025 / annex3 still resolve."""
    assert resolve_semantic_profile("ICAO_2025") is not None
    assert resolve_semantic_profile("annex3") is not None
    assert "ICAO_2025" in canonical_semantic_profile_wire_ids()
    assert canonical_semantic_profile_wire_ids() == ("ICAO_2025",)


def _issue_codes(result: object) -> set[str]:
    issues = getattr(result, "issues", None) or []
    return {str(getattr(issue, "code", "")) for issue in issues}


@pytest.mark.parametrize("profile_id", ["US_FAA_NWS", "CA_ECCC", "AU_BOM", "NZ_CAA_MET", "iwxxm_us"])
def test_convert_rejects_dropped_national_profiles(profile_id: str) -> None:
    """Convert fail-closes dropped national profiles."""
    result = convert(_SAMPLE_METAR, product="METAR", profile=profile_id)
    assert result.ok is False
    assert "UNSUPPORTED_PROFILE" in _issue_codes(result)


@pytest.mark.parametrize("variant", ["LWIS", "SAWR"])
def test_lwis_sawr_variants_unsupported(variant: str) -> None:
    """LWIS/SAWR report variants are gone with CA_ECCC (FR-012)."""
    assert variant not in supported_report_variants_for_profile("CA_ECCC", "METAR")
    assert variant not in supported_report_variants_for_profile("ICAO_2025", "METAR")
    result = convert(
        _SAMPLE_METAR,
        product="METAR",
        profile="ICAO_2025",
        report_variant=variant,
    )
    assert result.ok is False
    assert "INVALID_REPORT_VARIANT" in _issue_codes(result)
