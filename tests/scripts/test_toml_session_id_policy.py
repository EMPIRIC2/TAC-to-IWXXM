"""Mandatory evolve-auto matrix for TOML session-id ban.

Gates tracked ``*.toml`` files against ``S###`` planning/session ids.
[Corpus: tests]
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import scripts.ci.check_toml_session_ids as policy

REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# S — Success: clean TOML text / tracked scan
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_clean_toml_text_has_no_hits() -> None:
    """S / Read happy path — plain description accepted."""
    hits = policy.scan_toml_text(
        "demo.toml",
        'description = "PyO3 native core for iwxxm-validate"\n',
    )
    assert hits == ()


@pytest.mark.unit
def test_tracked_tomls_scan_succeeds() -> None:
    """S / repo gate — every tracked TOML is free of S### tokens."""
    result = policy.scan_tracked_tomls(REPO_ROOT)
    assert result.ok, [f"{h.path}:{h.line}:{h.token}" for h in result.hits]


# ---------------------------------------------------------------------------
# F — Failure: banned tokens rejected
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize(
    "snippet",
    [
        "# S008 F6 members listed below.\n",
        'description = "core (D-S014-T33-crates)"\n',
        "note = 'legacy S000 bootstrap'\n",
        "authors = ['S057 follow-on']\n",
    ],
)
def test_session_ids_in_toml_fail(snippet: str) -> None:
    """F / rejected op — S### tokens produce hits."""
    hits = policy.scan_toml_text("bad.toml", snippet)
    assert hits
    assert all(policy.SESSION_ID_RE.fullmatch(h.token) for h in hits)


# ---------------------------------------------------------------------------
# V+ / V- — Validation of token finder
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("plain workspace members", ()),
        ("S08 too short", ()),
        ("S008 exact", ("S008",)),
        ("S000 and S023 together", ("S000", "S023")),
        ("D-S014-T33 compound", ("S014",)),
        ("feature F13 stays", ()),
    ],
)
def test_find_session_ids_validation(text: str, expected: tuple[str, ...]) -> None:
    """V+ / V- — finder accepts clean text and extracts banned tokens."""
    assert policy.find_session_ids(text) == expected


# ---------------------------------------------------------------------------
# M — Mutation permutations (create / update / delete of banned tokens)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_mutation_create_banned_token_then_delete() -> None:
    """M / Create+validation fail then Delete+allowed."""
    created = 'description = "iwxxm-validate (S011 crates)"\n'
    create_hits = policy.scan_toml_text("mut.toml", created)
    assert create_hits
    assert create_hits[0].token == "S011"

    cleaned = created.replace("S011 ", "")
    delete_hits = policy.scan_toml_text("mut.toml", cleaned)
    assert delete_hits == ()


@pytest.mark.unit
def test_mutation_update_replaces_banned_with_plain_language() -> None:
    """M / Update+validation pass — rewrite removes S###."""
    before = "# S008 F6 members: tac2iwxxm\n"
    assert policy.scan_toml_text("u.toml", before)

    after = "# Workspace F6 members: tac2iwxxm\n"
    assert policy.scan_toml_text("u.toml", after) == ()


@pytest.mark.unit
def test_mutation_update_that_keeps_token_still_fails() -> None:
    """M / Update+validation fail — superficial edit leaves S###."""
    before = 'description = "core (D-S014-T33)"\n'
    after = 'description = "updated core (D-S014-T33)"\n'
    assert policy.scan_toml_text("u.toml", before)
    assert policy.scan_toml_text("u.toml", after)


@pytest.mark.unit
def test_mutation_create_clean_toml_passes() -> None:
    """M / Create+validation pass — new plain-language TOML has no hits."""
    created = 'description = "native IWXXM validation crate"\n'
    assert policy.scan_toml_text("new.toml", created) == ()


# ---------------------------------------------------------------------------
# CLI — main() exit codes (CI gate surface)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_main_ok_on_real_repo(capsys: pytest.CaptureFixture[str]) -> None:
    """S / Read happy path — CLI exits 0 on current checkout."""
    assert policy.main(["--root", str(REPO_ROOT)]) == 0
    assert "ok:" in capsys.readouterr().out


@pytest.mark.unit
def test_main_fails_when_tracked_toml_has_session_id(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """F / CLI rejection — exit 1 and print banned token locus."""
    repo = tmp_path / "repo"
    repo.mkdir()
    bad = repo / "bad.toml"
    bad.write_text('# S008 leftover\nname = "x"\n', encoding="utf-8")
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "add", "bad.toml"], cwd=repo, check=True, capture_output=True
    )

    assert policy.main(["--root", str(repo)]) == 1
    out = capsys.readouterr().out
    assert "S008" in out
    assert "bad.toml" in out


@pytest.mark.unit
def test_mutation_delete_partial_leaving_token_still_fails() -> None:
    """M / Delete+rejected — removing sibling text leaves banned token."""
    before = "# S008 F6 members: tac2iwxxm, tac-validate\n"
    partial = "# S008 members\n"
    assert policy.scan_toml_text("d.toml", before)
    assert policy.scan_toml_text("d.toml", partial)


@pytest.mark.unit
def test_main_ok_on_empty_tracked_toml_repo(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """S / Read happy path — empty git repo with no TOML exits 0."""
    repo = tmp_path / "empty"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    assert policy.main(["--root", str(repo)]) == 0
    assert "ok:" in capsys.readouterr().out