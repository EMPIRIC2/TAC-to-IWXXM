"""Coverage denominator audit script (EV quality tooling; [Corpus: tests])."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from scripts.ci import audit_coverage_denominator as mod

ROOT = Path(__file__).resolve().parents[2]


def _member(root: Path, omit: str = "") -> Path:
    member = root / "pkg"
    (member / "src" / "pkg").mkdir(parents=True)
    (member / "src" / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (member / "src" / "pkg" / "a.py").write_text("x = 1\n", encoding="utf-8")
    omit_line = f'omit = ["{omit}"]\n' if omit else ""
    (member / "pyproject.toml").write_text(
        f'[tool.coverage.run]\nsource = ["src/pkg"]\n{omit_line}',
        encoding="utf-8",
    )
    (root / "pyproject.toml").write_text(
        '[tool.uv.workspace]\nmembers = ["pkg"]\n',
        encoding="utf-8",
    )
    return member


def _report(files: list[str], statements: int = 1) -> dict[str, object]:
    return {"files": {f: {} for f in files}, "totals": {"num_statements": statements}}


def test_workspace_members_lists_members_with_src(tmp_path: Path) -> None:
    _member(tmp_path)
    assert mod.workspace_members(tmp_path) == ["pkg"]


def test_run_audit_passes_when_all_files_measured(tmp_path: Path) -> None:
    _member(tmp_path)
    artifact = tmp_path / "cov.json"
    artifact.write_text(
        json.dumps(_report(["src/pkg/__init__.py", "src/pkg/a.py"])), encoding="utf-8"
    )
    audit = mod.run_audit([f"pkg={artifact}"], None, omits_only=False, root=tmp_path)
    assert audit.ok


def test_run_audit_fails_on_empty_report(tmp_path: Path) -> None:
    _member(tmp_path)
    artifact = tmp_path / "cov.json"
    artifact.write_text(json.dumps(_report([], 0)), encoding="utf-8")
    audit = mod.run_audit([f"pkg={artifact}"], None, omits_only=False, root=tmp_path)
    assert not audit.ok
    assert "empty denominator" in audit.findings[0].message


def test_run_audit_fails_on_zero_statements(tmp_path: Path) -> None:
    _member(tmp_path)
    artifact = tmp_path / "cov.json"
    artifact.write_text(json.dumps(_report(["src/pkg/a.py"], 0)), encoding="utf-8")
    audit = mod.run_audit([f"pkg={artifact}"], None, omits_only=False, root=tmp_path)
    assert "zero statements" in audit.findings[0].message


def test_run_audit_fails_on_missing_source_file(tmp_path: Path) -> None:
    _member(tmp_path)
    artifact = tmp_path / "cov.json"
    artifact.write_text(json.dumps(_report(["src/pkg/__init__.py"])), encoding="utf-8")
    audit = mod.run_audit([f"pkg={artifact}"], None, omits_only=False, root=tmp_path)
    assert any("src/pkg/a.py" in f.message for f in audit.findings)


def test_run_audit_known_gap_is_accepted(tmp_path: Path) -> None:
    _member(tmp_path)
    artifact = tmp_path / "cov.json"
    artifact.write_text(json.dumps(_report(["src/pkg/__init__.py"])), encoding="utf-8")
    audit = mod.run_audit(
        [f"pkg={artifact}"],
        None,
        omits_only=False,
        known_gaps=frozenset({"pkg/src/pkg/a.py"}),
        root=tmp_path,
    )
    assert audit.ok


def test_run_audit_fails_when_artifact_missing(tmp_path: Path) -> None:
    _member(tmp_path)
    audit = mod.run_audit(
        [f"pkg={tmp_path / 'nope.json'}"], None, omits_only=False, root=tmp_path
    )
    assert "not found" in audit.findings[0].message


def test_run_audit_fails_when_member_has_no_artifact(tmp_path: Path) -> None:
    _member(tmp_path)
    audit = mod.run_audit([], None, omits_only=False, root=tmp_path)
    assert "no coverage artifact" in audit.findings[0].message


def test_omit_policy_rejects_hand_written_omit(tmp_path: Path) -> None:
    _member(tmp_path, omit="src/pkg/a.py")
    audit = mod.run_audit([], None, omits_only=True, root=tmp_path)
    assert not audit.ok


def test_omit_policy_allows_generated_omit(tmp_path: Path) -> None:
    _member(tmp_path, omit="*/iwxxm_xsd/v*/**")
    audit = mod.run_audit([], None, omits_only=True, root=tmp_path)
    assert audit.ok


def test_measured_files_handles_absolute_paths(tmp_path: Path) -> None:
    member = _member(tmp_path)
    report = _report(
        [str((member / "src" / "pkg" / "a.py").resolve()), "/elsewhere/x.py"]
    )
    assert mod.measured_files(report, member) == {"src/pkg/a.py"}


def test_parse_artifact_rejects_bad_spec() -> None:
    with pytest.raises(ValueError, match="MEMBER_DIR=JSON_PATH"):
        mod.parse_artifact("nonsense")


def test_main_exit_codes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert mod.main(["--omits-only"]) == 0
    assert mod.main(["--artifact", "bad"]) == 2
    assert "error:" in capsys.readouterr().err
    assert (
        mod.main(
            [
                "--member",
                "apps/backend",
                "--artifact",
                f"apps/backend={tmp_path / 'x.json'}",
            ]
        )
        == 1
    )
    with pytest.raises(SystemExit):
        mod.main([])


def test_source_dirs_honors_source_pkgs(tmp_path: Path) -> None:
    member = tmp_path / "pkg"
    (member / "src" / "pkg").mkdir(parents=True)
    (member / "src" / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (member / "pyproject.toml").write_text(
        '[tool.coverage.run]\nsource_pkgs = ["pkg"]\n',
        encoding="utf-8",
    )
    toml = mod.load_toml(member / "pyproject.toml")
    dirs = mod.source_dirs(member, toml)
    assert any(d.name == "pkg" for d in dirs)


def test_expected_files_skips_pycache_and_omit(tmp_path: Path) -> None:
    member = _member(tmp_path, omit="src/pkg/a.py")
    cache = member / "src" / "pkg" / "__pycache__"
    cache.mkdir(exist_ok=True)
    (cache / "ghost.py").write_text("x = 1\n", encoding="utf-8")
    egg = member / "src" / "pkg.egg-info"
    egg.mkdir(exist_ok=True)
    (egg / "x.py").write_text("x = 1\n", encoding="utf-8")
    toml = mod.load_toml(member / "pyproject.toml")
    files = mod.expected_files(member, toml)
    assert "src/pkg/a.py" not in files
    assert "src/pkg/__init__.py" in files
    assert not any("__pycache__" in f for f in files)
    assert not any(".egg-info" in f for f in files)


def test_audit_main_entrypoint_omits_only(monkeypatch: pytest.MonkeyPatch) -> None:
    """Execute the ``__main__`` guard for scripts coverage."""
    import runpy

    path = Path(mod.__file__).resolve()
    monkeypatch.setattr("sys.argv", [str(path), "--omits-only"])
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(str(path), run_name="__main__")
    assert exc.value.code == 0
