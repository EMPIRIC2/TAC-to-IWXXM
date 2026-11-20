"""Tests for inherit factory types and merge helpers."""

from __future__ import annotations

import pytest

from metar_shared.inherit_factory import (
    DEFAULT_PROFILE_IDS,
    PREFER_PRODUCTS,
    EffectiveBundle,
    InheritNode,
    LayerOverrides,
    apply_scalar_keys,
    empty_bundle,
    merge_code_sets,
    merge_overrides,
    merge_scalar_maps,
    resolve_inherit_tree,
    should_prefer_station,
)


def test_prefer_products_include_metar_speci_sigmet_taf() -> None:
    assert frozenset({"METAR", "SPECI", "TAF", "SIGMET"}) == PREFER_PRODUCTS


def test_should_prefer_station_default_profile_metar() -> None:
    assert should_prefer_station(profile="annex3", product="METAR") is True
    assert should_prefer_station(profile="ICAO_2025", product="speci") is True
    assert should_prefer_station(profile="annex3", product="SIGMET") is True


def test_should_prefer_station_explicit_national_skips() -> None:
    assert should_prefer_station(profile="iwxxm_us", product="METAR") is False
    assert should_prefer_station(profile="ca_eccc", product="TAF") is False


def test_should_prefer_station_non_prefer_product() -> None:
    assert should_prefer_station(profile="annex3", product="VAA") is False


def test_merge_scalar_maps_child_wins() -> None:
    assert merge_scalar_maps({"a": "1", "b": "2"}, {"b": "9", "c": "3"}) == {
        "a": "1",
        "b": "9",
        "c": "3",
    }


def test_merge_code_sets_union_and_replace() -> None:
    parent = frozenset({"A", "B"})
    child = frozenset({"B", "C"})
    assert merge_code_sets(parent, child, replace=False) == frozenset({"A", "B", "C"})
    assert merge_code_sets(parent, child, replace=True) == frozenset({"B", "C"})


def test_merge_overrides_sets_and_scalars() -> None:
    parent = LayerOverrides(
        scalars={"lint_profile_id": "annex3", "emit_key": "annex3"},
        allow_codes=frozenset({"X"}),
        deny_codes=frozenset({"D1"}),
    )
    child = LayerOverrides(
        scalars={"lint_profile_id": "iwxxm_us"},
        allow_codes=frozenset({"Y"}),
        deny_codes=frozenset({"D2"}),
        replace_deny=True,
    )
    merged = merge_overrides(parent, child)
    assert merged.scalars["lint_profile_id"] == "iwxxm_us"
    assert merged.scalars["emit_key"] == "annex3"
    assert merged.allow_codes == frozenset({"X", "Y"})
    assert merged.deny_codes == frozenset({"D2"})


def test_resolve_inherit_tree_product_region_country_station() -> None:
    tree = InheritNode(
        id="TAF",
        overrides=LayerOverrides(
            scalars={"lint_profile_id": "annex3", "emit_key": "annex3"},
            deny_codes=frozenset({"BASE"}),
        ),
        children={
            "NAM": InheritNode(
                id="NAM",
                overrides=LayerOverrides(scalars={"region_note": "north-america"}),
                children={
                    "iwxxm_us": InheritNode(
                        id="iwxxm_us",
                        overrides=LayerOverrides(
                            scalars={
                                "lint_profile_id": "iwxxm_us",
                                "emit_key": "iwxxm_us",
                            },
                            deny_codes=frozenset({"US_DENY"}),
                        ),
                        children={
                            "KORD": InheritNode(
                                id="KORD",
                                overrides=LayerOverrides(
                                    scalars={"lint_profile_id": "iwxxm_us"},
                                    allow_codes=frozenset({"STN_ALLOW"}),
                                ),
                            )
                        },
                    )
                },
            )
        },
    )
    bundle = resolve_inherit_tree(
        tree,
        product="taf",
        region="NAM",
        country="iwxxm_us",
        station="kord",
    )
    assert bundle.product == "TAF"
    assert bundle.region == "NAM"
    assert bundle.country == "iwxxm_us"
    assert bundle.station == "KORD"
    assert bundle.lint_profile_id == "iwxxm_us"
    assert bundle.emit_key == "iwxxm_us"
    assert bundle.deny_codes == frozenset({"BASE", "US_DENY"})
    assert bundle.allow_codes == frozenset({"STN_ALLOW"})
    assert bundle.chain == (
        "product:TAF",
        "region:NAM",
        "country:iwxxm_us",
        "station:KORD",
    )


def test_resolve_inherit_tree_root_mismatch_raises() -> None:
    root = InheritNode(id="METAR")
    with pytest.raises(ValueError, match="does not match product"):
        resolve_inherit_tree(root, product="TAF")


def test_empty_bundle_and_default_profile_ids() -> None:
    bundle = empty_bundle("metar")
    assert isinstance(bundle, EffectiveBundle)
    assert bundle.product == "METAR"
    assert bundle.chain == ("product:METAR",)
    assert "annex3" in DEFAULT_PROFILE_IDS
    assert "icao_2025" in DEFAULT_PROFILE_IDS


def test_resolve_skips_none_layers_and_unmapped_keys() -> None:
    root = InheritNode(
        id="METAR",
        overrides=LayerOverrides(scalars={"lint_profile_id": "annex3"}),
        children={"ca_eccc": InheritNode(id="ca_eccc")},
    )
    # region/country/station omitted → None branches continue
    only_product = resolve_inherit_tree(root, product="METAR")
    assert only_product.chain == ("product:METAR",)
    assert only_product.lint_profile_id == "annex3"
    # unmapped region still echoes in chain
    with_gap = resolve_inherit_tree(root, product="METAR", region="UNMAPPED")
    assert "region:UNMAPPED" in with_gap.chain


def test_resolve_station_uppercase_child_key() -> None:
    root = InheritNode(
        id="TAF",
        children={
            "KORD": InheritNode(
                id="KORD",
                overrides=LayerOverrides(scalars={"lint_profile_id": "iwxxm_us"}),
            )
        },
    )
    bundle = resolve_inherit_tree(root, product="TAF", station="kord")
    assert bundle.lint_profile_id == "iwxxm_us"
    assert bundle.station == "KORD"
    assert bundle.chain[-1] == "station:KORD"


def test_apply_scalar_keys_child_wins() -> None:
    base = empty_bundle("SIGMET")
    updated = apply_scalar_keys(
        base,
        {
            "lint_profile_id": "us_nws_convective_sigmet",
            "decode_pack_id": "sigmet",
        },
    )
    assert updated.lint_profile_id == "us_nws_convective_sigmet"
    assert updated.decode_pack_id == "sigmet"
    assert updated.product == "SIGMET"


def test_types_module_exports_constructible() -> None:
    from metar_shared.inherit_factory_types import EffectiveBundle, LayerOverrides

    assert LayerOverrides().allow_codes == frozenset()
    assert EffectiveBundle(product="METAR").product == "METAR"
