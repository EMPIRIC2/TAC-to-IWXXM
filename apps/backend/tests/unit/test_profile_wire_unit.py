"""Unit tests for profile wire resolution (F35 / EV-063)."""

from __future__ import annotations

import pytest
from fastapi import HTTPException
from src.utilities import profile_wire as pw


def test_default_semantic_profile_legacy_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PROFILE_WIRE_V2", raising=False)
    monkeypatch.delenv("DEFAULT_SEMANTIC_PROFILE", raising=False)
    assert pw.default_semantic_profile() == "annex3"


def test_default_semantic_profile_wire_v2(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROFILE_WIRE_V2", "true")
    monkeypatch.delenv("DEFAULT_SEMANTIC_PROFILE", raising=False)
    assert pw.default_semantic_profile() == "ICAO_2025"


def test_resolve_canonical_semantic_profile() -> None:
    sel = pw.resolve_route_profiles(semantic_profile="ICAO_2025")
    assert sel.emit_key == "annex3"
    assert sel.semantic_canonical == "icao_2025"
    assert sel.deprecated_alias_used is False


def test_resolve_ca_eccc_semantic_profile() -> None:
    sel = pw.resolve_route_profiles(semantic_profile="CA_ECCC")
    assert sel.emit_key == "ca_eccc"
    assert sel.semantic_canonical == "ca_eccc"
    assert sel.deprecated_alias_used is False


def test_resolve_legacy_alias_marks_deprecation() -> None:
    sel = pw.resolve_route_profiles(profile="annex3")
    assert sel.emit_key == "annex3"
    assert sel.deprecated_alias_used is True


def test_unknown_semantic_raises_400() -> None:
    with pytest.raises(HTTPException) as exc:
        pw.resolve_route_profiles(semantic_profile="NOPE")
    assert exc.value.status_code == 400
    assert exc.value.detail["code"] == "invalid_semantic_profile"


def test_unknown_exchange_raises_400() -> None:
    with pytest.raises(HTTPException) as exc:
        pw.resolve_route_profiles(profile="annex3", exchange_profile="NOPE")
    assert exc.value.status_code == 400
    assert exc.value.detail["code"] == "invalid_exchange_profile"


def test_global_afs_exchange_accepted() -> None:
    sel = pw.resolve_route_profiles(profile="annex3", exchange_profile="GLOBAL_AFS")
    assert sel.exchange_profile == "GLOBAL_AFS"


def test_packaging_path_defaults_global_afs() -> None:
    sel = pw.resolve_route_profiles(profile="annex3", for_packaging=True)
    assert sel.exchange_profile == "GLOBAL_AFS"


def test_convert_only_path_omits_exchange_default() -> None:
    sel = pw.resolve_route_profiles(profile="annex3", for_packaging=False)
    assert sel.exchange_profile is None
