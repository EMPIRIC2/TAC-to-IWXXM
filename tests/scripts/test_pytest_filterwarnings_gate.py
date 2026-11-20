"""Combinatorial gate for pytest filterwarnings=error policy.

Covers success / mutation / failure / validation permutations for
``scripts/ci/check_pytest_filterwarnings.py``.

[Corpus: tech-spec] [Corpus: tests]
"""

from __future__ import annotations

import runpy
import subprocess
import sys
from pathlib import Path

import pytest
from scripts.ci import check_pytest_filterwarnings as gate

_MINIMAL_PROJECT = """
[project]
name = "sample"
version = "0.0.1"
requires-python = ">=3.12"
"""


def _write_pkg(
    root: Path,
    *,
    name: str,
    kind: str = "packages",
    with_tests: bool = True,
    pytest_block: str | None = None,
) -> Path:
    member = root / kind / name
    member.mkdir(parents=True)
    body = _MINIMAL_PROJECT
    if pytest_block is not None:
        body += "\n" + pytest_block
    (member / "pyproject.toml").write_text(body, encoding="utf-8")
    if with_tests:
        tests = member / "tests"
        tests.mkdir()
        (tests / "test_noop.py").write_text(
            "def test_ok():\n    assert True\n", encoding="utf-8"
        )
    return member / "pyproject.toml"


def _root_pyproject(root: Path, pytest_block: str) -> Path:
    path = root / "pyproject.toml"
    path.write_text(_MINIMAL_PROJECT + "\n" + pytest_block, encoding="utf-8")
    (root / "tests").mkdir(exist_ok=True)
    return path


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """Isolated mini-repo with apps/ and packages/."""
    (tmp_path / "apps").mkdir()
    (tmp_path / "packages").mkdir()
    return tmp_path


class TestSuccessPaths:
    """Happy-path audits."""

    def test_clean_tree_with_error_everywhere_passes(self, repo: Path) -> None:
        block = '[tool.pytest.ini_options]\nfilterwarnings = [\n  "error",\n]\n'
        _root_pyproject(repo, block)
        _write_pkg(repo, name="auth", pytest_block=block)
        _write_pkg(repo, name="backend", kind="apps", pytest_block=block)
        assert gate.audit_tree(repo) == []
        assert gate.main(["--root", str(repo)]) == 0

    def test_member_without_tests_and_without_pytest_section_is_skipped(
        self, repo: Path
    ) -> None:
        block = '[tool.pytest.ini_options]\nfilterwarnings = [\n  "error",\n]\n'
        _root_pyproject(repo, block)
        _write_pkg(repo, name="leaf", with_tests=False, pytest_block=None)
        assert gate.audit_tree(repo) == []


class TestMutationModes:
    """Create / update / delete of filterwarnings config."""

    def test_create_pytest_section_with_error_passes_validation(
        self, repo: Path
    ) -> None:
        block = '[tool.pytest.ini_options]\nfilterwarnings = [\n  "error",\n]\n'
        _root_pyproject(repo, block)
        path = _write_pkg(repo, name="shared", pytest_block=None)
        # create
        path.write_text(_MINIMAL_PROJECT + "\n" + block, encoding="utf-8")
        assert gate.audit_pyproject(path, root=repo) == []

    def test_update_replacing_ignore_with_error_passes(self, repo: Path) -> None:
        bad = (
            "[tool.pytest.ini_options]\n"
            'filterwarnings = [\n  "error",\n  "ignore:noise:DeprecationWarning",\n]\n'
        )
        good = '[tool.pytest.ini_options]\nfilterwarnings = [\n  "error",\n]\n'
        _root_pyproject(repo, good)
        path = _write_pkg(repo, name="tac-decoding", pytest_block=bad)
        assert any(
            f.code == "forbidden_ignore" for f in gate.audit_pyproject(path, root=repo)
        )
        # update
        path.write_text(_MINIMAL_PROJECT + "\n" + good, encoding="utf-8")
        assert gate.audit_pyproject(path, root=repo) == []

    def test_delete_filterwarnings_fails_audit(self, repo: Path) -> None:
        good = '[tool.pytest.ini_options]\nfilterwarnings = [\n  "error",\n]\n'
        stripped = '[tool.pytest.ini_options]\ntestpaths = ["tests"]\n'
        _root_pyproject(repo, good)
        path = _write_pkg(repo, name="workflows", pytest_block=good)
        # delete key
        path.write_text(_MINIMAL_PROJECT + "\n" + stripped, encoding="utf-8")
        codes = {f.code for f in gate.audit_pyproject(path, root=repo)}
        assert "missing_filterwarnings" in codes


class TestFailureModes:
    """Rejected configs and CLI failure."""

    def test_missing_pytest_section_on_pack_with_tests_fails(self, repo: Path) -> None:
        block = '[tool.pytest.ini_options]\nfilterwarnings = [\n  "error",\n]\n'
        _root_pyproject(repo, block)
        path = _write_pkg(repo, name="reference-lookup", pytest_block=None)
        findings = gate.audit_pyproject(path, root=repo)
        assert findings
        assert findings[0].code == "missing_pytest_section"
        assert gate.main(["--root", str(repo)]) == 1

    def test_filterwarnings_without_error_fails(self, repo: Path) -> None:
        block = '[tool.pytest.ini_options]\nfilterwarnings = [\n  "default",\n]\n'
        _root_pyproject(repo, block)
        findings = gate.audit_tree(repo)
        assert any(f.code == "missing_error" for f in findings)

    def test_intentional_runtime_warning_fails_pytest_subprocess(
        self, tmp_path: Path
    ) -> None:
        """Prove filterwarnings=error turns a warning into a test failure."""
        test_file = tmp_path / "test_warns.py"
        test_file.write_text(
            "import warnings\n"
            "def test_emits_warning():\n"
            "    warnings.warn('intentional', UserWarning)\n",
            encoding="utf-8",
        )
        conf = tmp_path / "pytest.ini"
        conf.write_text("[pytest]\nfilterwarnings =\n    error\n", encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_file), "-q", "-c", str(conf)],
            check=False,
            capture_output=True,
            text=True,
            cwd=tmp_path,
        )
        assert proc.returncode != 0
        assert "UserWarning" in proc.stdout + proc.stderr or "Warnings as errors" in (
            proc.stdout + proc.stderr
        )


