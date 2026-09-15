"""TC-EVBRIDGE — five Libraries first-party catalog (package layer)."""

from __future__ import annotations

import pytest
from tac2iwxxm.library_assets import (
    LIBRARY_KINDS,
    LibraryAsset,
    assert_first_party_immutable,
    canonical_national_line_ids,
    conversion_rules_for_asset,
    first_party_library_id,
    fork_first_party_library,
    get_first_party_library_asset,
    list_first_party_library_assets,
    require_rule_for_group,
)


def test_tc_evbridge_002_national_split_five_defaults() -> None:
    """Each national line has five first-party library defaults."""
    lines = canonical_national_line_ids()
    assert "ICAO_2025" in lines
    assert "US_FAA_NWS" in lines
    assets = list_first_party_library_assets()
    assert len(assets) == len(lines) * len(LIBRARY_KINDS)
    for national in lines:
        for kind in LIBRARY_KINDS:
            asset_id = first_party_library_id(kind, national)
            found = get_first_party_library_asset(asset_id)
            assert found is not None
            assert found.access == "first_party"
            assert found.engine_profile_id == national
            assert found.attached_national_line == national
            assert found.kind == kind
            as_dict = found.to_dict()
            assert as_dict["id"] == asset_id
            assert as_dict["kind"] == kind
            assert as_dict["fork_of"] is None


def test_tc_evbridge_003_fork_on_edit_leaves_builtin() -> None:
    """Fork creates custom copy; first-party source unchanged."""
    base_id = first_party_library_id("conversion", "ICAO_2025")
    base = get_first_party_library_asset(base_id)
    assert base is not None
    forked = fork_first_party_library(base_id, new_id="custom-conv-1")
    assert forked.access == "custom"
    assert forked.fork_of == base_id
    assert forked.engine_profile_id == base.engine_profile_id
    again = get_first_party_library_asset(base_id)
    assert again is not None
    assert again.access == "first_party"
    assert again.body == base.body


def test_tc_evbridge_003b_unknown_asset_and_fork() -> None:
    """Unknown id returns None; fork raises KeyError."""
    assert get_first_party_library_asset("LIB.CONVERSION.DOES_NOT_EXIST") is None
    with pytest.raises(KeyError, match="unknown first-party"):
        fork_first_party_library("LIB.CONVERSION.DOES_NOT_EXIST", new_id="x")


def test_tc_evbridge_004_first_party_non_deletable() -> None:
    """Mutate/delete of first-party fails closed."""
    base = get_first_party_library_asset(first_party_library_id("decoding", "CA_ECCC"))
    assert base is not None
    with pytest.raises(PermissionError):
        assert_first_party_immutable(base, mutating=True)
    assert_first_party_immutable(base, mutating=False)
    custom = fork_first_party_library(base.id, new_id="custom-dec-1", name="Custom dec")
    assert custom.name == "Custom dec"
    assert_first_party_immutable(custom, mutating=True)


def test_tc_evbridge_011_require_rule_for_group() -> None:
    """AC11: matched group resolves a rule; unmatched fails closed."""
    asset = get_first_party_library_asset(first_party_library_id("conversion", "ICAO_2025"))
    assert asset is not None
    rule = require_rule_for_group(asset, focus_group="18012G20KT")
    assert rule.id == "CV.WIND"
    with pytest.raises(ValueError, match="no conversion rule"):
        require_rule_for_group(asset, focus_group="NOTAGROUPXYZ")


def test_tc_evbridge_011b_rules_helpers_and_kind_guard() -> None:
    """conversion_rules_for_asset + require_rule kind / empty-body guards."""
    dissem = get_first_party_library_asset(
        first_party_library_id("dissemination", "ICAO_2025"),
    )
    assert dissem is not None
    assert conversion_rules_for_asset(dissem) == ()
    with pytest.raises(ValueError, match="conversion library"):
        require_rule_for_group(dissem, focus_group="18012G20KT")

    empty_rules = LibraryAsset(
        id="custom-empty",
        kind="conversion",
        name="Empty",
        access="custom",
        engine_profile_id="ICAO_2025",
        attached_national_line="ICAO_2025",
        body={"rules": "not-a-list"},
    )
    assert conversion_rules_for_asset(empty_rules) == ()
    # Empty/non-list body falls back to first-party templates
    rule = require_rule_for_group(empty_rules, focus_group="18012G20KT")
    assert rule.id == "CV.WIND"
