"""TC-EV036 - local-first CI / husky / slim remote workflow contracts (S044 / EV-036).

Dense asserts for M5 deepen: commit medium validate, push Compose via ``make ci``,
remote drops validate + Compose, keeps unit matrix + coverage PR comment.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
HUSKY_PRE_COMMIT = ROOT / ".husky" / "pre-commit"
HUSKY_PRE_PUSH = ROOT / ".husky" / "pre-push"
MAKEFILE = ROOT / "Makefile"
CI_CD = ROOT / ".github" / "workflows" / "ci-cd.yml"
COVERAGE_SCRIPT = ROOT / "scripts" / "ci" / "format_coverage_pr_comment.py"
PRE_COMMIT_CFG = ROOT / ".pre-commit-config.yaml"


@pytest.fixture(scope="module")
def makefile_text() -> str:
    assert MAKEFILE.is_file()
    return MAKEFILE.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def workflow_text() -> str:
    assert CI_CD.is_file()
    return CI_CD.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def workflow_doc(workflow_text: str) -> dict:
    doc = yaml.safe_load(workflow_text)
    assert isinstance(doc, dict)
    assert "jobs" in doc
    return doc


@pytest.mark.unit
class TestTcEv036001PreCommitMediumValidate:
    """TC-EV036-001 - husky pre-commit runs fast + medium validate."""

    def test_husky_pre_commit_exists_and_executable_bit_path(self) -> None:
        assert HUSKY_PRE_COMMIT.is_file()
        text = HUSKY_PRE_COMMIT.read_text(encoding="utf-8")
        assert text.startswith("#!/"), "husky pre-commit must be a shell script"
        assert "set -e" in text

    def test_husky_pre_commit_runs_pre_commit_framework(self) -> None:
        text = HUSKY_PRE_COMMIT.read_text(encoding="utf-8")
        assert "pre-commit run" in text
        assert "uv run pre-commit" in text or "pre-commit run" in text

    def test_husky_pre_commit_runs_validate_ci_medium(self) -> None:
        text = HUSKY_PRE_COMMIT.read_text(encoding="utf-8")
        assert "validate-ci-medium" in text
        assert "make validate-ci-medium" in text

    def test_husky_pre_commit_does_not_run_full_ci_or_integration(self) -> None:
        text = HUSKY_PRE_COMMIT.read_text(encoding="utf-8")
        assert "make ci\n" not in text
        assert not re.search(r"\bmake ci\b", text)
        assert "test-integration" not in text
        assert "ci-prepush" not in text

    def test_makefile_defines_validate_ci_medium(self, makefile_text: str) -> None:
        assert re.search(r"^validate-ci-medium:", makefile_text, re.M)
        assert "config-guard" in makefile_text
        assert "env-check" in makefile_text
        assert "audit-frontend" in makefile_text
        # medium target should not pull validate-fast (de-dupe with husky fast hooks)
        medium_block = _makefile_recipe(makefile_text, "validate-ci-medium")
        assert "validate-fast" not in medium_block
        assert "config-guard" in medium_block
        assert "env-check" in medium_block
        assert "audit-frontend" in medium_block

    def test_makefile_validate_ci_composes_fast_and_medium(
        self, makefile_text: str
    ) -> None:
        recipe = _makefile_recipe(makefile_text, "validate-ci")
        assert "validate-fast" in recipe
        assert "validate-ci-medium" in recipe

    def test_pre_commit_run_target_includes_medium(self, makefile_text: str) -> None:
        recipe = _makefile_recipe(makefile_text, "pre-commit-run")
        assert "validate-ci-medium" in recipe

    def test_pre_commit_config_documents_ev036_split(self) -> None:
        text = PRE_COMMIT_CFG.read_text(encoding="utf-8")
        assert "EV-036" in text or "validate-ci-medium" in text
        assert "pre-push" in text.lower()


@pytest.mark.unit
class TestTcEv036002PrePushMakeCi:
    """TC-EV036-002 - husky pre-push runs make ci; no validate-ci; no remote Compose."""

    def test_husky_pre_push_runs_make_ci(self) -> None:
        text = HUSKY_PRE_PUSH.read_text(encoding="utf-8")
        assert HUSKY_PRE_PUSH.is_file()
        assert "set -e" in text
        assert re.search(r"\bmake ci\b", text)
        assert "18000" in text or "18001" in text or "Docker" in text

    def test_husky_pre_push_does_not_rerun_validate(self) -> None:
        text = HUSKY_PRE_PUSH.read_text(encoding="utf-8")
        # Ignore comments; assert no make validate* invocation.
        code_lines = [
            ln
            for ln in text.splitlines()
            if ln.strip() and not ln.strip().startswith("#")
        ]
        code = "\n".join(code_lines)
        assert not re.search(r"\bmake\s+validate", code)
        assert not re.search(r"\bvalidate-ci(-medium)?\b", code)

    def test_makefile_ci_includes_integration(self, makefile_text: str) -> None:
        recipe = _makefile_recipe(makefile_text, "ci")
        assert "ci-prepush" in recipe
        assert "test-integration" in recipe

    def test_makefile_pre_push_run_is_make_ci(self, makefile_text: str) -> None:
        recipe = _makefile_recipe(makefile_text, "pre-push-run")
        assert re.search(r"\bci\b", recipe)
        code_lines = [
            ln
            for ln in recipe.splitlines()
            if ln.strip() and not ln.lstrip().startswith("#")
        ]
        code = "\n".join(code_lines)
        assert not re.search(r"\bvalidate-ci\b", code)
        assert re.search(r"\bci\b", code)

    def test_remote_workflow_has_no_integration_matrix_entry(
        self, workflow_doc: dict
    ) -> None:
        test_job = workflow_doc["jobs"]["test"]
        matrix = test_job["strategy"]["matrix"]["package"]
        assert "integration" not in matrix
        assert "backend" in matrix
        assert "frontend" in matrix
        assert "tac2iwxxm" in matrix

    def test_remote_workflow_has_no_compose_integration_steps(
        self, workflow_text: str
    ) -> None:
        assert "docker compose up -d backend frontend" not in workflow_text
        assert "Set integration stack environment" not in workflow_text
        assert "Run wis2box Compose harness hook" not in workflow_text
        assert "matrix.package == 'integration'" not in workflow_text


@pytest.mark.unit
class TestTcEv036003RemoteUnitsCoverageNoValidate:
    """TC-EV036-003 - no validate job; units+coverage+PR comment; deploy needs test."""

    def test_no_validate_job(self, workflow_doc: dict) -> None:
        jobs = workflow_doc["jobs"]
        assert "validate" not in jobs
        assert "test" in jobs
        assert "coverage-pr-comment" in jobs
        assert "test-alembic" in jobs
        assert "tac2iwxxm-native" in jobs
        assert "e2e-smoke" in jobs
        assert "deploy" in jobs

    def test_no_job_needs_validate(self, workflow_text: str) -> None:
        assert "needs: [validate]" not in workflow_text
        assert "needs: [validate," not in workflow_text

    def test_unit_matrix_packages_present(self, workflow_doc: dict) -> None:
        packages = set(workflow_doc["jobs"]["test"]["strategy"]["matrix"]["package"])
        required = {
            "shared",
            "auth",
            "backend",
            "frontend",
            "tac2iwxxm",
            "iwxxm-validate",
            "tac-validate",
            "dissemination",
            "bugs",
        }
        assert required.issubset(packages)
        assert "integration" not in packages

    def test_coverage_xml_and_fail_under_remain(self, workflow_text: str) -> None:
        assert "--cov-fail-under" in workflow_text
        assert "coverage.xml" in workflow_text
        assert "Upload package coverage XML artifact" in workflow_text
        assert "coverage-xml-" in workflow_text

    def test_coverage_pr_comment_job_shape(self, workflow_doc: dict) -> None:
        job = workflow_doc["jobs"]["coverage-pr-comment"]
        assert job["needs"] == ["test"] or job["needs"] == "test"
        assert job.get("if") == "github.event_name == 'pull_request'"
        perms = job.get("permissions") or {}
        assert perms.get("pull-requests") == "write"
        step_names = [s.get("name", "") for s in job.get("steps", [])]
        assert any("Format coverage" in n for n in step_names)
        assert any("sticky" in n.lower() or "Post or update" in n for n in step_names)

    def test_coverage_formatter_script_exists(self) -> None:
        assert COVERAGE_SCRIPT.is_file()
        text = COVERAGE_SCRIPT.read_text(encoding="utf-8")
        assert "EV-036-coverage-comment" in text
        assert "coverage.xml" in text

    def test_deploy_needs_includes_test(self, workflow_doc: dict) -> None:
        needs = workflow_doc["jobs"]["deploy"]["needs"]
        assert "test" in needs
        assert "test-alembic" in needs
        assert "tac2iwxxm-native" in needs
        assert "validate" not in needs

    def test_retained_runner_only_jobs_have_no_validate_dep(
        self, workflow_doc: dict
    ) -> None:
        for name in ("test-alembic", "tac2iwxxm-native", "e2e-smoke"):
            job = workflow_doc["jobs"][name]
            needs = job.get("needs")
            if needs is None:
                continue
            if isinstance(needs, str):
                needs = [needs]
            assert "validate" not in needs

    def test_workflow_comments_document_ev036(self, workflow_text: str) -> None:
        assert "EV-036" in workflow_text
        assert (
            "local pre-commit" in workflow_text.lower()
            or "local-push" in workflow_text.lower()
            or "pre-push" in workflow_text.lower()
        )


def _makefile_recipe(makefile: str, target: str) -> str:
    """Return the recipe lines for a simple single-line or continued Makefile target."""
    pattern = re.compile(rf"^{re.escape(target)}:(.*)$", re.M)
    match = pattern.search(makefile)
    assert match is not None, f"missing Makefile target {target}"
    # Prefer same-line prerequisites / recipe fragment plus following tab lines until next target
    start = match.end()
    lines = [match.group(1)]
    for line in makefile[start:].splitlines()[1:]:
        if (
            not line.startswith("\t")
            and line.strip()
            and not line.startswith("#")
            and re.match(r"^[A-Za-z0-9_.-]+:", line)
        ):
            break
        if (
            line.startswith("\t")
            or line.endswith("\\")
            or (lines and lines[-1].endswith("\\"))
        ):
            lines.append(line)
        elif not line.strip():
            continue
        else:
            break
    return "\n".join(lines)
