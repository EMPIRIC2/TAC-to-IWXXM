"""Coverage for scripts/ci/check_pnpm_action_package_manager.py (EV-096 / #1096)."""

from __future__ import annotations

from pathlib import Path

import pytest
import scripts.ci.check_pnpm_action_package_manager as guard


def _write_pkg(root: Path, *, package_manager: str | None) -> None:
    if package_manager is None:
        root.joinpath("package.json").write_text("{}\n", encoding="utf-8")
    else:
        root.joinpath("package.json").write_text(
            '{\n  "packageManager": "' + package_manager + '"\n}\n',
            encoding="utf-8",
        )


def _write_workflow(root: Path, name: str, body: str) -> None:
    wf = root / ".github" / "workflows"
    wf.mkdir(parents=True, exist_ok=True)
    (wf / name).write_text(body, encoding="utf-8")


@pytest.mark.unit
def test_ok_when_action_setup_without_version(tmp_path: Path) -> None:
    fake = tmp_path / "repo"
    fake.mkdir()
    _write_pkg(fake, package_manager="pnpm@9.15.4")
    _write_workflow(
        fake,
        "mutation.yml",
        "jobs:\n  j:\n    steps:\n      - uses: pnpm/action-setup@v4\n"
        "      - uses: actions/setup-node@v5\n        with:\n          node-version: '22'\n",
    )
    assert guard.find_dual_specs(fake) == []
    assert guard.main(["prog", str(fake)]) == 0


@pytest.mark.unit
def test_ok_when_later_step_has_version(tmp_path: Path) -> None:
    """Next-step with.version must not count as pnpm dual-spec (PR #1114 review)."""
    fake = tmp_path / "repo"
    fake.mkdir()
    _write_pkg(fake, package_manager="pnpm@9.15.4")
    _write_workflow(
        fake,
        "x.yml",
        "jobs:\n  j:\n    steps:\n      - uses: pnpm/action-setup@v4\n"
        "      - uses: supabase/setup-cli@v1\n        with:\n          version: 2.0.0\n",
    )
    assert guard.find_dual_specs(fake) == []
    assert guard.main(["prog", str(fake)]) == 0


@pytest.mark.unit
def test_fails_when_version_and_package_manager(tmp_path: Path) -> None:
    fake = tmp_path / "repo"
    fake.mkdir()
    _write_pkg(fake, package_manager="pnpm@9.15.4")
    _write_workflow(
        fake,
        "mutation.yml",
        "jobs:\n  j:\n    steps:\n      - name: Install pnpm\n"
        "        uses: pnpm/action-setup@v4\n"
        "        with:\n          version: 9\n",
    )
    hits = guard.find_dual_specs(fake)
    assert len(hits) == 1
    assert "mutation.yml" in hits[0]
    assert guard.main(["prog", str(fake)]) == 1


@pytest.mark.unit
def test_skips_when_no_package_manager(tmp_path: Path) -> None:
    fake = tmp_path / "repo"
    fake.mkdir()
    _write_pkg(fake, package_manager=None)
    _write_workflow(
        fake,
        "x.yml",
        "jobs:\n  j:\n    steps:\n      - uses: pnpm/action-setup@v4\n"
        "        with:\n          version: 9\n",
    )
    assert guard.find_dual_specs(fake) == []


@pytest.mark.unit
def test_ok_on_real_repo_root() -> None:
    """Tip should already use packageManager-only for pnpm/action-setup."""
    root = Path(__file__).resolve().parents[2]
    assert guard.main(["prog", str(root)]) == 0


@pytest.mark.unit
def test_no_package_json_file(tmp_path: Path) -> None:
    fake = tmp_path / "repo"
    fake.mkdir()
    assert guard.find_dual_specs(fake) == []


@pytest.mark.unit
def test_no_workflows_dir(tmp_path: Path) -> None:
    fake = tmp_path / "repo"
    fake.mkdir()
    _write_pkg(fake, package_manager="pnpm@9.15.4")
    assert guard.find_dual_specs(fake) == []


@pytest.mark.unit
def test_main_default_argv_uses_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = tmp_path / "repo"
    fake.mkdir()
    _write_pkg(fake, package_manager="pnpm@9.15.4")
    monkeypatch.chdir(fake)
    assert guard.main(["prog"]) == 0


@pytest.mark.unit
def test_module_as_main(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import runpy
    import sys

    fake = tmp_path / "repo"
    fake.mkdir()
    _write_pkg(fake, package_manager="pnpm@9.15.4")
    monkeypatch.setattr(
        sys, "argv", ["check_pnpm_action_package_manager.py", str(fake)]
    )
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(
            str(
                Path(__file__).resolve().parents[2]
                / "scripts"
                / "ci"
                / "check_pnpm_action_package_manager.py"
            ),
            run_name="__main__",
        )
    assert exc.value.code == 0
