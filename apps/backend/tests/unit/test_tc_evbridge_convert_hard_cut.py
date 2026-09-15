"""TC-EVBRIDGE — Convert hard-cut helpers + reject legacy fields."""

from __future__ import annotations

import pytest
from metar_iwxxm_api.convert_library_hard_cut import (
    DEFAULT_CONVERSION_LIBRARY_ID,
    legacy_convert_fields_present,
    legacy_convert_reject_detail,
    library_id_for_semantic_or_alias,
    resolve_engine_profile_from_conversion_library,
)


def test_legacy_fields_detected() -> None:
    """Non-empty legacy fields are listed."""
    assert legacy_convert_fields_present(semantic_profile="ICAO_2025") == ["semantic_profile"]
    assert legacy_convert_fields_present(profile="annex3", preset_id="x") == [
        "profile",
        "preset_id",
    ]
    assert legacy_convert_fields_present() == []


def test_legacy_reject_detail_is_operator_plain() -> None:
    """422 detail names fields without planning vocabulary."""
    detail = legacy_convert_reject_detail(["semantic_profile", "overlay_id"])
    assert "semantic_profile" in detail
    assert "conversion_library_id" in detail
    assert "Corpus" not in detail
    assert "ADR" not in detail


def test_resolve_default_icao_library() -> None:
    """Empty library id defaults to ICAO Conversion."""
    lib_id, engine = resolve_engine_profile_from_conversion_library("")
    assert lib_id == DEFAULT_CONVERSION_LIBRARY_ID
    assert engine == "ICAO_2025"


def test_resolve_us_library() -> None:
    """US Conversion library maps to US_FAA_NWS."""
    lib_id, engine = resolve_engine_profile_from_conversion_library("LIB.CONVERSION.US_FAA_NWS")
    assert lib_id == "LIB.CONVERSION.US_FAA_NWS"
    assert engine == "US_FAA_NWS"


def test_resolve_unknown_library_raises() -> None:
    """Unknown library id fails closed."""
    with pytest.raises(ValueError, match="Unknown"):
        resolve_engine_profile_from_conversion_library("LIB.CONVERSION.NOT_REAL")


def test_library_id_for_alias_annex3() -> None:
    """annex3 alias maps to ICAO Conversion library."""
    assert library_id_for_semantic_or_alias("annex3") == "LIB.CONVERSION.ICAO_2025"
    assert library_id_for_semantic_or_alias("iwxxm_us") == "LIB.CONVERSION.US_FAA_NWS"
    assert library_id_for_semantic_or_alias("CA_ECCC") == "LIB.CONVERSION.CA_ECCC"
