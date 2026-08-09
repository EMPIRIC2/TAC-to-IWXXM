"""TC-EV050-001 / AC1 — offline harvest → membership sets (S059 / EV-050)."""

from __future__ import annotations

import urllib.request
from pathlib import Path

import pytest

from tac_validate import membership

REPO = Path(__file__).resolve().parents[3]


def test_harvest_includes_v1_family_keys() -> None:
    sets = membership.harvest_membership(root=REPO)
    for key in membership.V1_FAMILY_KEYS:
        assert key in sets, f"missing family {key}"
        assert len(sets[key]) > 0


def test_harvest_known_notations() -> None:
    sets = membership.harvest_membership(root=REPO)
    assert "RA" in sets["weather_306_4678"]
    assert "RA" in sets["present_or_forecast_weather"]
    assert "RERA" in sets["recent_weather"]
    assert "FEW" in sets["cloud_amount"]
    assert "TCU" in sets["cloud_type"]
    assert "VA" in sets["sigwx_phenomena"]
    assert "ISOL_TS" in sets["airwx_phenomena"]
    assert "inapplicable" in sets["nil_common"]
    assert "inapplicable" in sets["nil_common_rdf"]


def test_harvest_is_offline_only(monkeypatch: pytest.MonkeyPatch) -> None:
    def _blocked(*_a: object, **_k: object) -> None:
        raise AssertionError("network fetch attempted during harvest")

    monkeypatch.setattr(urllib.request, "urlopen", _blocked)
    membership.harvest_membership(root=REPO)


def test_committed_artifact_loads_and_matches_harvest() -> None:
    path = membership.membership_artifact_path()
    assert path.is_file(), "missing wmo_membership.json — run make membership-regen"
    membership.load_membership_sets.cache_clear()
    loaded = membership.load_membership_sets()
    harvested = membership.harvest_membership(root=REPO)
    for key in membership.V1_FAMILY_KEYS:
        assert loaded[key] == harvested[key]


def test_is_member_happy_sad() -> None:
    membership.load_membership_sets.cache_clear()
    assert membership.is_member("recent_weather", "RERA")
    assert not membership.is_member("recent_weather", "REZZZZ")
