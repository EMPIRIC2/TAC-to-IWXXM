"""Coverage denominator audit script (EV quality tooling; [Corpus: tests])."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "ci" / "audit_coverage_denominator.py"


@pytest.fixture(scope="module")
def mod() -> ModuleType:
    spec = importlib.util.spec_from_file_location("audit_coverage_denominator", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


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


def test_workspace_members_lists_members_with_src(
    mod: ModuleType, tmp_path: Path
) -> None:
    _member(tmp_path)
    assert mod.workspace_members(tmp_path) == ["pkg"]


def test_run_audit_passes_when_all_files_measured(
    mod: ModuleType, tmp_path: Path
) -> None:
    _member(tmp_path)
    artifact = tmp_path / "cov.json"
    artifact.write_text(
        json.dumps(_report(["src/pkg/__init__.py", "src/pkg/a.py"])), encoding="utf-8"
    )
    audit = mod.run_audit([f"pkg={artifact}"], None, omits_only=False, root=tmp_path)
    assert audit.ok


def test_run_audit_fails_on_empty_report(mod: ModuleType, tmp_path: Path) -> None:
    _member(tmp_path)
    artifact = tmp_path / "cov.json"
    artifact.write_text(json.dumps(_report([], 0)), encoding="utf-8")
    audit = mod.run_audit([f"pkg={artifact}"], None, omits_only=False, root=tmp_path)
    assert not audit.ok
    assert "empty denominator" in audit.findings[0].message


def test_run_audit_fails_on_zero_statements(mod: ModuleType, tmp_path: Path) -> None:
    _member(tmp_path)
    artifact = tmp_path / "cov.json"
    artifact.write_text(json.dumps(_report(["src/pkg/a.py"], 0)), encoding="utf-8")
    audit = mod.run_audit([f"pkg={artifact}"], None, omits_only=False, root=tmp_path)
    assert "zero statements" in audit.findings[0].message


def test_run_audit_fails_on_missing_source_file(
    mod: ModuleType, tmp_path: Path
) -> None:
    _member(tmp_path)
    artifact = tmp_path / "cov.json"
    artifact.write_text(json.dumps(_report(["src/pkg/__init__.py"])), encoding="utf-8")
    audit = mod.run_audit([f"pkg={artifact}"], None, omits_only=False, root=tmp_path)
    assert any("src/pkg/a.py" in f.message for f in audit.findings)


def test_run_audit_known_gap_is_accepted(mod: ModuleType, tmp_path: Path) -> None:
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


def test_run_audit_fails_when_artifact_missing(mod: ModuleType, tmp_path: Path) -> None:
    _member(tmp_path)
    audit = mod.run_audit(
        [f"pkg={tmp_path / 'nope.json'}"], None, omits_only=False, root=tmp_path
    )
    assert "not found" in audit.findings[0].message


def test_run_audit_fails_when_member_has_no_artifact(
    mod: ModuleType, tmp_path: Path
) -> None:
    _member(tmp_path)
    audit = mod.run_audit([], None, omits_only=False, root=tmp_path)
    assert "no coverage artifact" in audit.findings[0].message


def test_omit_policy_rejects_hand_written_omit(mod: ModuleType, tmp_path: Path) -> None:
    _member(tmp_path, omit="src/pkg/a.py")
    audit = mod.run_audit([], None, omits_only=True, root=tmp_path)
    assert not audit.ok


def test_omit_policy_allows_generated_omit(mod: ModuleType, tmp_path: Path) -> None:
    _member(tmp_path, omit="*/iwxxm_xsd/v*/**")
    audit = mod.run_audit([], None, omits_only=True, root=tmp_path)
    assert audit.ok


def test_measured_files_handles_absolute_paths(mod: ModuleType, tmp_path: Path) -> None:
    member = _member(tmp_path)
    report = _report(
        [str((member / "src" / "pkg" / "a.py").resolve()), "/elsewhere/x.py"]
    )
    assert mod.measured_files(report, member) == {"src/pkg/a.py"}


def test_parse_artifact_rejects_bad_spec(mod: ModuleType) -> None:
    with pytest.raises(ValueError, match="MEMBER_DIR=JSON_PATH"):
        mod.parse_artifact("nonsense")


def test_main_exit_codes(
    mod: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
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
