"""TC-EVBRIDGE — conversion_library_id resolves engine profile on convert."""

from __future__ import annotations

from tac2iwxxm.library_assets import get_first_party_library_asset


def test_conversion_library_icao_resolves_engine_profile() -> None:
    """LIB.CONVERSION.ICAO_2025 maps to ICAO_2025."""
    asset = get_first_party_library_asset("LIB.CONVERSION.ICAO_2025")
    assert asset is not None
    assert asset.kind == "conversion"
    assert asset.engine_profile_id == "ICAO_2025"


def test_conversion_library_us_resolves_engine_profile() -> None:
    """LIB.CONVERSION.US_FAA_NWS maps to US_FAA_NWS."""
    asset = get_first_party_library_asset("LIB.CONVERSION.US_FAA_NWS")
    assert asset is not None
    assert asset.engine_profile_id == "US_FAA_NWS"
