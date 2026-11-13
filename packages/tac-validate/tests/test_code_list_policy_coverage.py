"""Coverage battery for tac_validate.code_list_policy (#1034)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from tac_validate import code_list_policy as policy


@pytest.fixture(autouse=True)
def _clear_cache() -> None:
    policy.national_replace_tokens.cache_clear()
    yield
    policy.national_replace_tokens.cache_clear()


@pytest.mark.parametrize(
    ("mode", "payload", "expect_empty"),
    [
        (
            "success",
            {
                "entries": [
                    {"kind": "replace", "token": "IC"},
                    {"kind": "extend", "token": "GFA"},
                    {"kind": "replace", "token": "*"},
                    1,
                ]
            },
            False,
        ),
        ("failure", "bad", True),
        ("validation", {"entries": "bad"}, True),
    ],
)
def test_national_replace_tokens_modes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mode: str,
    payload: object,
    expect_empty: bool,
) -> None:
    del mode
    matrix = tmp_path / "CA_ECCC.code-list-deviations.yaml"
    matrix.write_text(yaml.safe_dump(payload), encoding="utf-8")
    monkeypatch.setattr(policy, "_DEFAULT_REPO_ROOT", tmp_path)
    monkeypatch.setattr(policy, "_MATRIX", "CA_ECCC.code-list-deviations.yaml")
    (tmp_path / "config" / "profiles").mkdir(parents=True, exist_ok=True)
    tokens = policy.national_replace_tokens()
    if expect_empty:
        assert tokens == frozenset()
    else:
        assert "IC" in tokens
        assert "GFA" not in tokens
        assert "*" not in tokens


def test_missing_matrix_and_repo_walk(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(policy, "_DEFAULT_REPO_ROOT", tmp_path / "missing")
    root = policy._repo_root()
    assert (root / "config" / "profiles").is_dir()
    monkeypatch.setattr(policy, "_DEFAULT_REPO_ROOT", tmp_path)
    monkeypatch.setattr(policy, "_MATRIX", "nope.yaml")
    (tmp_path / "config" / "profiles").mkdir(parents=True, exist_ok=True)
    assert policy.national_replace_tokens() == frozenset()


def test_repo_root_fallback_candidate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
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


def test_check_global_only_tokens_dedupes() -> None:
    issues = policy.check_global_only_tokens(
        ["IC", "ic", "NOPE"],
        profile="ca_eccc",
        product="METAR",
    )
    assert len([i for i in issues if i.code == "CA_CODE_LIST_NATIONAL_REQUIRED"]) == 1
