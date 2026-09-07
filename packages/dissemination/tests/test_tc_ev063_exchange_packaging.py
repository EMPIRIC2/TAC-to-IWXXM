"""Unit tests for exchange_registry and packaging (EV-063 / #921)."""

from __future__ import annotations

import pytest
from dissemination.collect_namespaces import is_collect_bulletin
from dissemination.exchange_registry import (
    DEFAULT_EXCHANGE_PROFILE_ID,
    normalize_exchange_id,
    normalize_exchange_id_key,
    resolve_exchange_profile,
)
from dissemination.packaging import apply_exchange_packaging, wrap_global_afs_collect

_MEMBER_XML = (
    '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2" gml:id="uuid.member"><iwxxm:observation/></iwxxm:METAR>'
)


def test_default_exchange_profile_id_is_global_afs() -> None:
    assert DEFAULT_EXCHANGE_PROFILE_ID == "GLOBAL_AFS"


def test_normalize_exchange_id_helpers() -> None:
    assert normalize_exchange_id(" global-afs ") == "GLOBAL_AFS"
    assert normalize_exchange_id_key(" Global-AFS ") == "global_afs"


@pytest.mark.parametrize("wire_id", ["GLOBAL_AFS", "global_afs", "global-afs"])
def test_resolve_exchange_profile_accepts_wire_forms(wire_id: str) -> None:
    resolved = resolve_exchange_profile(wire_id)
    assert resolved is not None
    assert resolved.wire_id == "GLOBAL_AFS"


def test_resolve_exchange_profile_unknown_returns_none() -> None:
    assert resolve_exchange_profile("NOT_AN_EXCHANGE") is None
    assert resolve_exchange_profile("") is None


def test_resolve_exchange_profile_wire_id_lookup(monkeypatch: pytest.MonkeyPatch) -> None:
    """Wire-id branch when lowercase canonical key differs from wire token."""

    monkeypatch.setattr(
        "dissemination.exchange_registry._CANONICAL_TO_WIRE",
        {"other_canonical": "GLOBAL_AFS"},
    )
    resolved = resolve_exchange_profile("GLOBAL_AFS")
    assert resolved is not None
    assert resolved.canonical == "other_canonical"
    assert resolved.wire_id == "GLOBAL_AFS"


def test_known_exchange_profile_ids_includes_wire_and_canonical() -> None:
    from dissemination.exchange_registry import known_exchange_profile_ids

    ids = known_exchange_profile_ids()
    assert "GLOBAL_AFS" in ids
    assert "global_afs" in ids
    assert "APAC_ROBEX" in ids
    assert "apac_robex" in ids
    assert "EUR_RODEX" in ids
    assert "AFI" in ids
    assert "CAR_SAM" in ids


def test_wrap_global_afs_collect_preserves_member() -> None:
    packaged = wrap_global_afs_collect(_MEMBER_XML, bulletin_identifier="A_SAMPLE.xml")
    assert is_collect_bulletin(packaged)
    assert _MEMBER_XML in packaged
    assert "A_SAMPLE.xml" in packaged


def test_wrap_global_afs_collect_default_bulletin_identifier() -> None:
    packaged = wrap_global_afs_collect(_MEMBER_XML)
    assert "A_UNKNOWN.xml" in packaged


def test_apply_exchange_packaging_global_afs() -> None:
    packaged = apply_exchange_packaging(_MEMBER_XML, exchange_profile="GLOBAL_AFS", bulletin_identifier="A_TEST.xml")
    assert is_collect_bulletin(packaged)
    assert "A_TEST.xml" in packaged


def test_apply_exchange_packaging_apac_robex_collect_wrap() -> None:
    """TC-EV065-002 - APAC_ROBEX P0 stub uses GLOBAL_AFS COLLECT baseline."""
    packaged = apply_exchange_packaging(
        _MEMBER_XML,
        exchange_profile="APAC_ROBEX",
        bulletin_identifier="A_APAC.xml",
    )
    assert is_collect_bulletin(packaged)
    assert "A_APAC.xml" in packaged


def test_apply_exchange_packaging_rejects_unknown_profile() -> None:
    with pytest.raises(ValueError, match="unknown exchange profile"):
        apply_exchange_packaging(_MEMBER_XML, exchange_profile="NOT_AN_EXCHANGE")


def test_apply_exchange_packaging_rejects_unimplemented_canonical(monkeypatch: pytest.MonkeyPatch) -> None:
    """Resolved but unregistered packaging path returns a clear not-implemented error."""

    def fake_resolve(_profile: str):
        from dissemination.exchange_registry import ResolvedExchangeProfile

        return ResolvedExchangeProfile(canonical="future_overlay", wire_id="FUTURE_OVERLAY")

    monkeypatch.setattr("dissemination.packaging.resolve_exchange_profile", fake_resolve)
    with pytest.raises(ValueError, match="not implemented"):
        apply_exchange_packaging(_MEMBER_XML, exchange_profile="FUTURE_OVERLAY")


def test_wrap_global_afs_collect_strips_xml_declaration() -> None:
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + _MEMBER_XML
    packaged = wrap_global_afs_collect(xml)
    assert is_collect_bulletin(packaged)
    assert packaged.count("<?xml") == 1
    assert _MEMBER_XML in packaged

    once = wrap_global_afs_collect(_MEMBER_XML)
    twice = wrap_global_afs_collect(once)
    assert twice == once
