"""TC-EVBRIDGE — Convert hard-cut helpers + reject legacy fields."""

from __future__ import annotations

from unittest.mock import MagicMock

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


def test_resolve_non_conversion_library_raises() -> None:
    """Non-conversion first-party ids are rejected."""
    with pytest.raises(ValueError, match="Conversion library"):
        resolve_engine_profile_from_conversion_library("LIB.DISSEMINATION.ICAO_2025")


def test_resolve_custom_engine_profile_callback() -> None:
    """Custom lookup resolves engine profile via semantic alias or raw wire id."""
    lib_id, engine = resolve_engine_profile_from_conversion_library(
        "custom-asset-1",
        get_custom_engine_profile_id=lambda _aid: "annex3",
    )
    assert lib_id == "custom-asset-1"
    assert engine == "ICAO_2025"

    lib_id2, engine2 = resolve_engine_profile_from_conversion_library(
        "custom-asset-2",
        get_custom_engine_profile_id=lambda _aid: "NOT_A_SEMANTIC",
    )
    assert lib_id2 == "custom-asset-2"
    assert engine2 == "NOT_A_SEMANTIC"


def test_resolve_custom_callback_none_still_unknown() -> None:
    """Callback that returns None / empty still fails closed."""
    with pytest.raises(ValueError, match="Unknown"):
        resolve_engine_profile_from_conversion_library(
            "missing-custom",
            get_custom_engine_profile_id=lambda _aid: None,
        )


def test_library_id_for_alias_annex3() -> None:
    """annex3 alias maps to ICAO Conversion library."""
    assert library_id_for_semantic_or_alias("annex3") == "LIB.CONVERSION.ICAO_2025"
    assert library_id_for_semantic_or_alias("iwxxm_us") == "LIB.CONVERSION.US_FAA_NWS"
    assert library_id_for_semantic_or_alias("CA_ECCC") == "LIB.CONVERSION.CA_ECCC"


def test_library_id_for_empty_lib_prefix_and_unknown() -> None:
    """Empty / LIB. passthrough / unknown alias → default or raw LIB id."""
    assert library_id_for_semantic_or_alias("") == DEFAULT_CONVERSION_LIBRARY_ID
    assert library_id_for_semantic_or_alias("   ") == DEFAULT_CONVERSION_LIBRARY_ID
    assert library_id_for_semantic_or_alias("LIB.CONVERSION.US_FAA_NWS") == "LIB.CONVERSION.US_FAA_NWS"
    assert library_id_for_semantic_or_alias("not-a-real-profile") == DEFAULT_CONVERSION_LIBRARY_ID
    assert library_id_for_semantic_or_alias("") == DEFAULT_CONVERSION_LIBRARY_ID
    assert library_id_for_semantic_or_alias("LIB.CONVERSION.US_FAA_NWS") == ("LIB.CONVERSION.US_FAA_NWS")
    assert library_id_for_semantic_or_alias("not-a-real-profile") == DEFAULT_CONVERSION_LIBRARY_ID


def test_resolve_rejects_non_conversion_library() -> None:
    """Dissemination library id is not valid as conversion_library_id."""
    with pytest.raises(ValueError, match="Conversion library"):
        resolve_engine_profile_from_conversion_library("LIB.DISSEMINATION.ICAO_2025")


def test_resolve_custom_library_via_callback() -> None:
    """Custom assets resolve through get_custom_engine_profile_id."""
    lib_id, engine = resolve_engine_profile_from_conversion_library(
        "custom-conv-xyz",
        get_custom_engine_profile_id=lambda _aid: "US_FAA_NWS",
    )
    assert lib_id == "custom-conv-xyz"
    assert engine == "US_FAA_NWS"

    lib_id2, engine2 = resolve_engine_profile_from_conversion_library(
        "custom-alias",
        get_custom_engine_profile_id=lambda _aid: "annex3",
    )
    assert lib_id2 == "custom-alias"
    assert engine2 == "ICAO_2025"


def test_resolve_dissemination_first_party_and_custom() -> None:
    """Dissemination transforms load from first-party or custom body callback."""
    from metar_iwxxm_api.convert_library_hard_cut import resolve_dissemination_transforms

    transforms = resolve_dissemination_transforms("LIB.DISSEMINATION.ICAO_2025")
    assert isinstance(transforms, list)
    assert transforms  # seeded transforms present

    custom = resolve_dissemination_transforms(
        "custom-dissem-1",
        get_custom_dissemination_body=lambda _aid: {
            "transforms": [{"type": "checksum", "params": {}}],
        },
    )
    assert custom == [{"type": "checksum", "params": {}}]

    with pytest.raises(ValueError, match="Unknown dissemination"):
        resolve_dissemination_transforms("custom-missing")

    with pytest.raises(ValueError, match="Dissemination library"):
        resolve_dissemination_transforms("LIB.CONVERSION.ICAO_2025")


def test_resolve_dissemination_empty_id_raises() -> None:
    """Empty dissemination id fails closed."""
    from metar_iwxxm_api.convert_library_hard_cut import resolve_dissemination_transforms

    with pytest.raises(ValueError, match="required"):
        resolve_dissemination_transforms("")


def test_resolve_dissemination_custom_non_list_transforms() -> None:
    """Custom body with non-list transforms yields empty list."""
    from metar_iwxxm_api.convert_library_hard_cut import resolve_dissemination_transforms

    out = resolve_dissemination_transforms(
        "custom-x",
        get_custom_dissemination_body=lambda _aid: {"transforms": "nope"},
    )
    assert out == []


def test_resolve_dissemination_custom_callback_returns_none() -> None:
    """Callback present but returning None falls through to unknown-id error."""
    from metar_iwxxm_api.convert_library_hard_cut import resolve_dissemination_transforms

    with pytest.raises(ValueError, match="Unknown dissemination"):
        resolve_dissemination_transforms(
            "custom-absent-body",
            get_custom_dissemination_body=lambda _aid: None,
        )


def test_resolve_dissemination_first_party_non_list_transforms(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """First-party asset with non-list transforms yields empty list."""
    from metar_iwxxm_api import convert_library_hard_cut as cut

    fake = MagicMock()
    fake.kind = "dissemination"
    fake.body = {"transforms": "broken"}
    monkeypatch.setattr(cut, "get_first_party_library_asset", lambda _aid: fake)
    assert cut.resolve_dissemination_transforms("LIB.DISSEMINATION.ICAO_2025") == []


def test_resolve_custom_callback_raises_kind_error() -> None:
    """Callback ValueError for wrong kind propagates."""

    def _bad(_aid: str) -> str | None:
        raise ValueError("conversion_library_id must reference a Conversion library")

    with pytest.raises(ValueError, match="Conversion library"):
        resolve_engine_profile_from_conversion_library(
            "custom-wrong-kind",
            get_custom_engine_profile_id=_bad,
        )
