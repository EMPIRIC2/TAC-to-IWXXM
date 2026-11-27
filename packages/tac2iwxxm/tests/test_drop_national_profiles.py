"""Drop-guard: product ship list is ICAO-only (FR-019..022 / M1).

Emit packages and ``resolve_semantic_profile`` remain for unit suites; product
HTTP / first-party library seeds / inspector use ``is_shipped_product_semantic_profile``.

[Corpus: fr] epic #1688
"""

from __future__ import annotations

import pytest
from tac2iwxxm.library_assets import get_first_party_library_asset
from tac2iwxxm.profile_registry import (
    canonical_semantic_profile_wire_ids,
    is_shipped_product_semantic_profile,
    resolve_semantic_profile,
    shipped_product_semantic_wire_ids,
)

_DROPPED_WIRE_IDS = [
    "US_FAA_NWS",
    "iwxxm_us",
    "CA_ECCC",
    "AU_BOM",
    "NZ_CAA_MET",
]


@pytest.mark.parametrize("profile_id", _DROPPED_WIRE_IDS)
def test_dropped_nationals_not_on_product_ship_list(profile_id: str) -> None:
    """National ids still resolve for emit suites but are not product-shipped."""
    # Emit keys / nationals may need allow_emit_key after #1025 wire cutover.
    assert resolve_semantic_profile(profile_id, allow_emit_key=True) is not None
    assert is_shipped_product_semantic_profile(profile_id) is False


def test_baseline_icao_is_shipped() -> None:
    """ICAO baseline remains the only shipped product profile."""
    assert is_shipped_product_semantic_profile("ICAO_2025") is True
    assert is_shipped_product_semantic_profile("annex3") is False  # wire alias removed #1025
    assert is_shipped_product_semantic_profile("not_a_profile") is False
    assert shipped_product_semantic_wire_ids() == ("ICAO_2025",)
    # Full emit registry still lists nationals for unit suites.
    assert "CA_ECCC" in canonical_semantic_profile_wire_ids()
    assert "ICAO_2025" in canonical_semantic_profile_wire_ids()


@pytest.mark.parametrize(
    "library_id",
    [
        "LIB.CONVERSION.US_FAA_NWS",
        "LIB.CONVERSION.CA_ECCC",
        "LIB.CONVERSION.AU_BOM",
        "LIB.CONVERSION.NZ_CAA_MET",
    ],
)
def test_first_party_library_seeds_exclude_nationals(library_id: str) -> None:
    """First-party conversion library catalog does not seed dropped nationals."""
    assert get_first_party_library_asset(library_id) is None
