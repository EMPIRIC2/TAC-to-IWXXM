"""TC-EV045 — Rust crate CI contracts (S054 / EV-045 / #725).

Asserts Makefile ``rust-check`` parity and ``ci-cd.yml`` locked job names /
deploy.needs for F13/F14 deepen (D-S054-04).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
MAKEFILE = ROOT / "Makefile"
CI_CD = ROOT / ".github" / "workflows" / "ci-cd.yml"
RULESETS = ROOT / "scripts" / "deploy" / "apply_gh_branch_rulesets.sh"

LOCKED_RUST_GATE = "Rust crates (fmt/clippy/test)"
LOCKED_TAC2IWXXM = "tac2iwxxm PyO3 (maturin)"
LOCKED_IWXXM_VALIDATE = "iwxxm-validate PyO3 (maturin)"


@pytest.fixture(scope="module")
def makefile_text() -> str:
    assert MAKEFILE.is_file()
    return MAKEFILE.read_text(encoding="utf-8")


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


def _makefile_recipe(makefile: str, target: str) -> str:
    pattern = re.compile(rf"^{re.escape(target)}:(.*)$", re.M)
    match = pattern.search(makefile)
    assert match is not None, f"missing Makefile target {target}"
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


def _job_by_name(jobs: dict[str, Any], name: str) -> tuple[str, dict[str, Any]]:
    for job_id, job in jobs.items():
        if not isinstance(job, dict):
            continue
        if job.get("name") == name:
            return job_id, job
    raise AssertionError(f"no job with name={name!r}")


@pytest.mark.unit
class TestTcEv045005MakefileRustCheck:
    """TC-EV045-005 — make rust-check mirrors CI (cargo both + both maturin)."""

    def test_rust_check_target_exists(self, makefile_text: str) -> None:
        assert re.search(r"^rust-check:", makefile_text, re.M)

    def test_rust_check_covers_both_crates_and_native(self, makefile_text: str) -> None:
        recipe = _makefile_recipe(makefile_text, "rust-check")
        # Cargo path for both packages (direct or via helper targets)
        assert "tac2iwxxm" in recipe
        assert "iwxxm-validate" in recipe
        assert "fmt" in recipe or "cargo fmt" in recipe
        assert "clippy" in recipe
        assert "cargo test" in recipe or "test-*-native" in recipe or "test-" in recipe
        assert "test-tac2iwxxm-native" in recipe
        assert "test-iwxxm-validate-native" in recipe


@pytest.mark.unit
class TestTcEv045CiJobNames:
    """TC-EV045-001..004 / AC6 — locked check contexts in ci-cd.yml."""

    def test_rust_gate_job_exact_name(self, workflow_doc: dict[str, Any]) -> None:
        jobs = workflow_doc["jobs"]
        job_id, job = _job_by_name(jobs, LOCKED_RUST_GATE)
        assert job_id
        needs = job.get("needs")
        assert needs, "gate job must need the cargo matrix"
        if isinstance(needs, str):
            needs = [needs]
        assert any("rust" in str(n) for n in needs)

    def test_rust_crates_matrix_present(
        self, workflow_doc: dict[str, Any], workflow_text: str
    ) -> None:
        jobs = workflow_doc["jobs"]
        assert "rust-crates" in jobs
        rust = jobs["rust-crates"]
        assert isinstance(rust.get("strategy"), dict)
        assert "matrix" in rust["strategy"]
        assert "fmt --check" in workflow_text
        assert "clippy" in workflow_text
        assert "-D warnings" in workflow_text
        assert "cargo test" in workflow_text

    def test_maturin_locked_names_via_check_name(
        self, workflow_doc: dict[str, Any], workflow_text: str
    ) -> None:
        assert LOCKED_TAC2IWXXM in workflow_text
        assert LOCKED_IWXXM_VALIDATE in workflow_text
        assert "matrix.check_name" in workflow_text or "${{ matrix.check_name }}" in (
            workflow_text
        )
        assert "IWXXM_VALIDATE_REQUIRE_RUST" in workflow_text
        assert "TAC2IWXXM_REQUIRE_RUST" in workflow_text

    def test_no_path_filter_only_on_workflow(
        self, workflow_doc: dict[str, Any]
    ) -> None:
        """D-S054-04-trigger=1 — default PR/push, not path-filter-only rust jobs."""
        on = workflow_doc.get("on") or workflow_doc.get(True)
        assert isinstance(on, dict)
        assert "pull_request" in on
        assert "push" in on
        # Top-level path filters would skip most PRs — forbid for this workflow.
        for key in ("push", "pull_request"):
            node = on[key]
            if isinstance(node, dict):
                assert "paths" not in node
                assert "paths-ignore" not in node


@pytest.mark.unit
class TestTcEv045DeployNeeds:
    """Deploy must wait on rust gate + native maturin matrix."""

    def test_deploy_needs_rust_and_native(self, workflow_doc: dict[str, Any]) -> None:
        deploy = workflow_doc["jobs"]["deploy"]
        needs = deploy.get("needs")
        assert needs
        if isinstance(needs, str):
            needs = [needs]
        need_set = set(needs)
        assert "test" in need_set
        assert "test-alembic" in need_set
        # Gate job id (not display name)
        assert "rust-crates-gate" in need_set
        # Job id retained for EV-036 contracts; matrix covers both PyO3 packages.
        assert "tac2iwxxm-native" in need_set


@pytest.mark.unit
class TestTcEv045006RulesetScript:
    """TC-EV045-006 docs half — apply script lists locked contexts."""

    def test_apply_script_lists_locked_contexts(self) -> None:
        text = RULESETS.read_text(encoding="utf-8")
        assert LOCKED_RUST_GATE in text
        assert LOCKED_TAC2IWXXM in text
        assert LOCKED_IWXXM_VALIDATE in text
