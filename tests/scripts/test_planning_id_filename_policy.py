"""Policy tests for scripts/ci/check_test_file_naming.py.

Covers success, failure, validation edge cases, and mutation permutations.
[Corpus: tests]
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import scripts.ci.check_test_file_naming as policy

# ---------------------------------------------------------------------------
# Success — behavior-named paths pass
# ---------------------------------------------------------------------------

_SUCCESS_PATHS = (
    "packages/tac-validate/tests/test_rvr_trend_slash_accepted.py",
    "tests/unit/test_cors_policy.py",
    "apps/backend/tests/unit/test_health_endpoint.py",
    "packages/tac-validate/tests/test_catalog_rule_examples.py",
)


@pytest.mark.unit
@pytest.mark.parametrize("rel", _SUCCESS_PATHS)
def test_behavior_named_paths_pass_when_new(rel: str) -> None:
    verdict = policy.classify_path(rel, is_new=True)
    assert verdict.allowed is True
    assert verdict.reason == "behavior_named_or_unrelated"


# ---------------------------------------------------------------------------
# Failure — planning-id stems fail for new files
# ---------------------------------------------------------------------------

_FAILURE_PATHS = (
    "packages/tac-validate/tests/test_ev_foo.py",
    "packages/tac-validate/tests/test_tc_ev_bar.py",
    "tests/unit/test_m4_baz.py",
    "tests/unit/test_m10_qux.py",
    "apps/backend/tests/unit/test_ev040_catalog.py",
    "packages/x/tests/test_EV_UPPER.py",
)


@pytest.mark.unit
@pytest.mark.parametrize("rel", _FAILURE_PATHS)
def test_planning_id_stems_fail_when_new(rel: str) -> None:
    verdict = policy.classify_path(rel, is_new=True)
    assert verdict.allowed is False
    assert verdict.reason == "banned_planning_id_stem_on_new_file"


# ---------------------------------------------------------------------------
# Validation — edge cases (eval product, AHL fc_, m_prefix, migration)
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize(
    ("rel", "is_new", "expect_allowed", "reason_substr"),
    [
        (
            "apps/backend/tests/evaluation/test_evaluation_endpoints.py",
            True,
            True,
            "behavior",
        ),
        (
            "apps/backend/tests/evaluation/test_evaluation_mode_single.py",
            True,
            True,
            "behavior",
        ),
        (
            "packages/tac2iwxxm/tests/fixtures/ahl/fc_taf_with_body.txt",
            True,
            True,
            "ahl_fc",
        ),
        (
            "packages/tac2iwxxm/tests/fixtures/ahl/fc_taf_short.txt",
            True,
            True,
            "ahl_fc",
        ),
        (
            "fixtures/visibility/metar_low_m_prefix_sample.txt",
            True,
            True,
            "non_python",
        ),
        (
            "tests/migration/test_m4_auth_layout.py",
            False,
            True,
            "historical",
        ),
        (
            "tests/migration/test_m10_ci_monorepo_paths.py",
            False,
            True,
            "historical",
        ),
        (
            "tests/migration/test_m4_auth_layout.py",
            True,
            False,
            "banned",
        ),
        (
            "tests/unit/test_m4_auth_layout.py",
            True,
            False,
            "banned",
        ),
        (
            "packages/tac-validate/tests/test_every_catalog_item.py",
            True,
            True,
            "behavior",
        ),
        (
            "docs/notes/readme.md",
            True,
            True,
            "non_python",
        ),
    ],
)
def test_validation_edge_cases(
    rel: str,
    is_new: bool,
    expect_allowed: bool,
    reason_substr: str,
) -> None:
    verdict = policy.classify_path(rel, is_new=is_new)
    assert verdict.allowed is expect_allowed
    assert reason_substr in verdict.reason


@pytest.mark.unit
def test_historical_allowlist_overrides_new_flag() -> None:
    path = "tests/migration/test_m3_gifts_layout.py"
    verdict = policy.classify_path(
        path,
        is_new=True,
        historical_allowlist={path},
    )
    assert verdict.allowed is True
    assert verdict.reason == "historical_allowlist"


# ---------------------------------------------------------------------------
# Mutation / combinatorial — prefix x extension x directory x allowlist
# ---------------------------------------------------------------------------

_PREFIXES = (
    ("test_rvr_trend_slash_accepted", False),
    ("test_ev_foo", True),
    ("test_ev040_catalog", True),
    ("test_tc_ev_bar", True),
    ("test_tc_f15_example", False),
    ("test_m4_baz", True),
    ("test_m10_qux", True),
    ("test_evaluation_job", False),
    ("test_every_item", False),
    ("test_m_prefix_visibility", False),
    ("fc_taf_body", False),
    ("metar_low_m_prefix", False),
)

_EXTENSIONS = (".py", ".txt", ".md", ".tac")

_DIRECTORIES = (
    "packages/tac-validate/tests",
    "tests/unit",
    "tests/migration",
    "apps/backend/tests/unit",
    "packages/tac2iwxxm/tests/fixtures/ahl",
)


@pytest.mark.unit
@pytest.mark.parametrize(("stem", "banned_if_py"), _PREFIXES)
@pytest.mark.parametrize("ext", _EXTENSIONS)
@pytest.mark.parametrize("directory", _DIRECTORIES)
@pytest.mark.parametrize("on_allowlist", [False, True])
def test_mutation_prefix_ext_dir_allowlist(
    stem: str,
    banned_if_py: bool,
    ext: str,
    directory: str,
    on_allowlist: bool,
) -> None:
    rel = f"{directory}/{stem}{ext}"
    allow = {rel} if on_allowlist else set()
    verdict = policy.classify_path(rel, is_new=True, historical_allowlist=allow)

    if policy.is_ahl_fc_fixture(rel):
        assert verdict.allowed is True
        return

    if ext != ".py":
        assert verdict.allowed is True
        return

    if banned_if_py and on_allowlist:
        assert verdict.allowed is True
        assert verdict.reason == "historical_allowlist"
        return

    if banned_if_py:
        assert verdict.allowed is False
        return

    assert verdict.allowed is True


@pytest.mark.unit
@pytest.mark.parametrize(
    "stem",
    [
        "test_ev",
        "test_ev_",
        "test_ev1",
        "TEST_EV_FOO",
        "test_tc_ev",
        "test_tc_ev999_001",
        "test_m1_x",
        "test_m99_detector",
    ],
)
def test_matches_banned_planning_stem_true(stem: str) -> None:
    assert policy.matches_banned_planning_stem(stem) is True


@pytest.mark.unit
@pytest.mark.parametrize(
    "stem",
    [
        "test_evaluation",
        "test_every",
        "test_event_log",
        "test_m_prefix",
        "test_tc_f15",
        "test_rvr_trend",
        "fc_taf_short",
    ],
)
def test_matches_banned_planning_stem_false(stem: str) -> None:
    assert policy.matches_banned_planning_stem(stem) is False


# ---------------------------------------------------------------------------
# findings_for_new_paths + CLI main
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_findings_for_new_paths_reports_only_failures() -> None:
    paths = [
        "tests/unit/test_rvr_trend_slash_accepted.py",
        "tests/unit/test_ev_foo.py",
        "fixtures/ahl/fc_taf_short.txt",
    ]
    failed = policy.findings_for_new_paths(paths)
    assert [item.path for item in failed] == ["tests/unit/test_ev_foo.py"]


@pytest.mark.unit
def test_main_ok_with_explicit_good_paths(tmp_path: Path) -> None:
    code = policy.main(
        [
            "prog",
            str(tmp_path),
            "--path",
            "tests/unit/test_rvr_trend_slash_accepted.py",
            "--path",
            "fixtures/ahl/fc_taf_short.txt",
        ]
    )
    assert code == 0


@pytest.mark.unit
def test_main_fails_with_explicit_banned_path(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = policy.main(
        [
            "prog",
            str(tmp_path),
            "--path",
            "tests/unit/test_ev_foo.py",
        ]
    )
    assert code == 1
    err = capsys.readouterr().err
    assert "FAIL:" in err
    assert "test_ev_foo.py" in err


@pytest.mark.unit
def test_main_ok_on_real_repo_against_stage() -> None:
    """Smoke: this branch must not introduce banned new stems vs origin/stage."""
    assert policy.main(["prog", "--base", "origin/stage"]) == 0


@pytest.mark.unit
def test_list_new_paths_sees_added_file(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "ci@example.invalid"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "ci"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    (repo / "keep.txt").write_text("a\n", encoding="utf-8")
    subprocess.run(
        ["git", "add", "keep.txt"], cwd=repo, check=True, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "base"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    base = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo, text=True
    ).strip()
    bad = repo / "tests"
    bad.mkdir()
    (bad / "test_ev_new.py").write_text("pass\n", encoding="utf-8")
    subprocess.run(
        ["git", "add", "tests/test_ev_new.py"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "add banned"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    new_paths = policy.list_new_paths(repo, base)
    assert "tests/test_ev_new.py" in new_paths
    assert policy.main(["prog", str(repo), "--base", base]) == 1
