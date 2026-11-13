"""Coverage battery for code_list_policy edge paths (#1034)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from iwxxm_validate import code_list_policy as policy


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    policy.load_code_list_policy.cache_clear()
    yield
    policy.load_code_list_policy.cache_clear()


@pytest.mark.parametrize(
    ("mode", "payload", "expect_empty"),
    [
        (
            "success",
            {
                "profile": "CA_ECCC",
                "entries": [
                    {
                        "id": "x",
                        "area": "ic",
                        "token": "IC",
                        "kind": "replace",
                        "global_uri": "g",
                        "ca_uri": "c",
                        "disallow_global": True,
                        "products": ["METAR"],
                    }
                ],
            },
            False,
        ),
        ("failure", "not-a-mapping", True),
        ("validation", {"profile": "CA_ECCC", "entries": "bad"}, True),
    ],
)
def test_load_code_list_policy_modes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mode: str,
    payload: object,
    expect_empty: bool,
) -> None:
    del mode
    profiles = tmp_path / "config" / "profiles" / "semantic"
    profiles.mkdir(parents=True)
    matrix = profiles / "CA_ECCC.code-list-deviations.yaml"
    matrix.write_text(yaml.safe_dump(payload), encoding="utf-8")
    monkeypatch.setattr(policy, "_DEFAULT_REPO_ROOT", tmp_path)
    loaded = policy.load_code_list_policy("CA_ECCC")
    if expect_empty:
        assert loaded.entries == ()
    else:
        assert loaded.entries
        assert loaded.resolve_ca_uri(area="ic", token="IC")
        assert loaded.resolve_ca_uri(area="ic", token="NOPE") is None


def test_load_missing_matrix_returns_empty(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "config" / "profiles").mkdir(parents=True)
    monkeypatch.setattr(policy, "_DEFAULT_REPO_ROOT", tmp_path)
    loaded = policy.load_code_list_policy("MISSING")
    assert loaded.entries == ()


def test_repo_root_walks_parents(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """When default root lacks profiles, walk parents from this module."""
    monkeypatch.setattr(policy, "_DEFAULT_REPO_ROOT", tmp_path / "no-profiles-here")
    root = policy._repo_root()
    assert (root / "config" / "profiles").is_dir()
    assert root != tmp_path / "no-profiles-here"


def test_skip_non_dict_entries(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    profiles = tmp_path / "config" / "profiles" / "semantic"
    profiles.mkdir(parents=True)
    matrix = profiles / "CA_ECCC.code-list-deviations.yaml"
    matrix.write_text(
        yaml.safe_dump(
            {
                "profile": "CA_ECCC",
                "entries": [
                    None,
                    "x",
                    {"id": "ok", "area": "ic", "token": "IC", "kind": "replace", "ca_uri": "c"},
                ],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(policy, "_DEFAULT_REPO_ROOT", tmp_path)
    loaded = policy.load_code_list_policy("CA_ECCC")
    assert len(loaded.entries) == 1