class TestValidationModes:
    """Schema / policy validation success and failure."""

    def test_validation_success_error_only_list(self) -> None:
        text = '[tool.pytest.ini_options]\nfilterwarnings = [\n  "error",\n]\n'
        assert gate.parse_filterwarnings(text) == ["error"]

    def test_validation_failure_ignore_entry_rejected(self, repo: Path) -> None:
        block = (
            "[tool.pytest.ini_options]\n"
            'filterwarnings = [\n  "error",\n'
            "  \"ignore:'crypt' is deprecated:DeprecationWarning:passlib.utils\",\n]\n"
        )
        path = _root_pyproject(repo, block)
        codes = {f.code for f in gate.audit_pyproject(path, root=repo)}
        assert "forbidden_ignore" in codes

    def test_validation_success_live_repo_candidates_include_apps_packages(
        self,
    ) -> None:
        paths = gate.iter_candidate_pyprojects(gate.ROOT)
        rels = {str(p.relative_to(gate.ROOT)) for p in paths}
        assert "pyproject.toml" in rels
        assert "packages/auth/pyproject.toml" in rels
        assert "apps/backend/pyproject.toml" in rels

    def test_validation_success_live_repo_audit_clean(self) -> None:
        """Live tree must already satisfy the gate after this PR's edits."""
        assert gate.audit_tree(gate.ROOT) == []

    def test_validation_success_parse_skips_comments_and_keeps_unquoted(
        self,
    ) -> None:
        text = (
            "[tool.pytest.ini_options]\n"
            "filterwarnings = [\n"
            "  # keep errors\n"
            '  "error",\n'
            "  default,\n"
            "]\n"
        )
        assert gate.parse_filterwarnings(text) == ["error", "default"]

    def test_validation_failure_filterwarnings_key_without_list(self) -> None:
        text = "[tool.pytest.ini_options]\nfilterwarnings = true\n"
        assert gate.parse_filterwarnings(text) is None

    def test_validation_success_rel_outside_root_falls_back(self) -> None:
        outside = Path("/tmp/not-in-repo/pyproject.toml")
        assert gate._rel(outside) == str(outside)

    def test_validation_success_iter_skips_missing_trees(self, tmp_path: Path) -> None:
        # no apps/ or packages/; no root pyproject
        assert gate.iter_candidate_pyprojects(tmp_path) == []
        (tmp_path / "apps").mkdir()
        (tmp_path / "apps" / "orphan.txt").write_text("x", encoding="utf-8")
        assert gate.iter_candidate_pyprojects(tmp_path) == []

    def test_validation_success_member_dir_rejects_foreign_paths(
        self, tmp_path: Path
    ) -> None:
        foreign = tmp_path / "elsewhere" / "pyproject.toml"
        foreign.parent.mkdir()
        foreign.write_text(_MINIMAL_PROJECT, encoding="utf-8")
        assert gate._member_dir(foreign, root=tmp_path / "repo") is None
        shallow = tmp_path / "pyproject.toml"
        shallow.write_text(_MINIMAL_PROJECT, encoding="utf-8")
        assert gate._member_dir(shallow, root=tmp_path) is None

    def test_validation_success_root_without_section_still_required(
        self, tmp_path: Path
    ) -> None:
        (tmp_path / "apps").mkdir()
        (tmp_path / "packages").mkdir()
        root_py = tmp_path / "pyproject.toml"
        root_py.write_text(_MINIMAL_PROJECT, encoding="utf-8")
        assert gate.requires_pytest_filterwarnings(root_py, root=tmp_path) is True
        findings = gate.audit_pyproject(root_py, root=tmp_path)
        assert findings[0].code == "missing_pytest_section"

    def test_validation_success_non_member_pyproject_not_required(
        self, tmp_path: Path
    ) -> None:
        (tmp_path / "apps").mkdir()
        (tmp_path / "packages").mkdir()
        extra = tmp_path / "tooling" / "pyproject.toml"
        extra.parent.mkdir()
        extra.write_text(_MINIMAL_PROJECT, encoding="utf-8")
        assert gate.requires_pytest_filterwarnings(extra, root=tmp_path) is False
        assert gate.audit_pyproject(extra, root=tmp_path) == []

    def test_validation_success_module_main_entrypoint(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        block = '[tool.pytest.ini_options]\nfilterwarnings = [\n  "error",\n]\n'
        _root_pyproject(tmp_path, block)
        (tmp_path / "apps").mkdir(exist_ok=True)
        (tmp_path / "packages").mkdir(exist_ok=True)
        script = Path(gate.__file__).resolve()
        monkeypatch.setattr(sys, "argv", [str(script), "--root", str(tmp_path)])
        with pytest.raises(SystemExit) as excinfo:
            runpy.run_path(str(script), run_name="__main__")
        assert excinfo.value.code == 0
