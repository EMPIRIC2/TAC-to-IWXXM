"""CI logout fixture must stay a non-production stub. [Corpus: tests]"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import scripts.ci.check_e2e_logout_fixture as guard

REPO_ROOT = Path(__file__).resolve().parents[2]


def _write_fixture(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


@pytest.mark.unit
def test_unset_env_is_an_error(tmp_path: Path) -> None:
    assert guard.fixture_error("  ", tmp_path) == "E2E_LOGOUT_FIXTURE is unset"


@pytest.mark.unit
def test_missing_file_is_an_error(tmp_path: Path) -> None:
    assert (
        guard.fixture_error("missing.json", tmp_path)
        == "logout fixture file is missing"
    )
    assert (
        guard.fixture_error(str(tmp_path / "missing.json"), tmp_path)
        == "logout fixture file is missing"
    )


@pytest.mark.unit
def test_invalid_json_and_non_object(tmp_path: Path) -> None:
    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    listed = tmp_path / "list.json"
    _write_fixture(listed, ["not-an-object"])
    assert (
        guard.fixture_error(broken.name, tmp_path) == "logout fixture is not valid JSON"
    )
    assert (
        guard.fixture_error(listed.name, tmp_path)
        == "logout fixture must be a JSON object"
    )


@pytest.mark.unit
def test_rejects_non_stub_identity(tmp_path: Path) -> None:
    bad_email = tmp_path / "email.json"
    _write_fixture(bad_email, {"email": 1, "password": guard.FIXTURE_SENTINEL})
    wrong_domain = tmp_path / "domain.json"
    _write_fixture(
        wrong_domain,
        {"email": "person@example.com", "password": guard.FIXTURE_SENTINEL},
    )
    bad_secret = tmp_path / "secret.json"
    _write_fixture(
        bad_secret, {"email": "e2e.logout.ci@example.invalid", "password": 1}
    )
    wrong_secret = tmp_path / "wrong.json"
    _write_fixture(
        wrong_secret,
        {"email": "e2e.logout.ci@example.invalid", "password": "other-value"},
    )
    assert "example.invalid" in (guard.fixture_error(bad_email.name, tmp_path) or "")
    assert "example.invalid" in (guard.fixture_error(wrong_domain.name, tmp_path) or "")
    assert "sentinel" in (guard.fixture_error(bad_secret.name, tmp_path) or "")
    assert "sentinel" in (guard.fixture_error(wrong_secret.name, tmp_path) or "")


@pytest.mark.unit
def test_accepts_relative_and_absolute_stub(tmp_path: Path) -> None:
    payload = {
        "email": "e2e.logout.ci@example.invalid",
        "password": guard.FIXTURE_SENTINEL,
    }
    relative = tmp_path / "ci-logout.json"
    _write_fixture(relative, payload)
    assert guard.fixture_error(relative.name, tmp_path) is None
    assert guard.fixture_error(str(relative), tmp_path) is None


@pytest.mark.unit
def test_main_fails_without_printing_sentinel(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv("E2E_LOGOUT_FIXTURE", raising=False)
    assert guard.main(["prog", str(tmp_path)]) == 1
    captured = capsys.readouterr()
    assert "unset" in captured.err
    assert guard.FIXTURE_SENTINEL not in captured.err
    assert guard.FIXTURE_SENTINEL not in captured.out


@pytest.mark.unit
def test_main_reads_process_argv(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    fixture = tmp_path / "ci-logout.json"
    _write_fixture(
        fixture,
        {
            "email": "e2e.logout.ci@example.invalid",
            "password": guard.FIXTURE_SENTINEL,
        },
    )
    monkeypatch.setenv("E2E_LOGOUT_FIXTURE", fixture.name)
    monkeypatch.setattr(guard.sys, "argv", ["prog", str(tmp_path)])
    assert guard.main(None) == 0
    assert "ok" in capsys.readouterr().out


@pytest.mark.unit
def test_main_defaults_root_to_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    fixture = tmp_path / "ci-logout.json"
    _write_fixture(
        fixture,
        {
            "email": "e2e.logout.ci@example.invalid",
            "password": guard.FIXTURE_SENTINEL,
        },
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("E2E_LOGOUT_FIXTURE", fixture.name)
    assert guard.main(["prog"]) == 0
    assert "ok" in capsys.readouterr().out


@pytest.mark.unit
def test_repo_fixture_and_workflow_wiring(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("E2E_LOGOUT_FIXTURE", "apps/e2e/fixtures/ci-logout.json")
    assert guard.main(["prog", str(REPO_ROOT)]) == 0
    workflow = (REPO_ROOT / ".github" / "workflows" / "ci-cd.yml").read_text(
        encoding="utf-8"
    )
    assert workflow.count("E2E_LOGOUT_FIXTURE: apps/e2e/fixtures/ci-logout.json") == 2
    assert workflow.count("python3 scripts/ci/check_e2e_logout_fixture.py") == 2
    assert guard.FIXTURE_SENTINEL not in workflow
    assert "@example.invalid" not in workflow
