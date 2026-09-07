"""TC-EV050-001 / AC1 - offline harvest → membership sets (S059 / EV-050)."""

from __future__ import annotations

import json
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
    assert path.is_file(), "missing wmo_membership.json - run make membership-regen"
    membership.load_membership_sets.cache_clear()
    loaded = membership.load_membership_sets()
    harvested = membership.harvest_membership(root=REPO)
    for key in membership.V1_FAMILY_KEYS:
        assert loaded[key] == harvested[key]


def test_is_member_happy_sad() -> None:
    membership.load_membership_sets.cache_clear()
    assert membership.is_member("recent_weather", "RERA")
    assert not membership.is_member("recent_weather", "REZZZZ")


def test_repo_root_env_override(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("TAC_VALIDATE_REPO_ROOT", str(tmp_path))
    assert membership.repo_root() == tmp_path.resolve()


def test_write_membership_artifact_roundtrip(tmp_path: Path) -> None:
    dest = tmp_path / "wmo_membership.json"
    harvested = membership.harvest_membership(root=REPO)
    written = membership.write_membership_artifact(harvested, dest=dest)
    assert written == dest
    payload = json.loads(dest.read_text(encoding="utf-8"))
    assert payload["offline_only"] is True
    assert payload["schema_version"] == 1
    assert set(payload["families"]) >= set(membership.V1_FAMILY_KEYS)
    assert payload["families"]["cloud_type"] == sorted(harvested["cloud_type"])


def test_write_membership_artifact_harvests_when_sets_omitted(tmp_path: Path) -> None:
    dest = tmp_path / "out.json"
    membership.write_membership_artifact(root=REPO, dest=dest)
    payload = json.loads(dest.read_text(encoding="utf-8"))
    assert "RA" in payload["families"]["weather_306_4678"]


def test_csv_notations_missing_file() -> None:
    with pytest.raises(FileNotFoundError, match=r".*"):
        membership._csv_notations(REPO / "no-such-file.csv")


def test_csv_notations_missing_column(tmp_path: Path) -> None:
    path = tmp_path / "bad.csv"
    path.write_text("id,label\n1,x\n", encoding="utf-8")
    with pytest.raises(ValueError, match="notation"):
        membership._csv_notations(path)


def test_csv_notations_empty(tmp_path: Path) -> None:
    path = tmp_path / "empty.csv"
    path.write_text("notation\n\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no notations"):
        membership._csv_notations(path)


def test_rdf_notations_missing_file() -> None:
    with pytest.raises(FileNotFoundError, match=r".*"):
        membership._rdf_notations(
            REPO / "missing.rdf",
            register_uri="http://codes.wmo.int/common/nil",
        )


def test_rdf_notations_empty_register(tmp_path: Path) -> None:
    path = tmp_path / "empty.rdf"
    path.write_text("<rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'/>\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no skos:Concept"):
        membership._rdf_notations(path, register_uri="http://codes.wmo.int/common/nil")


def test_load_membership_sets_missing_families(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "bad.json"
    path.write_text('{"schema_version": 1}\n', encoding="utf-8")
    monkeypatch.setattr(membership, "_ARTIFACT", path)
    membership.load_membership_sets.cache_clear()
    with pytest.raises(ValueError, match="families"):
        membership.load_membership_sets()
    membership.load_membership_sets.cache_clear()


def test_load_membership_sets_missing_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(membership, "_ARTIFACT", tmp_path / "absent.json")
    membership.load_membership_sets.cache_clear()
    with pytest.raises(FileNotFoundError, match=r".*"):
        membership.load_membership_sets()
    membership.load_membership_sets.cache_clear()


def test_is_member_unknown_family() -> None:
    with pytest.raises(KeyError, match="unknown membership family"):
        membership.is_member("not_a_family", "RA", sets={"weather_306_4678": frozenset({"RA"})})
