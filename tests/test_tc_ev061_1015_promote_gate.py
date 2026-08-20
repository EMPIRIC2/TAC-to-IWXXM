"""TC-EV061-1015 — Stricter stage→main promote gate (S071 / EV-061 / #1015).

Inventory + CI/ruleset contracts for D-S071-ci / UJ-DEV-009.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
CI_CD = ROOT / ".github" / "workflows" / "ci-cd.yml"
RULESETS = ROOT / "scripts" / "deploy" / "apply_gh_branch_rulesets.sh"
DEPLOY_MD = ROOT / "docs" / "deploy.md"
PROMOTE_TEMPLATE = (
    ROOT / ".github" / "PULL_REQUEST_TEMPLATE" / "promote-stage-to-main.md"
)

# Locked GitHub check contexts (must match job `name:` and ruleset script).
LOCKED_LINT = "Lint"
LOCKED_TYPECHECK = "Typecheck"
LOCKED_E2E_FULL = "E2E Full (Playwright)"
LOCKED_E2E_SMOKE = "E2E Smoke (Playwright)"
LOCKED_STAGING_GATE = "Staging gate"

# Full unit matrix display names (Test (*)).
UNIT_TEST_CONTEXTS = (
    "Test (shared)",
    "Test (auth)",
    "Test (backend)",
    "Test (frontend)",
    "Test (tac2iwxxm)",
    "Test (iwxxm-validate)",
    "Test (tac-validate)",
    "Test (dissemination)",
    "Test (worker)",
    "Test (bugs)",
    "Test (alembic / TC-EV031-002)",
)

PROMOTE_REQUIRED = (
    *UNIT_TEST_CONTEXTS,
    LOCKED_LINT,
    LOCKED_TYPECHECK,
    LOCKED_E2E_FULL,
    LOCKED_STAGING_GATE,
)


@pytest.fixture(scope="module")
def workflow_text() -> str:
    assert CI_CD.is_file()
    return CI_CD.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def workflow_doc(workflow_text: str) -> dict[str, Any]:
    doc = yaml.safe_load(workflow_text)
    assert isinstance(doc, dict)
    assert "jobs" in doc
    return doc


def _job_by_name(jobs: dict[str, Any], name: str) -> tuple[str, dict[str, Any]]:
    for job_id, job in jobs.items():
        if not isinstance(job, dict):
            continue
        if job.get("name") == name:
            return job_id, job
    raise AssertionError(f"no job with name={name!r}")


@pytest.mark.unit
class TestTcEv0611015001Inventory:
    """TC-EV061-1015-001 — promote required-check inventory is documented + wired."""

    def test_deploy_md_lists_promote_required_contexts(self) -> None:
        text = DEPLOY_MD.read_text(encoding="utf-8")
        assert "EV-061" in text or "#1015" in text
        for ctx in PROMOTE_REQUIRED:
            assert ctx in text, f"deploy.md missing required context {ctx!r}"
        # Smoke alone is not the promote E2E bar.
        assert LOCKED_E2E_SMOKE in text or "smoke-only" in text.lower()
        assert LOCKED_E2E_FULL in text

    def test_promote_pr_template_calls_out_stricter_gate(self) -> None:
        text = PROMOTE_TEMPLATE.read_text(encoding="utf-8")
        assert "lint" in text.lower()
        assert "typecheck" in text.lower()
        assert "full E2E" in text or "E2E Full" in text
        assert "Staging gate" in text

    def test_workflow_jobs_exist_with_locked_names(
        self, workflow_doc: dict[str, Any]
    ) -> None:
        jobs = workflow_doc["jobs"]
        _job_by_name(jobs, LOCKED_LINT)
        _job_by_name(jobs, LOCKED_TYPECHECK)
        _job_by_name(jobs, LOCKED_E2E_FULL)
        _job_by_name(jobs, LOCKED_STAGING_GATE)
        # Smoke remains for Deploy needs; full is separate.
        _job_by_name(jobs, LOCKED_E2E_SMOKE)

    def test_unit_matrix_covers_test_star_packages(
        self, workflow_doc: dict[str, Any]
    ) -> None:
        packages = set(workflow_doc["jobs"]["test"]["strategy"]["matrix"]["package"])
        expected = {
            "shared",
            "auth",
            "backend",
            "frontend",
            "tac2iwxxm",
            "iwxxm-validate",
            "tac-validate",
            "dissemination",
            "worker",
            "bugs",
        }
        assert expected.issubset(packages)


@pytest.mark.unit
class TestTcEv0611015002CiAndRulesets:
    """TC-EV061-1015-002 — CI jobs + ruleset script enforce the stricter set."""

    def test_lint_job_runs_make_lint(
        self, workflow_doc: dict[str, Any], workflow_text: str
    ) -> None:
        _job_id, job = _job_by_name(workflow_doc["jobs"], LOCKED_LINT)
        assert job.get("if") in (None, "")
        assert "make lint" in workflow_text or "lint-py" in workflow_text
        step_runs = "\n".join(
            str(s.get("run", "")) for s in job.get("steps", []) if isinstance(s, dict)
        )
        assert "make lint" in step_runs or (
            "ruff check" in step_runs and "lint" in step_runs
        )

    def test_typecheck_job_runs_make_typecheck(
        self, workflow_doc: dict[str, Any]
    ) -> None:
        _job_id, job = _job_by_name(workflow_doc["jobs"], LOCKED_TYPECHECK)
        assert job.get("if") in (None, "")
        step_runs = "\n".join(
            str(s.get("run", "")) for s in job.get("steps", []) if isinstance(s, dict)
        )
        assert "make typecheck" in step_runs

    def test_e2e_full_runs_on_promote_prs_only(
        self, workflow_doc: dict[str, Any]
    ) -> None:
        _job_id, job = _job_by_name(workflow_doc["jobs"], LOCKED_E2E_FULL)
        cond = job.get("if") or ""
        assert "pull_request" in cond
        assert "main" in cond
        step_runs = "\n".join(
            str(s.get("run", "")) for s in job.get("steps", []) if isinstance(s, dict)
        )
        assert "test-e2e-playwright" in step_runs
        assert "test-e2e-playwright-smoke" not in step_runs

    def test_e2e_full_distinct_from_smoke(self, workflow_doc: dict[str, Any]) -> None:
        full_id, _ = _job_by_name(workflow_doc["jobs"], LOCKED_E2E_FULL)
        smoke_id, _ = _job_by_name(workflow_doc["jobs"], LOCKED_E2E_SMOKE)
        assert full_id != smoke_id

    def test_ruleset_script_lists_promote_contexts(self) -> None:
        text = RULESETS.read_text(encoding="utf-8")
        # Shared base checks
        for ctx in (
            LOCKED_LINT,
            LOCKED_TYPECHECK,
            *UNIT_TEST_CONTEXTS,
        ):
            assert ctx in text, f"ruleset script missing {ctx!r}"
        # Main-only extras
        assert LOCKED_STAGING_GATE in text
        assert LOCKED_E2E_FULL in text
        # Must not treat smoke as the promote E2E bar.
        main_extra = text[text.index("protect-main") :]
        assert LOCKED_E2E_FULL in main_extra
        assert LOCKED_E2E_SMOKE not in main_extra or LOCKED_E2E_FULL in main_extra
