"""Unit tests for lint catalog profile filter helpers (EV-1120)."""

from __future__ import annotations

from src.services.lint_catalog_profile_filter import (
    exchange_profiles_from_tags,
    row_matches_profile,
    semantic_profiles_from_tags,
)


def test_semantic_profiles_from_tags_maps_us_and_ca() -> None:
    assert semantic_profiles_from_tags(("taf", "us_faa_nws")) == ["us_faa_nws"]
    assert semantic_profiles_from_tags(("remark", "ca_eccc", "manobs")) == ["ca_eccc"]
    assert semantic_profiles_from_tags(("terminator", "metar")) == []


def test_exchange_profiles_from_tags() -> None:
    assert exchange_profiles_from_tags(("global_afs",)) == ["GLOBAL_AFS"]
    assert exchange_profiles_from_tags(("exchange:EUR_RODEX",)) == ["EUR_RODEX"]
    assert exchange_profiles_from_tags(("metar",)) == []


def test_row_matches_profile_shared_and_specific() -> None:
    assert row_matches_profile([], selected="icao_2025") is True
    assert row_matches_profile(["us_faa_nws"], selected="us_faa_nws") is True
    assert row_matches_profile(["us_faa_nws"], selected="icao_2025") is False
