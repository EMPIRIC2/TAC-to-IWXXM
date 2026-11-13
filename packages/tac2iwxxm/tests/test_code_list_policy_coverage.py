"""Coverage battery for tac2iwxxm code_list_policy edge paths (#1034)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tac2iwxxm import code_list_policy as policy


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    policy._entries.cache_clear()
    yield
    policy._entries.cache_clear()


@pytest.mark.parametrize(
    ("mode", "payload", "expect_none"),
    [
        (
            "success",
            {
                "entries": [
                    {
                        "area": "ic",
                        "token": "IC",
                        "kind": "replace",
                        "ca_uri": "https://ca.example/IC",
                    }
                ]
            },
            False,
        ),
        ("failure", "bad", True),
        ("validation", {"entries": "bad"}, True),
    ],
)
def test_resolve_national_href_modes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mode: str,
    payload: object,
    expect_none: bool,
) -> None:
    del mode
    matrix = tmp_path / "CA_ECCC.code-list-deviations.yaml"
    matrix.write_text(yaml.safe_dump(payload), encoding="utf-8")
    monkeypatch.setattr(policy, "_DEFAULT_REPO_ROOT", tmp_path)
    monkeypatch.setattr(policy, "_MATRIX", "CA_ECCC.code-list-deviations.yaml")
    (tmp_path / "config" / "profiles").mkdir(parents=True, exist_ok=True)
    got = policy.resolve_national_href(area="ic", token="IC")
    if expect_none:
        assert got is None
    else:
        assert got == "https://ca.example/IC"
        assert policy.resolve_national_href(area="ic", token="NOPE") is None


def test_missing_matrix_and_non_dict_entries(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(policy, "_DEFAULT_REPO_ROOT", tmp_path)
    monkeypatch.setattr(policy, "_MATRIX", "missing.yaml")
    (tmp_path / "config" / "profiles").mkdir(parents=True, exist_ok=True)
    assert policy.resolve_national_href(area="ic", token="IC") is None
    policy._entries.cache_clear()
    matrix = tmp_path / "CA_ECCC.code-list-deviations.yaml"
    matrix.write_text(
        yaml.safe_dump({"entries": [1, {"area": "ic", "token": "IC", "kind": "none"}]}),
        encoding="utf-8",
    )
    monkeypatch.setattr(policy, "_MATRIX", "CA_ECCC.code-list-deviations.yaml")
    assert policy.resolve_national_href(area="ic", token="IC") is None


def test_repo_root_walk(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(policy, "_DEFAULT_REPO_ROOT", tmp_path / "no-profiles-here")
    root = policy._repo_root()
    assert (root / "config" / "profiles").is_dir()


def test_repo_root_fallback_candidate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Cover final return when no parent tree has config/profiles."""
    monkeypatch.setattr(policy, "_DEFAULT_REPO_ROOT", tmp_path / "fallback")

    class _Leaf:
        def resolve(self) -> _Leaf:
            return self

        @property
        def parents(self) -> tuple[Path, ...]:
            return (tmp_path / "alone",)

    real_path_ctor = policy.Path

    def _factory(*args, **kwargs):  # type: ignore[no-untyped-def]
        if args:
            return _Leaf()
        return real_path_ctor(*args, **kwargs)

    monkeypatch.setattr(policy, "Path", _factory)
    assert policy._repo_root() == tmp_path / "fallback"
