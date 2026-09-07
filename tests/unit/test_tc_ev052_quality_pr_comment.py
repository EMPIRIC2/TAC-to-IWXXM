"""TC-EV052-004 / TC-EV052-005 - quality sticky PR comment (EV-052 / S061).

Contract asserts for ``quality-pr-comment`` job + sticky marker parity with
EV-036 ``coverage-pr-comment`` (update-in-place; distinct marker).
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
CI_CD = ROOT / ".github" / "workflows" / "ci-cd.yml"
FORMAT_SCRIPT = ROOT / "scripts" / "ci" / "format_quality_pr_comment.py"
COLLECT_SCRIPT = ROOT / "scripts" / "ci" / "collect_quality_pr_stats.py"
QUALITY_MARKER = "<!-- quality-pr-comment -->"
COVERAGE_MARKER = "<!-- EV-036-coverage-comment -->"


@pytest.fixture(scope="module")
def workflow_doc() -> dict:
    assert CI_CD.is_file()
    doc = yaml.safe_load(CI_CD.read_text(encoding="utf-8"))
    assert isinstance(doc, dict)
    return doc


@pytest.mark.unit
class TestTcEv052004QualityStickyJob:
    """TC-EV052-004 - second sticky comment job wired in ci-cd.yml."""

    def test_quality_pr_comment_job_present(self, workflow_doc: dict) -> None:
        jobs = workflow_doc["jobs"]
        assert "quality-pr-comment" in jobs
        assert "coverage-pr-comment" in jobs

    def test_job_shape_parity_with_coverage(self, workflow_doc: dict) -> None:
        job = workflow_doc["jobs"]["quality-pr-comment"]
        assert job.get("if") == "github.event_name == 'pull_request'"
        perms = job.get("permissions") or {}
        assert perms.get("pull-requests") == "write"
        step_names = [s.get("name", "") for s in job.get("steps", [])]
        assert any("Collect quality" in n for n in step_names)
        assert any("Format quality" in n for n in step_names)
        assert any("sticky" in n.lower() or "Post or update" in n for n in step_names)

    def test_scripts_exist(self) -> None:
        assert FORMAT_SCRIPT.is_file()
        assert COLLECT_SCRIPT.is_file()


@pytest.mark.unit
class TestTcEv052005StickyIdempotenceParity:
    """TC-EV052-005 - distinct marker + update-in-place github-script pattern."""

    def test_markers_distinct(self) -> None:
        fmt = FORMAT_SCRIPT.read_text(encoding="utf-8")
        assert QUALITY_MARKER in fmt
        assert COVERAGE_MARKER not in fmt
        cov = (ROOT / "scripts" / "ci" / "format_coverage_pr_comment.py").read_text(
            encoding="utf-8"
        )
        assert COVERAGE_MARKER in cov
        assert QUALITY_MARKER not in cov

    def test_github_script_updates_in_place(self, workflow_doc: dict) -> None:
        job = workflow_doc["jobs"]["quality-pr-comment"]
        scripts = [
            s.get("with", {}).get("script", "")
            for s in job.get("steps", [])
            if s.get("uses", "").startswith("actions/github-script")
        ]
        assert scripts, "expected github-script sticky step"
        body = scripts[0]
        assert "quality-pr-comment" in body
        assert "EV-036-coverage-comment" in body  # guard: must not reuse
        assert "updateComment" in body
        assert "createComment" in body
        assert "listComments" in body
        assert "c.body?.includes(marker)" in body or "includes(marker)" in body

    def test_ops_doc_lists_quality_pr_comment(self) -> None:
        ops = ROOT / "docs" / "ops" / "DEVELOPMENT.md"
        text = ops.read_text(encoding="utf-8")
        assert "coverage-pr-comment" in text
        # T2.4 docs parity - mention quality sticky job alongside coverage.
        assert "quality-pr-comment" in text
