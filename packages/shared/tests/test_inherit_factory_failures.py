"""Inherit-factory FAILURE / validation edges (ADR-055)."""

from __future__ import annotations

import pytest

from metar_shared.inherit_factory import (
    InheritNode,
    LayerOverrides,
    merge_code_sets,
    merge_overrides,
    normalize_product,
    normalize_profile_id,
    resolve_inherit_tree,
    should_prefer_station,
)


def test_resolve_inherit_tree_rejects_blank_product_vs_named_root() -> None:
    root = InheritNode(id="METAR")
    with pytest.raises(ValueError, match="does not match product"):
        resolve_inherit_tree(root, product="   ")


def test_resolve_inherit_tree_rejects_case_mismatched_product_family() -> None:
    root = InheritNode(id="TAF")
    with pytest.raises(
        ValueError, match=r"inherit root id 'TAF' does not match product 'METAR'"
    ):
        resolve_inherit_tree(root, product="metar")


def test_normalize_helpers_treat_none_like_empty() -> None:
    assert normalize_product(None) == ""  # type: ignore[arg-type]
    assert normalize_profile_id(None) == ""  # type: ignore[arg-type]
    assert should_prefer_station(profile="  ", product="METAR") is False
    assert should_prefer_station(profile="annex3", product="") is False


def test_merge_overrides_replace_allow_drops_parent_codes() -> None:
    parent = LayerOverrides(allow_codes=frozenset({"A", "B"}))
    child = LayerOverrides(allow_codes=frozenset({"C"}), replace_allow=True)
    merged = merge_overrides(parent, child)
    assert merged.allow_codes == frozenset({"C"})
    assert merge_code_sets(
        frozenset({"A"}), frozenset({"B"}), replace=True
    ) == frozenset({"B"})


def test_resolve_whitespace_only_layers_are_skipped() -> None:
    root = InheritNode(
        id="METAR",
        overrides=LayerOverrides(scalars={"lint_profile_id": "annex3"}),
        children={"NAM": InheritNode(id="NAM")},
    )
    bundle = resolve_inherit_tree(
        root,
        product="METAR",
        region="   ",
        country="",
        station="\t",
    )
    assert bundle.chain == ("product:METAR",)
    assert bundle.region is None
    assert bundle.country is None
    assert bundle.station is None
